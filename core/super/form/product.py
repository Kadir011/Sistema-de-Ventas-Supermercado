from django import forms
from django.forms import ModelForm
from django.utils import timezone
from core.super.models import Product

class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['production_date'].initial = timezone.now()
        self.fields['expiration_date'].widget.attrs.update({'readonly': True})
        self.fields['state'].widget.attrs.update({'readonly': True})

    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'description', 'price', 'stock', 'image', 'barcode', 'production_date', 'expiration_date', 'state']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'production_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            # Configuración específica para Barcode
            'barcode': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Código de barras (13 dígitos)',
                'maxlength': '13',  # Límite para EAN-13
                'minlength': '13',
                'pattern': '[0-9]{13}',
                'autocomplete': 'off'
            }),
        }