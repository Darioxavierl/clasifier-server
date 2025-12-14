# ⚙️ Variables de Configuración - Qué Cambiar y Qué No

## 🟢 Variables que PUEDES cambiar en `.env`

### 1. **MODEL_PATH** ✅
```env
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
```

**Puedes cambiar a:**
```env
# TensorFlow models
MODEL_PATH=models/mobilenetv2_waste.h5
MODEL_PATH=models/mobilenetv2_waste_best.h5

# PyTorch models
MODEL_PATH=models/mobilenetv2_waste_pytorch.pth
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
```

**Efecto:** Inmediato (se recarga en siguiente predicción)

---

### 2. **CONFIDENCE_THRESHOLD** ✅
```env
CONFIDENCE_THRESHOLD=0.7
```

**Rango:** 0.0 - 1.0 (probabilidad)

**Ejemplos:**
```env
CONFIDENCE_THRESHOLD=0.5  # Más permisivo (más positivos)
CONFIDENCE_THRESHOLD=0.8  # Más exigente (menos positivos)
CONFIDENCE_THRESHOLD=0.95 # Muy exigente
```

**Efecto:** Inmediato (próxima predicción)

---

### 3. **MAX_FILE_SIZE** ✅
```env
MAX_FILE_SIZE=5000000  # 5MB en bytes
```

**Conversión:**
```env
# 1MB
MAX_FILE_SIZE=1000000

# 10MB
MAX_FILE_SIZE=10000000

# 50MB
MAX_FILE_SIZE=50000000
```

**Efecto:** Inmediato (próximo upload)

---

### 4. **LOG_LEVEL** ✅
```env
LOG_LEVEL=INFO
```

**Opciones:**
```env
LOG_LEVEL=DEBUG    # Máximo detalle (desarrollo)
LOG_LEVEL=INFO     # Información normal (recomendado)
LOG_LEVEL=WARNING  # Solo advertencias
LOG_LEVEL=ERROR    # Solo errores
LOG_LEVEL=CRITICAL # Solo críticos
```

**Efecto:** Inmediato (próximos logs)

---

### 5. **LOG_DIR** ✅
```env
LOG_DIR=logs
```

**Cambios válidos:**
```env
LOG_DIR=./logs
LOG_DIR=/var/log/myapp
LOG_DIR=/tmp/logs
```

**Efecto:** Inmediato (próximos logs van aquí)

---

### 6. **ENABLE_FILE_LOGGING** ✅
```env
ENABLE_FILE_LOGGING=true
```

**Opciones:**
```env
ENABLE_FILE_LOGGING=true   # Guardar logs en archivo
ENABLE_FILE_LOGGING=false  # No guardar (solo consola)
```

**Efecto:** Inmediato

---

### 7. **ENABLE_CONSOLE_LOGGING** ✅
```env
ENABLE_CONSOLE_LOGGING=true
```

**Opciones:**
```env
ENABLE_CONSOLE_LOGGING=true   # Mostrar en consola/docker logs
ENABLE_CONSOLE_LOGGING=false  # No mostrar en consola
```

**Efecto:** Inmediato

---

### 8. **LOG_PREDICTIONS** ✅
```env
LOG_PREDICTIONS=true
```

**Opciones:**
```env
LOG_PREDICTIONS=true   # Registrar cada predicción en logs
LOG_PREDICTIONS=false  # No registrar predicciones
```

**Efecto:** Inmediato

---

### 9. **PORT** ✅
```env
PORT=8000
```

**Cambios válidos:**
```env
PORT=8000    # Puertos altos (no privilegiados)
PORT=8080
PORT=8888
PORT=9000
PORT=3000
```

**Efecto:** Requiere `docker compose restart` o rebuild

---

### 10. **HOST** ✅
```env
HOST=0.0.0.0
```

**Opciones:**
```env
HOST=0.0.0.0      # Escuchar en todas las interfaces (recomendado)
HOST=127.0.0.1    # Solo localhost (desarrollo local)
HOST=192.168.1.10 # IP específica (si sabes lo que haces)
```

**Efecto:** Requiere `docker compose restart`

---

## 🔴 Variables que NO puedes cambiar en `.env`

### 1. **IMG_SIZE** ❌
```env
# ❌ NO FUNCIONA EN .env
IMG_SIZE=(224, 224)
```

**Razón:** Pydantic no puede parsear tuplas desde strings `.env`

**Solución:** Está hardcodeada en `app/config.py`
```python
IMG_SIZE: Tuple[int, int] = (224, 224)
```

**Si necesitas cambiarla:**
```bash
# Editar en código
nano app/config.py
# Cambiar: IMG_SIZE: Tuple[int, int] = (224, 224)
```

