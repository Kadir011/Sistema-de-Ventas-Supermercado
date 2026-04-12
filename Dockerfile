# Usa la imagen oficial de Python 3.10 slim
FROM python:3.10.11-slim

# Evitar archivos .pyc y habilitar salida sin buffer para ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL, Pillow, pycairo y GDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python (esto aprovecha el cache de Docker)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente del proyecto al contenedor
COPY . .

# Crear directorios para archivos estáticos y de medios
RUN mkdir -p /app/media /app/staticfiles

# Recolectar archivos estáticos para que WhiteNoise pueda servirlos
RUN python manage.py collectstatic --noinput

# Render asigna el puerto dinámicamente, por lo que exponemos el 8000 como referencia
EXPOSE 8000

# Comando de inicio para Producción:
# 1. Aplica migraciones pendientes a la base de datos (Neon).
# 2. Inicia el servidor profesional Gunicorn vinculado a la variable $PORT de Render.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"]