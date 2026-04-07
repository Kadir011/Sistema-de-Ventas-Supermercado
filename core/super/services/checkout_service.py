from decimal import Decimal
from django.utils import timezone
from core.super.models import Sale, SaleDetail, Customer, Seller, PaymentMethod

# SRP — Extraer servicios de CheckoutView y sale.py

# Métodos de pago que sí admiten descuento personalizado.
# Consumidor Final (pago en Efectivo sin datos) queda EXCLUIDO porque
# el dni_type == 'final' nunca genera un Customer real con descuento.
# Aquí la restricción es a nivel de método de pago permitido.
DISCOUNT_ELIGIBLE_PAYMENT_NAMES = {
    'efectivo',
    'tarjeta de crédito',
    'tarjeta de débito',
}

# Clase que se encarga de resolver el checkout (SRP - Single Responsibility Principle)
class CheckoutService:
    """Orquesta la creación de una venta desde el carrito."""

    # Método que se encarga de la información del cliente
    def resolve_customer(self, user, dni_type, customer_dni):
        """
        Devuelve el Customer que corresponde a la compra.
 
        - dni_type == 'final'    → Cliente genérico "CONSUMIDOR FINAL" (sin descuento)
        - dni_type == 'personal' → Cliente identificado por su email/DNI (puede tener descuento)
        """
        if dni_type == 'final':
            customer, _ = Customer.objects.get_or_create(
                dni='9999999999',
                defaults={
                    'name': 'CONSUMIDOR', 
                    'last_name': 'FINAL', 
                    'address': 'S/N'
                }
            )
            return customer

        customer, _ = Customer.objects.get_or_create(
            email=user.email,
            defaults={
                'name': user.first_name,
                'last_name': user.last_name,
                'dni': customer_dni,
                'phone': user.phone_number,
                'address': user.address,
            }
        )
        if customer.dni != customer_dni:
            customer.dni = customer_dni
            customer.save()
        return customer

    # Método que se encarga de calcular los totales de la venta
    def calculate_totals(self, cart, customer, payment_name: str = '', dni_type: str = 'personal'):
        """
        Calcula subtotal, IVA, descuento y total.
 
        El descuento personal se aplica SOLO cuando:
          1. El tipo de factura es 'personal' (tiene datos del cliente)
          2. El método de pago admite descuento (Efectivo o Tarjeta)
          3. El cliente tiene un descuento activo y su vigencia no ha expirado
 
        En cualquier otro caso (Consumidor Final, Transferencia, descuento expirado)
        el descuento se fija en 0.
        """
        cart_total = cart.get_total()
        discount_amount = Decimal('0.00')
 
        is_eligible_payment = payment_name.lower() in DISCOUNT_ELIGIBLE_PAYMENT_NAMES
        is_personal = dni_type == 'personal'
        
        if is_personal and is_eligible_payment and customer.has_active_discount():
            discount_amount = cart_total * (customer.discount_percentage / 100)
        return {
            'subtotal': cart.get_subtotal(),
            'iva': cart.get_iva(),
            'discount': discount_amount,
            'total': cart_total - discount_amount,
        }

    # Método que se encarga de crear la venta
    def create_sale(self, user, customer, payment_id, totals,
                    amount_received, change, idempotency_key,
                    card_number_masked='', transfer_account_masked=''):
        seller, _ = Seller.objects.get_or_create(
            dni='9999999999',
            defaults={'name': 'Vendedor', 'last_name': 'Online'}
        )
        return Sale.objects.create(
            user=user,
            customer=customer,
            seller=seller,
            payment_id=payment_id,
            sale_date=timezone.now(),
            idempotency_key=idempotency_key,
            card_number_masked=card_number_masked,
            transfer_account_masked=transfer_account_masked,
            **totals,
            amount_received=amount_received,
            change=change,
        )
    
    # Método que se encarga de guardar los detalles de la venta
    def register_items(self, sale, items):
        for item in items:
            SaleDetail.objects.create(
                sale=sale,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.get_subtotal(),
            )
            item.product.stock -= item.quantity
            item.product.save()
        items.delete()