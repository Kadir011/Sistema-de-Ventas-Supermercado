import json
from google import genai
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
            
            # Inicializar cliente (usando la clave que ya verificaste que funciona)
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Obtener nombre del usuario para el saludo personalizado
            user_name = request.user.first_name if request.user.is_authenticated else "Invitado"
            
            # Generar contenido usando el modelo que te dio ÉXITO
            response = client.models.generate_content(
                model="gemini-3-flash-preview", # Modelo de Gemini Actualizado
                contents=user_message,
                config={
                    'system_instruction': (
                        f"Eres el asistente virtual de 'My Supermarket'. Saludas a {user_name}. "
                        "Ayudas con dudas sobre productos y facturación. "
                        "Regla de Oro: Si el cliente es 'Consumidor Final', SOLO aceptamos Efectivo. "
                        "Si usa datos personales, acepta Tarjeta o QR. "
                        "Sé amable, usa emojis 🛒 y responde en español de Ecuador."
                    ),
                    'temperature': 0.7,
                }
            )
            
            return JsonResponse({"reply": response.text})
            
        except Exception as e:
            # Imprime el error en la terminal de VS Code para verlo
            print(f"Error en Chatbot: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)