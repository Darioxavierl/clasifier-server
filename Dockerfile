FROM python:3.10-slim

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

WORKDIR /code

# Instalar solo las dependencias necesarias (más específicas para Debian slim)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libopenblas0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app
COPY ./models /code/models

# Crear directorio de logs
RUN mkdir -p /code/logs && chown -R appuser:appuser /code

# Cambiar al usuario no-root
USER appuser

# Volumen para persistir logs
VOLUME ["/code/logs"]

# Variables de entorno por defecto
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn app.main:app --host ${HOST} --port ${PORT}"]