# 🔄 Docker en Estado "Restarting" - Solución

## ¿Qué significa "Restarting"?

```bash
sudo docker ps
# STATUS: Restarting (exit code X) X seconds ago
```

Significa que el contenedor **se está crasheando constantemente**. Docker intenta reiniciarlo pero falla inmediatamente.

---

## 🔍 Paso 1: Capturar el Error

### En Ubuntu 24, ejecuta:

```bash
# Ver último error
sudo docker logs waste-classifier-api --tail 50

# Ver logs completos
sudo docker logs waste-classifier-api

# Ver en tiempo real
sudo docker logs -f waste-classifier-api

# Detener y reintentar para ver error
sudo docker compose down
sudo docker compose up  # (sin -d para ver output)
```

**Busca líneas que digan:**
- `ERROR`
- `Traceback`
- `ModuleNotFoundError`
- `ImportError`
- `FileNotFoundError`

---

## 🐛 Causas Comunes (Soluciones)

### 1. **ModuleNotFoundError: No module named 'X'**

```
ModuleNotFoundError: No module named 'tensorflow'
```

**Causa:** Dependencias no instaladas en Docker

**Solución:**
```bash
# En Ubuntu
cd ~/clasifier-server

# Reconstruir imagen (instala dependencias)
docker compose down
docker system prune -a  # Limpia caché viejo
docker compose build --no-cache
docker compose up -d

# Ver si se instala bien
docker logs waste-classifier-api --tail 20
```

---

### 2. **Port Already in Use**

```
Address already in use
port 8000 is already allocated
```

**Causa:** Otro proceso usa el puerto

**Solución - Opción A:** Cambiar puerto
```bash
nano .env
# Cambiar: PORT=9000

docker compose down
docker compose up -d
```

**Solución - Opción B:** Matar proceso existente
```bash
# Ver qué usa puerto 8000
sudo lsof -i :8000

# Matar proceso
sudo kill -9 <PID>

# Reiniciar Docker
docker compose restart
```

---

### 3. **No space left on device**

```
No space left on device
write error
```

**Causa:** Disco lleno

**Solución:**
```bash
# Ver espacio
df -h

# Limpiar Docker
docker system prune -a

# Limpiar old logs
sudo find /var/log -name "*.log" -mtime +7 -delete

# Ver carpeta más grande
du -sh ~/* | sort -rh | head
```

---

### 4. **Out of Memory**

```
Killed: 9
OOMKilled
```

**Causa:** Memoria insuficiente

**Solución:**
```bash
# Ver memoria disponible
free -h

# Parar otros servicios
sudo systemctl stop nginx  # u otro servicio

# Reiniciar Docker
docker compose down
docker compose up -d
```

---

### 5. **FileNotFoundError: .env**

```
FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

**Causa:** Falta el archivo `.env`

**Solución:**
```bash
cd ~/clasifier-server

# Crear .env desde template
cp .env.example .env

# Editar si necesario
nano .env

# Reiniciar
docker compose down
docker compose up -d
```

---

### 6. **ImportError en config.py**

```
ImportError: cannot import name 'BaseSettings' from 'pydantic_settings'
```

**Causa:** Versión incorrecta de pydantic

**Solución:**
```bash
# Reconstruir con dependencias correctas
docker compose down
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

---

### 7. **Model file not found**

```
FileNotFoundError: [Errno 2] No such file or directory: 'models/mobilenetv2_waste_pytorch_best.pth'
```

**Causa:** Archivo de modelo falta

**Solución:**
```bash
# Verificar modelos existen
ls -lah models/

# Si faltan, descargarlos o usar otro
# Editar .env
nano .env
# MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# Verificar
docker exec waste-classifier-api ls /code/models/

# Reiniciar
docker compose restart
```

---

## 🔧 Diagnóstico Automático

En Ubuntu, usa el script de diagnóstico:

```bash
cd ~/clasifier-server

# Hacer ejecutable
chmod +x diagnose_docker.sh

# Ejecutar
./diagnose_docker.sh

# O desde Windows:
bash diagnose_docker.sh
```

**Esto mostrará:**
- Estado del contenedor
- Últimos logs (con error)
- Espacio en disco
- Memoria disponible
- Primer intento de reinicio con error

---

## 📋 Checklist de Troubleshooting

```bash
# 1. Ver estado actual
sudo docker ps -a

# 2. Capturar error
sudo docker logs waste-classifier-api --tail 100

# 3. Verificar archivos
ls -la ~/clasifier-server/.env
ls -la ~/clasifier-server/models/
ls -la ~/clasifier-server/app/

# 4. Verificar espacio
df -h /
free -h

# 5. Limpiar y reconstruir
docker compose down
docker system prune -a
docker compose build --no-cache
docker compose up -d

# 6. Verificar nuevamente
sudo docker ps
sudo docker logs waste-classifier-api --tail 20
```

---

## 🚨 Si Nada Funciona

### Opción 1: Reset Completo

```bash
cd ~/clasifier-server

# Parar todo
docker compose down

# Limpiar imágenes y volúmenes
docker system prune -a --volumes

# Actualizar código
git pull origin main

# Reconstruir desde cero
docker compose build --no-cache
docker compose up -d

# Esperar 30 segundos y verificar
sleep 30
sudo docker ps
```

### Opción 2: Verificar Configuración

```bash
# 1. Verificar .env es válido
cat .env

# 2. Verificar config.py
python -c "from app.config import settings; print(settings)"

# 3. Verificar imagen se construye
docker build -t test-image . --no-cache

# 4. Si todo OK, levantar
docker compose up -d
```

### Opción 3: Ejecutar Manualmente para Ver Error

```bash
# Entrar en el contenedor
docker run -it clasifier-server-api bash

# Ejecutar comando manualmente
python -c "from app.main import app; print('OK')"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Recolectar Info para Soporte

Si necesitas ayuda, proporciona:

```bash
# 1. Estado actual
sudo docker ps -a

# 2. Logs (primeras 100 líneas)
sudo docker logs waste-classifier-api | head -100

# 3. Configuración
cat .env

# 4. Espacio y memoria
df -h /
free -h

# 5. Información del sistema
uname -a
docker --version
docker compose version
```

---

## ✅ Señales de Que Está Bien

```bash
sudo docker ps
# STATUS: Up X seconds (sin Restarting)

sudo docker logs waste-classifier-api | tail -5
# Ningún ERROR
# Muestra: "Uvicorn running on..."

curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## 🎯 Resumen Rápido

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError` | Dependencias falta | `docker compose build --no-cache` |
| `Port already in use` | Puerto ocupado | Cambiar `PORT` en `.env` |
| `No space left` | Disco lleno | `docker system prune -a` |
| `Out of Memory` | RAM insuficiente | Parar otros servicios |
| `FileNotFoundError: .env` | Falta `.env` | `cp .env.example .env` |
| `Model not found` | Modelo falta | Verificar `models/` |
| Restarting infinito | Crash en startup | Ver logs con `docker logs` |

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
