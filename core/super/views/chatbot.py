import json
from google import genai
from google.genai import types
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.super.models import Product, Category, Brand, PaymentMethod


def _build_store_context():
    """
    Genera un resumen del inventario actual para el system prompt del chatbot.
    """
    try:
        categories = list(
            Category.objects.values_list("name", flat=True).order_by("name")
        )

        brands = list(
            Brand.objects.values_list("name", flat=True).order_by("name")
        )

        products_qs = (
            Product.objects.filter(state=True, stock__gt=0)
            .select_related("category", "brand")
            .order_by("name")
        )

        product_lines = []
        for p in products_qs:
            cat_name   = p.category.name if p.category else "Sin categoría"
            brand_name = p.brand.name    if p.brand    else "Sin marca"
            product_lines.append(
                f"  - {p.name} | Categoría: {cat_name} | Marca: {brand_name} "
                f"| Precio: ${p.price:.2f} | Stock: {p.stock}"
            )

        active_payment_names = {"Efectivo", "Tarjeta de crédito", "Tarjeta de débito"}
        all_payments      = PaymentMethod.objects.values_list("name", flat=True)
        active_payments   = [p for p in all_payments if p in active_payment_names]
        inactive_payments = [p for p in all_payments if p not in active_payment_names]

        ctx_parts = []

        if categories:
            ctx_parts.append(
                "CATEGORÍAS DISPONIBLES EN LA TIENDA:\n  " + ", ".join(categories)
            )

        if brands:
            ctx_parts.append(
                "MARCAS DISPONIBLES EN LA TIENDA:\n  " + ", ".join(brands)
            )

        if product_lines:
            ctx_parts.append(
                "PRODUCTOS DISPONIBLES (con stock):\n" + "\n".join(product_lines)
            )
        else:
            ctx_parts.append(
                "PRODUCTOS DISPONIBLES: No hay productos con stock en este momento."
            )

        payment_info = []
        if active_payments:
            payment_info.append("Métodos ACTIVOS: " + ", ".join(active_payments))
        if inactive_payments:
            payment_info.append(
                "Métodos NO DISPONIBLES por el momento: "
                + ", ".join(inactive_payments)
                + " (en stand-by, no aceptados)"
            )
        ctx_parts.append("MÉTODOS DE PAGO:\n  " + "\n  ".join(payment_info))

        return "\n\n".join(ctx_parts)

    except Exception as exc:
        return f"(No se pudo cargar el inventario: {exc})"


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotProxyView(View):
    """
    Endpoint POST para el chatbot.
    Funciona para todos: invitados, clientes y administradores.

    Body JSON esperado:
    {
        "message": "texto del usuario",
        "history": [
            {"role": "user",  "content": "..."},
            {"role": "model", "content": "..."}
        ]
    }
    """

    def post(self, request):
        try:
            data         = json.loads(request.body)
            user_message = data.get("message", "").strip()
            history      = data.get("history", [])

            if not user_message:
                return JsonResponse({"error": "Mensaje vacío"}, status=400)

            # ── Contexto dinámico de la tienda ───────────────────────────
            store_ctx = _build_store_context()

            # ── Datos del usuario (invitado / cliente / admin) ───────────
            if request.user.is_authenticated:
                user_name = request.user.first_name or request.user.username
                if request.user.is_superuser or request.user.user_type == 'admin':
                    user_role = "Administrador"
                else:
                    user_role = "Cliente"
            else:
                user_name = "Invitado"
                user_role = "Visitante"

            # ── System prompt ────────────────────────────────────────────
            system_prompt = f"""Eres el asistente virtual de 'My Supermarket', una tienda en línea en Guayaquil, Ecuador.
Estás atendiendo a: {user_name} (Rol: {user_role}).

=== INFORMACIÓN ACTUALIZADA DE LA TIENDA ===
{store_ctx}

=== REGLAS DE NEGOCIO ===

1. MÉTODOS DE PAGO:
   - Aceptamos: Efectivo, Tarjeta de Crédito y Tarjeta de Débito.
   - La Transferencia Bancaria está temporalmente SUSPENDIDA (NO disponible).
   - Si el cliente elige "Consumidor Final" como tipo de factura: SOLO se acepta Efectivo.
   - Si el cliente proporciona sus datos personales: puede pagar con Efectivo o Tarjeta.

2. PRODUCTOS:
   - Solo informa sobre los productos listados arriba (con stock disponible).
   - Si te preguntan por un producto que no está en la lista, informa que no está disponible.
   - Puedes comparar productos, sugerir alternativas dentro del catálogo y dar información de precios.

3. ESCÁNER DE CÓDIGO DE BARRAS 🔍:
   - Disponible para usuarios registrados desde el menú de navegación.
   - URL directa: /scan_barcode/
   - Soporta códigos EAN-13. Requiere iniciar sesión.

4. PROCESO DE COMPRA PASO A PASO 🛒:
   Paso 1 — REGISTRO/LOGIN: Ir a /security/register/ o /security/login/
   Paso 2 — TIENDA: Ir a "Tienda" en el menú. Filtrar por marca, categoría o nombre.
   Paso 3 — AGREGAR AL CARRITO: Botón "Agregar" en cada producto.
   Paso 4 — CARRITO: Ver productos, ajustar cantidades, eliminar ítems.
   Paso 5 — CHECKOUT: Elegir factura (Consumidor Final o Datos Personales), método de pago.
   Paso 6 — CONFIRMACIÓN: El sistema genera la venta y redirige al detalle de la orden.

5. FACTURACIÓN Y COMPROBANTES 🧾:
   - Al completar la compra se genera una FACTURA PDF descargable.
   - Incluye: número de orden, fecha, cliente, productos, subtotal, IVA (15%), descuento y total.
   - Si pagó con tarjeta: número censurado (ej: 1234 XXXX XXXX 5678).
   - Acceso a facturas pasadas: "Mis Compras" en el menú.

6. DESCUENTOS:
   - Algunos clientes tienen descuento asignado por el administrador.
   - Se aplica automáticamente en el checkout.

7. TONO Y FORMATO:
   - Responde siempre en español de Ecuador.
   - Sé amable, conciso y usa emojis ocasionalmente 🛒.
   - Si el usuario es Invitado/Visitante, invítalo a registrarse para comprar.
   - Si el usuario es Administrador, puedes mencionar funciones del panel admin si pregunta.
   - No inventes productos, precios ni políticas.
   - Si no sabes algo, indícalo con honestidad.

8. REGISTRO E INICIO DE SESIÓN 🔐:
   - Solo clientes se registran por cuenta propia en /security/register/
   - Campos obligatorios: Nombre, Apellido, Cédula (10 dígitos), Usuario, Email, Contraseña.
   - Los administradores son creados directamente por el sistema.
   - Login en /security/login/ — pestañas: "Cliente" (verde) y "Administrador" (rojo).

9. CONTINUIDAD:
   - Mantén el hilo de la conversación.
   - No cambies de tema abruptamente a menos que el usuario lo solicite.
"""

            # ── Construir historial para Gemini ──────────────────────────
            gemini_contents = []

            for turn in history:
                role    = turn.get("role", "user")
                content = turn.get("content", "")
                if role == "assistant":
                    role = "model"
                if role not in ("user", "model"):
                    continue
                gemini_contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=content)],
                    )
                )

            gemini_contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)],
                )
            )

            # ── Llamada a Gemini ─────────────────────────────────────────
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.6,
                    max_output_tokens=600,
                ),
            )

            reply = response.text or "Lo siento, no pude generar una respuesta."
            return JsonResponse({"reply": reply})

        except Exception as exc:
            print(f"[Chatbot ERROR] {exc}")
            return JsonResponse({"error": str(exc)}, status=500)