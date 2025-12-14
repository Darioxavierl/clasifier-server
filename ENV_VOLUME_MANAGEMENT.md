# 🔄 Volumen Compartido .env - Cambios Dinámicos

## ¿Qué hace el volumen compartido?

```yaml
volumes:
  - ./.env:/code/.env:ro    # Host .env → Container .env (read-only)
```

Esto permite que:
- ✅ Cambies `.env` en el HOST (tu Ubuntu)
- ✅ El contenedor vea los cambios automáticamente
- ✅ Sin necesidad de reconstruir la imagen

---

## ⚠️ IMPORTANTE: Limitaciones Técnicas

### 1. Variables de Entorno - Cargadas UNA SOLA VEZ

```bash
# Cuando levantás el contenedor:
docker compose up -d

# compose.yml carga .env una sola vez al iniciar
# Luego esas variables están "congeladas" en memoria
PORT=8900  # Se carga aquí
```

**Esto significa:**
- ❌ Cambiar `PORT` en `.env` NO recarga automáticamente
- ❌ Necesitarías `docker compose restart` (o down/up)
- ✅ Cambiar `MODEL_PATH`, `LOG_LEVEL`, etc., SÍ funciona (app las re-lee)

### 2. Qué SÍ cambia dinámicamente (sin restart)

```
✅ LOG_LEVEL    → app.config.py lo re-lee
✅ CONFIDENCE_THRESHOLD → app.config.py lo re-lee
✅ MODEL_PATH   → app.config.py lo re-lee
✅ CLASSES      → app.config.py lo re-lee
✅ MAX_FILE_SIZE → app.config.py lo re-lee

❌ PORT         → Necesita restart (mapeo de puertos)
❌ HOST         → Necesita restart (binding)
```

**Razón técnica:**
- El `PORT` afecta el mapeo de puertos en Docker (necesita restart)
- Las variables de configuración de la app (config.py) se re-leen en cada request

---

## 🚀 Cómo Usar el Volumen Compartido

### Caso 1: Cambiar Configuración de la App (sin restart)

```bash
# 1. En Ubuntu, editar .env
nano .env
# Cambiar: LOG_LEVEL=DEBUG
# O: CONFIDENCE_THRESHOLD=0.8

# 2. El contenedor verá el cambio automáticamente
# No necesitas restart porque Settings re-lee .env en cada petición

# 3. Verificar cambio (opcional)
docker logs -f waste-classifier-api | grep "THRESHOLD"
```

### Caso 2: Cambiar Puerto (necesita restart)

```bash
# 1. En Ubuntu, editar .env
nano .env
# Cambiar: PORT=9000

# 2. Necesitas reiniciar (el puerto se mapea al iniciar)
docker compose down
docker compose up -d

# 3. Acceder al nuevo puerto
curl http://localhost:9000/health
```

### Caso 3: Cambiar Modelo (sin restart)

```bash
# 1. Editar .env
nano .env
# Cambiar: MODEL_PATH=models/otro_modelo.h5

# 2. Copiar nuevo modelo al directorio
cp ~/mi_modelo.h5 models/otro_modelo.h5

# 3. El contenedor cargará el nuevo modelo
# No necesitas restart porque app.models.base_model re-lee en cada inference

# 4. Ver logs
docker logs -f waste-classifier-api
```

---

## 📋 Tabla de Cambios Dinámicos vs Requiere Restart

| Variable | Tipo | Requiere Restart | Cómo Funciona |
|----------|------|------------------|---------------|
| `PORT` | Docker | ✅ SÍ | Mapeo de puertos (build-time) |
| `HOST` | Docker | ✅ SÍ | Binding de red (build-time) |
| `LOG_LEVEL` | App | ❌ NO | Se re-lee en cada log |
| `LOG_DIR` | App | ❌ NO | Se re-lee en cada log |
| `CONFIDENCE_THRESHOLD` | App | ❌ NO | Se re-lee en cada prediction |
| `MODEL_PATH` | App | ❌ NO | Se re-lee en cada init |
| `CLASSES` | App | ❌ NO | Se re-lee en cada prediction |
| `MAX_FILE_SIZE` | App | ❌ NO | Se re-lee en cada request |
| `IMG_SIZE` | App | ❌ NO | Se re-lee en cada prediction |

---

## 🔒 Seguridad: Read-Only (`:ro`)

```yaml
volumes:
  - ./.env:/code/.env:ro    # ro = read-only
```

