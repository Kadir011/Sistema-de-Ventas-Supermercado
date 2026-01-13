from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, View
from core.super.models import Product, Category, Brand
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings

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

class ContactView(View):
    template_name = 'components/contact.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'title': 'Contáctanos'})

    def post(self, request, *args, **kwargs):
        # 1. Captura de datos del formulario
        full_name = request.POST.get('name')
        user_email = request.POST.get('email') # Correo ingresado por el cliente
        subject_form = request.POST.get('subject')
        message_body = request.POST.get('message')

        # 2. Cuerpo del mensaje para el Administrador
        email_content = f"""
        Has recibido un nuevo mensaje de contacto:

        CLIENTE: {full_name}
        CORREO DEL CLIENTE: {user_email}
        ASUNTO: {subject_form}

        MENSAJE:
        ------------------------------------------
        {message_body}
        ------------------------------------------
        """

        try:
            # 3. Formateo del remitente (Header 'From')
            # Al usar el correo del cliente aquí, Gmail dejará de mostrar "Yo"
            # Formato esperado: "Nombre Cliente <correo_cliente@dominio.com>"
            sender_header = f"{full_name} <{user_email}>"

            email = EmailMessage(
                subject=f"SISTEMA: {subject_form}",
                body=email_content,
                from_email=sender_header,            # "De": Aquí va el correo del cliente
                to=[settings.EMAIL_HOST_USER],        # "Para": Tu correo de admin
                reply_to=[user_email],                # "Responder a": El correo del cliente
            )
            
            email.send()
            
            messages.success(request, '¡Tu mensaje ha sido enviado con éxito!')
            return redirect('super:contact')
            
        except Exception as e:
            messages.error(request, f'Error al procesar el envío: {str(e)}')
            return render(request, self.template_name, {'title': 'Contáctanos'})

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

