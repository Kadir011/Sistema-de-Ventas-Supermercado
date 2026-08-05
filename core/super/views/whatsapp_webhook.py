import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from core.super.services.whatsapp_service import WhatsAppService

User = get_user_model()


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
            # Puede ser un evento de "mensaje leído" u otro, no un mensaje nuevo
            return JsonResponse({'status': 'ignored'})

        message = entry['messages'][0]
        from_number = message['from']  # ej: "593998222804", sin el "+"
        text = message.get('text', {}).get('body', '')

        user = _find_user_by_phone(from_number)
        reply_text = _generate_reply(user, text)

        WhatsAppService().send_message(from_number, reply_text)
        return JsonResponse({'status': 'ok'})

    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"[WhatsApp] Payload inesperado: {exc}")
        return JsonResponse({'status': 'error'}, status=200)  # 200 igual, para que Meta no reintente


def _find_user_by_phone(phone_number: str):
    """
    Busca al User asociado a ese teléfono, comparando por el Customer.
    Meta manda el número sin "+" y con código de país (ej: 593998222804).
    """
    digits_only = ''.join(filter(str.isdigit, phone_number))

    from core.super.models import Customer
    customer = Customer.objects.filter(phone__icontains=digits_only[-9:]).first()
    if not customer or not customer.email:
        return None

    return User.objects.filter(email=customer.email).first()


def _generate_reply(user, message_text: str) -> str:
    """
    TODO: reemplazar este placeholder por la llamada real a tu servicio
    de Gemini una vez que compartas ese archivo. Por ahora responde genérico
    para poder probar que el webhook end-to-end funciona.
    """
    if not user:
        return "Hola, no encontré tu cuenta registrada. Escríbenos desde el número con el que te registraste."
    return f"Hola {user.first_name}, recibí tu mensaje: \"{message_text}\". (Respuesta de Gemini pendiente de conectar)"
