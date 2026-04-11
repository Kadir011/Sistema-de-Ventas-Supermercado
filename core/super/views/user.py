"""
Vistas para que el admin gestione los usuarios del sistema.
"""
 
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from core.security.models import User
from core.super.mixins.auth import AdminRequiredMixin
from core.super.form.user import UserCreateForm, UserUpdateForm 

class UserListView(AdminRequiredMixin, ListView):
    """Lista todos los usuarios del sistema con búsqueda y paginación."""
 
    model = User
    template_name = 'super/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 12
    
    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        qs = User.objects.all().order_by('-date_joined')
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Usuarios'
        context['create_url'] = reverse_lazy('super:user_create')
        context['search_query'] = self.request.GET.get('q', '')
        return context 
    

class UserCreateView(AdminRequiredMixin, CreateView):
    """Crea un nuevo usuario del sistema."""
 
    model = User
    form_class = UserCreateForm
    template_name = 'super/users/user_form.html'
    success_url = reverse_lazy('super:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{form.instance.username}" creado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Usuario'
        context['grabar'] = 'Crear Usuario'
        context['back_url'] = self.success_url
        return context
    

class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Edita un usuario existente. La contraseña es opcional."""
 
    model = User
    form_class = UserUpdateForm
    template_name = 'super/users/user_form.html'
    success_url = reverse_lazy('super:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{form.instance.username}" actualizado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Usuario'
        context['grabar'] = 'Guardar Cambios'
        context['back_url'] = self.success_url
        return context
    

class UserDeleteView(AdminRequiredMixin, DeleteView):
    """Elimina un usuario. Impide que el admin se elimine a sí mismo."""
 
    model = User
    template_name = 'super/users/user_delete.html'
    success_url = reverse_lazy('super:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
            return self._redirect_back()
        return super().dispatch(request, *args, **kwargs)
    
    def _redirect_back(self):
        from django.shortcuts import redirect
        return redirect(self.success_url)
    
    def form_valid(self, form):
        username = self.get_object().username
        messages.success(self.request, f'Usuario "{username}" eliminado correctamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['title'] = 'Eliminar Usuario'
        context['grabar'] = 'Eliminar Usuario'
        context['description'] = f'¿Estás seguro de eliminar al usuario "{obj.username}" ({obj.get_full_name()})?'
        context['back_url'] = self.success_url
        return context 