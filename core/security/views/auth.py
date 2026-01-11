from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from core.security.models import User
from django.db import IntegrityError
from django import forms

class CustomerRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'gender']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.user_type = 'customer'  # Siempre es cliente
        if commit:
            user.save()
        return user


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
        else:
            return reverse_lazy('super:shop')

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