from django.urls import path
from core.security.views import auth, errors

app_name = 'security'

urlpatterns = [
    # AUTENTICACIÓN
    path('register/', auth.UserRegisterView.as_view(), name='register'),
    path('login/', auth.UserLoginView.as_view(), name='login'),
    path('logout/', auth.logout_view, name='logout'),
    
    # ERRORES
    path('error/400/', errors.bad_request_view, name='preview_error_400'),
    path('error/403/', errors.permission_denied_view, name='preview_error_403'),
    path('error/404/', errors.page_not_found_view, name='preview_error_404'),
    path('error/503/', errors.service_unavailable_view, name='preview_error_503'),
]
