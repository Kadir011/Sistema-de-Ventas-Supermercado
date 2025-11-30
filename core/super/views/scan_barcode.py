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

    def preprocess_image(self, image):
        """
        Preprocesa la imagen para mejorar la detección de códigos de barras
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro bilateral para reducir ruido manteniendo bordes
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Mejorar contraste usando CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Binarización adaptativa para manejar diferentes condiciones de iluminación
        binary = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Operaciones morfológicas para limpiar la imagen
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return [gray, denoised, enhanced, binary, morph]

    def detect_barcode_regions(self, image):
        """
        Detecta posibles regiones que contienen códigos de barras
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calcular gradientes en X e Y
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        
        # Restar gradientes para enfatizar regiones con líneas verticales
        gradient = cv2.subtract(grad_x, grad_y)
        gradient = cv2.convertScaleAbs(gradient)
        
        # Aplicar blur y umbralización
        blurred = cv2.blur(gradient, (9, 9))
        _, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)
        
        # Operaciones morfológicas para cerrar gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Erosión y dilatación
        closed = cv2.erode(closed, None, iterations=4)
        closed = cv2.dilate(closed, None, iterations=4)
        
        return closed

    def try_decode_barcode(self, images):
        """
        Intenta decodificar el código de barras de múltiples versiones de la imagen
        """
        for img in images:
            try:
                barcodes = decode(img)
                if barcodes:
                    return barcodes
            except Exception as e:
                logger.debug(f"Error al decodificar: {str(e)}")
                continue
        return []

    def post(self, request, *args, **kwargs):
        try:
            logger.info("Recibiendo solicitud POST para escanear código de barras.") 
            
            if 'barcode' not in request.FILES:
                logger.error("No se recibió ninguna imagen.") 
                return JsonResponse({
                    'success': False, 
                    'error': 'No se recibió ninguna imagen.'
                }) 
            
            image_file = request.FILES['barcode'] 
            logger.info(f"Archivo recibido: {image_file.name}, tipo: {image_file.content_type}")  

            if not image_file.content_type.startswith('image/'):
                logger.error("El archivo no es una imagen válida.")
                return JsonResponse({
                    'success': False, 
                    'error': 'El archivo no es una imagen válida.'
                }) 
            
            # Leer la imagen
            np_array = np.frombuffer(image_file.read(), np.uint8) 
            frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            if frame is None:
                logger.error("No se pudo decodificar la imagen.")
                return JsonResponse({
                    'success': False, 
                    'error': 'No se pudo procesar la imagen.'
                })

            # Intentar detectar código de barras en la imagen original
            barcodes = decode(frame)
            
            # Si no se detectó, preprocesar la imagen
            if not barcodes:
                logger.info("No se detectó código en imagen original, preprocesando...")
                processed_images = self.preprocess_image(frame)
                barcodes = self.try_decode_barcode(processed_images)
            
            # Si aún no se detectó, intentar con regiones específicas
            if not barcodes:
                logger.info("Buscando regiones con códigos de barras...")
                barcode_region = self.detect_barcode_regions(frame)
                processed_regions = self.preprocess_image(
                    cv2.cvtColor(barcode_region, cv2.COLOR_GRAY2BGR)
                )
                barcodes = self.try_decode_barcode(processed_regions)
            
            # Si aún no se detectó, rotar la imagen
            if not barcodes:
                logger.info("Probando con rotaciones de imagen...")
                for angle in [90, 180, 270]:
                    rotated = cv2.rotate(
                        frame, 
                        cv2.ROTATE_90_CLOCKWISE if angle == 90 else 
                        cv2.ROTATE_180 if angle == 180 else 
                        cv2.ROTATE_90_COUNTERCLOCKWISE
                    )
                    barcodes = decode(rotated)
                    if barcodes:
                        break
                    
                    processed_rotated = self.preprocess_image(rotated)
                    barcodes = self.try_decode_barcode(processed_rotated)
                    if barcodes:
                        break

            if not barcodes:
                logger.warning("No se detectó ningún código de barras después de todos los intentos.")
                return JsonResponse({
                    'success': False, 
                    'error': 'No se detectó ningún código de barras. Intente con mejor iluminación o acerque más el código.'
                }) 
            
            barcode_data = barcodes[0].data.decode('utf-8').strip() 
            logger.info(f"Código de barras detectado: {barcode_data}") 

            try:
                product = Product.objects.get(
                    Q(barcode=barcode_data), 
                    Q(state=True), 
                    Q(stock__gt=0)
                ) 

                logger.info(f"Producto encontrado: {product.name}")
                return JsonResponse({
                    'success': True,
                    'barcode': barcode_data,
                    'product_name': product.name,
                    'price': float(product.price),
                    'stock': product.stock,
                    'category': product.category.name if product.category else 'Sin categoría',
                    'brand': product.brand.name if product.brand else 'Sin marca',
                    'image_url': product.image.url if product.image else '/static/img/no_image.png'
                })
            except Product.DoesNotExist:
                logger.warning(f"No se encontró producto con código: {barcode_data}")
                return JsonResponse({
                    'success': False, 
                    'barcode': barcode_data,
                    'error': f'Producto con código {barcode_data} no disponible o sin stock.'
                })
        except cv2.error as e:
            logger.error(f"Error de OpenCV: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': 'Error al procesar la imagen. Intente nuevamente.'
            })
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return JsonResponse({
                'success': False, 
                'error': f'Error inesperado: {str(e)}'
            })