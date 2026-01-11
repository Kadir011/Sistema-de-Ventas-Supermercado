from django.urls import path 
from core.super.views import customer, product, seller, sale, scan_barcode, shop, cart
from core.super.views import home

app_name = 'super'

urlpatterns = [
    # HOME
    path('', home.HomeView.as_view(), name='home'),
    path('about/', home.AboutView.as_view(), name='about'),
    path('contact/', home.ContactView.as_view(), name='contact'),
    path('catalogo/', home.ProductCatalogView.as_view(), name='catalog'),

    # TIENDA PARA CLIENTES
    path('tienda/', shop.ShopView.as_view(), name='shop'),
    path('producto/<int:pk>/', shop.ProductDetailCustomerView.as_view(), name='product_detail_customer'),
    
    # CARRITO
    path('carrito/', cart.CartView.as_view(), name='cart'),
    path('carrito/agregar/<int:product_id>/', cart.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:item_id>/', cart.update_cart_item, name='update_cart_item'),
    path('carrito/eliminar/<int:item_id>/', cart.remove_from_cart, name='remove_from_cart'),
    path('carrito/checkout/', cart.CheckoutView.as_view(), name='checkout'),
    path('cart/count/', cart.cart_count, name='cart_count'),
    
    # MIS COMPRAS
    path('mis-compras/', shop.MyOrdersView.as_view(), name='my_orders'),
    path('mis-compras/<int:pk>/', shop.OrderDetailView.as_view(), name='order_detail'),

    # ADMIN MENU
    path('menu/', home.MenuView.as_view(), name='menu'),

    # CLIENTES (ADMIN)
    path('clientes/', customer.CustomerListView.as_view(), name='customer_list'),
    path('clientes/crear/', customer.CustomerCreateView.as_view(), name='customer_create'),
    path('clientes/editar/<int:pk>/', customer.CustomerUpdateView.as_view(), name='customer_update'),
    path('clientes/eliminar/<int:pk>/', customer.CustomerDeleteView.as_view(), name='customer_delete'),

    # VENDEDORES (ADMIN)
    path('vendedores/', seller.SellerListView.as_view(), name='seller_list'), 
    path('vendedores/crear/', seller.SellerCreateView.as_view(), name='seller_create'),
    path('vendedores/editar/<int:pk>/', seller.SellerUpdateView.as_view(), name='seller_update'),
    path('vendedores/eliminar/<int:pk>/', seller.SellerDeleteView.as_view(), name='seller_delete'),

    # PRODUCTOS (ADMIN)
    path('productos/', product.ProductListView.as_view(), name='product_list'),
    path('productos/crear/', product.ProductCreateView.as_view(), name='product_create'),
    path('productos/editar/<int:pk>/', product.ProductUpdateView.as_view(), name='product_update'),
    path('productos/eliminar/<int:pk>/', product.ProductDeleteView.as_view(), name='product_delete'),
    path('productos/<int:pk>/', product.ProductDetailView.as_view(), name='product_detail'),

    # VENTAS (ADMIN)
    path('ventas/', sale.SaleListView.as_view(), name='sale_list'),
    path('ventas/crear/', sale.SaleCreateView.as_view(), name='sale_create'),
    path('ventas/editar/<int:pk>/', sale.SaleUpdateView.as_view(), name='sale_update'),
    path('ventas/eliminar/<int:pk>/', sale.SaleDeleteView.as_view(), name='sale_delete'),
    path('ventas/<int:pk>', sale.SaleDetailView.as_view(), name='sale_detail'),
    path('api/products/', sale.ProductView.as_view(), name='get_products'),
    path('ventas/factura/<int:pk>/', sale.SalePDFView.as_view(), name='sale_pdf'),
    
    # ESCANEAR PRODUCTOS
    path('scan_barcode/', scan_barcode.ScannerTemplate.as_view(), name='scan_barcode'),
]