from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from config.utils import get_image
from django.forms import model_to_dict

class Brand(models.Model):
    id_brand = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)

    @property
    def id(self):
        return self.id_brand
    
    def __str__(self):
        return f'Marca : {self.name}'
    
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['id_brand', 'name'] 
        indexes = [
            models.Index(fields=['name']),
        ]

class Category(models.Model):
    id_category = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)

    @property
    def id(self):
        return self.id_category
    
    def __str__(self):
        return f'Categoria : {self.name}'
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['id_category', 'name'] 
        indexes = [
            models.Index(fields=['name']),
        ]

class PaymentMethod(models.Model):
    id_payment_method = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)

    @property
    def id(self):
        return self.id_payment_method
    
    def __str__(self):
        return f'Forma de Pago : {self.name}'
    
    class Meta:
        verbose_name = "Forma de Pago"
        verbose_name_plural = "Forma de Pagos"
        ordering = ['id_payment_method', 'name'] 
        indexes = [
            models.Index(fields=['name']),
        ]

class Customer(models.Model):
    class GenderChoices(models.IntegerChoices):
        Male = 1, 'Masculino'
        Female = 2, 'Femenino'
    
    id_customer = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Apellido", blank=True, null=True)
    dni = models.CharField(max_length=100, verbose_name="Cédula", blank=False, null=False, unique=True)
    email = models.EmailField(max_length=100, verbose_name="Email", blank=True, null=True, unique=True)
    address = models.CharField(max_length=100, verbose_name="Dirección", blank=True, null=True)
    phone = models.CharField(max_length=100, verbose_name="Telefono", blank=True, null=True, unique=True)
    birth_date = models.DateField(verbose_name="Fecha de nacimiento", blank=True, null=True)
    gender = models.IntegerField(choices=GenderChoices.choices, default=GenderChoices.Male, verbose_name="Genero", blank=True, null=True)

    @property
    def id(self):
        return self.id_customer
    
    def get_full_name(self):
        return f'{self.name} {self.last_name}'
    
    def __str__(self):
        return f'Cliente : {self.get_full_name()}'
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['id_customer', 'name', 'last_name'] 
        indexes = [models.Index(fields=['name']),
                   models.Index(fields=['last_name']),
                   models.Index(fields=['dni']),
                   models.Index(fields=['email']),
                   models.Index(fields=['address']),
                   models.Index(fields=['phone']),
                   models.Index(fields=['birth_date']),
                   models.Index(fields=['gender']),
        ]

class Seller(models.Model):
    class GenderChoices(models.IntegerChoices):
        Male = 1, 'Masculino'
        Female = 2, 'Femenino'

    id_seller = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Apellido", blank=True, null=True)
    dni = models.CharField(max_length=100, verbose_name="Cédula", blank=False, null=False, unique=True)
    email = models.EmailField(max_length=100, verbose_name="Email", blank=True, null=True, unique=True)
    address = models.CharField(max_length=100, verbose_name="Dirección", blank=True, null=True)
    phone = models.CharField(max_length=100, verbose_name="Telefono", blank=True, null=True, unique=True)
    birth_date = models.DateField(verbose_name="Fecha de nacimiento", blank=True, null=True)
    gender = models.IntegerField(choices=GenderChoices.choices, default=GenderChoices.Male, verbose_name="Genero", blank=True, null=True)

    @property
    def id(self):
        return self.id_seller
    
    def get_full_name(self):
        return f'{self.name} {self.last_name}'
    
    def __str__(self):
        return f'Vendedor : {self.get_full_name()}'
    
    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ['id_seller', 'name', 'last_name']
        indexes = [models.Index(fields=['name']),
                   models.Index(fields=['last_name']),
                   models.Index(fields=['dni']),
                   models.Index(fields=['email']),
                   models.Index(fields=['address']),
                   models.Index(fields=['phone']),
                   models.Index(fields=['birth_date']),
                   models.Index(fields=['gender']),
        ]

class Product(models.Model):
    id_product = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Marca", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoria", blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Nombre", blank=True, null=True)
    description = models.TextField(verbose_name="Descripción", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio", blank=True, null=True)
    stock = models.IntegerField(default=0, verbose_name="Stock", blank=True, null=True)
    image = models.ImageField(upload_to='products', verbose_name="Imágen", blank=True, null=True)
    barcode = models.CharField(max_length=100, verbose_name="Código de barras", blank=True, null=True, unique=True)
    production_date = models.DateField(default=timezone.now, verbose_name="Fecha de elaboración", blank=True, null=True)
    expiration_date = models.DateField(verbose_name="Fecha de vencimiento", blank=True, null=True) 
    state = models.BooleanField(default=True, verbose_name="Estado", blank=True, null=True)

    @property
    def id(self):
        return self.id_product

    def save(self, *args, **kwargs):
        self.state = self.stock > 0  # Asegura que el estado se calcule antes de guardar
        super().save(*args, **kwargs)

    def get_image_url(self):
        return get_image(self.image)
    
    def __str__(self):
        return f'Producto : {self.name}'
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['id_product', 'name'] 
        indexes = [models.Index(fields=['name']),
                   models.Index(fields=['brand']),
                   models.Index(fields=['category']),
                   models.Index(fields=['description']),
                   models.Index(fields=['stock']),
                   models.Index(fields=['barcode']),
                   models.Index(fields=['production_date']),
                   models.Index(fields=['expiration_date']),
                   models.Index(fields=['state']),
        ]
        constraints = [
            CheckConstraint(check=Q(stock__gte=0), name='product_stock_non_negative'),
            CheckConstraint(check=Q(price__gt=0), name='product_price_non_negative')
        ]

class Sale(models.Model):
    id_sale = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Cliente", blank=True, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name="Vendedor", blank=True, null=True)
    payment = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="Forma de pago", blank=True, null=True)
    sale_date = models.DateField(default=timezone.now, verbose_name="Fecha de venta", blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Subtotal", blank=True, null=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="IVA", blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Descuento", blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Total", blank=True, null=True)

    @property
    def id(self):
        return self.id_sale

    def __str__(self):
        return f'Venta N°{self.id} - {self.sale_date}'

    def get_model_dict(self):
        return model_to_dict(self)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['id_sale']
        indexes = [
            models.Index(fields=['sale_date']),
            models.Index(fields=['customer']),
            models.Index(fields=['seller']),
        ]
        constraints = [
            CheckConstraint(check=Q(subtotal__gte=0), name='sale_subtotal_non_negative'),
            CheckConstraint(check=Q(iva__gte=0), name='sale_iva_non_negative'),
            CheckConstraint(check=Q(discount__gte=0), name='sale_discount_non_negative'),
            CheckConstraint(check=Q(total__gte=0), name='sale_total_non_negative'),
        ]

class SaleDetail(models.Model):
    id_detail = models.AutoField(primary_key=True, verbose_name="ID", blank=False, null=False, unique=True)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name="Venta", blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto", blank=True, null=True)
    quantity = models.IntegerField(default=1, verbose_name="Cantidad", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio", blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Subtotal", blank=True, null=True)

    @property
    def id(self):
        return self.id_detail

    def __str__(self):
        return f'Detalle de Venta : {self.sale.id}'

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalle de Ventas"
        ordering = ['id_detail', 'sale', 'product']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sale']),
        ]
        constraints = [
            CheckConstraint(check=Q(quantity__gte=1), name='saledetail_quantity_non_negative'),
            CheckConstraint(check=Q(price__gte=0), name='saledetail_price_non_negative'),
            CheckConstraint(check=Q(subtotal__gte=0), name='saledetail_subtotal_non_negative')
        ]

# Models para clientes compradores

# Agregar al archivo core/super/models.py

from django.conf import settings
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    def __str__(self):
        return f'Carrito de {self.user.username}'
    
    def get_total(self):
        items = self.items.all()  # Ahora usa 'items' en lugar de 'cartitem_set'
        total = sum(item.get_subtotal() for item in items)
        return total
    
    def get_subtotal(self):
        return self.get_total() / Decimal('1.15')  # Sin IVA
    
    def get_iva(self):
        return self.get_total() - self.get_subtotal()
    
    def get_item_count(self):
        return self.items.count()  # Ahora usa 'items' en lugar de 'cartitem_set'
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Carrito")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.IntegerField(default=1, verbose_name="Cantidad")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de agregado")
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
    
    def get_subtotal(self):
        return self.product.price * self.quantity
    
    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ('cart', 'product')

