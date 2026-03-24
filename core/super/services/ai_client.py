from abc import ABC, abstractmethod
from google import genai
from google.genai import types

# DIP — Interface para el cliente AI

class AIClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, history: list, user_message: str) -> str:
        pass
    
class GeminiAIClient(AIClient):
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