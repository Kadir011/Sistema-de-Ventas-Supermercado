"""
Vistas para las páginas de error del sistema (400, 403, 404, 503).

Estas vistas reemplazan las páginas de error por defecto de Django,
manteniendo el mismo lenguaje visual (Tailwind + CSS propio) que el
resto de la aplicación, pero sin navbar ni footer, ya que se muestran
cuando algo en el flujo normal de la app se interrumpió.

- bad_request_view, permission_denied_view y page_not_found_view están
  registradas como handler400 / handler403 / handler404 en
  config/urls.py. Django las invoca automáticamente al levantar
  Http404, PermissionDenied o SuspiciousOperation, siempre que
  DEBUG=False (en DEBUG=True, Django muestra su página de depuración
  en su lugar).

- service_unavailable_view no tiene un "handler" nativo en Django (no
  existe handler503 en el framework), así que queda disponible para
  invocarla manualmente desde cualquier vista, middleware o bloque
  except que detecte que un servicio del que depende la app (base de
  datos, WhatsApp, Gemini, etc.) no está disponible temporalmente.
"""
from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
def bad_request_view(request, exception=None):
    """400 - Solicitud incorrecta (datos malformados, CSRF inválido, etc.)."""
    return render(request, 'errors/400.html', status=400)


@never_cache
def permission_denied_view(request, exception=None):
    """403 - Acceso denegado (permisos insuficientes o límite de intentos)."""
    return render(request, 'errors/403.html', status=403)


@never_cache
def page_not_found_view(request, exception=None):
    """404 - El recurso solicitado no existe."""
    return render(request, 'errors/404.html', status=404)


@never_cache
def service_unavailable_view(request, exception=None):
    """
    503 - Servicio no disponible temporalmente.

    Django no la dispara automáticamente. Úsala explícitamente, por
    ejemplo:

        from core.security.views.errors import service_unavailable_view

        try:
            ...
        except OperationalError:
            return service_unavailable_view(request)
    """
    return render(request, 'errors/503.html', status=503)