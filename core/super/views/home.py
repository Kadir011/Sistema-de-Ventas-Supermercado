from django.views.generic import TemplateView, ListView
from core.super.models import Product, Category, Brand
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class HomeView(TemplateView):
    template_name = 'components/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Supermarket'
        return context
    
class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'components/menu.html'
    login_url = '/security/auth/login'

class AboutView(TemplateView):
    template_name = 'components/about.html'

class ContactView(TemplateView):
    template_name = 'components/contact.html'

class ProductCatalogView(ListView):
    model = Product 
    template_name = 'super/catalog/catalog.html'
    context_object_name = 'products' 
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset() 
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
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)  
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Catálogo de productos'	
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['selected_brand'] = self.request.GET.get('brand')
        context['selected_category'] = self.request.GET.get('category') 
        context['search_query'] = self.request.GET.get('search', '') 
        return context