**Beneficios:**
- ✅ Contenedor NO puede modificar `.env` del host
- ✅ Protege el archivo de cambios accidentales
- ✅ Mejor seguridad en producción
- ✅ Solo lectura desde dentro del contenedor

**Si necesitaras escritura (no recomendado en producción):**
```yaml
volumes:
  - ./.env:/code/.env       # Sin `:ro` = read-write
```

---

## 📁 Estructura de Volúmenes Actual

```
HOST (Ubuntu)                    CONTAINER
├── .env                         ├── /code/.env (read-only)
├── app/                         ├── /code/app
├── models/                      ├── /code/models
├── logs/  ←────────────────────→ ├── /code/logs
└── compose.yml
```

**Flujo de cambios:**

1. **Cambias `.env` en host** → Contenedor ve el cambio automáticamente
2. **app/config.py re-lee** `.env` en cada request
3. **Settings actualiza** valores en memoria
4. **Próxima petición** usa nuevos valores

---

## 🛠️ Comandos Útiles con Volumen Compartido

### Ver qué tiene el contenedor

```bash
# Ver .env del contenedor
docker exec waste-classifier-api cat /code/.env

# Ver si es igual al host
diff .env <(docker exec waste-classifier-api cat /code/.env)
# Sin output = iguales ✅
```

### Cambiar y verificar cambio

```bash
# En host
nano .env
# Cambiar: CONFIDENCE_THRESHOLD=0.95

# Verificar en contenedor
docker exec waste-classifier-api grep CONFIDENCE .env
# Output: CONFIDENCE_THRESHOLD=0.95 ✅

# Verificar que la app lo usa
curl -X POST http://localhost:8000/predict \
  -F "image=@test.jpg" | jq .

# Los logs mostrarán el nuevo threshold
docker logs -f waste-classifier-api
```

### Resetear a defaults

```bash
# Si el contenedor está funcionando con configuración vieja
docker compose down
docker compose up -d

# Nuevamente lee .env fresco
```

---

## ⚡ Casos de Uso Reales

### Caso 1: Aumentar Confianza Dinámicamente

```bash
# 1. En producción, notás muchos falsos positivos
nano .env
# CONFIDENCE_THRESHOLD=0.9    # Más exigente

# 2. El cambio se aplica inmediatamente en siguientes predicciones
# NO necesitas downtime ni rebuild
```

### Caso 2: Cambiar a Modo Debug

```bash
# 1. Problema en producción
nano .env
# LOG_LEVEL=DEBUG

# 2. Inmediatamente ves logs detallados
docker logs -f waste-classifier-api

# 3. Cuando resuelves, vuelves a INFO
nano .env
# LOG_LEVEL=INFO
```

### Caso 3: Pruebas de Diferentes Modelos

```bash
# 1. Tienes multiple modelos entrenados
ls models/
# mobilenetv2_waste_v1.h5
# mobilenetv2_waste_v2.h5
# mobilenetv2_waste_v3.h5

# 2. Cambiar sin rebuild
nano .env
# MODEL_PATH=models/mobilenetv2_waste_v2.h5

# 3. Contenedor carga automáticamente
# No necesitas rebuild ni restart
```

---

## 🔄 Cuando SÍ Necesitas docker compose restart

```bash
# Si cambias variables que afectan Docker (no la app):
# - PORT
# - HOST
# - RESTART policy
# - Cualquier que afecte networking

nano .env
PORT=9000

docker compose down
docker compose up -d

# O más rápido:
docker compose restart
# Pero si cambió PORT, necesitas down/up
```

---

## 📊 Resumen: Volumen Compartido `.env`

✅ **Ventajas:**
- Cambios dinámicos en configuración de app
- Sin necesidad de rebuild
- Downtime mínimo
- Gestión flexible

❌ **Limitaciones:**
- Variables de Docker (PORT, HOST) requieren restart
- Solo lee-lectura en container (seguridad)
- Necesita .env.example para template

✅ **Best Practice:**
- Úsalo para configuración de app
- Usa restart/rebuild para cambios de Docker
- Mantén .env.example en Git (sin secretos)

---

## 📝 .env.example (Commit a Git)

```bash
# ✅ Esto SÍ va a Git
.env.example

# ❌ Esto NO va a Git
.env             # (privado, en .gitignore)
```

Asegúrate de que `.gitignore` tiene:
```
.env
.env.local
.env.*.local
!.env.example    # Excepto template
```

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
