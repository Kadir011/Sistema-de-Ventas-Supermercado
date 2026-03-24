from decimal import Decimal
from abc import ABC, abstractmethod

# OCP + Strategy — Procesadores de pago
# Clase Padre que se encarga de resolver el tipo de pago
class PaymentProcessor(ABC):
    @abstractmethod
    def calculate_received_and_change(self, total, post_data) -> tuple[Decimal, Decimal]:
        pass

class CashPaymentProcessor(PaymentProcessor):
    def calculate_received_and_change(self, total, post_data):
        received_str = post_data.get('amount_received', '0')
        received = Decimal(received_str) if received_str else Decimal('0')
        return received, received - total

class CardPaymentProcessor(PaymentProcessor):
    def calculate_received_and_change(self, total, post_data):
        return total, Decimal('0.00')

class TransferPaymentProcessor(PaymentProcessor):
    def calculate_received_and_change(self, total, post_data):
        return total, Decimal('0.00')

# Registry — agregar nuevos métodos aquí sin tocar el checkout
PAYMENT_PROCESSORS = {
    'efectivo': CashPaymentProcessor(),
    'tarjeta de crédito': CardPaymentProcessor(),
    'tarjeta de débito': CardPaymentProcessor(),
    'transferencia bancaria': TransferPaymentProcessor(),
}

def get_processor(payment_name: str) -> PaymentProcessor:
    return PAYMENT_PROCESSORS.get(payment_name.lower(), CashPaymentProcessor())