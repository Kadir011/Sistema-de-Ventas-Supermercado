from django import forms
from django.forms import ModelForm
from core.super.models import Customer

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'last_name', 'dni', 'email', 'address', 'phone', 'birth_date', 'gender']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control only-numbers', # Clase clave para el JS
                'placeholder': 'Cédula (10 dígitos)',
                'maxlength': '10',  # Límite estricto de caracteres
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Teléfono (10 dígitos)',
                'maxlength': '10',  # Límite estricto
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }