import json
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods 
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from core.super.models import Sale, SaleDetail, Product
from core.super.form.sale import SaleForm

class SaleListView(ListView):
    model = Sale
    template_name = 'super/sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 12
    
    def get_queryset(self):
        q = self.request.GET.get('q')
        self.query = Q()
        if q is not None:
            self.query.add(Q(id__icontains=q)|
                         Q(customer__name__icontains=q)|
                         Q(customer__last_name__icontains=q)|
                         Q(seller__name__icontains=q)|
                         Q(seller__last_name__icontains=q)|
                         Q(payment__name__icontains=q), Q.OR)
        return self.model.objects.filter(self.query).order_by('sale_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ventas'
        context['create_url'] = reverse_lazy('super:sale_create')
        return context

class SaleCreateView(CreateView):
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
        return context 
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('Content-Type') == 'application/json':
           return self.handle_ajax(request)
        return super().post(request, 
                            *args, 
                            **kwargs)
    
    @transaction.atomic
    def handle_ajax(self, request):
        try:
            # Decodificar datos JSON
            data = json.loads(request.body) 

            # Crear la venta
            sale = Sale(customer_id=data.get('customer'),
                        seller_id=data.get('seller'),
                        payment_id=data.get('payment'),
                        sale_date=data.get('sale_date'),
                        subtotal=Decimal(data.get('subtotal', '0')),
                        iva=Decimal(data.get('iva', '0')),
                        discount=Decimal(data.get('discount', '0')),
                        total=Decimal(data.get('total', '0'))) 
            sale.save() 

            # Procesar detalles de venta
            for detail in data.get('details', []):
                product = get_object_or_404(Product, pk=detail.get('product'))
                quantity = int(detail.get('quantity', 1)) 

                # Verificar stock disponible
                if product.stock < quantity:
                   raise ValueError(f"Stock insuficiente para el producto {product.name}")
                
                # Crear detalle de venta
                sale_detail = SaleDetail(sale=sale,
                                        product=product,
                                        quantity=quantity,
                                        price=Decimal(detail.get('price', '0')),
                                        subtotal=Decimal(detail.get('subtotal', '0')))
                sale_detail.save()

                # Actualizar stock del producto
                product.stock -= quantity
                product.save() 
            
            return JsonResponse({'success':True, 'redirect_url':self.success_url})
        except ValueError as e:
            return JsonResponse({'success':False, 'error': str(e)}, status=400)
        except Exception as e:
            # Rollback automático debido a @transaction.atomic
            return JsonResponse({'success':False, 'error':f'Error al procesar la venta: {str(e)}'}, status=500) 

class SaleUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'super/sales/sale_form.html'
    success_url = reverse_lazy('super:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Venta'
        context['grabar'] = 'Editar Venta'
        context['back_url'] = self.success_url
        context['products'] = Product.objects.filter(state=True, stock__gt=0)

        if self.object:
            # Detalles de los productos
            context['details'] = SaleDetail.objects.filter(sale=self.object)
            details_data = [
                {
                    'product': detail.product.id,
                    'name': detail.product.name,
                    'quantity': detail.quantity,
                    'price': float(detail.price),
                    'subtotal': float(detail.subtotal),
                    'stock': detail.product.stock
                } for detail in context['details']
            ]
            context['initial_details'] = json.dumps(details_data)

            # Totales iniciales de la venta
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

            # Actualizar la venta
            sale.customer_id = data.get('customer')
            sale.seller_id = data.get('seller')
            sale.payment_id = data.get('payment')
            sale.sale_date = data.get('sale_date')
            sale.subtotal = Decimal(data.get('subtotal', '0'))
            sale.iva = Decimal(data.get('iva', '0'))
            sale.discount = Decimal(data.get('discount', '0'))
            sale.total = Decimal(data.get('total', '0'))
            sale.save()

            new_details = {detail.get('product'): detail for detail in data.get('details', [])}
            old_details = SaleDetail.objects.filter(sale=sale)

            # Devolver stock de detalles eliminados o reducidos
            for detail in old_details:
                product_id = str(detail.product.id)
                if product_id not in new_details:
                    product = detail.product
                    product.stock += detail.quantity
                    product.save()
                else:
                    new_quantity = int(new_details[product_id].get('quantity', 1))
                    if new_quantity < detail.quantity:
                        product = detail.product
                        product.stock += (detail.quantity - new_quantity)
                        product.save()

            # Eliminar detalles que ya no están
            old_details_to_delete = [d for d in old_details if str(d.product.id) not in new_details]
            SaleDetail.objects.filter(id__in=[d.id for d in old_details_to_delete]).delete()

            # Procesar nuevos o actualizados detalles
            for detail in data.get('details', []):
                product = get_object_or_404(Product, pk=detail.get('product'))
                quantity = int(detail.get('quantity', 1))
                price = Decimal(detail.get('price', '0'))
                subtotal = Decimal(detail.get('subtotal', '0'))

                existing_detail = SaleDetail.objects.filter(sale=sale, product=product).first()
                if existing_detail:
                    old_quantity = existing_detail.quantity
                    existing_detail.quantity = quantity
                    existing_detail.price = price
                    existing_detail.subtotal = subtotal
                    existing_detail.save()
                    if quantity > old_quantity:  # Aumentar cantidad
                        if product.stock < (quantity - old_quantity):
                            raise ValueError(f"Stock insuficiente para el producto {product.name}")
                        product.stock -= (quantity - old_quantity)
                        product.save()
                else:
                    if product.stock < quantity:
                        raise ValueError(f"Stock insuficiente para el producto {product.name}")
                    sale_detail = SaleDetail(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=price,
                        subtotal=subtotal
                    )
                    sale_detail.save()
                    product.stock -= quantity
                    product.save()

            return JsonResponse({'success': True, 'redirect_url': self.success_url})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error': f'Error al decodificar JSON: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la venta: {str(e)}'}, status=500)

class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'super/sales/sale_delete.html'
    success_url = reverse_lazy('super:sale_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Venta'
        context['grabar'] = 'Eliminar Venta'
        context['description'] = f'¿Está seguro de eliminar la venta?'
        context['back_url'] = self.success_url
        return context

# API para obtener productos
@method_decorator(require_http_methods(["GET"]), name='dispatch')
class ProductView(View):
    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.filter(state=True, stock__gt=0)
            products_list = [
                {
                    'id': product.id,
                    'name': str(product),
                    'price': float(product.price),
                    'stock': product.stock
                }
                for product in products
            ]
            return JsonResponse(products_list, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)









