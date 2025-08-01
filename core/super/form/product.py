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
        fields = ['name', 'category', 'brand', 'description', 'price', 'stock', 'image', 'barcode', 'production_date', 'production_date', 'expiration_date', 'state']
        help_texts = {k: "" for k in fields}
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'production_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Fecha de elaboración'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Fecha de vencimiento'}),
        }





