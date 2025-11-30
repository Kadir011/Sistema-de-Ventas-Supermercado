from django import forms
from django.forms import ModelForm
from core.super.models import Seller

class SellerForm(ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'last_name', 'dni', 'email', 'address', 'phone', 'birth_date', 'gender']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Cédula (10 dígitos)',
                'maxlength': '10',
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Teléfono (10 dígitos)',
                'maxlength': '10',
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off'
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }