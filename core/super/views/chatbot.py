import json
from google import genai
from google.genai import types # Importante para la configuración
from django.conf import settings
from django.http import JsonResponse
from django.views import View

class ChatbotProxyView(View):    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Mensaje vacío"}, status=400)
            
            # Obtener nombre del usuario para personalizar la experiencia
            user_name = request.user.first_name if request.user.is_authenticated else "Invitado"
            
            # Inicializar cliente con la nueva librería google-genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Configuración del sistema (Instrucciones)
            sys_instruct = (
                f"Eres el asistente virtual de 'My Supermarket'. Saludas a {user_name}. "
                "Ayudas con dudas sobre categorías (Frutas, Carnes, Lácteos, etc.) y facturación. "
                "Regla de Oro: Si el cliente es 'Consumidor Final', SOLO aceptamos Efectivo. "
                "Si quiere factura con datos, puede usar Tarjeta o QR. "
                "Sé muy amable, usa emojis 🛒 y responde en español de Ecuador."
            )

            # Generar contenido con la sintaxis correcta del SDK 0.x
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
                config=types.GenerateConfig(
                    system_instruction=sys_instruct,
                    temperature=0.7
                )
            )
            
            # Validar que la respuesta tenga texto
            reply_text = response.text if response.text else "Lo siento, no pude procesar eso."
            return JsonResponse({"reply": reply_text})
            
        except Exception as e:
            # Esto te ayudará a ver el error real en la consola del navegador
            return JsonResponse({"error": str(e)}, status=500)