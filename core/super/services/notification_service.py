from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from collections import defaultdict
from core.super.models import RepurchasePattern

NOTIFICATION_COOLDOWN_DAYS = 7  # no reenviar antes de 7 días, aunque siga is_due


class RepurchaseNotificationService:
    """Servicio para enviar notificaciones de reposición a clientes con productos por reponer."""
    def notify_all_due(self):
        today = timezone.localdate()

        due_patterns = (
            RepurchasePattern.objects
            .filter(is_due=True, customer__email__isnull=False)
            .exclude(customer__email='')
            .filter(
                Q(last_notified__isnull=True) |
                Q(last_notified__lte=today - timezone.timedelta(days=NOTIFICATION_COOLDOWN_DAYS))
            )
            .select_related('customer', 'product')
        )

        # Agrupamos por cliente: si tiene 3 productos por reponer, un solo correo, no tres.
        by_customer = defaultdict(list)
        for pattern in due_patterns:
            by_customer[pattern.customer].append(pattern)

        sent_count = 0
        for customer, patterns in by_customer.items():
            if self._send_email(customer, patterns):
                for p in patterns:
                    p.last_notified = today
                RepurchasePattern.objects.bulk_update(patterns, ['last_notified'])
                sent_count += 1

        return sent_count

    def _send_email(self, customer, patterns):
        product_lines = "\n".join(
            f"  • {p.product.name} (sueles comprarlo cada {round(p.avg_interval_days)} días)"
            for p in patterns
        )

        subject = "¿Se te está acabando algo? 🛒"
        message = (
            f"Hola {customer.name},\n\n"
            f"Notamos que probablemente necesites reponer:\n\n"
            f"{product_lines}\n\n"
            f"Visítanos en la tienda cuando quieras.\n\n"
            f"— My Supermarket"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False,
            )
            return True
        except Exception:
            return False
