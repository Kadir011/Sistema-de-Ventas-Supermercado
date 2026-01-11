from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login 
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from core.security.models import User
from core.super.models import Customer
from django.db import IntegrityError
from django import forms

class CustomerRegistrationForm(forms.ModelForm):
    # Agregamos campo DNI explícitamente
    dni = forms.CharField(label='Cédula', max_length=10, min_length=10, 
                         widget=forms.TextInput(attrs={'class': 'form-control only-numbers', 'placeholder': 'Cédula'}))
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
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Customer.objects.filter(dni=dni).exists():
            raise forms.ValidationError('Ya existe un cliente registrado con esta cédula.')
        return dni
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.user_type = 'customer'  # Siempre es cliente
        
        if commit:
            user.save()
            # CREAR CLIENTE AUTOMÁTICAMENTE EN EL CRUD
            try:
                Customer.objects.create(
                    name=user.first_name,
                    last_name=user.last_name,
                    dni=self.cleaned_data['dni'], # Usamos el DNI del formulario
                    email=user.email,
                    address=user.address,
                    phone=user.phone_number,
                    birth_date=user.date_of_birth,
                    gender=1 if user.gender == 'M' else 2 # Mapeo de género (ajustar según tu modelo)
                )
            except Exception as e:
                # Logear error si es necesario, pero permitimos el registro del usuario
                print(f"Error creando cliente automático: {e}")
                
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
        # El usuario ya fue autenticado correctamente por el form, ahora verificamos permisos
        user = form.get_user()
        login_type = self.request.POST.get('login_type', 'customer')

        # CASO 1: Admin intentando entrar como cliente
        if login_type == 'customer' and user.is_admin_user():
            messages.error(self.request, 'Solo ingreso de clientes')
            # Renderizamos de nuevo el login con el error, sin loguear al usuario
            return self.render_to_response(self.get_context_data(form=form))

        # CASO 2: Cliente (o intruso) intentando entrar como admin
        if login_type == 'admin' and not user.is_admin_user():
            messages.error(self.request, 'Acceso no autorizado. Solo administrador@')
            return self.render_to_response(self.get_context_data(form=form))

        # Si pasa las validaciones, procedemos con el login estándar
        messages.success(self.request, 'Inicio de sesión exitoso')
        return super().form_valid(form)

    def form_invalid(self, form):
        # CASO 3: Credenciales incorrectas
        messages.error(self.request, 'Credenciales Incorrectas, intente de nuevo...')
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, _('Has cerrado sesión correctamente.'))
    return redirect('super:home')