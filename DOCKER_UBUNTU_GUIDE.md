# 🐳 Guía Docker - Despliegue en Ubuntu 24

Instrucciones completas para clonar, construir y ejecutar el clasificador de residuos en Docker en Ubuntu 24.

---

## ✅ Checklist Pre-Despliegue

Antes de clonar el repositorio, verifica que tienes todo en tu servidor Ubuntu 24:

### Sistema Operativo
- [x] Ubuntu 24.04 LTS
- [ ] SSH acceso al servidor
- [ ] Conexión a internet estable

### Dependencias del Sistema
```bash
# Verificar Docker instalado
docker --version

# Verificar Docker Compose instalado
docker compose version

# Si no tienes Docker, instálalo:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Si no tienes Docker Compose:
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Git
```bash
# Verificar Git
git --version

# Si no tienes Git:
sudo apt-get update
sudo apt-get install -y git
```

---

## 🚀 Pasos para Desplegar en Ubuntu 24

### Paso 1: Clonar el Repositorio

```bash
# Navega a donde quieras el proyecto
cd ~
# O en una carpeta específica: cd /opt

# Clona el repositorio
git clone https://github.com/Darioxavierl/clasifier-server.git
cd clasifier-server

# (Opcional) Verifica que estés en la rama main
git branch
```

**Expected output:**
```
Cloning into 'clasifier-server'...
remote: Enumerating objects... 150
remote: Counting objects... 100% (150/150)
...
✓ Clonado exitosamente
```

### Paso 2: Verificar Estructura

```bash
# Verifica que existan archivos esenciales
ls -la | grep -E "Dockerfile|compose.yml|requirements.txt|.env.example"
```

**Estructura esperada:**
```
-rw-r--r-- Dockerfile
-rw-r--r-- compose.yml
-rw-r--r-- requirements.txt
-rw-r--r-- .env.example
drwxr-xr-x app/
drwxr-xr-x models/
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar configuración por defecto
cp .env.example .env

# (Opcional) Editar si necesitas cambios
# nano .env
# O
# vi .env

# Verificar contenido
cat .env
```

**Configuración recomendada para Ubuntu:**
```bash
# .env
MODEL_PATH=models/mobilenetv2_waste.h5          # TensorFlow para Linux
# O
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth  # PyTorch

IMG_SIZE=(224, 224)
CONFIDENCE_THRESHOLD=0.7
MAX_FILE_SIZE=5000000

CLASSES=["plastico", "papel", "vidrio", "metal", "carton", "trash"]

LOG_LEVEL=INFO
LOG_DIR=logs
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
LOG_PREDICTIONS=true
```

### Paso 4: Construir la Imagen Docker

```bash
# Opción A: Construir con nombre específico
docker build -t waste-classifier:latest .

# Opción B: Usando Docker Compose (recomendado)
docker compose build
```

**Expected output:**
```
[+] Building 45.2s (10/10) FINISHED
 => [internal] load build context
 => COPY requirements.txt .
 => RUN pip install --no-cache-dir -r requirements.txt
 => COPY ./app /code/app
 => COPY ./models /code/models
 ...
✓ Imagen construida: waste-classifier:latest
```

### Paso 5: Verificar la Imagen

```bash
# Listar imágenes
docker images | grep waste-classifier

# Ver detalles
docker inspect waste-classifier:latest | head -20
```

**Expected output:**
```
REPOSITORY              TAG       IMAGE ID       CREATED        SIZE
waste-classifier        latest    a1b2c3d4e5f6   2 minutes ago  1.2GB
```

### Paso 6: Ejecutar el Contenedor

#### Opción A: Con Docker Compose (RECOMENDADO)

```bash
# Inicia el servicio
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Detener servicio
docker compose down
```

**Expected output:**
```
[+] Building 0.1s (0/0)
[+] Running 1/1
 ✓ Container waste-classifier-api-1  Started
```

#### Opción B: Con Docker run (Manual)

```bash
# Ejecutar contenedor
docker run -d \
  --name waste-classifier-api \
  -p 8000:8000 \
  -v $(pwd)/logs:/code/logs \
  -e LOG_LEVEL=INFO \
  -e LOG_PREDICTIONS=true \
  waste-classifier:latest

# Ver estado
docker ps | grep waste-classifier

# Ver logs
docker logs -f waste-classifier-api
```

### Paso 7: Verificar que está Funcionando

```bash
# Verificar que el contenedor está corriendo
docker ps | grep waste-classifier

