from django import forms
from django.forms import ModelForm
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from core.super.models import Customer


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'last_name', 'dni', 'email', 'address',
            'phone', 'birth_date', 'gender',
            'discount_percentage', 'discount_expiry',
        ]
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Cédula (10 dígitos)',
                'maxlength': '10',
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control only-numbers',
                'placeholder': 'Teléfono (10 dígitos)',
                'maxlength': '10',
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'autocomplete': 'off',
            }),
            'discount_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 10.00',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'id': 'id_discount_percentage',
            }),
            'discount_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_discount_expiry',
            }),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
        
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        qs = Customer.objects.filter(dni=dni)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Customer.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este email ya está registrado.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            qs = Customer.objects.filter(phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este número de teléfono ya existe.')
        return phone
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es un nuevo cliente y no hay valor inicial para discount_expiry,
        # sugiere hoy + 2 meses como conveniente por defecto.
        # El admin puede cambiarlo libremente.
        if not self.instance.pk and not self.initial.get('discount_expiry'):
            default_expiry = timezone.localdate() + relativedelta(months=2)
            self.fields['discount_expiry'].initial = default_expiry 