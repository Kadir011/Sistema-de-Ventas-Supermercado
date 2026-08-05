from django.core.management.base import BaseCommand
from core.super.services.notification_service import RepurchaseNotificationService


class Command(BaseCommand):
    help = 'Envía recordatorios de reposición a clientes con productos por reponer.'

    def handle(self, *args, **options):
        self.stdout.write('Enviando recordatorios de reposición...')
        count = RepurchaseNotificationService().notify_all_due()
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} correos enviados.'))
