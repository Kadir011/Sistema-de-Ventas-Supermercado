from core.super.models import Product, Category, Brand, PaymentMethod, Sale, SaleDetail
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# SRP — Separar builders del chatbot

class StoreContextBuilder:
    """Construye el contexto de inventario para el chatbot."""
    def build(self) -> str:
        categories = list(Category.objects.values_list('name', flat=True).order_by('name'))
        brands = list(Brand.objects.values_list('name', flat=True).order_by('name'))
        products = (
            Product.objects
            .filter(state=True, stock__gt=0)
            .select_related('category', 'brand')
            .order_by('name')
        )
        
        lines = [
            f"  - {p.name} | Categoría: {p.category.name if p.category else 'Sin categoría'}"
            f" | Marca: {p.brand.name if p.brand else 'Sin marca'}"
            f" | Precio: ${p.price:.2f} | Stock: {p.stock}"
            for p in products
        ]
        parts = []
        if categories:
            parts.append("CATEGORÍAS:\n  " + ", ".join(categories))
        if brands:
            parts.append("MARCAS:\n  " + ", ".join(brands))
        
        parts.append("PRODUCTOS:\n" + ("\n".join(lines) if lines else "Sin productos disponibles."))

        # Agregar métodos de pago
        active_payment_names = {"Efectivo", "Tarjeta de crédito", "Tarjeta de débito"}
        all_payments = PaymentMethod.objects.values_list("name", flat=True)
        active_payments = [p for p in all_payments if p in active_payment_names]
        inactive_payments = [p for p in all_payments if p not in active_payment_names]

        payment_info = []
        if active_payments:
            payment_info.append("Métodos ACTIVOS: " + ", ".join(active_payments))
        if inactive_payments:
            payment_info.append(
                "Métodos NO DISPONIBLES por el momento: "
                + ", ".join(inactive_payments)
                + " (en stand-by, no aceptados)"
            )
        parts.append("MÉTODOS DE PAGO:\n  " + "\n  ".join(payment_info))

        return "\n\n".join(parts)
    
class SalesContextBuilder:
    """Construye el contexto de ventas (solo para admins)."""

    def build(self) -> str:
        # exactamente lo que tenías en _build_sales_context() pero encapsulado
        # en un método para que puedas llamarlo desde otros context builders
        return self._build_sales_context()
    
    def _build_sales_context(self):
        """
        Contexto de ventas para administradores.
        Incluye: resumen de las últimas 24h, últimas 7 días, últimas 10 ventas detalladas
        y el top 5 de productos más vendidos.
        """
        try:
            now = timezone.now()
            last_24h  = now - timedelta(hours=24)
            last_7d   = now - timedelta(days=7)
            last_30d  = now - timedelta(days=30)

            # ── Conteos por período ───────────────────────────────────────
            count_24h = Sale.objects.filter(sale_date__gte=last_24h).count()
            count_7d  = Sale.objects.filter(sale_date__gte=last_7d).count()
            count_30d = Sale.objects.filter(sale_date__gte=last_30d).count()
            count_all = Sale.objects.count()

            # ── Totales recaudados ────────────────────────────────────────
            total_24h = Sale.objects.filter(sale_date__gte=last_24h).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
            total_7d  = Sale.objects.filter(sale_date__gte=last_7d).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
            total_30d = Sale.objects.filter(sale_date__gte=last_30d).aggregate(t=Sum('total'))['t'] or Decimal('0.00')

            # ── Últimas 10 ventas ─────────────────────────────────────────
            recent_sales = (
                Sale.objects
                .select_related("customer", "payment")
                .order_by("-sale_date")[:10]
            )

            recent_lines = []
            for s in recent_sales:
                fecha      = s.sale_date.strftime('%d/%m/%Y %H:%M')
                cliente    = s.customer.get_full_name() if s.customer else "Sin cliente"
                pago       = s.payment.name if s.payment else "N/A"
                recent_lines.append(
                    f"  - Venta #{s.id_sale:06d} | {fecha} | Cliente: {cliente} "
                    f"| Pago: {pago} | Total: ${s.total:.2f}"
                )

            # ── Top 5 productos más vendidos (últimos 30 días) ────────────
            top_products = (
                SaleDetail.objects
                .filter(sale__sale_date__gte=last_30d)
                .values("product__name")
                .annotate(total_qty=Sum("quantity"))
                .order_by("-total_qty")[:5]
            )

            top_lines = []
            for idx, tp in enumerate(top_products, 1):
                top_lines.append(
                    f"  {idx}. {tp['product__name']} — {tp['total_qty']} unidades vendidas"
                )

            # ── Construir el bloque de texto ──────────────────────────────
            parts = [
                "RESUMEN DE VENTAS (datos en tiempo real):",
                f"  • Últimas 24 horas : {count_24h} venta(s) | Recaudado: ${total_24h:.2f}",
                f"  • Últimos 7 días   : {count_7d} venta(s) | Recaudado: ${total_7d:.2f}",
                f"  • Últimos 30 días  : {count_30d} venta(s) | Recaudado: ${total_30d:.2f}",
                f"  • Total histórico  : {count_all} venta(s)",
            ]

            if recent_lines:
                parts.append("\nÚLTIMAS 10 VENTAS REGISTRADAS:")
                parts.extend(recent_lines)
            else:
                parts.append("\nÚLTIMAS VENTAS: No hay ventas registradas aún.")

            if top_lines:
                parts.append("\nTOP 5 PRODUCTOS MÁS VENDIDOS (últimos 30 días):")
                parts.extend(top_lines)

            return "\n".join(parts)

        except Exception as exc:
            return f"(No se pudo cargar el historial de ventas: {exc})"
    
class ChatContextDirector:
    """Ensambla el contexto completo según el rol del usuario."""

    def __init__(self, store_builder=None, sales_builder=None):
        self.store_builder = store_builder or StoreContextBuilder()
        self.sales_builder = sales_builder or SalesContextBuilder()

    def build_for_role(self, is_admin: bool) -> tuple[str, str]:
        store = self.store_builder.build()
        sales = self.sales_builder.build() if is_admin else ''
        return store, sales