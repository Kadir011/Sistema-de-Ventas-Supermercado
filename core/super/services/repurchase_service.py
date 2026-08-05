from django.db.models import Count
from django.utils import timezone
from core.super.models import SaleDetail, RepurchasePattern


class RepurchasePredictionService:
    """Calcula patrón de recompra por cliente/producto y predice cuándo avisar."""
    MIN_PURCHASES = 3  # menos de esto, el promedio es ruido

    def recalculate_all(self):
        today = timezone.localdate()

        pairs = (
            SaleDetail.objects
            .filter(sale__customer__isnull=False, product__isnull=False)
            .values('sale__customer', 'product')
            .annotate(count=Count('id_detail'))
            .filter(count__gte=self.MIN_PURCHASES)
        )

        count = 0
        for pair in pairs:
            customer_id = pair['sale__customer']
            product_id = pair['product']

            dates = list(
                SaleDetail.objects
                .filter(sale__customer_id=customer_id, product_id=product_id)
                .order_by('sale__sale_date')
                .values_list('sale__sale_date', flat=True)
            )
            if len(dates) < 2:
                continue

            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            avg_interval = sum(intervals) / len(intervals)
            last_date = dates[-1].date()
            days_since = (today - last_date).days

            RepurchasePattern.objects.update_or_create(
                customer_id=customer_id, product_id=product_id,
                defaults={
                    'avg_interval_days': avg_interval,
                    'last_purchase_date': last_date,
                    'purchase_count': pair['count'],
                    'is_due': days_since >= avg_interval * 0.9,
                }
            )
            count += 1
        return count
