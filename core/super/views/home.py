"""
Vistas de componentes base o principales.
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, View
from core.super.models import Product, Category, Brand, Sale
from django.db.models import Q
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.super.mixins.auth import AdminRequiredMixin

class HomeView(TemplateView):
    """ Vista principal de la página principal o HomePage. """
    
    template_name = 'components/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Supermarket'
        return context
    
class MenuView(AdminRequiredMixin, TemplateView):
    """
    Vista de menú o panel de admin incluyendo el notificador de ventas realizadas en tiempo real. 
    """
    
    template_name = 'components/menu.html'
    login_url = '/security/auth/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ventas de las últimas 24 horas para la notificación de bienvenida
        since = timezone.now() - timedelta(hours=24)
        recent_sales_count = Sale.objects.filter(sale_date__gte=since).count()
        context['recent_sales_count'] = recent_sales_count
        
        return context

class AboutView(TemplateView):
    """
    Vista de la página de información sobre nosotros o AboutPage. 
    """
    template_name = 'components/about.html'

class ContactView(View):
    """ 
    Vista de la página de contacto o ContactPage, con formulario de contacto y envío de correo electrónico. 
    """
    
    template_name = 'components/contact.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'title': 'Contáctanos'})

    def post(self, request, *args, **kwargs):
        # 1. Captura de datos del formulario
        full_name    = request.POST.get('name', '').strip()
        user_email   = request.POST.get('email', '').strip()
        subject_form = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()

        # 2. Fecha y hora actuales
        now    = timezone.localtime(timezone.now())
        date_str = now.strftime('%d/%m/%Y')
        time_str = now.strftime('%H:%M hrs')

        # 3. Inicial para el avatar
        initial = full_name[0].upper() if full_name else '?'

        # 4. Cuerpo HTML del correo
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Nuevo Mensaje de Contacto</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:#f0f4f0; font-family:'DM Sans',Arial,sans-serif; color:#1a1a1a; padding:32px 16px; }}
    .wrapper {{ max-width:580px; margin:0 auto; }}

    /* Header */
    .header {{ background:linear-gradient(135deg,#16a34a 0%,#15803d 60%,#166534 100%); border-radius:16px 16px 0 0; padding:36px 40px 28px; position:relative; overflow:hidden; }}
    .header::before {{ content:''; position:absolute; top:-40px; right:-40px; width:180px; height:180px; background:rgba(255,255,255,0.06); border-radius:50%; }}
    .header::after  {{ content:''; position:absolute; bottom:-60px; left:-20px; width:220px; height:220px; background:rgba(255,255,255,0.04); border-radius:50%; }}
    .header-logo {{ display:flex; align-items:center; gap:10px; margin-bottom:20px; }}
    .header-logo-icon {{ width:40px; height:40px; background:rgba(255,255,255,0.2); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px; }}
    .header-logo-text {{ color:rgba(255,255,255,0.9); font-size:13px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; }}
    .header-badge {{ display:inline-block; background:rgba(255,255,255,0.18); color:#ffffff; font-size:11px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; padding:4px 12px; border-radius:20px; margin-bottom:14px; position:relative; z-index:1; }}
    .header-title {{ color:#ffffff; font-size:26px; font-weight:700; line-height:1.2; position:relative; z-index:1; }}
    .header-subtitle {{ color:rgba(255,255,255,0.75); font-size:14px; margin-top:6px; position:relative; z-index:1; }}

    /* Body */
    .body {{ background:#ffffff; padding:36px 40px; }}
    .sender-card {{ background:#f8fdf9; border:1.5px solid #d1fae5; border-radius:12px; padding:20px 24px; margin-bottom:28px; display:flex; align-items:center; gap:16px; }}
    .sender-avatar {{ width:52px; height:52px; background:linear-gradient(135deg,#16a34a,#4ade80); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; color:white; font-weight:700; flex-shrink:0; }}
    .sender-name  {{ font-size:17px; font-weight:700; color:#111827; }}
    .sender-email {{ font-size:13px; color:#16a34a; font-family:'DM Mono',monospace; margin-top:2px; word-break:break-all; }}
    .section-label {{ font-size:10px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#9ca3af; margin-bottom:8px; }}
    .subject-row {{ background:#fffbeb; border-left:4px solid #f59e0b; border-radius:0 8px 8px 0; padding:14px 18px; margin-bottom:28px; }}
    .subject-text {{ font-size:16px; font-weight:600; color:#92400e; }}
    .message-box {{ background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px; padding:24px; margin-bottom:28px; }}
    .message-text {{ font-size:15px; line-height:1.75; color:#374151; white-space:pre-wrap; word-break:break-word; }}
    .meta-row {{ display:flex; gap:12px; margin-bottom:28px; flex-wrap:wrap; }}
    .meta-chip {{ background:#f3f4f6; border-radius:8px; padding:10px 14px; flex:1; min-width:120px; }}
    .meta-chip-label {{ font-size:10px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#9ca3af; margin-bottom:3px; }}
    .meta-chip-value {{ font-size:13px; font-weight:600; color:#1f2937; font-family:'DM Mono',monospace; }}
    .divider {{ border:none; border-top:1px solid #e5e7eb; margin:28px 0; }}
    .cta-wrap {{ text-align:center; margin-bottom:4px; }}
    .cta-btn {{ display:inline-block; background:linear-gradient(135deg,#16a34a,#15803d); color:#ffffff !important; text-decoration:none; font-size:14px; font-weight:700; letter-spacing:0.03em; padding:14px 36px; border-radius:10px; box-shadow:0 4px 14px rgba(22,163,74,0.35); }}

    /* Footer */
    .footer {{ background:#1f2937; border-radius:0 0 16px 16px; padding:24px 40px; text-align:center; }}
    .footer-logo {{ color:#4ade80; font-size:15px; font-weight:700; letter-spacing:0.06em; margin-bottom:8px; }}
    .footer-text {{ color:#9ca3af; font-size:12px; line-height:1.6; }}
    .footer-links {{ margin-top:14px; display:flex; justify-content:center; gap:20px; }}
    .footer-link {{ color:#6b7280; font-size:12px; text-decoration:none; }}
  </style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <div class="header-logo">
      <div class="header-logo-icon">&#128722;</div>
      <span class="header-logo-text">MySupermarket</span>
    </div>
    <div class="header-badge">&#128236; Formulario de Contacto</div>
    <div class="header-title">Nuevo mensaje recibido</div>
    <div class="header-subtitle">Un cliente ha enviado un mensaje desde el sitio web</div>
  </div>

  <div class="body">

    <div class="section-label">Remitente</div>
    <div class="sender-card">
      <div class="sender-avatar">{initial}</div>
      <div>
        <div class="sender-name">{full_name}</div>
        <div class="sender-email">{user_email}</div>
      </div>
    </div>

    <div class="section-label">Asunto del mensaje</div>
    <div class="subject-row">
      <div class="subject-text">{subject_form}</div>
    </div>

    <div class="section-label">Mensaje</div>
    <div class="message-box">
      <div class="message-text">{message_body}</div>
    </div>

    <div class="meta-row">
      <div class="meta-chip">
        <div class="meta-chip-label">&#128197; Fecha</div>
        <div class="meta-chip-value">{date_str}</div>
      </div>
      <div class="meta-chip">
        <div class="meta-chip-label">&#128336; Hora</div>
        <div class="meta-chip-value">{time_str}</div>
      </div>
      <div class="meta-chip">
        <div class="meta-chip-label">&#127760; Canal</div>
        <div class="meta-chip-value">Web</div>
      </div>
    </div>

    <hr class="divider" />

    <div class="cta-wrap">
      <a href="mailto:{user_email}" class="cta-btn">&#9993;&#65039; Responder al cliente</a>
    </div>

  </div>

  <div class="footer">
    <div class="footer-logo">&#128722; MySupermarket</div>
    <div class="footer-text">
      Este correo fue generado autom&aacute;ticamente por el sistema de contacto.<br>
      Av. Principal 123, Guayaquil, Ecuador &middot; contacto@mysupermarket.com
    </div>
  </div>

</div>
</body>
</html>"""

        # 5. Texto plano (fallback)
        text_content = (
            f"Nuevo mensaje de contacto\n"
            f"{'='*40}\n"
            f"CLIENTE : {full_name}\n"
            f"CORREO  : {user_email}\n"
            f"ASUNTO  : {subject_form}\n"
            f"FECHA   : {date_str} {time_str}\n"
            f"{'='*40}\n\n"
            f"{message_body}\n\n"
            f"{'='*40}\n"
            f"Responder a: {user_email}"
        )

        try:
            email = EmailMultiAlternatives(
                subject=f"[MySupermarket] {subject_form}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,   # Siempre el remitente autenticado
                to=[settings.EMAIL_HOST_USER],
                reply_to=[f"{full_name} <{user_email}>"], # "Responder a" apunta al cliente
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            messages.success(request, '¡Tu mensaje ha sido enviado con éxito!')
            return redirect('super:contact')

        except Exception as e:
            messages.error(request, f'Error al procesar el envío: {str(e)}')
            return render(request, self.template_name, {'title': 'Contáctanos'})


class ProductCatalogView(ListView):
    """ 
    Vista de catálogo de productos con filtros por categoría, marca y búsqueda por nombre o descripción.
    """
    
    model = Product 
    template_name = 'super/catalog/catalog.html'
    context_object_name = 'products' 
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset() 
        category_id = self.request.GET.get('category')
        brand_id    = self.request.GET.get('brand')
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