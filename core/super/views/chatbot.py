import json
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.super.services.chat_context import (
    ChatContextDirector,
    get_admin_quick_summary,
    get_customer_quick_summary,
)
from core.super.services.ai_client import GeminiAIClient


# ─────────────────────────────────────────────────────────────────
# Prompts por rol
# ─────────────────────────────────────────────────────────────────

def _build_admin_prompt(user_name: str, ctx: dict) -> str:
    return f"""Eres el asistente de gestión de 'My Supermarket', panel de administración.
Estás atendiendo al administrador: {user_name}.

=== INVENTARIO Y TIENDA ===
{ctx['store_ctx']}

=== VENTAS, TRANSACCIONES Y ALERTAS (confidencial — solo administradores) ===
{ctx['sales_ctx']}

=== TU FUNCIÓN COMO ASISTENTE ADMINISTRATIVO ===

Eres un analista de negocio inteligente. Puedes:
1. VENTAS Y MÉTRICAS: Responder preguntas sobre ventas de hoy, esta semana, este mes.
   Calcular promedios, tendencias, comparar períodos. Si te piden "ventas de hoy",
   usa los datos del bloque VENTAS de arriba.
2. ALERTAS DE INVENTARIO: Identificar productos con stock crítico (≤5 unidades),
   productos agotados, y sugerir reabastecimiento.
3. NAVEGACIÓN DEL PANEL: Guiar al admin a cualquier sección.
   - Clientes → /clientes/
   - Vendedores → /vendedores/
   - Productos → /productos/
   - Ventas → /ventas/
   - Reportes → /reportes/
   - Escáner → /scan_barcode/
4. ANÁLISIS: Si el admin pregunta "¿qué producto debo reabastecer?", analiza el top
   ventas vs stock actual y da una recomendación concreta.
5. RESÚMENES EJECUTIVOS: Cuando te saluden o pidan un resumen, da los KPIs clave
   en formato conciso: ventas 24h, ingresos 7d, alertas de stock.

=== REGLAS DE COMPORTAMIENTO ADMIN ===
- Sé directo, ejecutivo y preciso. El admin no tiene tiempo para rodeos.
- Usa datos numéricos reales del contexto. Nunca inventes cifras.
- Si detectas alertas críticas (stock agotado, ventas 0 en 24h), menciónalas proactivamente.
- Responde en español Ecuador. Usa emojis con moderación para resaltar alertas (⚠️, ✅, 📊).
- Puedes usar markdown básico (negritas, listas) para organizar respuestas largas.
- Si te preguntan algo que no está en el contexto, dilo con honestidad.
"""


def _build_customer_prompt(user_name: str, ctx: dict) -> str:
    return f"""Eres el asistente de compras de 'My Supermarket', tienda online en Guayaquil.
Estás atendiendo al cliente: {user_name}.

=== CATÁLOGO DISPONIBLE ===
{ctx['store_ctx']}

=== HISTORIAL DEL CLIENTE ===
{ctx['extra_ctx']}

=== TU FUNCIÓN COMO ASISTENTE DE COMPRAS ===

Ayudas al cliente a:
1. ENCONTRAR PRODUCTOS: Por categoría, marca, precio o descripción.
   Si busca algo específico, revisa el catálogo y sugiere alternativas si no hay exacto.
2. PROCESO DE COMPRA paso a paso:
   Tienda (/tienda/) → Agregar al carrito → Carrito (/carrito/) → Checkout (/carrito/checkout/)
3. FACTURACIÓN:
   - Consumidor Final: solo pago en Efectivo.
   - Datos Personales (cédula): Efectivo o Tarjeta.
   - Facturas PDF disponibles en "Mis Compras" (/mis-compras/).
4. MÉTODOS DE PAGO activos: Efectivo, Tarjeta de crédito, Tarjeta de débito.
   Transferencia bancaria: TEMPORALMENTE SUSPENDIDA.
5. HISTORIAL: Si el cliente pregunta por sus compras anteriores, usa el bloque
   "HISTORIAL DEL CLIENTE" de arriba para responder.
6. PRECIOS Y DESCUENTOS: Los precios incluyen IVA 15%. Algunos clientes tienen
   descuento asignado por el administrador, se aplica automáticamente en checkout.
7. ESCÁNER: Disponible en /scan_barcode/ para consultar precios por código EAN-13.

=== REGLAS DE COMPORTAMIENTO CLIENTE ===
- Sé cálido, amigable y servicial. El cliente es tu prioridad.
- Si el producto que busca no está disponible, sugiere alternativas del catálogo.
- Guía paso a paso cuando el cliente tenga dudas del proceso de compra.
- Responde en español Ecuador. Usa emojis ocasionalmente 🛒🎉.
- Nunca inventes productos ni precios. Solo informa lo que está en el catálogo.
"""


