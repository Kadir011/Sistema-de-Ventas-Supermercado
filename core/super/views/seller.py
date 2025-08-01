from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from core.super.models import Seller
from core.super.form.seller import SellerForm

class SellerListView(ListView):
    model = Seller 
    template_name = 'super/sellers/seller_list.html' 
    context_object_name = 'sellers'
    paginate_by = 12 

    def get_queryset(self):
        q = self.request.GET.get('q') 
        self.query = Q()
        if q is not None:
            self.query.add(Q(name__icontains=q)|Q(last_name__icontains=q)|
                           Q(dni__icontains=q)|Q(email__icontains=q)|
                           Q(address__icontains=q)|Q(phone__icontains=q)|
                           Q(birth_date__icontains=q)|Q(gender__icontains=q), Q.OR)        
        return self.model.objects.filter(self.query).order_by('id_seller')  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['title'] = 'Vendedores'
        context['create_url'] = reverse_lazy('super:seller_create') 
        return context 
    
class SellerCreateView(CreateView):
    model = Seller
    form_class = SellerForm 
    template_name = 'super/sellers/seller_form.html' 
    success_url = reverse_lazy('super:seller_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['title'] = 'Crear Vendedor'
        context['grabar'] = 'Crear Vendedor' 
        context['back_url'] = self.success_url 
        return context 
    
class SellerUpdateView(UpdateView):
    model = Seller 
    form_class = SellerForm
    template_name = 'super/sellers/seller_form.html'
    success_url = reverse_lazy('super:seller_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['title'] = 'Editar Vendedor'
        context['grabar'] = 'Editar Vendedor' 
        context['back_url'] = self.success_url 
        return context 

class SellerDeleteView(DeleteView):
    model = Seller
    template_name = 'super/sellers/seller_delete.html'
    success_url = reverse_lazy('super:seller_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['title'] = 'Eliminar Vendedor'
        context['grabar'] = 'Eliminar Vendedor'
        context['description'] = f'¿Está seguro de eliminar el vendedor {self.object.get_full_name()}?'
        context['back_url'] = self.success_url
        return context



