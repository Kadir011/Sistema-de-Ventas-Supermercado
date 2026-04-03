from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from core.security.forms.auth import CustomerRegistrationForm


class UserRegisterView(FormView):
    template_name = 'security/auth/signup.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('super:home')

    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            messages.success(self.request, _('¡Registro exitoso! Bienvenido.'))
            return super().form_valid(form)
        except IntegrityError:
            form.add_error('username', _('Este usuario ya existe.'))
        except Exception as e:
            form.add_error(None, _('Ocurrió un error inesperado: {}').format(e))
        return self.form_invalid(form)


class UserLoginView(LoginView):
    template_name = 'security/auth/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_admin_user():
            return reverse_lazy('super:menu')
        return reverse_lazy('super:shop')

    def form_valid(self, form):
        user = form.get_user()
        login_type = self.request.POST.get('login_type', 'customer')

        if login_type == 'customer' and user.is_admin_user():
            messages.error(self.request, 'Solo ingreso de clientes')
            return self.render_to_response(self.get_context_data(form=form))

        if login_type == 'admin' and not user.is_admin_user():
            messages.error(self.request, 'Acceso no autorizado. Solo administrador@')
            return self.render_to_response(self.get_context_data(form=form))

        messages.success(self.request, 'Inicio de sesión exitoso')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales Incorrectas, intente de nuevo...')
        return super().form_invalid(form)


def logout_view(request):
    """
    Cierra la sesión y renderiza una página intermedia que limpia el
    localStorage del chatbot antes de redirigir al login.
    Esto evita que el historial de un usuario quede visible si otro
    usuario inicia sesión en el mismo navegador.
    """
    logout(request)
    messages.info(request, _('Has cerrado sesión correctamente.'))
    # Renderizamos el template de logout que borra localStorage y redirige
    return render(request, 'security/auth/logout.html')