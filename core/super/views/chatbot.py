import json
import google.generativeai as genai
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
            
            # Configurar Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=(
                    "Eres el asistente virtual de 'My Supermarket'. "
                    "Ayuda a los clientes con dudas sobre productos, categorías (Frutas, Carnes, Lácteos, etc.), "
                    "facturación (pueden ser Consumidor Final o con datos) y métodos de pago (Efectivo, Tarjeta, QR). "
                    "Si el cliente es Consumidor Final, solo aceptamos Efectivo. "
                    "Sé amable, usa emojis de supermercado 🛒 y responde siempre en español de Ecuador. "
                    "Si no sabes algo, diles que contacten al admin en la sección de Contacto."
                )
            )
            response = model.generate_content(user_message)
            return JsonResponse({"reply": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)