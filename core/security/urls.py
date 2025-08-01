from django.urls import path
from core.security.views import auth

app_name = 'security'

urlpatterns = [
    path('register/', auth.UserRegisterView.as_view(), name='register'),
    path('login/', auth.UserLoginView.as_view(), name='login'),
    path('logout/', auth.logout_view, name='logout'),
]



