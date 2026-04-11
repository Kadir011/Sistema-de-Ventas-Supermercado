from django import forms
from core.security.models import User

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'field-input', 'placeholder': 'Mínimo 8 caracteres'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'field-input', 'placeholder': 'Repite la contraseña'}),
    )
 
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'address',
            'date_of_birth', 'gender', 'is_active',
        ]
 
    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return p2
 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
 
 
class UserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        label='Nueva contraseña (opcional)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'field-input',
            'placeholder': 'Dejar vacío para no cambiar',
        }),
    )
 
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone_number', 'address',
            'date_of_birth', 'gender', 'is_active',
        ]
 
    def save(self, commit=True):
        user = super().save(commit=False)
        new_pw = self.cleaned_data.get('new_password')
        if new_pw:
            user.set_password(new_pw)
        if commit:
            user.save()
        return user