"""
Comando de desarrollo: crea ventas de prueba con fechas escalonadas
para poder ver los 4 segmentos RFM (campeon, leal, en_riesgo, perdido)
y generar datos suficientes para RepurchasePattern.

Uso:
    python manage.py seed_test_sales
    python manage.py seed_test_sales --clear   # borra solo las ventas creadas por este comando

NOTA: marca cada venta creada con card_number_masked='TEST-SEED' para
poder identificarlas y borrarlas después sin tocar ventas reales.
"""

import datetime
import uuid
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from core.super.models import Customer, Product, PaymentMethod, Sale, SaleDetail

TEST_MARKER = 'TEST-SEED'


class Command(BaseCommand):
    help = 'Crea ventas de prueba con fechas escalonadas para probar segmentación RFM y reposición.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Borra únicamente las ventas creadas por este comando (marcadas con TEST-SEED).',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()
            return

        customers = list(Customer.objects.all()[:3])
        if len(customers) < 3:
            self.stdout.write(self.style.ERROR(
                f'Se necesitan al menos 3 clientes registrados, encontré {len(customers)}.'
            ))
            return

        payment = PaymentMethod.objects.first()
        if not payment:
            self.stdout.write(self.style.ERROR(
                'No hay ninguna Forma de Pago registrada. Crea al menos una antes de correr esto.'
            ))
            return

        product = Product.objects.first()
        if not product:
            self.stdout.write(self.style.ERROR(
                'No hay ningún Producto registrado. Crea al menos uno antes de correr esto.'
            ))
            return

        today = timezone.localdate()
        c_campeon, c_riesgo, c_perdido = customers[0], customers[1], customers[2]

        created = 0

        # ── Cliente 1: CAMPEÓN → 3 ventas dentro de los últimos 15 días ──
        for days_ago in (2, 6, 12):
            self._create_sale(c_campeon, payment, product, today - datetime.timedelta(days=days_ago))
            created += 1

        # ── Cliente 2: EN RIESGO → 1 venta hace ~30 días (rango 21-45) ──
        self._create_sale(c_riesgo, payment, product, today - datetime.timedelta(days=30))
        created += 1

        # ── Cliente 3: PERDIDO → 1 venta hace ~60 días (más de 45) ──
        self._create_sale(c_perdido, payment, product, today - datetime.timedelta(days=60))
        created += 1

        # ── Reposición: 3 compras del mismo producto para el cliente CAMPEÓN,
        #    espaciadas ~8 días, para que RepurchasePattern tenga con qué calcular ──
        for days_ago in (24, 16, 8):
            self._create_sale(c_campeon, payment, product, today - datetime.timedelta(days=days_ago), with_detail=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {created} ventas de prueba creadas.'))
        self.stdout.write('Ahora corre: python manage.py recalculate_insights')
        self.stdout.write(self.style.WARNING(
            f'Recuerda: {c_campeon.get_full_name()} → Campeón | '
            f'{c_riesgo.get_full_name()} → En riesgo | '
            f'{c_perdido.get_full_name()} → Perdido'
        ))

    def _create_sale(self, customer, payment, product, sale_date, with_detail=False):
        naive_dt = datetime.datetime.combine(sale_date, datetime.time(12, 0))
        aware_dt = timezone.make_aware(naive_dt) if timezone.is_naive(naive_dt) else naive_dt

        subtotal = product.price or Decimal('10')
        iva = (subtotal * Decimal('0.15')).quantize(Decimal('0.01'))
        total = subtotal + iva

        sale = Sale.objects.create(
            customer=customer,
            payment=payment,
            sale_date=aware_dt,
            subtotal=subtotal,
            iva=iva,
            discount=0,
            total=total,
            amount_received=total,
            change=0,
            card_number_masked=TEST_MARKER,
            idempotency_key=uuid.uuid4(),
        )

        if with_detail:
            SaleDetail.objects.create(
                sale=sale,
                product=product,
                quantity=1,
                price=product.price or Decimal('10'),
                subtotal=product.price or Decimal('10'),
            )

        return sale

    def _clear(self):
        qs = Sale.objects.filter(card_number_masked=TEST_MARKER)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'✓ {count} ventas de prueba eliminadas.'))
        self.stdout.write('Corre de nuevo: python manage.py recalculate_insights para limpiar los segmentos.')
