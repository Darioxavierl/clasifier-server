FROM python:3.10-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app
COPY ./models /code/models

# Crear directorio de logs
RUN mkdir -p /code/logs

# Volumen para persistir logs
VOLUME ["/code/logs"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]