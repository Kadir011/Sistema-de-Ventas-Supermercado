from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from core.super.models import Cart, CartItem, Product, Sale, SaleDetail, Customer, PaymentMethod, Seller

@login_required
def add_to_cart(request, product_id):
    """Agregar producto al carrito"""
    product = get_object_or_404(Product, pk=product_id, state=True)
    
    if product.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Producto sin stock'}, status=400)
    
    # Obtener o crear carrito
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Verificar si el producto ya está en el carrito
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not item_created:
        # Si ya existe, aumentar cantidad
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            return JsonResponse({'success': False, 'error': 'No hay suficiente stock'}, status=400)
    
    messages.success(request, f'{product.name} agregado al carrito')
    return JsonResponse({'success': True, 'cart_count': cart.get_item_count()})


@login_required
def update_cart_item(request, item_id):
    """Actualizar cantidad de un item del carrito"""
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
    """Eliminar producto del carrito"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} eliminado del carrito')
    return redirect('super:cart')


@login_required
def cart_count(request):
    """API para obtener cantidad de items en el carrito"""
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
                
        except Cart.DoesNotExist:
            return redirect('super:cart')
        
        context['title'] = 'Finalizar Compra'
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
            items = CartItem.objects.filter(cart=cart).select_related('product')
            
            if not items.exists():
                return redirect('super:cart')
            
            # Lógica Consumidor Final vs Datos Personales
            dni_type = request.POST.get('dni_type')
            if dni_type == 'final':
                customer_dni = '9999999999'
                # Buscamos el cliente genérico
                customer, _ = Customer.objects.get_or_create(
                    dni=customer_dni,
                    defaults={'name': 'CONSUMIDOR', 'last_name': 'FINAL', 'address': 'S/N'}
                )
            else:
                customer_dni = request.POST.get('dni')
                customer, _ = Customer.objects.get_or_create(
                    email=request.user.email,
                    defaults={
                        'name': request.user.first_name,
                        'last_name': request.user.last_name,
                        'dni': customer_dni,
                        'phone': request.user.phone_number,
                        'address': request.user.address
                    }
                )
                if customer.dni != customer_dni:
                    customer.dni = customer_dni
                    customer.save()

            # Asegurar Vendedor Online
            seller, _ = Seller.objects.get_or_create(dni='9999999999', defaults={'name': 'Vendedor', 'last_name': 'Online'})

            # Totales
            cart_total = cart.get_total()
            discount_amount = cart_total * (customer.discount_percentage / 100)
            final_total = cart_total - discount_amount
            amount_received = Decimal(request.POST.get('amount_received', '0'))
            
            if amount_received < final_total:
                messages.error(request, 'Monto recibido insuficiente')
                return redirect('super:checkout')
            
            change = amount_received - final_total

            # Crear Venta
            sale = Sale.objects.create(
                customer=customer,
                seller=seller,
                payment_id=request.POST.get('payment_method'),
                sale_date=timezone.now(),
                subtotal=cart.get_subtotal(),
                iva=cart.get_iva(),
                discount=discount_amount,
                total=final_total,
                amount_received=amount_received,
                change=change
            )
            
            for item in items:
                SaleDetail.objects.create(
                    sale=sale, product=item.product, quantity=item.quantity,
                    price=item.product.price, subtotal=item.get_subtotal()
                )
                item.product.stock -= item.quantity
                item.product.save()
            
            items.delete()
            cart.delete()
            
            messages.success(request, '¡Compra finalizada!')
            return redirect('super:order_detail', pk=sale.pk)
            
        except Customer.DoesNotExist:
            messages.error(request, 'Error al procesar el cliente')
            return redirect('super:checkout')
        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Método de pago inválido')
            return redirect('super:checkout')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('super:checkout')
        except Exception as e:
            messages.error(request, f'Error al procesar la compra: {str(e)}')
            return redirect('super:checkout')