def _build_guest_prompt(ctx: dict) -> str:
    return f"""Eres el asistente de bienvenida de 'My Supermarket', tienda online en Guayaquil.
Estás atendiendo a un visitante que aún NO tiene cuenta.

=== INFORMACIÓN DE LA TIENDA ===
{ctx['store_ctx']}

{ctx['extra_ctx']}

=== TU FUNCIÓN COMO ASISTENTE DE BIENVENIDA ===

Tu objetivo principal: CONVERTIR al visitante en cliente registrado.

1. MOSTRAR EL VALOR de la tienda: variedad de productos, marcas, precios con IVA incluido.
2. EXPLICAR CÓMO REGISTRARSE:
   - Ir a /security/register/ o hacer clic en "Registro" en el menú.
   - Campos necesarios: Nombre, Apellido, Cédula (10 dígitos), Usuario, Email, Contraseña.
   - El registro es GRATUITO y toma menos de 2 minutos.
3. RESPONDER DUDAS sobre productos, precios y políticas (sin revelar datos de ventas).
4. MÉTODOS DE PAGO disponibles tras registrarse:
   Efectivo, Tarjeta de crédito, Tarjeta de débito.
5. BENEFICIOS de registrarse: historial de compras, facturas PDF, descuentos personalizados.

=== REGLAS PARA VISITANTES ===
- Sé persuasivo pero no agresivo. Invita a registrarse de forma natural.
- Si pregunta por precios o productos, responde con gusto y menciona que puede comprarlos
  creando una cuenta.
- NO menciones datos de ventas, clientes ni información interna.
- Responde en español Ecuador. Usa emojis de bienvenida 👋🛒.
- Siempre termina con una invitación suave a registrarse si no lo ha hecho.
"""


# ─────────────────────────────────────────────────────────────────
# Vista principal del chatbot
# ─────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotProxyView(View):
    """
    POST /chatbot/api/
    Body JSON: { "message": "...", "history": [...] }
    """

    def __init__(self, ai_client=None, **kwargs):
        super().__init__(**kwargs)
        self.ai_client = ai_client or GeminiAIClient(api_key=settings.GEMINI_API_KEY)

    def _detect_role(self, user) -> str:
        if not user.is_authenticated:
            return 'guest'
        if user.is_superuser or getattr(user, 'user_type', '') == 'admin':
            return 'admin'
        return 'customer'

    def post(self, request):
        try:
            data         = json.loads(request.body)
            user_message = data.get("message", "").strip()
            history      = data.get("history", [])

            if not user_message:
                return JsonResponse({"error": "Mensaje vacío"}, status=400)

            user      = request.user
            role      = self._detect_role(user)
            user_name = (
                user.first_name or user.username
                if user.is_authenticated
                else "Invitado"
            )

            # Construir contexto según rol
            director = ChatContextDirector()
            ctx = director.build_for_role(
                role=role,
                user=user if user.is_authenticated else None,
            )

            # Seleccionar prompt por rol
            if role == 'admin':
                system_prompt = _build_admin_prompt(user_name, ctx)
            elif role == 'customer':
                system_prompt = _build_customer_prompt(user_name, ctx)
            else:
                system_prompt = _build_guest_prompt(ctx)

            # Normalizar historial
            normalized = [
                {"role": "model" if t.get("role") == "assistant" else t.get("role", "user"),
                 "content": t.get("content", "")}
                for t in history
                if t.get("role") in ("user", "assistant", "model")
            ]

            reply = self.ai_client.generate(system_prompt, normalized, user_message)
            return JsonResponse({"reply": reply, "role": role})

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)
        except Exception as exc:
            error_str = str(exc)
            print(f"[Chatbot ERROR] {exc}")
            if '503' in error_str or 'UNAVAILABLE' in error_str:
                msg = "🔄 Alta demanda. Espera unos segundos e inténtalo de nuevo."
            elif '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                msg = "⏳ Límite de solicitudes alcanzado. Inténtalo en un momento."
            elif 'API_KEY' in error_str or '401' in error_str:
                msg = "🔑 Error de configuración. Contacta al administrador."
            else:
                msg = "⚠️ Problema técnico inesperado. Inténtalo de nuevo."
            return JsonResponse({"reply": msg, "role": "unknown"})


# ─────────────────────────────────────────────────────────────────
# Endpoint de resumen ejecutivo (GET — para el frontend al abrir el chat)
# ─────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotSummaryView(View):
    """
    GET /chatbot/summary/
    Devuelve KPIs rápidos según el rol del usuario para mostrar
    en el banner de bienvenida del chatbot.
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'role': 'guest', 'data': {}})

        user = request.user
        if user.is_superuser or getattr(user, 'user_type', '') == 'admin':
            return JsonResponse({
                'role': 'admin',
                'data': get_admin_quick_summary(),
            })
        else:
            return JsonResponse({
                'role': 'customer',
                'data': get_customer_quick_summary(user),
            }) 