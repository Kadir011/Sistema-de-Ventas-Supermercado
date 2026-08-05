from django.core.management.base import BaseCommand
from django.utils import timezone
from core.super.services.rfm_service import RFMSegmentationService
from core.super.services.repurchase_service import RepurchasePredictionService


class Command(BaseCommand):
    help = 'Recalcula segmentación RFM y patrones de recompra de todos los clientes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--only',
            choices=['rfm', 'repurchase'],
            help='Ejecutar solo una de las dos tareas (por defecto corre ambas).',
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

        elapsed = (timezone.now() - start).total_seconds()
        self.stdout.write(self.style.SUCCESS(f'Listo en {elapsed:.1f}s.'))
