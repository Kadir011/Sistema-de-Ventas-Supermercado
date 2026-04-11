from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

class AdminRequiredMixin(AccessMixin):
    """
    Verifica que el usuario haya iniciado sesión y sea un administrador (superuser).
    Si es un cliente normal, lo envía directamente a la tienda.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_superuser:
            messages.error(request, "Acceso denegado: Área exclusiva para administradores.")
            return redirect('super:shop')
            
        return super().dispatch(request, *args, **kwargs)