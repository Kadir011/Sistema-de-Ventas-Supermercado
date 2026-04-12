"""
Vista de perfil de usuario — permite ver y editar datos personales,
cambiar foto de perfil y actualizar la contraseña.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView
from core.super.models import Sale
from core.super.form.profile import ProfileInfoForm, ProfileAvatarForm, ProfilePasswordForm
from core.super.mixins.auth import AdminRequiredMixin


class BaseProfileView(LoginRequiredMixin, TemplateView):
    """Vista base para el perfil de usuario."""
    login_url = '/security/login/'
    # Subclases deben definir success_url_name
    success_url_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['title'] = 'Mi Perfil'
        context['info_form'] = ProfileInfoForm(instance=user)
        context['avatar_form'] = ProfileAvatarForm(instance=user)
        context['password_form'] = ProfilePasswordForm(user=user)
        context['active_tab'] = self.request.GET.get('tab', 'info')

        if user.is_admin_user():
            context['total_sales'] = Sale.objects.count()
            context['role_label'] = 'Administrador'
        else:
            from django.db.models import Sum
            from decimal import Decimal
            user_orders = Sale.objects.filter(user=user)
            context['total_orders'] = user_orders.count()
            total_spent = float(user_orders.aggregate(t=Sum('total'))['t'] or Decimal('0'))
            context['total_spent'] = total_spent
            context['role_label'] = 'Cliente'
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        if action == 'update_info':
            return self._handle_info(request)
        if action == 'update_avatar':
            return self._handle_avatar(request)
        if action == 'update_password':
            return self._handle_password(request)

        messages.error(request, 'Acción no reconocida.')
        return redirect(self.success_url_name)

    def _handle_info(self, request):
        form = ProfileInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Datos actualizados correctamente.')
            return redirect(self.success_url_name)

        # Re-render con errores — pasar el form con errores al contexto
        context = self.get_context_data()
        context['info_form'] = form
        context['active_tab'] = 'info'
        return self.render_to_response(context)

    def _handle_avatar(self, request):
        form = ProfileAvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Foto de perfil actualizada.')
        else:
            messages.error(request, 'Error al subir la imagen. Verifica el formato (JPG, PNG, WEBP).')
        return redirect(self.success_url_name)

    def _handle_password(self, request):
        form = ProfilePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Evita que se cierre la sesión al cambiar la contraseña
            update_session_auth_hash(request, request.user)
            messages.success(request, '✅ Contraseña actualizada correctamente.')
            return redirect(self.success_url_name)

        context = self.get_context_data()
        context['password_form'] = form
        context['active_tab'] = 'password'
        return self.render_to_response(context)


# ── Vistas concretas ────────────────────────────────────────── #

class CustomerProfileView(BaseProfileView):
    """Vista de perfil para clientes."""
    template_name = 'super/profile/customer_profile.html'
    success_url_name = 'super:customer_profile'


class AdminProfileView(AdminRequiredMixin, BaseProfileView):
    """Vista de perfil para administradores."""
    template_name = 'super/profile/admin_profile.html'
    success_url_name = 'super:admin_profile'