# Verificar puerto 8000 está escuchando
sudo netstat -tlnp | grep 8000
# O
curl http://localhost:8000/health
```

**Expected output:**
```
CONTAINER ID   IMAGE                      STATUS       PORTS
a1b2c3d4e5f6   waste-classifier:latest    Up 10 sec    0.0.0.0:8000->8000/tcp
```

---

## 🧪 Pruebas de la API

### Test 1: Health Check

```bash
# Verificar que la API responde
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-14T10:30:45.123456Z"
}
```

### Test 2: Documentación Swagger

```bash
# Abre en tu navegador
http://<IP-DEL-SERVIDOR>:8000/docs

# O usa curl para verificar
curl -s http://localhost:8000/openapi.json | head -50
```

### Test 3: Predicción con Test Image

```bash
# Descargar test image
curl -o test_image.jpg https://example.com/test.jpg
# O usar una imagen local

# Hacer predicción
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

**Expected response:**
```json
{
  "class_id": 3,
  "class_name": "plastico",
  "confidence": 0.9551,
  "all_probabilities": {
    "carton": 0.0012,
    "metal": 0.0034,
    "papel": 0.0156,
    "plastico": 0.9551,
    "trash": 0.0187,
    "vidrio": 0.0060
  },
  "model_framework": "tensorflow"
}
```

### Test 4: Predicción con Python

```bash
# En tu servidor Ubuntu, crear script test.py
cat > test_prediction.py << 'EOF'
import requests
import json

# URL de la API
API_URL = "http://localhost:8000/predict"

# Ruta de imagen test
IMAGE_PATH = "test_image.jpg"

try:
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': f}
        response = requests.post(API_URL, files=files)
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
EOF

# Ejecutar test
python test_prediction.py
```

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Docker Compose
docker compose logs -f

# Docker run
docker logs -f waste-classifier-api

# Seguir solo últimas 50 líneas
docker logs -f --tail 50 waste-classifier-api
```

### Ver Logs de Predicciones

```bash
# Los logs se guardan en ./logs/ del host
ls -la logs/

# Ver último log
tail -f logs/waste_classifier.log

# Buscar predicciones específicas
grep "PREDICCIÓN" logs/waste_classifier.log
```

### Estadísticas del Contenedor

```bash
# Ver CPU, memoria, etc.
docker stats waste-classifier-api

# Ver con formato JSON
docker inspect waste-classifier-api | grep -A 20 "MemoryStats"
```

---

## � Seguridad

### Usuario No-Root

La imagen Docker está configurada para ejecutarse con un usuario no-root (`appuser`, UID 1000) en lugar de `root`. Esto es una best practice de seguridad para producción.

**Verificar que se ejecuta con usuario no-root:**

```bash
# Ver el usuario que ejecuta el contenedor
docker exec waste-classifier-api whoami
# Output esperado: appuser

# Ver los permisos del proceso
docker top waste-classifier-api
# Output esperado: UID 1000 en lugar de 0 (root)
```

**Configuración en el Dockerfile:**
- Usuario creado: `appuser` (UID 1000)
- Directorio de trabajo: `/code` (pertenece a appuser)
- Archivo logs: `/code/logs` (pertenece a appuser)
- Comando ejecutado: bajo usuario `appuser`

**Beneficios:**
- ✅ Aislamiento: Si se compromete la aplicación, el atacante tiene acceso limitado
- ✅ Permisos: No puede modificar directorios del sistema
- ✅ Cumplimiento: Sigue estándares de seguridad de contenedores (CIS Benchmarks)

---

## �🔧 Troubleshooting

### Problema 1: "Cannot connect to Docker daemon"

```bash
# Solución: Docker no está corriendo
sudo systemctl start docker

# O verificar status
sudo systemctl status docker

# (Opcional) Hacer que inicie automáticamente
sudo systemctl enable docker
```

### Problema 2: "Port 8000 already in use"

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000
# O
sudo netstat -tlnp | grep 8000

# Opción A: Cambiar puerto en compose.yml
# Cambiar: "8000:8000" por "8001:8000"

# Opción B: Matar proceso que usa el puerto
sudo kill -9 <PID>

# Opción C: Usar Docker Compose (detiene automáticamente)
docker compose down
```

### Problema 3: "No such file or directory: models/..."

```bash
# Verificar que existan los modelos
ls -la models/

# Si faltan archivos
git lfs pull  # Si usa Git LFS
# O
# Descargar modelos manualmente desde releases
```

