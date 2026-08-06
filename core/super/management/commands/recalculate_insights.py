from django.core.management.base import BaseCommand
from django.utils import timezone
from core.super.services.rfm_service import RFMSegmentationService
from core.super.services.repurchase_service import RepurchasePredictionService
from core.super.services.market_basket_service import MarketBasketService


class Command(BaseCommand):
    help = 'Recalcula segmentación RFM, patrones de recompra y afinidad de productos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only',
            choices=['rfm', 'repurchase', 'affinity'],
            help='Ejecutar solo una de las tareas (por defecto corren todas).',
        )

    def handle(self, *args, **options):
        start = timezone.now()
        only = options.get('only')

        if only in (None, 'rfm'):
            self.stdout.write('Recalculando segmentación RFM...')
            count = RFMSegmentationService().recalculate_all()
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count} clientes procesados.'))

        if only in (None, 'repurchase'):
            self.stdout.write('Recalculando patrones de recompra...')
            count = RepurchasePredictionService().recalculate_all()
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count} pares cliente-producto procesados.'))

        if only in (None, 'affinity'):
            self.stdout.write('Recalculando afinidad de productos...')
            count = MarketBasketService().recalculate_all()
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count} combinaciones de productos detectadas.'))

        elapsed = (timezone.now() - start).total_seconds()
        self.stdout.write(self.style.SUCCESS(f'Listo en {elapsed:.1f}s.'))
