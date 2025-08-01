from django import forms
from django.forms import ModelForm
from core.super.models import Seller

class SellerForm(ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'last_name', 'dni', 'email', 'address', 'phone', 'birth_date', 'gender']
        help_texts = {k: "" for k in fields}
        widgets = {
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Fecha de nacimiento'}),
        }



