import json
from google import genai
from google.genai import types
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from core.super.models import Product, Category, Brand, PaymentMethod

def _build_store_context():
    """
    Genera un resumen del inventario actual (productos, categorías, marcas
    y métodos de pago) para inyectarlo en el system prompt del chatbot.
    """
    try:
        # ── Categorías ──────────────────────────────────────────────────
        categories = list(
            Category.objects.values_list("name", flat=True).order_by("name")
        )

        # ── Marcas ───────────────────────────────────────────────────────
        brands = list(
            Brand.objects.values_list("name", flat=True).order_by("name")
        )

        # ── Productos disponibles (stock > 0) ────────────────────────────
        products_qs = (
            Product.objects.filter(state=True, stock__gt=0)
            .select_related("category", "brand")
            .order_by("name")
        )

        product_lines = []
        for p in products_qs:
            cat_name  = p.category.name if p.category else "Sin categoría"
            brand_name = p.brand.name   if p.brand    else "Sin marca"
            product_lines.append(
                f"  - {p.name} | Categoría: {cat_name} | Marca: {brand_name} "
                f"| Precio: ${p.price:.2f} | Stock: {p.stock}"
            )

        # ── Métodos de pago activos ──────────────────────────────────────
        # Reflejamos exactamente la lógica de checkout.js:
        #   ACTIVE_PAYMENT_METHODS = ['Efectivo', 'Tarjeta de crédito', 'Tarjeta de débito']
        #   Transferencia bancaria está en stand-by.
        active_payment_names = {"Efectivo", "Tarjeta de crédito", "Tarjeta de débito"}
        all_payments = PaymentMethod.objects.values_list("name", flat=True)
        active_payments   = [p for p in all_payments if p in active_payment_names]
        inactive_payments = [p for p in all_payments if p not in active_payment_names]

        # ── Construir bloque de texto ────────────────────────────────────
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


class ChatbotProxyView(View):
    """
    Endpoint POST para el chatbot.

    Body JSON esperado:
    {
        "message": "texto del usuario",
        "history": [
            {"role": "user",  "content": "..."},
            {"role": "model", "content": "..."},
            ...
        ]
    }

    La historia completa se reenvía a Gemini en cada request, de modo que
    la conversación tiene memoria real de turno a turno sin necesidad de
    guardar nada en sesión del servidor.
    """

    def post(self, request):
        try:
            data         = json.loads(request.body)
            user_message = data.get("message", "").strip()
            history      = data.get("history", [])   # lista de {role, content}

            if not user_message:
                return JsonResponse({"error": "Mensaje vacío"}, status=400)

            # ── Contexto dinámico de la tienda ───────────────────────────
            store_ctx = _build_store_context()

            # ── Nombre del usuario ───────────────────────────────────────
            user_name = (
                request.user.first_name
                if request.user.is_authenticated and request.user.first_name
                else "Cliente"
            )

            # ── System prompt ────────────────────────────────────────────
            system_prompt = f"""Eres el asistente virtual de 'My Supermarket', una tienda en línea en Guayaquil, Ecuador.
Estás atendiendo a: {user_name}.

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

3. TONO Y FORMATO:
   - Responde siempre en español de Ecuador.
   - Sé amable, conciso y usa emojis ocasionalmente 🛒.
   - No inventes productos, precios ni políticas que no estén en la información proporcionada.
   - Si no sabes algo, indícalo con honestidad.

4. CONTINUIDAD:
   - Mantén el hilo de la conversación: recuerda lo que se habló en mensajes anteriores.
   - No cambies de tema abruptamente a menos que el usuario lo solicite.
"""

            # ── Construir el historial para Gemini ───────────────────────
            # Gemini espera: [{"role": "user"|"model", "parts": [{"text": "..."}]}]
            gemini_contents = []

            for turn in history:
                role    = turn.get("role", "user")
                content = turn.get("content", "")
                # Normalizar: el frontend puede enviar "assistant" → convertir a "model"
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

            # Agregar el mensaje actual del usuario
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