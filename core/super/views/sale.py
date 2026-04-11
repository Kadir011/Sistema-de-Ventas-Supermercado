"""
Vistas para que el admin gestiona las ventas realizadas por las compras de productos
"""

import json
import uuid
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, F
from decimal import Decimal
from core.super.models import Sale, SaleDetail, Product
from core.super.form.sale import SaleForm
from core.super.services.idempotency_service import IdempotencyService
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render
from xhtml2pdf import pisa
from core.super.mixins.auth import AdminRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

class SaleListView(AdminRequiredMixin, ListView):
    """Vista para listar las ventas realizadas, con búsqueda y paginación"""
    
    model = Sale
    template_name = 'super/sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q')
        self.query = Q()
        if q is not None:
            self.query.add(
                Q(id_sale__icontains=q) |
                Q(customer__name__icontains=q) |
                Q(customer__last_name__icontains=q) |
                Q(seller__name__icontains=q) |
                Q(seller__last_name__icontains=q) |
                Q(payment__name__icontains=q),
                Q.OR
            )
        return self.model.objects.filter(self.query).order_by('-sale_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ventas'
        context['create_url'] = reverse_lazy('super:sale_create')
        return context


class SaleCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear una nueva venta"""
    
    model = Sale
    form_class = SaleForm
    template_name = 'super/sales/sale_form.html'
    success_url = reverse_lazy('super:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Venta'
        context['grabar'] = 'Crear Venta'
        context['back_url'] = self.success_url
        context['products'] = Product.objects.filter(state=True, stock__gt=0)
        # ── Idempotencia ──────────────────────────────────────────────────
        # UUID generado al abrir el formulario de creación (GET).
        # El JS lo incluye en el payload JSON que envía al servidor.
        context['idempotency_key'] = str(uuid.uuid4())
        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('Content-Type') == 'application/json':
            return self.handle_ajax(request)
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def handle_ajax(self, request):
        try:
            data = json.loads(request.body)

            # ── Guardia de idempotencia ───────────────────────────────────
            idempotency_service = IdempotencyService()
            raw_key = data.get('idempotency_key', '').strip()
            idempotency_key = idempotency_service.parse_key(raw_key)

            if idempotency_key:
                existing = idempotency_service.find_existing(idempotency_key)
                if existing:
                    return JsonResponse({
                        'success': True,
                        'redirect_url': str(self.success_url),
                        'idempotent': True,
                    })

            sale = Sale(
                customer_id=data.get('customer'),
                seller_id=data.get('seller'),
                payment_id=data.get('payment'),
                sale_date=data.get('sale_date'),
                subtotal=Decimal(data.get('subtotal', '0')),
                iva=Decimal(data.get('iva', '0')),
                discount=Decimal(data.get('discount', '0')),
                total=Decimal(data.get('total', '0')),
                idempotency_key=idempotency_key,   # ← guardada en BD
            )
            sale.save()

            for detail in data.get('details', []):
                # ── Concurrencia: bloqueo a nivel de fila ─────────────────
                # select_for_update() bloquea el registro del producto
                # hasta que termine esta transacción. Si dos requests
                # intentan descontar stock del mismo producto al mismo
                # tiempo, el segundo espera al primero — evitando que
                # ambos lean el mismo valor y sobreescriban el resultado.
                product = Product.objects.select_for_update().get(
                    pk=detail.get('product')
                )
                quantity = int(detail.get('quantity', 1))

                if product.stock < quantity:
                    raise ValueError(
                        f"Stock insuficiente para '{product.name}'. "
                        f"Disponible: {product.stock}, solicitado: {quantity}"
                    )

                SaleDetail.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=Decimal(detail.get('price', '0')),
                    subtotal=Decimal(detail.get('subtotal', '0'))
                )
                
                # Descuento atómico: usa F() para que la operación
                # ocurra en la BD, no en Python → inmune a race conditions.
                Product.objects.filter(pk=product.pk).update(
                    stock=F('stock') - quantity
                )

            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la venta: {str(e)}'}, status=500)


class SaleUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para editar una venta existente"""
    
    model = Sale
    form_class = SaleForm
    template_name = 'super/sales/sale_form.html'
    success_url = reverse_lazy('super:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Venta'
        context['grabar'] = 'Actualizar Venta'
        context['back_url'] = self.success_url
        context['products'] = Product.objects.filter(state=True, stock__gt=0)

        if self.object:
            details = SaleDetail.objects.filter(sale=self.object)
            details_data = [
                {
                    'product': detail.product.id_product,
                    'name': detail.product.name,
                    'quantity': detail.quantity,
                    'price': float(detail.price),
                    'subtotal': float(detail.subtotal),
                    'stock': detail.product.stock
                } for detail in details
            ]
            context['initial_details'] = json.dumps(details_data)
            context['initial_totals'] = json.dumps({
                'subtotal': float(self.object.subtotal),
                'iva': float(self.object.iva),
                'discount': float(self.object.discount),
                'total': float(self.object.total)
            })

        return context

    def post(self, request, *args, **kwargs):
        if request.headers.get('Content-Type') == 'application/json':
            return self.handle_ajax(request)
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def handle_ajax(self, request):
        try:
            sale = self.get_object()
            data = json.loads(request.body)

            if not data or 'details' not in data:
                raise ValueError("Datos inválidos enviados en la solicitud")

            sale.customer_id = data.get('customer')
            sale.seller_id = data.get('seller')
            sale.payment_id = data.get('payment')
            sale.sale_date = data.get('sale_date')
            sale.subtotal = Decimal(data.get('subtotal', '0'))
            sale.iva = Decimal(data.get('iva', '0'))
            sale.discount = Decimal(data.get('discount', '0'))
            sale.total = Decimal(data.get('total', '0'))
            sale.save()

            old_details = SaleDetail.objects.filter(sale=sale)
            old_details_dict = {str(detail.product.id_product): detail for detail in old_details}
            new_details_dict = {str(detail.get('product')): detail for detail in data.get('details', [])}
            
            # Bloque 1: productos eliminados (restaurar stock)
            for product_id, old_detail in old_details_dict.items():
                if product_id not in new_details_dict:
                    # select_for_update: bloquear antes de restaurar
                    product = Product.objects.select_for_update().get(
                        pk=old_detail.product.pk
                    )
                    Product.objects.filter(pk=product.pk).update(
                        stock=F('stock') + old_detail.quantity
                    )
                    old_detail.delete()  # ← eliminar antes de restaurar
                else:
                    new_quantity = int(new_details_dict[product_id].get('quantity', 1))
                    if new_quantity != old_detail.quantity:
                        product = Product.objects.select_for_update().get(
                            pk=old_detail.product.pk
                        )
                        stock_difference = old_detail.quantity - new_quantity
                        # Verificar que el nuevo stock no quedaría negativo
                        current_stock = Product.objects.get(pk=product.pk).stock
                        if current_stock + stock_difference < 0:
                            raise ValueError(
                                f"Stock insuficiente para '{product.name}'"
                            )
                        Product.objects.filter(pk=product.pk).update(
                            stock=F('stock') + stock_difference
                        )
                        old_detail.quantity = new_quantity
                        old_detail.price = Decimal(
                            new_details_dict[product_id].get('price', '0')
                        )
                        old_detail.subtotal = Decimal(
                            new_details_dict[product_id].get('subtotal', '0')
                        )
                        old_detail.save()
                        
            # Bloque 2: productos nuevos en edición            
            for product_id, new_detail in new_details_dict.items():
                if product_id not in old_details_dict:
                    product = Product.objects.select_for_update().get(
                        pk=int(product_id)
                    )
                    quantity = int(new_detail.get('quantity', 1))
                    if product.stock < quantity:
                        raise ValueError(
                            f"Stock insuficiente para '{product.name}'. "
                            f"Disponible: {product.stock}"
                        )
                    SaleDetail.objects.create(
                        sale=sale, product=product, quantity=quantity,
                        price=Decimal(new_detail.get('price', '0')),
                        subtotal=Decimal(new_detail.get('subtotal', '0')),
                    )
                    Product.objects.filter(pk=product.pk).update(
                        stock=F('stock') - quantity
                    )

            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})

        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f'Error al decodificar JSON: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la venta: {str(e)}'}, status=500)


class SaleDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar una venta. Antes de eliminar, restaura el stock de los productos involucrados."""
    
    model = Sale
    template_name = 'super/sales/sale_delete.html'
    success_url = reverse_lazy('super:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Venta'
        context['grabar'] = 'Eliminar Venta'
        context['description'] = f'¿Está seguro de eliminar la venta #{self.get_object().id_sale}?'
        context['back_url'] = self.success_url
        return context

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """
        Restaura el stock antes de eliminar la venta.

        El bloque @transaction.atomic garantiza que la restauración de stock
        y la eliminación de la venta ocurren juntas: si falla cualquiera de
        los dos pasos, toda la operación hace rollback y el estado queda
        consistente (no queda stock fantasma ni venta huérfana).
        """
        sale = self.get_object()
        details = SaleDetail.objects.filter(sale=sale)
        for detail in details:
            product = detail.product
            product.stock += detail.quantity
            product.save()
        return super().delete(request, *args, **kwargs)


@method_decorator(require_http_methods(["GET"]), name='dispatch')
class ProductView(AdminRequiredMixin, View):
    """
    Vista para obtener los productos en formato JSON para la visualización en el frontend desde el formulario de ventas. 
    """
    
    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.filter(state=True, stock__gt=0)
            products_list = [
                {
                    'id': product.id_product,
                    'name': str(product),
                    'price': float(product.price),
                    'stock': product.stock
                }
                for product in products
            ]
            return JsonResponse(products_list, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SalePDFView(LoginRequiredMixin, View):
    """
    Vista para generar un PDF de la factura de una venta específica. Solo el admin o el usuario que realizó la compra pueden acceder.
    """
    
    def get(self, request, *args, **kwargs):
        try:
            sale = get_object_or_404(Sale, pk=self.kwargs['pk'])

            # Si NO es administrador, Y la venta no le pertenece al usuario actual, lo bloqueamos.
            if not request.user.is_superuser and sale.user != request.user:
                return HttpResponse('No tienes permiso para ver la factura de otra persona.', status=403)

            details = SaleDetail.objects.filter(sale=sale)
            context = {
                'sale': sale,
                'details': details,
                'title': f'Factura #{sale.id_sale:06d}',
                'company': {
                    'name': 'My Supermarket',
                    'address': 'Guayaquil, Ecuador',
                    'phone': '0999999999',
                    'email': 'contacto@mysupermarket.com'
                }
            }
            template = get_template('super/sales/salePDF.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="factura_{sale.id_sale}.pdf"'
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Ocurrió un error al generar el PDF', status=400)
            return response
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)


class SaleDetailView(AdminRequiredMixin, DetailView):
    """Vista para ver el detalle de una venta (Solo Admin)."""
    
    model = Sale
    template_name = 'super/sales/sale_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            sale = self.get_object()
            details = SaleDetail.objects.filter(sale=sale)
            context = {
                'sale': sale,
                'details': details,
                'company': {
                    'name': 'My Supermarket',
                    'address': 'Av. Principal 123, Guayaquil',
                    'phone': '0999999999',
                    'email': 'contacto@mysupermarket.com'
                }
            }
            return render(request, self.template_name, context)
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}') 