### Problema 4: "Out of Memory"

```bash
# Ver logs de OOM
docker logs waste-classifier-api | grep -i memory

# Aumentar memoria disponible
# En docker-compose.yml, agregar:
# deploy:
#   resources:
#     limits:
#       memory: 4G

# O usar comando:
docker run -m 4g waste-classifier:latest
```

### Problema 5: "Module not found: tensorflow/torch"

```bash
# Verificar requirements.txt
cat requirements.txt

# Reconstruir imagen
docker compose down
docker compose build --no-cache
docker compose up
```

### Problema 6: Imagen muy grande

```bash
# Ver tamaño de imagen
docker images waste-classifier:latest

# Limpiar capas innecesarias
docker image prune

# Usar multi-stage build (en Dockerfile)
# Recomendación: cambiar FROM python:3.10-slim a alpine si es posible
```

---

## 🚦 Comandos Útiles

### Gestión de Contenedores

```bash
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores
docker ps -a

# Ver logs en tiempo real
docker logs -f <CONTAINER_ID>

# Entrar en contenedor (bash)
docker exec -it <CONTAINER_ID> bash

# Detener contenedor
docker stop <CONTAINER_ID>

# Iniciar contenedor
docker start <CONTAINER_ID>

# Eliminar contenedor
docker rm <CONTAINER_ID>

# Ver estadísticas
docker stats
```

### Gestión con Docker Compose

```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Detener servicios
docker compose down

# Rebuild sin caché
docker compose build --no-cache

# Ver estado de servicios
docker compose ps

# Ejecutar comando en contenedor
docker compose exec api bash
```

### Gestión de Imágenes

```bash
# Ver imágenes
docker images

# Ver historial de imagen
docker history waste-classifier:latest

# Limpiar imágenes no usadas
docker image prune

# Eliminar imagen
docker rmi waste-classifier:latest
```

---

## 🌐 Acceso Remoto desde Cliente

Si accedes desde otra máquina (no el servidor):

```bash
# Cambiar localhost por IP del servidor
SERVIDOR_IP="192.168.1.100"  # Reemplaza con tu IP

# Health check
curl http://$SERVIDOR_IP:8000/health

# Swagger UI en navegador
# http://192.168.1.100:8000/docs

# Predicción
curl -X POST "http://$SERVIDOR_IP:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"

# Python
import requests
response = requests.post(
    "http://192.168.1.100:8000/predict",
    files={"file": open("image.jpg", "rb")}
)
```

---

## 📋 Checklist Final de Despliegue

Antes de pasar a producción:

- [ ] Docker instalado y funcionando
- [ ] Repositorio clonado exitosamente
- [ ] `.env` configurado correctamente
- [ ] Imagen Docker construida sin errores
- [ ] Contenedor inicia sin crashes
- [ ] `/health` responde correctamente
- [ ] `/docs` Swagger UI accesible
- [ ] Predicción funciona con test image
- [ ] Logs se escriben en `./logs/`
- [ ] Port 8000 abierto en firewall (si es necesario)

```bash
# Script de verificación rápida
echo "=== VERIFICACIÓN RÁPIDA ==="
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker compose version)"
echo "Git: $(git --version)"
echo ""
echo "=== CONTENEDOR ==="
docker ps | grep waste-classifier
echo ""
echo "=== HEALTH CHECK ==="
curl -s http://localhost:8000/health | jq .
echo ""
echo "=== LISTO PARA PRODUCCIÓN ==="
```

---

## 🎉 Siguientes Pasos

Después de verificar que todo funciona:

1. **Configurar SSL/TLS** (HTTPS)
   - Usar Nginx como reverse proxy
   - O usar certbot con Let's Encrypt

2. **Configurar Reverse Proxy** (Nginx/Apache)
   - Ejemplo: `nginx.conf` para proxy a 8000

3. **Configurar Monitoreo**
   - Prometheus para métricas
   - Alertas con email

4. **Backup Automático**
   - Backup de modelos
   - Backup de logs

5. **Actualizar Modelos**
   - Script de actualización
   - Rollback automático si falla

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs -f`
2. Ejecuta verificación: `curl http://localhost:8000/health`
3. Verifica Docker: `docker ps`
4. Limpia e intenta de nuevo: `docker compose down --volumes`

---

**Última actualización:** Diciembre 2024  
**Versión Docker:** 3.8  
**Versión Ubuntu:** 24.04 LTS