---

### 2. **CLASSES** ❌
```env
# ❌ NO FUNCIONA EN .env
CLASSES=["plastico", "papel", "vidrio", "metal", "organico"]
```

**Razón:** Pydantic ClassVar no se carga de `.env`

**Ubicación real:** `app/config.py`
```python
CLASSES: ClassVar[List[str]] = ["carton", "metal", "papel", "plastico", "trash", "vidrio"]
```

**Si necesitas cambiarlas:**
```bash
# Editar en código
nano app/config.py
# Buscar CLASSES y modificar la lista
```

---

## 📋 Tabla de Referencia Rápida

| Variable | Cambiar | Requiere Restart | En `.env` |
|----------|---------|------------------|-----------|
| `MODEL_PATH` | ✅ Sí | ❌ No | ✅ Sí |
| `CONFIDENCE_THRESHOLD` | ✅ Sí | ❌ No | ✅ Sí |
| `MAX_FILE_SIZE` | ✅ Sí | ❌ No | ✅ Sí |
| `LOG_LEVEL` | ✅ Sí | ❌ No | ✅ Sí |
| `LOG_DIR` | ✅ Sí | ❌ No | ✅ Sí |
| `ENABLE_FILE_LOGGING` | ✅ Sí | ❌ No | ✅ Sí |
| `ENABLE_CONSOLE_LOGGING` | ✅ Sí | ❌ No | ✅ Sí |
| `LOG_PREDICTIONS` | ✅ Sí | ❌ No | ✅ Sí |
| `PORT` | ✅ Sí | ✅ Sí | ✅ Sí |
| `HOST` | ✅ Sí | ✅ Sí | ✅ Sí |
| `IMG_SIZE` | ❌ No | N/A | ❌ No |
| `CLASSES` | ❌ No | N/A | ❌ No |

---

## 🚀 Ejemplos de Configuración Válida

### Configuración Mínima (defaults)
```env
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
CONFIDENCE_THRESHOLD=0.7
MAX_FILE_SIZE=5000000
LOG_LEVEL=INFO
LOG_DIR=logs
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
LOG_PREDICTIONS=true
PORT=8000
HOST=0.0.0.0
```

### Configuración Producción
```env
# Modelo más preciso
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
CONFIDENCE_THRESHOLD=0.85

# Logs mínimos (solo errores)
LOG_LEVEL=WARNING
ENABLE_CONSOLE_LOGGING=false
ENABLE_FILE_LOGGING=true

# Puerto personalizado
PORT=8080
HOST=0.0.0.0
```

### Configuración Desarrollo
```env
# Modelo más rápido
MODEL_PATH=models/mobilenetv2_waste_pytorch.pth
CONFIDENCE_THRESHOLD=0.5

# Logs detallados
LOG_LEVEL=DEBUG
LOG_PREDICTIONS=true
ENABLE_CONSOLE_LOGGING=true

# Puerto local
PORT=8000
HOST=127.0.0.1
```

---

## 🔧 Si Necesitas Cambiar IMG_SIZE o CLASSES

### Opción 1: Editar config.py

```bash
nano app/config.py
```

Busca:
```python
IMG_SIZE: Tuple[int, int] = (224, 224)
CLASSES: ClassVar[List[str]] = ["carton", "metal", "papel", "plastico", "trash", "vidrio"]
```

Modifica y guarda.

### Opción 2: Reentrenar Modelo

Si necesitas diferentes:
- **IMG_SIZE:** El modelo debe ser entrenado con ese tamaño
- **CLASSES:** El modelo debe ser entrenado con esas clases

Usa `scripts/train_waste_classifier_pytorch.py` o `scripts/train_waste_classifier_tf.py`

---

## ✅ Verificación en `.env`

```bash
# Verificar que .env sea válido
python -c "from app.config import settings; print(f'PORT: {settings.PORT}, MODEL: {settings.MODEL_PATH}')"

# Debería mostrar:
# PORT: 8000, MODEL: models/mobilenetv2_waste_pytorch_best.pth
```

---

## 📝 Formato Válido en `.env`

### ✅ VÁLIDO

```env
# Strings
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# Numbers
CONFIDENCE_THRESHOLD=0.7
MAX_FILE_SIZE=5000000
PORT=8000

# Booleans
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
LOG_PREDICTIONS=true

# Paths
LOG_DIR=logs
```

### ❌ INVÁLIDO

```env
# Tuplas
IMG_SIZE=(224, 224)

# Listas
CLASSES=["plastico", "papel"]

# JSON
CLASSES={"class1": "plastico"}
```

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
