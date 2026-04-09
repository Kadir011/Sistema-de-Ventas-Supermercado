FROM python:3.10.11-slim

# Evitar archivos .pyc y habilitar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2, Pillow y pycairo
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

# Copiar e instalar dependencias Python primero (aprovecha cache de capas)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Crear directorios de medios y archivos estáticos
RUN mkdir -p /app/media /app/staticfiles

# Exponer el puerto de Django
EXPOSE 8000

# Comando de inicio: recolectar estáticos y arrancar el servidor
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"] 