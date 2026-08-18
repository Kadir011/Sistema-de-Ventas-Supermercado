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

# Páginas de error del sistema: le indican a Django qué vista usar
# cuando se levanta Http404 / PermissionDenied / SuspiciousOperation.
# Solo entran en acción cuando DEBUG=False (en producción); con
# DEBUG=True, Django sigue mostrando su página de depuración normal.
handler400 = errors.bad_request_view
handler403 = errors.permission_denied_view
handler404 = errors.page_not_found_view

# Rutas de previsualización de las 4 páginas de error (incluida 503,
# que no tiene handler nativo en Django), solo disponibles en
# desarrollo para poder revisar su diseño sin forzar el error real.
if settings.DEBUG:
    urlpatterns += [
        path('', include('core.security.urls_errors')),
    ]
