from core.super.models import Product, Category, Brand, PaymentMethod, Sale, SaleDetail, Customer, RepurchasePattern
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


# ─────────────────────────────────────────────────────────────────
# Helpers compartidos
# ─────────────────────────────────────────────────────────────────

def _get_low_stock_products(threshold: int = 5) -> list[dict]:
    """Devuelve productos con stock ≤ threshold."""
    return list(
        Product.objects
        .filter(state=True, stock__lte=threshold, stock__gt=0)
        .select_related('category', 'brand')
        .order_by('stock')
        .values('name', 'stock', 'category__name', 'brand__name')[:10]
    )


def _get_out_of_stock_count() -> int:
    return Product.objects.filter(stock=0).count()


def _get_recent_products(days: int = 14, limit: int = 10):
    """
    Productos agregados al catálogo recientemente (created_at, NO
    production_date — eso es la fecha de fabricación del producto físico,
    esto es cuándo se registró en el sistema).

    Si no hay ninguno dentro de la ventana de `days`, cae al más reciente
    que exista igual (aunque sea uno solo) — así el bot siempre puede
    contestar "¿qué hay nuevo?" con algo, en vez de un vacío.
    Excluimos created_at nulo explícitamente: son productos que ya
    existían antes de agregar este campo, y NO deben aparecer como
    "recién agregados" solo porque Postgres podría ordenarlos primero
    al tener NULL en una fecha.
    """
    base_qs = Product.objects.filter(state=True, created_at__isnull=False).select_related('category', 'brand')

    cutoff = timezone.now() - timedelta(days=days)
    recent = list(base_qs.filter(created_at__gte=cutoff).order_by('-created_at')[:limit])
    if recent:
        return recent, True   # sí hay novedades dentro de la ventana normal

    fallback = list(base_qs.order_by('-created_at')[:1])
    return fallback, False    # no hay nada reciente, mostramos el último que exista igual


# ─────────────────────────────────────────────────────────────────
# SRP — Builders separados por responsabilidad
# ─────────────────────────────────────────────────────────────────

class StoreContextBuilder:
    """Construye el contexto de inventario para el chatbot (todos los roles)."""

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

        # ── Productos agregados recientemente ───────────────────────────
        recent_products, within_window = _get_recent_products(days=14, limit=10)
        if recent_products:
            recent_lines = [
                f"  - {p.name} | Categoría: {p.category.name if p.category else 'Sin categoría'}"
                f" | Precio: ${p.price:.2f} | Agregado: {p.created_at.strftime('%d/%m/%Y')}"
                for p in recent_products
            ]
            header = (
                "PRODUCTOS NUEVOS (agregados en los últimos 14 días):"
                if within_window else
                "PRODUCTO MÁS RECIENTE AGREGADO AL CATÁLOGO (no hay novedades en los últimos 14 días, pero este es el último que se registró):"
            )
            parts.append(header + "\n" + "\n".join(recent_lines))
        else:
            parts.append(
                "PRODUCTOS NUEVOS:\n  No hay información de fecha de registro disponible "
                "para ningún producto todavía (se activó recién, los productos ya existentes no tienen esa fecha)."
            )

        # Métodos de pago
        active_payment_names = {"Efectivo", "Tarjeta de crédito", "Tarjeta de débito"}
        all_payments = PaymentMethod.objects.values_list("name", flat=True)
        active_payments = [p for p in all_payments if p in active_payment_names]
        inactive_payments = [p for p in all_payments if p not in active_payment_names]

        payment_info = []
        if active_payments:
            payment_info.append("Métodos ACTIVOS: " + ", ".join(active_payments))
        if inactive_payments:
            payment_info.append(
                "Métodos NO DISPONIBLES: "
                + ", ".join(inactive_payments)
                + " (en stand-by)"
            )
        parts.append("MÉTODOS DE PAGO:\n  " + "\n  ".join(payment_info))

        return "\n\n".join(parts)


class SalesContextBuilder:
    """Construye el contexto de ventas solo para admins."""

    def build(self) -> str:
        try:
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d  = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)

            count_24h = Sale.objects.filter(sale_date__gte=last_24h).count()
            count_7d  = Sale.objects.filter(sale_date__gte=last_7d).count()
            count_30d = Sale.objects.filter(sale_date__gte=last_30d).count()
            count_all = Sale.objects.count()

            total_24h = Sale.objects.filter(sale_date__gte=last_24h).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
            total_7d  = Sale.objects.filter(sale_date__gte=last_7d).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
            total_30d = Sale.objects.filter(sale_date__gte=last_30d).aggregate(t=Sum('total'))['t'] or Decimal('0.00')
            avg_ticket= Sale.objects.filter(sale_date__gte=last_30d).aggregate(a=Avg('total'))['a'] or Decimal('0.00')

            recent_sales = (
                Sale.objects
                .select_related("customer", "payment", "seller")
                .order_by("-sale_date")[:10]
            )

            recent_lines = []
            for s in recent_sales:
                fecha   = s.sale_date.strftime('%d/%m/%Y %H:%M')
                cliente = s.customer.get_full_name() if s.customer else "Sin cliente"
                pago    = s.payment.name if s.payment else "N/A"
                vendedor= s.seller.get_full_name() if s.seller else "N/A"
                recent_lines.append(
                    f"  - Venta #{s.id_sale:06d} | {fecha} | Cliente: {cliente} "
                    f"| Vendedor: {vendedor} | Pago: {pago} | Total: ${s.total:.2f}"
                )

            top_products = (
                SaleDetail.objects
                .filter(sale__sale_date__gte=last_30d)
                .values("product__name")
                .annotate(total_qty=Sum("quantity"), total_rev=Sum("subtotal"))
                .order_by("-total_qty")[:5]
            )

            top_lines = [
                f"  {i}. {tp['product__name']} — {tp['total_qty']} uds. / ${tp['total_rev']:.2f}"
                for i, tp in enumerate(top_products, 1)
            ]

            # Alertas de stock bajo
            low_stock = _get_low_stock_products(threshold=5)
            out_count = _get_out_of_stock_count()

            parts = [
                "RESUMEN DE VENTAS (tiempo real):",
                f"  • Últimas 24 horas : {count_24h} venta(s) | ${total_24h:.2f}",
                f"  • Últimos 7 días   : {count_7d} venta(s) | ${total_7d:.2f}",
                f"  • Últimos 30 días  : {count_30d} venta(s) | ${total_30d:.2f}",
                f"  • Ticket promedio  : ${avg_ticket:.2f}",
                f"  • Total histórico  : {count_all} venta(s)",
            ]

            if recent_lines:
                parts.append(f"\nÚLTIMAS {len(recent_lines)} VENTA(S):")
                parts.extend(recent_lines)

            if top_lines:
                parts.append("\nTOP 5 PRODUCTOS (últimos 30 días):")
                parts.extend(top_lines)

            # Alertas de inventario
            parts.append(f"\nALERTAS DE INVENTARIO:")
            parts.append(f"  • Productos agotados: {out_count}")
            if low_stock:
                parts.append(f"  • Stock crítico (≤5 unidades):")
                for p in low_stock:
                    parts.append(
                        f"    - {p['name']} | Stock: {p['stock']} | "
                        f"Cat: {p['category__name'] or 'N/A'}"
                    )
            else:
                parts.append("  • Sin productos en stock crítico ✅")

            return "\n".join(parts)

        except Exception as exc:
            return f"(Error al cargar datos de ventas: {exc})"


class CustomerContextBuilder:
    """Contexto extra para clientes autenticados: historial reciente, descuento activo y reposición."""

    def build(self, user) -> str:
        parts = []

        # ── Descuento personalizado ───────────────────────────────────────────
        try:
            customer = Customer.objects.filter(email=user.email).first()
            if customer and customer.has_active_discount():
                expiry_str = customer.discount_expiry.strftime('%d/%m/%Y')
                parts.append(
                    f"DESCUENTO ACTIVO DEL CLIENTE:\n"
                    f"  • {customer.discount_percentage}% de descuento vigente hasta {expiry_str}\n"
                    f"  • Aplica automáticamente al pagar con Efectivo o Tarjeta (NO aplica "
                    f"en Consumidor Final ni Transferencia bancaria)."
                )
            elif customer and customer.discount_percentage and customer.discount_percentage > 0:
                parts.append(
                    f"DESCUENTO CONFIGURADO (SIN VIGENCIA):\n"
                    f"  • Tiene configurado un {customer.discount_percentage}% de descuento, "
                    f"pero la vigencia ha expirado o no tiene fecha asignada. "
                    f"Actualmente NO aplica descuento."
                )
        except Exception:
            pass

        # ── Historial de compras ──────────────────────────────────────────────
        try:
            recent = (
                Sale.objects
                .filter(user=user)
                .select_related('payment')
                .order_by('-sale_date')[:5]
            )
            if recent:
                lines = [
                    f"  - Orden #{s.id_sale:06d} | {s.sale_date.strftime('%d/%m/%Y')} "
                    f"| Pago: {s.payment.name if s.payment else 'N/A'} | Total: ${s.total:.2f}"
                    for s in recent
                ]
                parts.append("COMPRAS RECIENTES DEL CLIENTE:\n" + "\n".join(lines))
            else:
                parts.append("El cliente aún no tiene compras registradas.")
        except Exception as exc:
            parts.append(f"(Error al cargar historial: {exc})")

        # ── Productos por reponer (predicción de recompra) ─────────────────────
        try:
            if customer: # reutiliza el Customer ya resuelto arriba, no user
                due_products = (
                    RepurchasePattern.objects
                    .filter(customer=customer, is_due=True)
                    .select_related('product')
                    .order_by('-purchase_count')[:5]
                )
                if due_products:
                    lines = [
                        f"  - {p.product.name} | Sueles comprarlo cada {round(p.avg_interval_days)} días, "
                        f"van {(timezone.localdate() - p.last_purchase_date).days} días desde la última compra"
                        for p in due_products
                    ]
                    parts.append(
                        "PRODUCTOS QUE PODRÍA NECESITAR REPONER:\n" + "\n".join(lines) +
                        "\n  • Si la conversación lo permite, sugiere naturalmente reponer alguno de estos, "
                        "sin forzarlo si el cliente está preguntando otra cosa."
                    )
        except Exception:
            pass

        return "\n\n".join(parts) if parts else "Sin información adicional del cliente."


