from datetime import timedelta
from decimal import Decimal
from django.db.models import Count, Avg, Max, Q
from django.utils import timezone
from core.super.models import Customer, CustomerInsight


class RFMSegmentationService:
    """Calcula segmentación RFM para todos los clientes."""
    def recalculate_all(self):
        today = timezone.localdate()
        thirty_days_ago = today - timedelta(days=30)

        customers = Customer.objects.annotate(
            last_sale=Max('sale__sale_date'),
            freq_30d=Count('sale', filter=Q(sale__sale_date__gte=thirty_days_ago)),
            avg_ticket=Avg('sale__total'),
        )

        count = 0
        for customer in customers:
            recency = (today - customer.last_sale.date()).days if customer.last_sale else 999
            segment = self._classify(recency, customer.freq_30d, customer.avg_ticket)

            CustomerInsight.objects.update_or_create(
                customer=customer,
                defaults={
                    'recency_days': recency,
                    'frequency_30d': customer.freq_30d,
                    'avg_ticket': customer.avg_ticket or Decimal('0'),
                    'segment': segment,
                }
            )
            count += 1
        return count

    def _classify(self, recency, freq_30d, avg_ticket):
        if recency >= 999:
            return 'nuevo'
        if recency <= 15 and freq_30d >= 3:
            return 'campeon'
        if recency <= 20 and freq_30d >= 1:
            return 'leal'
        if 20 < recency <= 45:
            return 'en_riesgo'
        return 'perdido'


class DiscountSuggestionService:
    """Sugiere descuentos basados en la segmentación RFM del cliente."""
    SUGGESTED_DISCOUNTS = {
        'en_riesgo': (15, 7),
        'perdido':   (20, 10),
        'campeon':   (5, 30),
    }

    def suggest_for(self, customer):
        insight = getattr(customer, 'insight', None)
        if not insight:
            return None
        rule = self.SUGGESTED_DISCOUNTS.get(insight.segment)
        if not rule:
            return None
        pct, days = rule
        return {'percentage': pct, 'expiry': timezone.localdate() + timedelta(days=days)}
