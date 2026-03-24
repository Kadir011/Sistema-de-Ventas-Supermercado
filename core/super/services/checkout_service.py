from decimal import Decimal
from django.utils import timezone
from core.super.models import Sale, SaleDetail, Customer, Seller, PaymentMethod

# SRP — Extraer servicios de CheckoutView y sale.py
# Clase que se encarga de resolver el checkout (SRP - Single Responsibility Principle)
class CheckoutService:
    """Orquesta la creación de una venta desde el carrito."""

    # Método que se encarga de la información del cliente
    def resolve_customer(self, user, dni_type, customer_dni):
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
    def calculate_totals(self, cart, customer):
        cart_total = cart.get_total()
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