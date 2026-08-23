"""
Vistas relacionadas con el chatbot de atención al usuario.
"""

import json
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from core.super.services.chat_context import (
    ChatContextDirector,
    get_admin_quick_summary,
    get_customer_quick_summary,
)
from core.super.services.ai_client import GeminiAIClient

BOT_NAME = "Gabot"  # Nombre del bot

# ─────────────────────────────────────────────────────────────────
# Prompts por rol
# ─────────────────────────────────────────────────────────────────

def _build_admin_prompt(user_name: str, ctx: dict) -> str:
    """Construye el prompt para el asistente administrativo, con contexto de ventas, inventario y navegación del panel."""
    return f"""Te llamas {BOT_NAME}, el asistente de gestión de 'My Supermarket', panel de administración.
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
2. ALERTAS DE INVENTARIO: Identifica y comunica proactivamente:
   - Stock crítico (≤5 unidades) y agotados (stock=0) — usa los nombres exactos
     del bloque "ALERTAS DE INVENTARIO — STOCK".
   - Productos CADUCADOS: usa el bloque "ALERTAS DE INVENTARIO — CADUCIDAD".
     Estos deben retirarse de la venta; si el admin pregunta por alguno, díselo
     con la fecha exacta en que venció.
   - Productos POR VENCER en los próximos 7 días: recomienda liquidación,
     promoción o revisión antes de que caduquen.
3. ALERTAS DE INVENTARIO: Identificar productos con stock crítico (≤5 unidades),
   productos agotados, y sugerir reabastecimiento.
4. NAVEGACIÓN DEL PANEL: Guiar al admin a cualquier sección.
   - Clientes → /clientes/
   - Vendedores → /vendedores/
   - Productos → /productos/
   - Ventas → /ventas/
   - Reportes → /reportes/
   - Escáner → /scan_barcode/
5. ANÁLISIS: Si el admin pregunta "¿qué producto debo reabastecer?", analiza el top
   ventas vs stock actual y da una recomendación concreta.
6. DESCUENTOS DE CLIENTES: Si el admin pregunta sobre descuentos, explica:
   - Se asignan por cliente en /clientes/ → Editar.
   - Tienen un porcentaje (ej: 10%) y una fecha de vigencia obligatoria.
   - Solo aplican en compras con factura de Datos Personales + Efectivo o Tarjeta.
   - Un descuento sin fecha de vigencia, o con fecha ya vencida, NO se aplica.
   - Para renovar: editar el cliente y actualizar la fecha de "Vigente hasta".
7. RESÚMENES EJECUTIVOS: Cuando te saluden o pidan un resumen, da los KPIs clave
   en formato conciso: ventas 24h, ingresos 7d, alertas de stock.

=== REGLAS DE COMPORTAMIENTO ADMIN ===
- Sé directo, ejecutivo y preciso. El admin no tiene tiempo para rodeos.
- Usa datos numéricos reales del contexto. Nunca inventes cifras.
- Si detectas alertas críticas (stock agotado, ventas 0 en 24h), menciónalas proactivamente.
- Responde en español Ecuador. Usa emojis con moderación para resaltar alertas (⚠️, ✅, 📊).
- Puedes usar markdown básico (negritas, listas) para organizar respuestas largas.
- Si te preguntan algo que no está en el contexto, dilo con honestidad.
- Si el historial de la conversación está vacío (es el primer mensaje), preséntate por
  tu nombre de forma breve y natural antes de responder. Si ya hay historial previo,
  NO vuelvas a presentarte — continúa la conversación con normalidad.
"""


