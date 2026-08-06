"""
Market basket analysis: detecta qué productos se compran juntos con
frecuencia, usando el historial real de SaleDetail. No usa nada de
machine learning — es conteo de co-ocurrencia + confianza, el mismo
principio detrás de "la gente que compró esto también compró...".
"""

from collections import defaultdict
from itertools import combinations
from core.super.models import SaleDetail, ProductAffinity


class MarketBasketService:
    MIN_CO_OCCURRENCE = 3   # menos de esto, es coincidencia, no patrón
    MIN_CONFIDENCE = 0.3    # bajo 30% de "si compra A, compra B", no vale la pena sugerirlo
    TOP_N_PER_PRODUCT = 3   # cuántas sugerencias guardar por producto, para no acumular basura

    def recalculate_all(self):
        baskets = self._build_baskets()
        purchase_counts = self._count_purchases_per_product(baskets)
        co_counts = self._count_co_occurrences(baskets)

        affinities = self._build_affinities(co_counts, purchase_counts)
        affinities = self._keep_top_n_per_product(affinities)

        # Reemplazo completo: las combinaciones cambian con el tiempo (productos
        # nuevos, patrones que dejan de cumplirse), así que en vez de ir
        # actualizando fila por fila, se recalcula desde cero cada vez.
        ProductAffinity.objects.all().delete()
        ProductAffinity.objects.bulk_create([
            ProductAffinity(
                product_a_id=a,
                product_b_id=b,
                co_occurrence_count=co_counts[frozenset((a, b))],
                confidence=confidence,
            )
            for (a, b), confidence in affinities.items()
        ])
        return len(affinities)

    def _build_baskets(self):
        """Un 'basket' = el conjunto de productos distintos comprados en UNA venta."""
        baskets = defaultdict(set)
        details = SaleDetail.objects.filter(product__isnull=False).values('sale_id', 'product_id')
        for row in details:
            baskets[row['sale_id']].add(row['product_id'])
        # Descartamos ventas de un solo producto — no aportan co-ocurrencia
        return {sale_id: products for sale_id, products in baskets.items() if len(products) >= 2}

    def _count_purchases_per_product(self, baskets):
        """En cuántos baskets (ventas) distintas aparece cada producto."""
        counts = defaultdict(int)
        for products in baskets.values():
            for product_id in products:
                counts[product_id] += 1
        return counts

    def _count_co_occurrences(self, baskets):
        """Cuántas veces aparecen A y B juntos en el mismo basket (no direccional)."""
        counts = defaultdict(int)
        for products in baskets.values():
            for a, b in combinations(sorted(products), 2):
                counts[frozenset((a, b))] += 1
        return counts

    def _build_affinities(self, co_counts, purchase_counts):
        """
        Genera confianza en AMBAS direcciones para cada par que cumpla el
        mínimo de co-ocurrencia: confidence(A→B) = co(A,B) / compras(A).
        """
        affinities = {}
        for pair, co_count in co_counts.items():
            if co_count < self.MIN_CO_OCCURRENCE:
                continue
            a, b = tuple(pair)
            for source, target in ((a, b), (b, a)):
                confidence = co_count / purchase_counts[source]
                if confidence >= self.MIN_CONFIDENCE:
                    affinities[(source, target)] = confidence
        return affinities

    def _keep_top_n_per_product(self, affinities):
        """Por cada producto origen, solo nos quedamos con sus N mejores sugerencias."""
        by_source = defaultdict(list)
        for (source, target), confidence in affinities.items():
            by_source[source].append((target, confidence))

        trimmed = {}
        for source, targets in by_source.items():
            targets.sort(key=lambda t: t[1], reverse=True)
            for target, confidence in targets[:self.TOP_N_PER_PRODUCT]:
                trimmed[(source, target)] = confidence
        return trimmed
