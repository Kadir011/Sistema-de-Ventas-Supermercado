import json
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.super.services.chat_context import ChatContextDirector
from core.super.services.ai_client import GeminiAIClient


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotProxyView(View):
    """
    Endpoint POST para el chatbot.
    Funciona para todos: invitados, clientes y administradores.
    Los administradores reciben contexto adicional con datos de ventas en tiempo real.

    Body JSON esperado:
    {
        "message": "texto del usuario",
        "history": [
            {"role": "user",  "content": "..."},
            {"role": "model", "content": "..."}
        ]
    }
    """
    def __init__(self, ai_client=None, **kwargs):
        super().__init__(**kwargs)
        self.ai_client = ai_client or GeminiAIClient(api_key=settings.GEMINI_API_KEY) # Crear cliente AI (DIP)

    def post(self, request):
        try:
            data         = json.loads(request.body)
            user_message = data.get("message", "").strip()
            history      = data.get("history", [])

            if not user_message:
                return JsonResponse({"error": "Mensaje vacío"}, status=400)

            # ── Detectar rol y construir contexto adicional ───────────
            is_admin = False
            if request.user.is_authenticated:
                user_name = request.user.first_name or request.user.username
                if request.user.is_superuser or request.user.user_type == 'admin':
                    user_role = "Administrador"
                    is_admin  = True
                else:
                    user_role = "Cliente"
            else:
                user_name = "Invitado"
                user_role = "Visitante"

            director = ChatContextDirector() # Clase que encarga de construir el contexto (SRP)
            store_ctx, sales_ctx = director.build_for_role(is_admin)

            # ── System prompt ─────────────────────────────────────────
            system_prompt = f"""Eres el asistente virtual de 'My Supermarket', una tienda en línea en Guayaquil, Ecuador.
Estás atendiendo a: {user_name} (Rol: {user_role}).

=== INFORMACIÓN ACTUALIZADA DE LA TIENDA ===
{store_ctx}
"""

            if is_admin and sales_ctx:
                system_prompt += f"""
=== DATOS DE VENTAS Y TRANSACCIONES (solo visibles para administradores) ===
{sales_ctx}

"""

            system_prompt += """
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
   - Si el admin pregunta por ventas, transacciones o reportes, usa los datos de la sección
     "DATOS DE VENTAS Y TRANSACCIONES" para responder con precisión.
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

            # ── Normalizar el historial para el cliente AI (user/model) ──
            normalized_history = []
            for turn in history:
                role = turn.get("role", "user")
                if role == "assistant":
                    role = "model"
                if role not in ("user", "model"):
                    continue
                normalized_history.append({"role": role, "content": turn.get("content", "")})

            # ── Pedir respuesta al cliente AI (Gemini) ────────────────
            reply = self.ai_client.generate(system_prompt, normalized_history, user_message) # Llamar a Gemini (DIP)
            return JsonResponse({"reply": reply})

        except Exception as exc:
            print(f"[Chatbot ERROR] {exc}")
            return JsonResponse({"error": str(exc)}, status=500)