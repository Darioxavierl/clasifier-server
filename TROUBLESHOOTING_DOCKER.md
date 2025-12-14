# 🛠️ Troubleshooting Docker - Ubuntu 24

Soluciones rápidas para problemas comunes al desplegar en Ubuntu 24.

---

## 🔍 Diagnóstico Rápido

Antes de reportar un problema, ejecuta esto:

```bash
# Verificación rápida
bash verify_docker_deployment.sh

# Si algo falla, ejecuta estos comandos individualmente:
docker --version
docker compose version
docker ps
curl http://localhost:8000/health
docker compose logs -f --tail 50
```

---

## ❌ Problemas Comunes y Soluciones

### 1. "Cannot connect to Docker daemon"

**Síntomas:**
```
Cannot connect to Docker daemon at unix:///var/run/docker.sock. 
Is the docker daemon running?
```

**Soluciones:**

```bash
# Opción 1: Docker no está corriendo
sudo systemctl start docker

# Verificar status
sudo systemctl status docker

# Hacer que inicie automáticamente
sudo systemctl enable docker

# Opción 2: Permisos insuficientes
sudo usermod -aG docker $USER

# IMPORTANTE: Cierra sesión y vuelve a conectar
exit

# Opción 3: Verificar que Docker está instalado correctamente
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
```

---

### 2. "Port 8000 already in use"

**Síntomas:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Soluciones:**

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# O con ss
sudo ss -tlnp | grep 8000

# Opción 1: Matar el proceso
sudo kill -9 <PID>

# Opción 2: Usar otro puerto (editar compose.yml)
nano compose.yml
# Cambiar: "8000:8000" por "8001:8000"
docker compose up -d

# Opción 3: Esperar a que se libere el puerto
sleep 60 && docker compose up -d

# Opción 4: Detener todos los contenedores Docker
docker compose down
docker stop $(docker ps -a -q)
```

---

### 3. "No space left on device"

**Síntomas:**
```
No space left on device
Error saving the file
```

**Soluciones:**

```bash
# Ver uso de disco
df -h

# Limpiar Docker (cuidado: borra imágenes no usadas)
docker system prune -a
docker volume prune

# Ver tamaño de imágenes
docker images --format "{{.Repository}}\t{{.Size}}"

# Expandir partición (si tienes espacio disponible)
# Esto requiere acceso root y herramientas de particionado

# Alternativa: Cambiar ubicación de Docker
sudo mkdir -p /mnt/docker-data
sudo systemctl stop docker

# Editar daemon.json
sudo nano /etc/docker/daemon.json
# Agregar: {"data-root": "/mnt/docker-data"}

sudo systemctl start docker
```

---

### 4. "Out of Memory"

**Síntomas:**
```
Killed (out of memory)
Process exited unexpectedly
Memory limit exceeded
```

**Soluciones:**

```bash
# Ver uso de memoria
docker stats

# Limitar memoria en compose.yml
nano compose.yml

# Agregar en services > api:
# deploy:
#   resources:
#     limits:
#       memory: 2G
#     reservations:
#       memory: 1G

docker compose up -d

# Reducir batch size si estás entrenando
# En app/config.py, reduce MAX_BATCH_SIZE

# Ver logs de OOM
dmesg | grep -i memory | tail -20
```

---

### 5. "Module not found: tensorflow/torch"

**Síntomas:**
```
ModuleNotFoundError: No module named 'tensorflow'
ModuleNotFoundError: No module named 'torch'
```

**Soluciones:**

```bash
# Opción 1: Reconstruir imagen sin caché
docker compose down
docker compose build --no-cache
docker compose up -d

# Opción 2: Verificar requirements.txt
cat requirements.txt | grep -E "tensorflow|torch"

# Opción 3: Entrar en contenedor y instalar manualmente
docker compose exec api bash
pip list | grep -i tensorflow
pip list | grep -i torch

# Opción 4: Actualizar requirements.txt e instalar
pip install --upgrade tensorflow
pip install --upgrade torch

# Ver logs de construcción
docker compose build --progress=plain
```

---

### 6. "Image build fails"

**Síntomas:**
```
Step X/Y : RUN pip install...
ERROR: Could not find a version...
```

**Soluciones:**

```bash
# Opción 1: Ver logs completos
docker compose build --progress=plain 2>&1 | tee build.log

# Opción 2: Actualizar requirements.txt
pip list --outdated > requirements_updated.txt
# Revisar y actualizar versions

# Opción 3: Usar requirements específico para Linux
# En Dockerfile, cambiar COPY requirements.txt a:
# COPY requirements-linux.txt requirements.txt

# Opción 4: Aumentar timeout de pip
docker compose build --build-arg PIP_DEFAULT_TIMEOUT=100

# Opción 5: Cambiar mirror de pip
# En Dockerfile agregar:
# RUN pip install -i https://pypi.tsinghua.edu.cn/simple -r requirements.txt
```

---

### 7. "API no responde" (Connection refused)

**Síntomas:**
```
curl: (7) Failed to connect to localhost port 8000
Connection refused
```

**Soluciones:**

```bash
# Opción 1: Verificar que el contenedor está corriendo
docker ps | grep waste-classifier

# Si no aparece:
docker compose up -d

# Opción 2: Ver logs
docker compose logs -f --tail 100

# Opción 3: Esperar más tiempo (FastAPI puede tardar en iniciar)
sleep 5
curl http://localhost:8000/health

# Opción 4: Verificar si el contenedor está crasheando
docker compose ps
# Si status dice "Exited", ver logs:
docker compose logs

# Opción 5: Verificar puerto
netstat -tlnp | grep 8000
# Si no aparece, el contenedor no está escuchando

# Opción 6: Probar dentro del contenedor
docker compose exec api curl http://localhost:8000/health
```

---

### 8. "Model not found"

**Síntomas:**
```
FileNotFoundError: models/mobilenetv2_waste.h5
Model file not found at path
```

**Soluciones:**

```bash
# Opción 1: Verificar archivos
ls -la models/

# Opción 2: Si faltan modelos, usar Git LFS
git lfs install
git lfs pull

# Opción 3: Descargar manualmente
# Desde: https://github.com/Darioxavierl/clasifier-server/releases

# Opción 4: Verificar ruta en .env
cat .env | grep MODEL_PATH

# Opción 5: La ruta debe ser relativa a /code en Docker
# En Docker: /code/models/
# En .env: models/mobilenetv2_waste.h5 ✓
# NO: /root/models/... ✗
# NO: ~/models/... ✗

# Opción 6: Ver logs del contenedor
docker compose logs | grep -i model
```

---

### 9. "SSL/TLS Certificate errors"

**Síntomas:**
```
SSL: CERTIFICATE_VERIFY_FAILED
ssl.SSLError
```

**Soluciones:**

```bash
# Opción 1: Actualizar certificados
sudo apt-get update
sudo apt-get install -y ca-certificates
sudo update-ca-certificates

# Opción 2: Desactivar verificación SSL (solo para desarrollo)
# En requirements.txt, agregar: certifi==2024.x.x

# Opción 3: Usar proxy HTTPS si estás detrás de firewall
export https_proxy=http://proxy:8080
docker compose build

# Opción 4: Ver certificados instalados
openssl s_client -connect pypi.org:443 -showcerts
```

---

### 10. "Permission denied" errors

**Síntomas:**
```
Permission denied while trying to connect to Docker daemon
Got permission denied while trying to read
```

**Soluciones:**

```bash
# Opción 1: Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Cierra sesión y vuelve a conectar

# Opción 2: Usar sudo explícitamente
sudo docker ps
sudo docker compose up -d

# Opción 3: Verificar permisos de archivo
ls -la compose.yml
chmod 644 compose.yml

