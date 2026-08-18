"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.security.views import errors

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.super.urls', namespace='super')),
    path('security/', include('core.security.urls', namespace='security')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

# Páginas de error del sistema: 400, 403, 404 y 503.
#
# Django solo reconoce automáticamente 400 / 403 / 404 (y 500, que no
# usamos aquí) a través de las variables handler400 / handler403 /
# handler404, que se disparan cuando se levanta SuspiciousOperation /
# PermissionDenied / Http404 respectivamente. Solo entran en acción
# cuando DEBUG=False (en producción); con DEBUG=True, Django sigue
# mostrando su página de depuración normal.
handler400 = errors.bad_request_view
handler403 = errors.permission_denied_view
handler404 = errors.page_not_found_view

# El 503 (errors.service_unavailable_view) NO tiene un handler nativo
# en Django -no existe "handler503"-, así que nunca se dispara solo.
# Debe invocarse manualmente desde el código (ej. en un except al
# fallar la conexión a la base de datos, o desde un middleware de
# modo mantenimiento) devolviendo esa vista con status=503.
#
# Las 4 páginas de error también se pueden revisar visitándolas
# directamente (ver sección "ERRORES" en core/security/urls.py):
# /security/error/400/, /security/error/403/, /security/error/404/
# y /security/error/503/. A diferencia de handler400/403/404, estas
# rutas SÍ están activas también en producción (no dependen de
# DEBUG), ya que viven junto a las demás rutas normales de la app.