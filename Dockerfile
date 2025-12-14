FROM python:3.10-slim

# Argumentos de build para UID/GID del usuario host
# Por defecto 1000:1000 (usuario estándar en Linux)
# Uso: docker build --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g) .
ARG UID
ARG GID
ARG APP_USER

ENV UID=${UID}
ENV GID=${GID}
ENV APP_USER=${APP_USER}

# Crear usuario no-root con los mismos UID/GID del host
# Esto evita problemas de permisos en volúmenes compartidos
RUN groupadd -g ${GID} ${APP_USER} && \
    useradd -m -u ${UID} -g ${GID} ${APP_USER}

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

# Crear directorio de logs y cambiar permisos al usuario correcto
RUN mkdir -p /code/logs && chown -R ${USER_UID}:${USER_GID} /code

# Cambiar al usuario no-root
USER ${APP_USER}

# Volumen para persistir logs
VOLUME ["/code/logs"]

# Variables de entorno por defecto
ENV PORT=8000
ENV HOST=0.0.0.0

# NOTA: No usamos EXPOSE porque es solo informativo y causa confusión
# cuando el puerto real es diferente. El puerto se define completamente
# mediante la variable PORT que puede cambiarse en .env

CMD ["sh", "-c", "uvicorn app.main:app --host ${HOST} --port ${PORT}"]