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
            
            # Obtener nombre del usuario
            user_name = request.user.first_name if request.user.is_authenticated else "Invitado"
            
            # Inicializar cliente
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Instrucciones del sistema
            sys_instruct = (
                f"Eres el asistente virtual de 'My Supermarket'. Saludas a {user_name}. "
                "Ayudas con dudas sobre productos y facturación. "
                "Si el cliente es 'Consumidor Final' (DNI 9999999999), SOLO aceptamos Efectivo. "
                "Si usa datos personales, acepta Tarjeta o QR. "
                "Sé amable, usa emojis 🛒 y responde en español de Ecuador."
            )

            # Generar respuesta usando un diccionario para la configuración (más seguro)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
                config={
                    'system_instruction': sys_instruct,
                    'temperature': 0.7,
                }
            )
            
            # El SDK nuevo devuelve la respuesta en response.text
            return JsonResponse({"reply": response.text})
            
        except Exception as e:
            # Imprime el error en tu terminal para que puedas verlo
            print(f"Error en Chatbot: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)