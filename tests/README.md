# 🧪 Tests Documentation

Guía para ejecutar y entender los tests del proyecto.

## Overview

El proyecto incluye 3 levels de testing:

1. **test_prediction.py** - Prueba el clasificador localmente (sin API)
2. **test_api.py** - Prueba API con HTTP (simple)
3. **test_comprehensive.py** - Suite completa (todos los endpoints)

## Requisitos

- Entorno virtual activado: `.venv\Scripts\activate`
- Modelo entrenado: `models/mobilenetv2_waste_pytorch_best.pth` o `.h5`
- Configuración `.env` correcta

## Test 1: Predicción Local

Prueba el clasificador sin iniciar el servidor.

### Ejecutar
```bash
python tests/test_prediction.py
```

### Qué Verifica
- ✅ Clasificador se carga correctamente
- ✅ Framework se detecta (pytorch/tensorflow)
- ✅ GPU se detecta si disponible
- ✅ Predicciones se generan
- ✅ Formato de respuesta es válido
- ✅ Valores están en rangos correctos

### Output Esperado
```
✅ Classifier initialized
   Framework: pytorch
   Classes: 6

✅ Prediction successful
   class_id: 1
   class_name: metal
   confidence: 0.9551863670349121

✅ VALIDATION SUCCESSFUL
```

### Tiempo
- **PyTorch**: ~2 segundos
- **TensorFlow**: ~3 segundos

## Test 2: API Simple

Inicia API, hace una predicción, detiene servidor.

### Ejecutar
```bash
python tests/test_api.py
```

### Qué Verifica
- ✅ API inicia sin errores
- ✅ `/docs` endpoint responde
- ✅ `/predict` endpoint funciona
- ✅ Respuesta JSON válida
- ✅ Servidor se detiene correctamente

### Output Esperado
```
📡 Starting API server...

🧪 Testing connection...
✅ API responding (HTTP 200)

📸 Creating test image...

🚀 Testing /predict endpoint...
✅ Prediction successful (HTTP 200)
   Class: metal
   Confidence: 93.5%
   Code: 1

🛑 Stopping server...

✅ API TEST PASSED
```

### Tiempo
- **Total**: ~10 segundos (5s inicio + 3s predicción + 2s cierre)

## Test 3: Suite Completa

Prueba todos los endpoints (predcit, health, docs).

### Ejecutar
```bash
python tests/test_comprehensive.py
```

### Qué Verifica
- ✅ Conexión a API
- ✅ Endpoint `/predict`
- ✅ Endpoint `/health`
- ✅ Documentación disponible
- ✅ Todas las respuestas válidas

### Output Esperado
```
============================================================
COMPREHENSIVE API TEST
============================================================

[1/3] Testing connection...
✅ API responding (HTTP 200)

[2/3] Testing /predict endpoint...
✅ /predict endpoint working
   Class: metal
   Confidence: 93.5%

[3/3] Testing /health endpoint...
✅ /health endpoint working
   Status: healthy

============================================================
RESULTS: 3/3 tests passed
✅ Connection
✅ Prediction
✅ Health
```

### Tiempo
- **Total**: ~12 segundos

## Ejecutar Todos los Tests

```bash
# Script conveniente (si lo quieres crear)
python tests/test_prediction.py && python tests/test_api.py && python tests/test_comprehensive.py
```

O uno por uno:

```bash
echo "Testing prediction..."
python tests/test_prediction.py

echo "Testing API..."
python tests/test_api.py

echo "Testing comprehensive..."
python tests/test_comprehensive.py
```

## Cambiar entre Frameworks

Los tests automáticamente usan el framework especificado en `.env`:

### Para PyTorch
```bash
# En .env:
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# Ejecutar
python tests/test_prediction.py
```

### Para TensorFlow
```bash
# En .env:
MODEL_PATH=models/mobilenetv2_waste.h5

# Ejecutar
python tests/test_prediction.py
```

## Troubleshooting Tests

### "No module named 'app'"
```bash
# Asegúrate de ejecutar desde directorio raíz
cd D:\Proyectos\Clasifier
python tests/test_prediction.py
```

### "Connection refused"
```bash
# El puerto 8000 puede estar en uso
# Espera 5+ segundos entre tests
# O cambia puerto en app/config.py
```

### "Model not found"
```bash
# Verificar archivo existe
ls models/

# Verificar ruta en .env
cat .env | grep MODEL_PATH
```

### "GPU not available"
```bash
# Normal para TensorFlow
# PyTorch debería detectar GPU automáticamente
# Si no, revisar CUDA installation
```

## Agregar Tus Propios Tests

### Formato Simple
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.mobilenet_classifier import MobileNetClassifier
from app.config import settings

def test_mi_funcionalidad():
    classifier = MobileNetClassifier()
    classifier.load_model(settings.MODEL_PATH)
    
    # Tu código de test aquí
    
    return True  # O False si falla

if __name__ == "__main__":
    success = test_mi_funcionalidad()
    sys.exit(0 if success else 1)
```

## Verificación Rápida

Script para verificar setup completo:

```bash
python verify_setup.py
```

Esto verifica:
- ✅ Estructura del proyecto
- ✅ Archivos de modelo
- ✅ Configuración
- ✅ Dependencias
- ✅ GPU disponible

## Performance Esperado

| Test | PyTorch | TensorFlow | GPU | CPU |
|------|---------|-----------|-----|-----|
| Predicción | 100-200ms | 150-250ms | ⚡ Rápido | Lento |
| API Startup | 3-5s | 4-6s | ⚡ Rápido | Lento |
| Total Suite | 12-15s | 15-20s | ✅ | ⚠️ |

## CI/CD Integration

Para integración continua:

```bash
#!/bin/bash
set -e

echo "Running tests..."
python tests/test_prediction.py
python tests/test_api.py
python tests/test_comprehensive.py

echo "✅ All tests passed!"
```

## Debugging Tests

### Agregar logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Ver respuestas JSON completas
```python
import json
print(json.dumps(response.json(), indent=2))
```

### Inspeccionar modelo
```python
from app.models.mobilenet_classifier import MobileNetClassifier
classifier = MobileNetClassifier()
classifier.load_model(settings.MODEL_PATH)
print(f"Framework: {classifier.framework}")
print(f"Num Classes: {classifier.num_classes}")
```

---

**Nota**: Los tests son independientes y pueden ejecutarse en cualquier orden.