# Opción 4: Cambiar propiedad de archivos
sudo chown $USER:$USER .
sudo chmod u+rwx .

# Opción 5: Ejecutar daemon como root (menos seguro)
sudo systemctl start docker
sudo docker ps
```

---

### 11. "Logs not showing" (docker logs vacío)

**Síntomas:**
```
docker logs: No output
docker compose logs: Nothing
```

**Soluciones:**

```bash
# Opción 1: Verificar que el contenedor existe
docker ps -a | grep waste-classifier

# Opción 2: Ver logs del contenedor desde Docker
docker logs $(docker ps -q -f ancestor=waste-classifier:latest)

# Opción 3: Ver logs en tiempo real
docker compose logs -f

# Opción 4: Los logs podrían estar en archivo
docker compose exec api tail -f /code/logs/waste_classifier.log

# Opción 5: Ver error de inicio
docker compose logs | head -50

# Opción 6: Aumentar nivel de log en .env
LOG_LEVEL=DEBUG
docker compose down
docker compose up -d
docker compose logs -f
```

---

### 12. "GPU not detected" (si tienes GPU)

**Síntomas:**
```
CUDA not available
GPU not detected
Running on CPU
```

**Soluciones:**

```bash
# Opción 1: Verificar GPU en host
nvidia-smi

# Opción 2: Instalar NVIDIA Docker Runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Opción 3: Configurar compose para usar GPU
# En compose.yml, agregar:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]

docker compose down
docker compose up -d

# Opción 4: Verificar que GPU está disponible en contenedor
docker compose exec api python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🔧 Comandos de Rescate

```bash
# Limpieza completa (ADVERTENCIA: borra todo)
docker compose down
docker system prune -a --volumes
rm -rf logs/*

# Reconstruir desde cero
docker compose build --no-cache
docker compose up -d

# Ver todo lo que Docker ocupa
docker system df

# Frenar y espiar procesos
docker compose down
sleep 5
docker compose up -d

# Entrar en modo debug
docker compose exec api bash

# Ver variables de entorno en contenedor
docker compose exec api env | grep -i log

# Reinstalar dependencias
docker compose exec api pip install --upgrade -r /code/requirements.txt

# Ver archivo de logs en contenedor
docker compose exec api tail -100 /code/logs/waste_classifier.log
```

---

## 📋 Checklist de Verificación

Cuando algo no funciona, sigue este orden:

1. **¿Docker está corriendo?**
   ```bash
   sudo systemctl status docker
   ```

2. **¿El contenedor está levantado?**
   ```bash
   docker compose ps
   ```

3. **¿Hay errores en los logs?**
   ```bash
   docker compose logs | tail -50
   ```

4. **¿Puedo acceder a la API?**
   ```bash
   curl http://localhost:8000/health
   ```

5. **¿El modelo está presente?**
   ```bash
   docker compose exec api ls -la /code/models/
   ```

6. **¿Hay espacio en disco?**
   ```bash
   df -h
   ```

7. **¿Hay suficiente memoria?**
   ```bash
   docker stats
   ```

8. **¿El puerto está disponible?**
   ```bash
   sudo lsof -i :8000
   ```

---

## 🆘 Soporte Avanzado

Si nada de lo anterior funciona:

1. Recopila información:
   ```bash
   uname -a > debug.txt
   docker --version >> debug.txt
   docker compose version >> debug.txt
   docker compose logs >> debug.txt
   docker ps -a >> debug.txt
   docker images >> debug.txt
   ```

2. Ejecuta verificación completa:
   ```bash
   bash verify_docker_deployment.sh > verification.log 2>&1
   ```

3. Crea un issue en GitHub con:
   - Los logs completos
   - Output de `verify_docker_deployment.sh`
   - Tu configuración (sanitizada)
   - Versión de Ubuntu y Docker

---

**Última actualización:** Diciembre 2024  
**Testeado en:** Ubuntu 24.04 LTS
