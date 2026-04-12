from django import forms
from core.security.models import User
from core.super.models import Customer
from django.db import IntegrityError, transaction

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
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return dni
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Buscamos duplicados tanto en User como en Customer
        if User.objects.filter(email=email).exists() or Customer.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            if User.objects.filter(phone_number=phone).exists() or Customer.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Este número de teléfono ya está registrado.')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.user_type = 'customer' # Siempre es cliente

        if commit:
            # ── Idempotencia + concurrencia en registro ──────────────────
            # select_for_update() no aplica en INSERT, pero sí usamos
            # get_or_create dentro de atomic para evitar race conditions.
            # Si dos requests llegan al mismo tiempo con el mismo username,
            # el constraint UNIQUE de BD garantiza que solo uno triunfa;
            # el otro recibe IntegrityError, que capturamos limpiamente.
            try:
                with transaction.atomic():
                    user.save()
            except IntegrityError:
                # Usuario ya existe: comportamiento idempotente →
                # devolvemos el usuario existente en lugar de fallar.
                existing = User.objects.filter(
                    username=user.username
                ).first() or User.objects.filter(
                    email=user.email
                ).first()
                if existing:
                    return existing
                raise  # Si no encontramos el duplicado, re-lanzar

            # ── Customer: idempotente con get_or_create ───────────────────
            # Antes usaba create() → fallaba si ya existía un Customer
            # con ese DNI o email (admin pudo haberlo creado antes).
            # Ahora: si ya existe, lo actualizamos con los datos frescos.
            try:
                with transaction.atomic():
                    customer, created = Customer.objects.get_or_create(
                        dni=self.cleaned_data['dni'],
                        defaults={
                            'name': user.first_name,
                            'last_name': user.last_name,
                            'email': user.email,
                            'address': user.address,
                            'phone': user.phone_number,
                            'birth_date': user.date_of_birth,
                            'gender': 1 if user.gender == 'M' else 2,  # Mapeo de género (ajustar según tu modelo)
                        }
                    )
                    if not created:
                        # El customer ya existía (ej: creado por admin).
                        # Actualizamos email y nombre si llegaron vacíos.
                        updated = False
                        if not customer.email and user.email:
                            customer.email = user.email
                            updated = True
                        if not customer.name and user.first_name:
                            customer.name = user.first_name
                            updated = True
                        if updated:
                            customer.save()
            except IntegrityError:
                # Email duplicado en Customer (otro campo UNIQUE).
                # No bloqueamos el registro del User, solo logueamos.
                import logging
                logging.getLogger(__name__).warning(
                    f"Customer duplicado al registrar usuario {user.username}"
                )

        return user 