from django.db import models
from config.utils import get_image
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=10, blank=True, help_text="Número de teléfono del usuario.")
    address = models.CharField(max_length=255, blank=True, help_text="Dirección del usuario.")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Fecha de nacimiento del usuario.")
    gender = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], blank=True, help_text="Género del usuario.")
    image = models.ImageField(upload_to='usuarios', blank=True, null=True, help_text="Imagen del usuario.", max_length=255)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    groups = models.ManyToManyField(Group, related_name='security_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='security_user_set', blank=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}' 
    
    def get_short_name(self):
        return self.username 
    
    def __str__(self):
        return f'Usuario : {self.username}'
    
    def get_groups(self):
        return self.groups.all()

    def get_image_url(self):
        return get_image(self.image)

    #save para contraseña aleatoria
    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)










