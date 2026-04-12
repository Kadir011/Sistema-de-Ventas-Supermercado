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
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        qs = Seller.objects.filter(dni=dni)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Seller.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este email ya está registrado.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            qs = Seller.objects.filter(phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este número de teléfono ya existe.')
        return phone 