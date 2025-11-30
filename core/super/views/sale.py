import os
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
from django.contrib.staticfiles import finders
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

class SaleListView(ListView):
    model = Sale
    template_name = 'super/sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 12
    
    def get_queryset(self):
        q = self.request.GET.get('q')
        self.query = Q()
        if q is not None:
            self.query.add(Q(id_sale__icontains=q)|
                         Q(customer__name__icontains=q)|
                         Q(customer__last_name__icontains=q)|
                         Q(seller__name__icontains=q)|
                         Q(seller__last_name__icontains=q)|
                         Q(payment__name__icontains=q), Q.OR)
        return self.model.objects.filter(self.query).order_by('-sale_date')
    
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
        return super().post(request, *args, **kwargs)
    
    @transaction.atomic
    def handle_ajax(self, request):
        try:
            data = json.loads(request.body) 

            # Crear la venta
            sale = Sale(
                customer_id=data.get('customer'),
                seller_id=data.get('seller'),
                payment_id=data.get('payment'),
                sale_date=data.get('sale_date'),
                subtotal=Decimal(data.get('subtotal', '0')),
                iva=Decimal(data.get('iva', '0')),
                discount=Decimal(data.get('discount', '0')),
                total=Decimal(data.get('total', '0'))
            ) 
            sale.save() 

            # Procesar detalles de venta
            for detail in data.get('details', []):
                product = get_object_or_404(Product, pk=detail.get('product'))
                quantity = int(detail.get('quantity', 1)) 

                # Verificar stock disponible
                if product.stock < quantity:
                   raise ValueError(f"Stock insuficiente para el producto {product.name}")
                
                # Crear detalle de venta
                sale_detail = SaleDetail(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price=Decimal(detail.get('price', '0')),
                    subtotal=Decimal(detail.get('subtotal', '0'))
                )
                sale_detail.save()

                # Actualizar stock del producto
                product.stock -= quantity
                product.save() 
            
            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la venta: {str(e)}'}, status=500) 

class SaleUpdateView(UpdateView):
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
            # Detalles de los productos
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

            # Actualizar los datos de la venta
            sale.customer_id = data.get('customer')
            sale.seller_id = data.get('seller')
            sale.payment_id = data.get('payment')
            sale.sale_date = data.get('sale_date')
            sale.subtotal = Decimal(data.get('subtotal', '0'))
            sale.iva = Decimal(data.get('iva', '0'))
            sale.discount = Decimal(data.get('discount', '0'))
            sale.total = Decimal(data.get('total', '0'))
            sale.save()

            # Obtener detalles actuales de la base de datos
            old_details = SaleDetail.objects.filter(sale=sale)
            old_details_dict = {str(detail.product.id_product): detail for detail in old_details}
            
            # Crear diccionario de nuevos detalles
            new_details_dict = {str(detail.get('product')): detail for detail in data.get('details', [])}

            # Procesar detalles eliminados o modificados
            for product_id, old_detail in old_details_dict.items():
                if product_id not in new_details_dict:
                    # Detalle eliminado: devolver stock
                    product = old_detail.product
                    product.stock += old_detail.quantity
                    product.save()
                    old_detail.delete()
                else:
                    # Detalle modificado: ajustar stock
                    new_quantity = int(new_details_dict[product_id].get('quantity', 1))
                    if new_quantity != old_detail.quantity:
                        product = old_detail.product
                        stock_difference = old_detail.quantity - new_quantity
                        product.stock += stock_difference
                        
                        if product.stock < 0:
                            raise ValueError(f"Stock insuficiente para el producto {product.name}")
                        
                        product.save()
                        
                        # Actualizar el detalle
                        old_detail.quantity = new_quantity
                        old_detail.price = Decimal(new_details_dict[product_id].get('price', '0'))
                        old_detail.subtotal = Decimal(new_details_dict[product_id].get('subtotal', '0'))
                        old_detail.save()

            # Procesar detalles nuevos
            for product_id, new_detail in new_details_dict.items():
                if product_id not in old_details_dict:
                    # Detalle nuevo: crear y descontar stock
                    product = get_object_or_404(Product, pk=int(product_id))
                    quantity = int(new_detail.get('quantity', 1))
                    
                    if product.stock < quantity:
                        raise ValueError(f"Stock insuficiente para el producto {product.name}")
                    
                    sale_detail = SaleDetail(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=Decimal(new_detail.get('price', '0')),
                        subtotal=Decimal(new_detail.get('subtotal', '0'))
                    )
                    sale_detail.save()
                    
                    product.stock -= quantity
                    product.save()

            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})
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
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """
        Sobrescribir delete para devolver el stock antes de eliminar
        """
        sale = self.get_object()
        
        # Devolver el stock de todos los productos
        details = SaleDetail.objects.filter(sale=sale)
        for detail in details:
            product = detail.product
            product.stock += detail.quantity
            product.save()
        
        # Eliminar la venta (cascade eliminará los detalles)
        return super().delete(request, *args, **kwargs)

# API para obtener productos
@method_decorator(require_http_methods(["GET"]), name='dispatch')
class ProductView(View):
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

# API para generar PDF tipo factura para cada venta realizada
class SalePDFView(View):
    def get(self, request, *args, **kwargs):
        try:
            # 1. Obtener la venta y sus detalles
            sale = get_object_or_404(Sale, pk=kwargs['pk'])
            details = SaleDetail.objects.filter(sale=sale)

            # 2. Contexto para la template
            context = {
                'sale': sale,
                'details': details,
                'title': f'Factura - {sale.id_sale}',
                # Puedes agregar info de la empresa aquí estáticamente o desde DB si existiera
                'company': {
                    'name': 'My Supermarket',
                    'address': 'Av. Principal 123, Guayaquil',
                    'phone': '0999999999',
                    'email': 'contacto@mysupermarket.com'
                }
            }

            # 3. Renderizar el template
            template_path = 'super/sales/salePDF.html'
            template = get_template(template_path)
            html = template.render(context)

            # 4. Crear el PDF
            response = HttpResponse(content_type='application/pdf')
            # Si quieres que se descargue automáticamente usa: attachment
            # response['Content-Disposition'] = f'attachment; filename="factura_{sale.id_sale}.pdf"'
            # Si quieres verlo en el navegador usa: inline
            response['Content-Disposition'] = f'inline; filename="factura_{sale.id_sale}_{sale.sale_date}.pdf"'

            # Generar PDF
            pisa_status = pisa.CreatePDF(
                html, dest=response
            )

            if pisa_status.err:
                return HttpResponse('Hubo un error al generar el PDF <pre>' + html + '</pre>')
            
            return response
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}')