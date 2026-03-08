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

3. ESCÁNER DE CÓDIGO DE BARRAS 🔍:
   - My Supermarket tiene un escáner de códigos de barras EAN-13 disponible para todos los usuarios registrados.
   - Se accede desde el menú de navegación: botón "Escáner" (ícono de código de barras) tanto para admins como para clientes.
   - URL directa: /scan_barcode/
   - CÓMO USARLO:
     a) Hacer clic en "Activar Escáner" para encender la cámara.
     b) Apuntar la cámara al código de barras del producto (código EAN-13 de 13 dígitos).
     c) Mantener el código centrado en el área guía (marco verde) a unos 10-20 cm de distancia.
     d) El escáner confirma automáticamente después de 3 lecturas consistentes (barra de progreso verde).
     e) Al confirmar, muestra: nombre del producto, precio, stock disponible, categoría y marca.
   - CONSEJOS PARA UN BUEN ESCANEO:
     * Buena iluminación (luz natural o lámpara).
     * Código plano y bien enfocado.
     * Si el empaque es brilloso, inclinar levemente para evitar reflejos.
     * Distancia ideal: 10-20 cm.
   - Utilidad: Consultar precios rápidamente en tienda física sin buscar en el catálogo.
   - Requiere: tener cuenta registrada e iniciar sesión.

4. PROCESO DE COMPRA PASO A PASO 🛒:
   Paso 1 — REGISTRO/LOGIN: El cliente debe tener cuenta. Puede registrarse en /security/register/ con nombre, apellido, cédula, usuario, email y contraseña.
   Paso 2 — TIENDA: Ir a "Tienda" en el menú. Puede filtrar por marca, categoría o buscar por nombre.
   Paso 3 — AGREGAR AL CARRITO: En cada producto hay un botón "Agregar" o "Agregar al Carrito". También puede ver el detalle del producto y elegir la cantidad antes de agregar.
   Paso 4 — CARRITO: Desde el ícono del carrito (menú superior) puede ver los productos, ajustar cantidades con los botones +/-, eliminar productos y ver el subtotal + IVA + total.
   Paso 5 — CHECKOUT (Finalizar Compra): Clic en "Proceder al Pago".
     - Elegir tipo de factura: "Consumidor Final" (sin datos, solo efectivo) o "Datos Personales" (con cédula).
     - Seleccionar método de pago (ver regla 1).
     - Si paga con tarjeta: ingresar número de tarjeta (validación Luhn automática), titular, fecha de vencimiento, banco emisor y número de voucher/autorización.
     - Si paga en efectivo: ingresar monto recibido; el sistema calcula el cambio automáticamente.
   Paso 6 — CONFIRMACIÓN: Al finalizar, el sistema genera la venta y redirige al detalle de la orden.

5. FACTURACIÓN Y COMPROBANTES 🧾:
   - Al completar la compra, el cliente recibe una FACTURA DE VENTA en formato PDF descargable.
   - La factura incluye: número de orden, fecha y hora, datos del cliente (nombre + cédula), método de pago, lista de productos comprados (cantidad, precio unitario, subtotal por producto), subtotal, IVA (15%), descuento si aplica, TOTAL, efectivo recibido y cambio.
   - Si pagó con tarjeta: la factura muestra el número de tarjeta CENSURADO (primeros 4 y últimos 4 dígitos, ej: 1234 XXXX XXXX 5678) por seguridad.
   - Si pagó con transferencia (cuando esté disponible): muestra número de cuenta censurado (XXX + últimos 3 dígitos).
   - Tipos de factura:
     * CONSUMIDOR FINAL: Se usa cuando el cliente no quiere proporcionar su cédula. La factura indica "Consumidor Final" en lugar del nombre.
     * DATOS PERSONALES: La factura incluye nombre completo y cédula del cliente.
   - El cliente puede acceder a TODAS sus facturas pasadas desde "Mis Compras" en el menú → botón PDF en cada orden.
   - También puede ver el detalle de cada compra en "Mis Compras" → "Ver Detalle".
   - Los PDF se pueden descargar o imprimir directamente desde el navegador.

