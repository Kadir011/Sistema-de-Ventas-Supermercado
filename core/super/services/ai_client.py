import time
from abc import ABC, abstractmethod
from google import genai
from google.genai import types

# DIP — Interface para el cliente AI

class AIClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, history: list, user_message: str) -> str:
        pass

class GeminiAIClient(AIClient):
    """
    Cliente Gemini con reintentos automáticos ante errores 503 (UNAVAILABLE).

    La API de Gemini puede devolver 503 por picos de demanda.
    Reintentamos hasta MAX_RETRIES veces con backoff exponencial antes de
    devolver un mensaje de error amigable al usuario.
    """
    MAX_RETRIES = 3          # número máximo de intentos
    BASE_DELAY  = 1.5        # segundos de espera inicial (se duplica en cada reintento)

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)
        self._types = types

    def generate(self, system_prompt: str, history: list, user_message: str) -> str:
        contents = [
            self._types.Content(role=t['role'], parts=[self._types.Part(text=t['content'])])
            for t in history
            if t.get('role') in ('user', 'model')
        ]
        contents.append(
            self._types.Content(role='user', parts=[self._types.Part(text=user_message)])
        )

        last_error = None
        delay = self.BASE_DELAY

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self._client.models.generate_content(
                    model='gemini-3-flash-preview',
                    contents=contents,
                    config=self._types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.6,
                        max_output_tokens=1500,
                    ),
                )
                return response.text or 'Lo siento, no pude generar una respuesta.'

            except Exception as exc:
                last_error = exc
                error_str = str(exc)

                # Solo reintentamos ante errores transitorios (503, timeout, etc.)
                is_transient = (
                    '503' in error_str
                    or 'UNAVAILABLE' in error_str
                    or 'timeout' in error_str.lower()
                    or 'DeadlineExceeded' in error_str
                )

                if is_transient and attempt < self.MAX_RETRIES:
                    print(f"[GeminiAIClient] Intento {attempt}/{self.MAX_RETRIES} fallido "
                          f"(transitorio). Reintentando en {delay:.1f}s... Error: {exc}")
                    time.sleep(delay)
                    delay *= 2          # backoff exponencial
                else:
                    # Error no recuperable o ya agotamos reintentos
                    break

        # Si llegamos aquí, todos los intentos fallaron
        print(f"[GeminiAIClient] Todos los intentos fallaron. Último error: {last_error}")
        raise last_error 