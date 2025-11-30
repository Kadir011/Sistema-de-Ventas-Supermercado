import logging
from core.super.models import Product
from django.http import JsonResponse
from django.db.models import Q
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)

class ScannerTemplate(TemplateView):
    template_name = 'super/products/scan_barcode.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Escanear Productos'
        return context 

    def post(self, request, *args, **kwargs):
        """
        Recibe un código de barras (string) y busca el producto.
        Ya no procesa imágenes, lo que lo hace instantáneo.
        """
        try:
            barcode_data = request.POST.get('barcode')
            
            if not barcode_data:
                return JsonResponse({
                    'success': False, 
                    'error': 'No se recibió ningún código de barras.'
                })
            
            logger.info(f"Buscando producto con código: {barcode_data}")

            try:
                # Buscar el producto activo y con stock
                product = Product.objects.get(
                    Q(barcode=barcode_data), 
                    Q(state=True),
                    Q(stock__gt=0)
                ) 

                return JsonResponse({
                    'success': True,
                    'barcode': barcode_data,
                    'product_name': product.name,
                    'price': float(product.price),
                    'stock': product.stock,
                    'category': product.category.name if product.category else 'Sin categoría',
                    'brand': product.brand.name if product.brand else 'Sin marca',
                    'image_url': product.image.url if product.image else '/static/img/default.jpg'
                })
            except Product.DoesNotExist:
                logger.warning(f"No se encontró producto con código: {barcode_data}")
                return JsonResponse({
                    'success': False, 
                    'barcode': barcode_data,
                    'error': 'Producto no encontrado o sin stock disponible.'
                })
                
        except Exception as e:
            logger.error(f"Error inesperado en scanner: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': f'Error del servidor: {str(e)}'
            })