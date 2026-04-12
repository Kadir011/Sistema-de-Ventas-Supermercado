from django import forms
from core.security.models import User


class ProfileInfoForm(forms.ModelForm):
    """Formulario para editar datos personales del perfil."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'phone_number', 'address', 'date_of_birth', 'gender',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este email ya está registrado por otro usuario.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            qs = User.objects.filter(phone_number=phone).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este número de teléfono ya está en uso.')
        return phone


class ProfileAvatarForm(forms.ModelForm):
    """Formulario exclusivo para cambiar la foto de perfil."""

    class Meta:
        model = User
        fields = ['image']


class ProfilePasswordForm(forms.Form):
    """Formulario para cambiar la contraseña del usuario."""

    current_password = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
        }),
    )
    new_password1 = forms.CharField(
        label='Nueva contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
        }),
    )
    new_password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get('current_password')
        if not self.user.check_password(pwd):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Las contraseñas no coinciden.')
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user