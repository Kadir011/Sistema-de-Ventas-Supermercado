from django import forms
from django.forms import ModelForm
from django.utils import timezone
from core.super.models import Sale, SaleDetail

class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'seller', 'sale_date', 'payment', 'subtotal', 'iva', 'discount', 'total']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}), 
            'subtotal': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'iva': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'discount': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'total': forms.NumberInput(attrs={'readonly': 'readonly'}),
        } 
    
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['sale_date'].initial = timezone.now() 

class SaleDetailForm(ModelForm):
    class Meta:
        model = SaleDetail
        fields = ['product', 'quantity', 'price', 'subtotal']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '1'}),
            'price': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'subtotal': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }









