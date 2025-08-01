import cv2
import logging
import numpy as np
from pyzbar.pyzbar import decode
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
        try:
            logger.info("Recibiendo solicitud POST para escanear código de barras.") 
            if 'barcode' not in request.FILES:
                logger.error("No se recibió ninguna imagen.") 
                return JsonResponse({'success': False, 'error': 'No se recibió ninguna imagen.'}) 
            
            image_file = request.FILES['barcode'] 
            logger.info(f"Archivo recibido: {image_file.name}, tipo: {image_file.content_type}")  

            if not image_file.content_type.startswith('image/'):
                logger.error("El archivo no es una imagen válida.")
                return JsonResponse({'success': False, 'error': 'El archivo no es una imagen válida.'}) 
            
            np_array = np.frombuffer(image_file.read(), np.uint8) 
            frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            barcodes = decode(frame) 
            if not barcodes:
                logger.warning("No se detectó ningún código de barras en la imagen.")
                return JsonResponse({'success': False, 'error': 'No se detectó ningún código de barras en la imagen.'}) 
            
            barcode_data = barcodes[0].data.decode('utf-8').strip() 
            logger.info(f"Código de barras detectado: {barcode_data}") 

            try:
                product = Product.objects.get(Q(barcode=barcode_data), 
                                              Q(state=True), 
                                              Q(stock__gt=0)) 

                logger.info(f"Producto encontrado: {product.name}")
                return JsonResponse({
                    'success': True,
                    'product_name': product.name,
                    'price': float(product.price),
                    'stock': product.stock,
                    'image_url': product.image.url if product.image else '/static/img/no_image.png'
                })
            except Product.DoesNotExist:
                logger.warning(f"No se encontró producto con barcode: {barcode_data}")
                return JsonResponse({'success': False, 'error': 'El producto no está disponible o no existe.'})
        except cv2.error as e:
            logger.error(f"Error de OpenCV: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error al procesar la imagen. Asegúrate de que es una imagen válida.'})
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})



