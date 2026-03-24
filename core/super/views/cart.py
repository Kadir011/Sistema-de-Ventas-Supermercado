from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.utils import timezone
import decimal
import uuid
from decimal import Decimal
from core.super.models import Cart, CartItem, Product, Sale, SaleDetail, Customer, PaymentMethod, Seller
from core.super.services.checkout_service import CheckoutService
from core.super.services.payment_processors import get_processor
from core.super.services.idempotency_service import IdempotencyService


@login_required
def add_to_cart(request, product_id):
    """
    Agrega un producto al carrito.

    Idempotencia: usa select_for_update() + F() para incrementar la cantidad
    de forma atómica, evitando que dos requests concurrentes (doble clic)
    sumen +2 en lugar de +1. Si el item ya está al tope de stock, devuelve
    error sin modificar nada.
    """
    product = get_object_or_404(Product, pk=product_id, state=True)

    if product.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Producto sin stock'}, status=400)

    with transaction.atomic():
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Bloqueo a nivel de fila para evitar race conditions en concurrencia
        cart_item, item_created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not item_created:
            # Recargar para tener el valor más actualizado tras el lock
            cart_item.refresh_from_db()
            if cart_item.quantity >= product.stock:
                return JsonResponse({'success': False, 'error': 'No hay suficiente stock'}, status=400)
            # Incremento atómico: evita que dos requests simultáneos lean el
            # mismo valor y ambos sumen 1 (race condition clásico)
            CartItem.objects.filter(pk=cart_item.pk).update(quantity=F('quantity') + 1)

    messages.success(request, f'{product.name} agregado al carrito')
    cart.refresh_from_db()
    return JsonResponse({'success': True, 'cart_count': cart.get_item_count()})


@login_required
def update_cart_item(request, item_id):
    """
    Actualiza la cantidad de un item.
    Ya era idempotente (fija valor absoluto). Se mantiene sin cambios.
    """
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
            messages.info(request, 'Producto eliminado del carrito')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Solo hay {cart_item.product.stock} unidades disponibles')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cantidad actualizada')

    return redirect('super:cart')


@login_required
def remove_from_cart(request, item_id):
    """
    Elimina un item del carrito.
    get_object_or_404 garantiza 404 si ya fue eliminado (no silencia el doble delete).
    """
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} eliminado del carrito')
    return redirect('super:cart')


@login_required
def cart_count(request):
    """API para obtener cantidad de items en el carrito."""
    try:
        cart = Cart.objects.get(user=request.user)
        count = cart.get_item_count()
    except Cart.DoesNotExist:
        count = 0
    return JsonResponse({'count': count})


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'super/shop/cart.html'
    login_url = '/security/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            cart = Cart.objects.get(user=self.request.user)
            items = CartItem.objects.filter(cart=cart).select_related('product')
            context['cart'] = cart
            context['items'] = items
            context['subtotal'] = cart.get_subtotal()
            context['iva'] = cart.get_iva()
            context['total'] = cart.get_total()
        except Cart.DoesNotExist:
            context['cart'] = None
            context['items'] = []
            context['subtotal'] = 0
            context['iva'] = 0
            context['total'] = 0

        context['title'] = 'Mi Carrito'
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'super/shop/checkout.html'
    login_url = '/security/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            cart = Cart.objects.get(user=self.request.user)
            items = CartItem.objects.filter(cart=cart).select_related('product')

            customer = Customer.objects.filter(email=self.request.user.email).first()
            discount_pct = customer.discount_percentage if customer else Decimal('0.00')

            cart_total = cart.get_total()
            discount_amount = cart_total * (discount_pct / 100)
            final_total = cart_total - discount_amount

            context['items'] = items
            context['subtotal'] = cart.get_subtotal()
            context['iva'] = cart.get_iva()
            context['discount'] = discount_amount
            context['discount_pct'] = discount_pct
            context['total'] = final_total
            context['payment_methods'] = PaymentMethod.objects.all()
            context['customer_dni'] = customer.dni if customer else ''

            # ── Idempotencia ──────────────────────────────────────────────
            # Se genera un UUID nuevo cada vez que el usuario ABRE el checkout
            # (GET). Este UUID viaja en un campo hidden del formulario y se
            # guarda en la venta. Si el mismo UUID llega dos veces (doble
            # submit, F5, botón atrás), el segundo request detecta la venta
            # existente y redirige sin crear nada nuevo.
            context['idempotency_key'] = str(uuid.uuid4())

        except Cart.DoesNotExist:
            pass

        context['title'] = 'Finalizar Compra'
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # ── Guardia de idempotencia ───────────────────────────────────────
        idempotency_service = IdempotencyService()
        raw_key = request.POST.get('idempotency_key', '').strip()
        idempotency_key = idempotency_service.parse_key(raw_key)

        if idempotency_key:
            existing_sale = idempotency_service.find_existing(idempotency_key)
            if existing_sale:
                messages.info(request, 'Esta compra ya fue procesada.')
                return redirect('super:order_detail', pk=existing_sale.pk)

        try:
            service = CheckoutService()  # Crear servicio de checkout (SRP)
            cart = Cart.objects.get(user=request.user)
            items = CartItem.objects.filter(cart=cart).select_related('product')

            if not items.exists():
                return redirect('super:cart')
            
            customer = service.resolve_customer(
                request.user,
                request.POST.get('dni_type'),
                request.POST.get('dni')
            )
            
            totals = service.calculate_totals(cart, customer)
            
            payment_method_id = request.POST.get('payment_method')
            payment_method = PaymentMethod.objects.get(id_payment_method=payment_method_id)

            processor = get_processor(payment_method.name)
            amount_received, change = processor.calculate_received_and_change(totals['total'], request.POST)

            if amount_received < totals['total']:
                messages.error(request, 'Monto recibido insuficiente')
                return redirect('super:checkout')

            sale = service.create_sale(
                request.user,
                customer,
                payment_method_id,
                totals,
                amount_received,
                change,
                idempotency_key,
                card_number_masked=request.POST.get('card_number_masked'),
                transfer_account_masked=request.POST.get('transfer_account_masked')
            )
            
            service.register_items(sale, items)
            cart.delete()
            
            messages.success(request, '¡Compra finalizada!')
            return redirect('super:order_detail', pk=sale.pk)

        except Customer.DoesNotExist:
            messages.error(request, 'Error al procesar el cliente')
            return redirect('super:checkout')
        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Método de pago inválido')
            return redirect('super:checkout')
        except (ValueError, decimal.ConversionSyntax) as e:
            messages.error(request, f'Error en los datos numéricos: {str(e)}')
            return redirect('super:checkout')
        except Exception as e:
            messages.error(request, f'Error al procesar la compra: {str(e)}')
            return redirect('super:checkout')