# 🐛 Error en .env - Solución Encontrada

## El Problema

```
WARNING:dotenv.main:Python-dotenv could not parse statement starting at line 1
```

### Causa

Tu `.env` tenía contenido accidental que no debería estar ahí:

```bash
# ❌ INCORRECTO - Contiene prompt de shell
casa@casa:~/server-trash/clasifier-server$ cat .env
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
...
```

**Esto pasó porque:** Copiaste el output completo del comando `cat .env` (incluyendo el prompt) en lugar de solo el contenido.

---

## La Solución

### ✅ CORRECTO - Solo el contenido

```bash
# ==================== CONFIGURACIÓN DEL MODELO ====================
# Usa solo estos modelos disponibles:
# - models/mobilenetv2_waste.h5 (TensorFlow)
# - models/mobilenetv2_waste_best.h5 (TensorFlow)
# - models/mobilenetv2_waste_pytorch.pth (PyTorch)
# - models/mobilenetv2_waste_pytorch_best.pth (PyTorch)
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# IMG_SIZE y CLASSES están hardcodeadas en config.py
CONFIDENCE_THRESHOLD=0.7
MAX_FILE_SIZE=5000000

# ==================== CONFIGURACIÓN DE LOGGING ====================
LOG_LEVEL=INFO
LOG_DIR=logs
ENABLE_FILE_LOGGING=true
ENABLE_CONSOLE_LOGGING=true
LOG_PREDICTIONS=true

# ==================== CONFIGURACIÓN DEL SERVIDOR ====================
PORT=8000
HOST=0.0.0.0
```

**Archivo ahora limpio y funcional.** ✅

---

## Variables Inválidas en .env

También encontré otros problemas:

### ❌ No Funcionan

```env
IMG_SIZE=(224, 224)          # ❌ Tuplas no se pueden parsear desde .env
CLASSES=["plastico", ...]    # ❌ Listas no se pueden parsear desde .env
```

### ✅ Se Removieron

Estas variables están **hardcodeadas** en `app/config.py`:

```python
IMG_SIZE: Tuple[int, int] = (224, 224)
CLASSES: ClassVar[List[str]] = ["carton", "metal", "papel", "plastico", "trash", "vidrio"]
```

**Si necesitas cambiarlas:**
- Edita `app/config.py` directamente
- Reemplaza el modelo (que debe ser entrenado con esos parámetros)

---

## Variables Que Puedes Cambiar en .env

✅ **Changeable (10 variables):**
- `MODEL_PATH` - Ruta al modelo
- `CONFIDENCE_THRESHOLD` - Umbral de confianza (0.0-1.0)
- `MAX_FILE_SIZE` - Tamaño máximo en bytes
- `LOG_LEVEL` - DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_DIR` - Directorio de logs
- `ENABLE_FILE_LOGGING` - true/false
- `ENABLE_CONSOLE_LOGGING` - true/false
- `LOG_PREDICTIONS` - true/false
- `PORT` - Puerto del servidor (requiere restart)
- `HOST` - Host del servidor (requiere restart)

---

## Cómo Evitar Este Error en el Futuro

### ❌ MAL - Copiar el output completo

```bash
$ cat .env
casa@casa:~/server-trash/clasifier-server$ cat .env
MODEL_PATH=...
```

### ✅ BIEN - Copiar solo el contenido

```bash
MODEL_PATH=...
CONFIDENCE_THRESHOLD=0.7
...
```

---

## Verificación

```bash
# Comprobar que .env es válido
python -c "from app.config import settings; print(settings)"

# Output esperado:
# Config loaded successfully:
# PORT: 8000
# MODEL: models/mobilenetv2_waste_pytorch_best.pth
# LOG_LEVEL: INFO
```

---

## Documentación

Se creó `ENV_VARIABLES_GUIDE.md` con:
- Todas las variables que puedes cambiar
- Cuales requieren restart
- Formatos válidos e inválidos
- Ejemplos de configuración

---

**Última actualización:** 2025-12-14  
**Versión:** 1.0