class GuestContextBuilder:
    """Contexto mínimo y motivador para visitantes no autenticados."""

    def build(self) -> str:
        total_products = Product.objects.filter(state=True, stock__gt=0).count()
        total_cats = Category.objects.count()
        total_brands = Brand.objects.count()
        return (
            f"DATOS DE LA TIENDA PARA EL VISITANTE:\n"
            f"  • {total_products} productos disponibles en tienda\n"
            f"  • {total_cats} categorías · {total_brands} marcas\n"
            f"  • Métodos de pago: Efectivo, Tarjeta de crédito, Tarjeta de débito\n"
            f"  • IVA 15% incluido en todos los precios\n"
            f"  • El visitante DEBE registrarse para comprar."
        )


# ─────────────────────────────────────────────────────────────────
# Director — ensambla todo según el rol
# ─────────────────────────────────────────────────────────────────

class ChatContextDirector:
    """Ensambla el contexto completo según el rol del usuario."""

    def __init__(
        self,
        store_builder=None,
        sales_builder=None,
        customer_builder=None,
        guest_builder=None,
    ):
        self.store_builder    = store_builder    or StoreContextBuilder()
        self.sales_builder    = sales_builder    or SalesContextBuilder()
        self.customer_builder = customer_builder or CustomerContextBuilder()
        self.guest_builder    = guest_builder    or GuestContextBuilder()

    def build_for_role(self, role: str, user=None) -> dict:
        """
        Devuelve un dict con las claves:
          store_ctx   → inventario general (todos)
          sales_ctx   → ventas + alertas (admin)
          extra_ctx   → historial cliente / datos invitado
          role        → 'admin' | 'customer' | 'guest'
        """
        store_ctx = self.store_builder.build()

        if role == 'admin':
            return {
                'role': 'admin',
                'store_ctx': store_ctx,
                'sales_ctx': self.sales_builder.build(),
                'extra_ctx': '',
            }
        elif role == 'customer' and user is not None:
            return {
                'role': 'customer',
                'store_ctx': store_ctx,
                'sales_ctx': '',
                'extra_ctx': self.customer_builder.build(user),
            }
        else:  # guest
            return {
                'role': 'guest',
                'store_ctx': store_ctx,
                'sales_ctx': '',
                'extra_ctx': self.guest_builder.build(),
            }


# ─────────────────────────────────────────────────────────────────
# Helpers públicos para el resumen ejecutivo del frontend
# ─────────────────────────────────────────────────────────────────

def get_admin_quick_summary() -> dict:
    """
    Datos numéricos para el resumen ejecutivo del chatbot (admin).
    Se serializa a JSON y se envía en la respuesta de apertura.
    """
    try:
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d  = now - timedelta(days=7)

        sales_24h = Sale.objects.filter(sale_date__gte=last_24h)
        total_24h = sales_24h.aggregate(t=Sum('total'))['t'] or Decimal('0')
        count_24h = sales_24h.count()

        sales_7d  = Sale.objects.filter(sale_date__gte=last_7d)
        total_7d  = sales_7d.aggregate(t=Sum('total'))['t'] or Decimal('0')

        low_stock = _get_low_stock_products(5)
        out_count = _get_out_of_stock_count()

        return {
            'count_24h': count_24h,
            'total_24h': float(total_24h),
            'total_7d':  float(total_7d),
            'low_stock_count': len(low_stock),
            'out_of_stock': out_count,
            'low_stock_items': [
                {'name': p['name'], 'stock': p['stock']}
                for p in low_stock[:3]
            ],
        }
    except Exception:
        return {}


def get_customer_quick_summary(user) -> dict:
    """Datos para el saludo inicial del cliente."""
    try:
        orders = Sale.objects.filter(user=user)
        total_spent = orders.aggregate(t=Sum('total'))['t'] or Decimal('0')
        last_order = orders.order_by('-sale_date').first()
        return {
            'order_count': orders.count(),
            'total_spent': float(total_spent),
            'last_order_date': last_order.sale_date.strftime('%d/%m/%Y') if last_order else None,
        }
    except Exception:
        return {}
