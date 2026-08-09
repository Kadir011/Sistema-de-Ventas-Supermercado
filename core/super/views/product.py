"""
Vistas para que el admin gestione los productos
"""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from core.super.models import Product, Category, Brand
from core.super.form.product import ProductForm
from django.contrib.auth.mixins import LoginRequiredMixin
from core.super.mixins.auth import AdminRequiredMixin

class ProductListView(AdminRequiredMixin, ListView):
    """Vista para listar los productos, con búsqueda y filtros"""

    model = Product
    template_name = 'super/products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        brand_id = self.request.GET.get('brand')
        state = self.request.GET.get('state')

        query = Q()
        if q:
            query &= (
                Q(name__icontains=q) | Q(description__icontains=q) |
                Q(brand__name__icontains=q) | Q(category__name__icontains=q) |
                Q(barcode__icontains=q)
            )

        qs = self.model.objects.filter(query).select_related('category', 'brand')

        if category_id:
            qs = qs.filter(category_id=category_id)
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        if state in ('1', '0'):
            qs = qs.filter(state=(state == '1'))

        return qs.order_by('id_product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['create_url'] = reverse_lazy('super:product_create')
        context['categories'] = Category.objects.order_by('name')
        context['brands'] = Brand.objects.order_by('name')
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_state'] = self.request.GET.get('state', '')
        return context
    
class ProductCreateView(AdminRequiredMixin, CreateView):
    """Vista para crear un nuevo producto"""
    
    model = Product
    form_class = ProductForm
    template_name = 'super/products/product_form.html'
    success_url = reverse_lazy('super:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Producto'
        context['grabar'] = 'Crear Producto'
        context['back_url'] = self.success_url
        return context
    
class ProductUpdateView(AdminRequiredMixin, UpdateView):
    """Vista para editar un producto existente"""
    
    model = Product
    form_class = ProductForm
    template_name = 'super/products/product_form.html'
    success_url = reverse_lazy('super:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Producto'
        context['grabar'] = 'Editar Producto'
        context['back_url'] = self.success_url
        return context

class ProductDeleteView(AdminRequiredMixin, DeleteView):
    """Vista para eliminar un producto"""
    
    model = Product
    template_name = 'super/products/product_delete.html'
    success_url = reverse_lazy('super:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminar Producto'
        context['grabar'] = 'Eliminar Producto'
        context['description'] = f'¿Está seguro de eliminar el producto {self.object.name}?'
        context['back_url'] = self.success_url
        return context

class ProductDetailView(DetailView, LoginRequiredMixin):
    """Vista para ver el detalle de un producto (Visitantes y Admin)"""
    
    model = Product
    template_name = 'super/products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Producto: {self.object.name}'
        context['back_url'] = reverse_lazy('super:product_list')
        return context