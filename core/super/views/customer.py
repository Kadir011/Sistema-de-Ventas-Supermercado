"""
Vistas para que el admin gestione los clientes
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from core.super.models import Customer
from core.super.form.customer import CustomerForm
from core.super.mixins.auth import AdminRequiredMixin

class CustomerListView(AdminRequiredMixin, ListView):
    """Vista para listar los clientes"""
    
    model = Customer
    template_name = 'super/customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q')
        self.query = Q()
        if q is not None:
            self.query.add(Q(name__icontains=q)|Q(last_name__icontains=q)|
                           Q(dni__icontains=q)|Q(email__icontains=q)|
                           Q(address__icontains=q)|Q(phone__icontains=q)|
                           Q(gender__icontains=q), Q.OR) 
        
        return self.model.objects.filter(self.query).order_by('id_customer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Clientes'
        context['create_url'] = reverse_lazy('super:customer_create')
        return context

class CustomerCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear un cliente"""
    
    model = Customer
    form_class = CustomerForm
    template_name = 'super/customers/customer_form.html'
    success_url = reverse_lazy('super:customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Cliente'
        context['grabar'] = 'Crear Cliente'
        context['back_url'] = self.success_url
        return context
    
class CustomerUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para editar un cliente"""
    
    model = Customer
    form_class = CustomerForm
    template_name = 'super/customers/customer_form.html'
    success_url = reverse_lazy('super:customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Cliente'
        context['grabar'] = 'Editar Cliente'
        context['back_url'] = self.success_url
        return context

class CustomerDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar un cliente"""
    
    model = Customer
    template_name = 'super/customers/customer_delete.html'
    success_url = reverse_lazy('super:customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Cliente'
        context['grabar'] = 'Eliminar Cliente'
        context['description'] = f'¿Está seguro de eliminar el cliente {self.object.get_full_name()}?'
        context['back_url'] = self.success_url
        return context 