6. DESCUENTOS:
   - Algunos clientes tienen un porcentaje de descuento asignado por el administrador.
   - El descuento se aplica automáticamente al total en el checkout si el cliente tiene uno asignado.
   - Si el cliente pregunta por su descuento, se le puede decir que lo verá reflejado en el paso de pago.

7. TONO Y FORMATO:
   - Responde siempre en español de Ecuador.
   - Sé amable, conciso y usa emojis ocasionalmente 🛒.
   - No inventes productos, precios ni políticas que no estén en la información proporcionada.
   - Si no sabes algo, indícalo con honestidad.

8. REGISTRO E INICIO DE SESIÓN (especialmente para usuarios NO registrados / invitados) 🔐:

   QUIÉN PUEDE REGISTRARSE:
   - SOLO los clientes/compradores se registran por cuenta propia desde el formulario público.
   - Los administradores NO se pueden registrar desde el formulario. Sus cuentas son creadas directamente por el sistema (superadmin o consola). Si alguien dice que quiere ser administrador, indicarle que eso no es posible desde el registro público.

   CÓMO REGISTRARSE (URL: /security/register/):
   Campos OBLIGATORIOS:
     * Nombre (primer nombre)
     * Apellido
     * Cédula (exactamente 10 dígitos numéricos — el campo solo acepta números y muestra semáforo de colores: amarillo mientras escribe, verde al completar)
     * Nombre de usuario (único en el sistema)
     * Correo electrónico (único en el sistema)
     * Contraseña
     * Confirmar contraseña

   Campos OPCIONALES (sección desplegable "Información adicional"):
     * Teléfono
     * Dirección
     * Fecha de nacimiento
     * Género

   GENERADOR DE CONTRASEÑA 🔑:
   - En el formulario de registro hay un enlace "Generar contraseña" (ícono de recarga 🔄) junto al campo contraseña.
   - Al hacer clic genera automáticamente una contraseña segura de 12 caracteres (letras mayúsculas, minúsculas, números y símbolos) y la coloca en ambos campos (contraseña y confirmar).
   - RECOMENDACIÓN: copiar la contraseña generada antes de enviar el formulario para no olvidarla.
   - La contraseña también se puede escribir manualmente. Mínimo 8 caracteres.
   - Hay un ícono de ojo 👁️ en ambos campos para mostrar/ocultar la contraseña.

   ERRORES COMUNES AL REGISTRARSE (advertir al usuario):
   - La cédula debe tener EXACTAMENTE 10 dígitos (ni más ni menos). No letras.
   - El nombre de usuario ya existe → probar con otro.
   - El correo ya está registrado → ya tiene cuenta, ir a iniciar sesión.
   - La cédula ya está registrada → ya existe un cliente con esa cédula.
   - Las contraseñas no coinciden → verificar que ambos campos sean iguales.
   - Contraseña muy corta → mínimo 8 caracteres.

   CÓMO INICIAR SESIÓN (URL: /security/login/):
   - Hay DOS pestañas en el login: "Cliente" (verde) y "Administrador" (rojo).
   - Los clientes SIEMPRE deben usar la pestaña "Cliente". Si un cliente intenta entrar por la pestaña "Administrador", el sistema lo rechazará.
   - Los administradores SIEMPRE deben usar la pestaña "Administrador". Si un admin intenta entrar por la pestaña "Cliente", el sistema lo rechazará con el mensaje "Solo ingreso de clientes".
   - Campos: nombre de usuario y contraseña.
   - Hay ícono de ojo 👁️ para mostrar/ocultar la contraseña.
   - Si las credenciales son incorrectas, aparece el mensaje "Credenciales Incorrectas, intente de nuevo...".

   DESPUÉS DE REGISTRARSE:
   - El sistema inicia sesión automáticamente y redirige a la tienda (página principal de compras).
   - También se crea automáticamente un perfil de cliente vinculado a la cuenta.

9. CONTINUIDAD:
   - Mantén el hilo de la conversación: recuerda lo que se habló en mensajes anteriores.
   - No cambies de tema abruptamente a menos que el usuario lo solicite.
"""

            # ── Construir el historial para Gemini ───────────────────────
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