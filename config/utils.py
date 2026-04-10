from django.conf import settings

def get_image(image):
    # Si hay imagen, devuelve su URL oficial (Cloudinary se encarga)
    if image and hasattr(image, 'url'):
        return image.url
    # Si no hay imagen, devuelve la imagen por defecto de tus archivos estáticos
    return f"{settings.STATIC_URL}img/default.jpg"