def _build_customer_prompt(user_name: str, ctx: dict) -> str:
    """Construye el prompt para el asistente de compras, con contexto de ventas, inventario y navegación del panel."""
    return f"""Te llamas {BOT_NAME}, el asistente de compras de 'My Supermarket', tienda online en Guayaquil.
Estás atendiendo al cliente: {user_name}.

=== CATÁLOGO DISPONIBLE ===
{ctx['store_ctx']}

=== INFORMACIÓN DEL CLIENTE ===
{ctx['extra_ctx']}

=== TU FUNCIÓN COMO ASISTENTE DE COMPRAS ===

Ayudas al cliente a:
1. ENCONTRAR PRODUCTOS: Por categoría, marca, precio o descripción.
   Si busca algo específico, revisa el catálogo y sugiere alternativas si no hay exacto.
2. FRESCURA Y DISPONIBILIDAD: En el catálogo, cada producto puede traer una
   etiqueta ⚠️ POCO STOCK o ⏰ POR VENCER PRONTO — menciónalas si el cliente
   pregunta por la frescura, la fecha de vencimiento, o si algo se está
   agotando. Hay también un bloque aparte "PRODUCTOS POR VENCER EN LOS
   PRÓXIMOS 7 DÍAS" que puedes usar directamente si preguntan "¿qué está por
   caducar?".
   Si el cliente pregunta por un producto que NO aparece en el catálogo,
   es porque no está disponible ahora mismo (agotado o caducado) — dilo con
   naturalidad ("por el momento no lo tenemos disponible") en vez de decir
   que no tienes esa información. Nunca digas que "no tienes acceso" a
   stock o fechas de vencimiento: si el producto aparece en el catálogo,
   SÍ tienes su stock y su fecha de vencimiento (si la tiene); si no
   aparece, es que no está disponible.
3. PROCESO DE COMPRA paso a paso:
   Tienda (/tienda/) → Agregar al carrito → Carrito (/carrito/) → Checkout (/carrito/checkout/)
4. FACTURACIÓN:
   - Consumidor Final: solo pago en Efectivo. El descuento personalizado NO aplica.
   - Datos Personales (cédula): Efectivo o Tarjeta. El descuento personalizado SÍ aplica si está vigente.
   - Facturas PDF disponibles en "Mis Compras" (/mis-compras/).
5. MÉTODOS DE PAGO activos: Efectivo, Tarjeta de crédito, Tarjeta de débito.
   Transferencia bancaria: TEMPORALMENTE SUSPENDIDA. El descuento NO aplica en transferencia.
6. DESCUENTOS PERSONALIZADOS:
   - Si el cliente tiene descuento activo, está indicado en "INFORMACIÓN DEL CLIENTE" arriba.
   - El descuento se aplica automáticamente al finalizar el checkout (no hay código que ingresar).
   - Si la vigencia expiró, el descuento NO se aplica aunque esté configurado.
   - Para beneficiarse del descuento: elegir factura con Datos Personales + Efectivo o Tarjeta.
   - Si el cliente pregunta por su descuento, usa la información del bloque de arriba.
7. HISTORIAL: Si el cliente pregunta por sus compras anteriores, usa el bloque
   "COMPRAS RECIENTES DEL CLIENTE" de arriba para responder.
8. PRECIOS Y IVA: Los precios incluyen IVA 15%.
9. ESCÁNER: Disponible en /scan_barcode/ para consultar precios por código EAN-13.

=== REGLAS DE COMPORTAMIENTO CLIENTE ===
- Sé cálido, amigable y servicial. El cliente es tu prioridad.
- Si el cliente tiene descuento activo, menciónalo de forma natural cuando sea relevante
  (ej: cuando pregunte por el total, por cómo pagar, o si puede ahorrar algo).
- Si el descuento expiró, díselo amablemente y sugiere que contacte al administrador para renovarlo.
- Si el producto que busca no está disponible, sugiere alternativas del catálogo.
- Guía paso a paso cuando el cliente tenga dudas del proceso de compra.
- Responde en español Ecuador. Usa emojis ocasionalmente 🛒🎉🏷️.
- Nunca inventes productos ni precios. Solo informa lo que está en el catálogo.
- Si el historial de la conversación está vacío (es el primer mensaje), preséntate por
  tu nombre de forma breve y natural antes de responder. Si ya hay historial previo,
  NO vuelvas a presentarte — continúa la conversación con normalidad.
"""


def _build_guest_prompt(ctx: dict) -> str:
    """Construye el prompt para el asistente de bienvenida, con contexto de ventas, inventario y navegación del panel."""
    return f"""Te llamas {BOT_NAME}, el asistente de bienvenida de 'My Supermarket', tienda online en Guayaquil.
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
- Si el historial de la conversación está vacío (es el primer mensaje), preséntate por
  tu nombre de forma breve y natural antes de responder. Si ya hay historial previo,
  NO vuelvas a presentarte — continúa la conversación con normalidad.
"""


# ─────────────────────────────────────────────────────────────────
# Vista principal del chatbot
# ─────────────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class ChatbotProxyView(View):
    """
    POST /chatbot/api/
    Body JSON: { "message": "...", "history": [...] }
    View principal del chatbot, que recibe mensajes de usuario y devuelve respuestas.
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
        response_data = {'role': 'guest', 'data': {}}
        if not request.user.is_authenticated:
            resp = JsonResponse(response_data)
            resp['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            return resp

        user = request.user
        if user.is_superuser or getattr(user, 'user_type', '') == 'admin':
            resp = JsonResponse({
                'role': 'admin',
                'data': get_admin_quick_summary(),
            })
            resp['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            return resp
        else:
            resp = JsonResponse({
                'role': 'customer',
                'data': get_customer_quick_summary(user),
            }) 
            resp['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            return resp 