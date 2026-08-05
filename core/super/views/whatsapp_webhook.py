import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from core.super.services.chat_context import ChatContextDirector
from core.super.services.ai_client import GeminiAIClient
from core.super.services.whatsapp_service import WhatsAppService
from core.super.views.chatbot import _build_customer_prompt, _build_guest_prompt

User = get_user_model()

# Un solo cliente Gemini reutilizado entre requests, igual que hace
# ChatbotProxyView vía su __init__ (evita crear un genai.Client nuevo
# en cada mensaje de WhatsApp).
_ai_client = GeminiAIClient(api_key=settings.GEMINI_API_KEY)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        return _verify_webhook(request)
    if request.method == 'POST':
        return _handle_incoming_message(request)
    return HttpResponse(status=405)


def _verify_webhook(request):
    """Meta llama esto UNA VEZ al configurar el webhook, para confirmar que es tuyo."""
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')

    if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
        return HttpResponse(challenge)
    return HttpResponse('Token inválido', status=403)


def _handle_incoming_message(request):
    """Meta llama esto cada vez que alguien le escribe al número de WhatsApp."""
    try:
        data = json.loads(request.body)
        entry = data['entry'][0]['changes'][0]['value']

        if 'messages' not in entry:
            # Puede ser un evento de "mensaje leído"/estado, no un mensaje nuevo
            return JsonResponse({'status': 'ignored'})

        message = entry['messages'][0]
        from_number = message['from']  # ej: "593998222804", sin el "+"
        text = message.get('text', {}).get('body', '')

        if not text:
            WhatsAppService().send_message(
                from_number, "Por ahora solo puedo leer mensajes de texto 🙂"
            )
            return JsonResponse({'status': 'ok'})

        user = _find_user_by_phone(from_number)
        reply_text = _generate_reply(user, text)

        WhatsAppService().send_message(from_number, reply_text)
        return JsonResponse({'status': 'ok'})

    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"[WhatsApp] Payload inesperado: {exc}")
        return JsonResponse({'status': 'error'}, status=200)  # 200 para que Meta no reintente


def _find_user_by_phone(phone_number: str):
    """
    Busca al User asociado a ese teléfono, comparando contra User.phone_number
    (no Customer.phone) porque ese es el campo que el cliente mantiene
    actualizado desde su propio perfil (ProfileInfoForm). Customer.phone solo
    se sincroniza una vez, al momento del registro, y puede quedar obsoleto
    si el cliente cambia su número después.

    Meta manda el número sin "+" y con código de país (ej: 593998222804).
    Comparamos por los últimos 9 dígitos para tolerar diferencias de formato
    (con/sin código de país, con/sin el 0 inicial ecuatoriano).
    """
    digits_only = ''.join(filter(str.isdigit, phone_number))
    local_digits = digits_only[-9:]

    return User.objects.filter(phone_number__icontains=local_digits).first()


def _generate_reply(user, message_text: str) -> str:
    """
    Reutiliza EXACTAMENTE el mismo pipeline que ChatbotProxyView (chat web):
    ChatContextDirector arma el contexto por rol, el prompt correspondiente
    lo envuelve, y GeminiAIClient genera la respuesta real.

    Nota de alcance: WhatsApp no mantiene el `history` de la conversación
    (cada mensaje se trata como turno único, sin memoria de mensajes previos).
    Eso es una limitación consciente del MVP, no un error — se puede agregar
    después guardando el historial reciente por número de teléfono.
    """
    director = ChatContextDirector()

    if user is not None:
        ctx = director.build_for_role(role='customer', user=user)
        user_name = user.first_name or user.username
        system_prompt = _build_customer_prompt(user_name, ctx)
    else:
        ctx = director.build_for_role(role='guest')
        system_prompt = _build_guest_prompt(ctx)

    try:
        return _ai_client.generate(system_prompt, [], message_text)
    except Exception as exc:
        print(f"[WhatsApp] Error generando respuesta con Gemini: {exc}")
        return "⚠️ Tuvimos un problema técnico. Inténtalo de nuevo en unos segundos."
