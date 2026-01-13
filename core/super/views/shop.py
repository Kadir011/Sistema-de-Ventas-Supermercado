from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from core.super.models import Product, Category, Brand, Sale, SaleDetail

class ShopView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'super/shop/shop.html'
    context_object_name = 'products'
    paginate_by = 12
    login_url = '/security/login/'

    def get_queryset(self):
        queryset = Product.objects.filter(state=True, stock__gt=0)
        
        category_id = self.request.GET.get('category')
        brand_id = self.request.GET.get('brand')
        search_query = self.request.GET.get('search')

        if category_id:
            queryset = queryset.filter(category=category_id)
        if brand_id:
            queryset = queryset.filter(brand=brand_id)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tienda'
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['selected_brand'] = self.request.GET.get('brand')
        context['selected_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProductDetailCustomerView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'super/shop/product_detail.html'
    context_object_name = 'product'
    login_url = '/security/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'super/shop/my_orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    login_url = '/security/login/'

    def get_queryset(self):
        # Filtramos directamente por el usuario autenticado
        return Sale.objects.filter(user=self.request.user).order_by('-sale_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mis Compras'
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'super/shop/order_detail.html'
    context_object_name = 'order'
    login_url = '/security/login/'

    def get_queryset(self):
        # Seguridad: Solo puedes ver la orden si tú la compraste
        return Sale.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Orden #{self.object.id_sale}'
        context['details'] = SaleDetail.objects.filter(sale=self.object)
        return context