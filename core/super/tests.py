from decimal import Decimal
import uuid
from django.test import TestCase
from core.super.services.payment_processors import get_processor, CashPaymentProcessor, CardPaymentProcessor, TransferPaymentProcessor
from core.super.services.idempotency_service import IdempotencyService
from core.super.models import Sale, Customer, Seller, PaymentMethod


class PaymentProcessorTestCase(TestCase):
    def test_cash_processor_calculates_received_and_change(self):
        processor = get_processor('efectivo')
        self.assertIsInstance(processor, CashPaymentProcessor)

        total = Decimal('100.00')
        post_data = {'amount_received': '150.00'}
        received, change = processor.calculate_received_and_change(total, post_data)
        self.assertEqual(received, Decimal('150.00'))
        self.assertEqual(change, Decimal('50.00'))

    def test_card_processor_returns_total_no_change(self):
        processor = get_processor('tarjeta de crédito')
        self.assertIsInstance(processor, CardPaymentProcessor)
        total = Decimal('100.00')
        received, change = processor.calculate_received_and_change(total, {})
        self.assertEqual(received, total)
        self.assertEqual(change, Decimal('0.00'))

    def test_unknown_processor_falls_back_to_cash(self):
        processor = get_processor('cheque no válido')
        self.assertIsInstance(processor, CashPaymentProcessor)


class IdempotencyServiceTestCase(TestCase):
    def test_singleton_instance(self):
        s1 = IdempotencyService()
        s2 = IdempotencyService()
        self.assertIs(s1, s2)

    def test_parse_key_valid_and_invalid(self):
        valid_id = str(uuid.uuid4())
        parsed = IdempotencyService().parse_key(valid_id)
        self.assertEqual(str(parsed), valid_id)

        parsed_none = IdempotencyService().parse_key('invalid-uuid-0000')
        self.assertIsNone(parsed_none)

    def test_find_existing_sale_by_idempotency_key(self):
        sale = Sale.objects.create(total=Decimal('5.00'))
        key = uuid.uuid4()
        sale.idempotency_key = key
        sale.save()

        found = IdempotencyService().find_existing(key)
        self.assertEqual(found.pk, sale.pk)

        missing = IdempotencyService().find_existing(uuid.uuid4())
        self.assertIsNone(missing)

