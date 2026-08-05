import requests
from django.conf import settings


class WhatsAppService:
    """Envía mensajes de texto usando la API de WhatsApp Cloud (Meta)."""

    BASE_URL = "https://graph.facebook.com/v25.0"

    def send_message(self, to: str, text: str) -> bool:
        url = f"{self.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            print(f"[WhatsApp] Error enviando mensaje a {to}: {exc}")
            return False
