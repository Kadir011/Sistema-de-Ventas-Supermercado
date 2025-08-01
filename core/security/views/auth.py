from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from core.security.models import User
from django.db import IntegrityError 

class UserRegisterView(FormView):
    template_name = 'security/auth/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('super:home')

    def form_valid(self, form):
        try:
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
            )
            login(self.request, user)  # Inicia sesión automáticamente
            messages.success(self.request, _('Registro exitoso. ¡Bienvenido!'))
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
    success_url = reverse_lazy('super:home')

    def form_valid(self, form):
        messages.success(self.request, _('Inicio de sesión exitoso'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Nombre de usuario o contraseña incorrectos'))
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, _('Has cerrado sesión correctamente.'))
    return redirect('super:home')







