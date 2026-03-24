import uuid
from core.super.models import Sale

# Singleton seguro para IdempotencyService

class IdempotencyService:
    """Verifica y resuelve claves de idempotencia para ventas.

    Implementación Singleton segura para evitar copy-paste y mantener una
    única instancia compartida de servicio dentro de la app.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # Método para la clave de análisis de idempotencia
    def parse_key(self, raw_key: str):
        if not raw_key:
            return None
        try:
            return uuid.UUID(raw_key.strip())
        except (ValueError, AttributeError):
            return None

    # Método para encontrar ventas existentes por clave de idempotencia
    def find_existing(self, key) -> Sale | None:
        if key is None:
            return None
        return Sale.objects.filter(idempotency_key=key).first()