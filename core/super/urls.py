from django.urls import path 
from core.super.views import customer, product, seller, sale, scan_barcode
from core.super.views import home

app_name = 'super'

urlpatterns = [
    #HOME
    path('', home.HomeView.as_view(), name='home'),
    path('menu/', home.MenuView.as_view(), name='menu'),    
    path('about/', home.AboutView.as_view(), name='about'),
    path('contact/', home.ContactView.as_view(), name='contact'),
    path('catalogo/', home.ProductCatalogView.as_view(), name='catalog'),

    #CLIENTES
    path('clientes/', customer.CustomerListView.as_view(), name='customer_list'),
    path('clientes/crear/', customer.CustomerCreateView.as_view(), name='customer_create'),
    path('clientes/editar/<int:pk>/', customer.CustomerUpdateView.as_view(), name='customer_update'),
    path('clientes/eliminar/<int:pk>/', customer.CustomerDeleteView.as_view(), name='customer_delete'),

    #VENDEDORES
    path('vendedores/', seller.SellerListView.as_view(), name='seller_list'), 
    path('vendedores/crear/', seller.SellerCreateView.as_view(), name='seller_create'),
    path('vendedores/editar/<int:pk>/', seller.SellerUpdateView.as_view(), name='seller_update'),
    path('vendedores/eliminar/<int:pk>/', seller.SellerDeleteView.as_view(), name='seller_delete'),

    #PRODUCTOS
    path('productos/', product.ProductListView.as_view(), name='product_list'),
    path('productos/crear/', product.ProductCreateView.as_view(), name='product_create'),
    path('productos/editar/<int:pk>/', product.ProductUpdateView.as_view(), name='product_update'),
    path('productos/eliminar/<int:pk>/', product.ProductDeleteView.as_view(), name='product_delete'),
    path('productos/<int:pk>/', product.ProductDetailView.as_view(), name='product_detail'),

    #VENTAS
    path('ventas/', sale.SaleListView.as_view(), name='sale_list'),
    path('ventas/crear/', sale.SaleCreateView.as_view(), name='sale_create'),
    path('ventas/editar/<int:pk>/', sale.SaleUpdateView.as_view(), name='sale_update'),
    path('ventas/eliminar/<int:pk>/', sale.SaleDeleteView.as_view(), name='sale_delete'),
    path('api/products/', sale.ProductView.as_view(), name='get_products'),

    #ESCANEAR PRODUCTOS
    path('scan_barcode/', scan_barcode.ScannerTemplate.as_view(), name='scan_barcode'),
]






