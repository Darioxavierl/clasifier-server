# Waste Classification API

API REST para clasificación de residuos usando MobileNetV2 con soporte dual para **PyTorch** y **TensorFlow**. Optimizado para GPU y diseñado para integración con dispositivos IoT como ESP32.

## Características

-  **Dual Framework**: Soporta modelos PyTorch (.pth) y TensorFlow (.h5)
-  **GPU Accelerated**: Entrenamiento 10x más rápido con NVIDIA CUDA
-  **Alta Precisión**: 91.88% de accuracy en clasificación de residuos
-  **6 Categorías**: carton, metal, papel, plastico, trash, vidrio
-  **IoT Ready**: Códigos numéricos para dispositivos ESP32
-  **Respuestas Detalladas**: Predicciones con confianza y alternativas
-  **Logging Completo**: Trazabilidad de requests y predicciones
-  **API Documentation**: Swagger UI en `/docs`

## Requisitos

### Hardware (Recomendado)
- GPU NVIDIA con CUDA Support (GTX 1660 SUPER o superior)
- Mínimo 2GB RAM libre
- 5GB espacio en disco

### Software
- Python 3.12+
- pip
- Git (opcional)

##  Instalación Rápida

### 1. Clonar Proyecto
```bash
git clone https://github.com/Darioxavierl/clasifier-server.git
cd Clasifier
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

#### Opción A: PyTorch (Recomendado para Windows con GPU)
```bash
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Opción B: TensorFlow (Para Linux/servidores)
```bash
pip install -r requirements.txt
pip install tensorflow[and-cuda]
```

### 4. Configuración
```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env si es necesario:
# MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth  # PyTorch
# O
# MODEL_PATH=models/mobilenetv2_waste.h5                # TensorFlow
```

##  Uso

### Iniciar API
```bash
python run.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Acceder a la API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Hacer Predicciones

#### Opción 1: Via Swagger UI
1. Abre http://localhost:8000/docs
2. Click en `POST /predict`
3. Click "Try it out"
4. Selecciona una imagen
5. Click "Execute"

#### Opción 2: Via Python
```python
import requests

with open('waste.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )
    print(response.json())
```

#### Opción 3: Via cURL
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@waste.jpg"
```

### Respuesta de Ejemplo
```json
{
  "code": 1,
  "class_name": "metal",
  "confidence": 0.9395,
  "is_confident": true,
  "description": "This image classified as metal",
  "alternative_classes": [
    {"class_name": "vidrio", "confidence": 0.0394}
  ],
  "requires_review": false,
  "special_handling": false
}
```

## Categorías de Clasificación

| Código | Categoría | Ejemplos |
|--------|-----------|----------|
| 0️⃣ | **carton** | Cajas de cartón, empaques de papel |
| 1️⃣ | **metal** | Latas, aluminio, contenedores metálicos |
| 2️⃣ | **papel** | Periódicos, documentos, papel |
| 3️⃣ | **plastico** | Botellas, bolsas, recipientes plásticos |
| 4️⃣ | **trash** | Basura mixta, materiales generales |
| 5️⃣ | **vidrio** | Botellas de vidrio, frascos, vidrio |

## 🔧 Seleccionar Framework

### Usar PyTorch (Recomendado para Windows)

**Ventajas:**
-  Detección automática de GPU en Windows
-  Mejor soporte comunitario
-  Más rápido en entrenamiento

**Pasos:**
```bash
# 1. Editar .env
# Cambiar:
# MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# 2. Instalar PyTorch con CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Iniciar API
python run.py

# 4. Verificar en logs: "Framework: pytorch"
```

### Usar TensorFlow (Para Linux/Servidores)

**Ventajas:**
-  Mejor optimización para servidores
-  Compatible con TPU
-  Modelos más pequeños

**Pasos:**
```bash
# 1. Editar .env
# Cambiar:
# MODEL_PATH=models/mobilenetv2_waste.h5

# 2. Instalar TensorFlow con CUDA
pip install tensorflow[and-cuda]

# 3. Iniciar API
python run.py

# 4. Verificar en logs: "Framework: tensorflow"
```

### Auto-Detección

El API **detecta automáticamente** el framework basado en:
- **Extensión del archivo** (.pth → PyTorch, .h5 → TensorFlow)
- **Disponibilidad de librerías** (cae al framework disponible)

No necesitas cambiar código, solo cambiar `MODEL_PATH` en `.env`.

##  Pruebas

### Test Local (Sin servidor)
Prueba el clasificador directamente sin iniciar API:
```bash
python tests/test_prediction.py
```

**Output esperado:**
```
 Classifier initialized
 Prediction successful
 VALIDATION SUCCESSFUL
```

### Test API Completo
Inicia API, hace predicciones, verifica respuestas:
```bash
python tests/test_api.py
```

**Output esperado:**
```
 API responding
 /predict endpoint working
 Stopping server...
 API TEST PASSED
```

### Test Comprehensive
Suite completa: conexión, predicción, health check:
```bash
python tests/test_comprehensive.py
```

**Output esperado:**
```
[1/3] Testing connection...
[2/3] Testing /predict endpoint...
[3/3] Testing /health endpoint...
RESULTS: 3/3 tests passed
```

##  Entrenar Modelo

### Preparar Dataset
```bash
# Capturar imágenes con webcam
cd training
python capture_dataset.py

# Analizar dataset
python analyze_dataset.py
```

### Entrenar con PyTorch (GPU)
```bash
# Rápido: 3-4 minutos
cd training
python train_waste_classifier_pytorch.py
```

**Output:**
```
✓ Detectadas 6 clases
✓ Accuracy: 91.88%
✓ Modelo guardado: mobilenetv2_waste_pytorch_best.pth
```

### Entrenar con TensorFlow
```bash
# Alternativo
cd training
python train_waste_classifier.py
```

##  Estructura de Proyecto

```
Clasifier/
├── app/
│   ├── main.py                      # Aplicación FastAPI
│   ├── config.py                    # Configuración
│   ├── api/
│   │   └── routes.py                # Endpoints /predict, /health
│   ├── models/
│   │   └── mobilenet_classifier.py  # Clasificador (dual framework)
│   ├── core/
│   │   ├── preprocessing.py
│   │   └── postprocessing.py
│   └── schemas/
│       └── prediction.py            # Modelos de respuesta
│
├── models/
│   ├── mobilenetv2_waste_pytorch_best.pth  # Modelo PyTorch ✅
│   └── mobilenetv2_waste.h5                # Modelo TensorFlow (opcional)
│
├── training/
│   ├── train_waste_classifier_pytorch.py   # Entrenar con PyTorch
│   ├── train_waste_classifier.py           # Entrenar con TensorFlow
│   ├── capture_dataset.py                  # Capturar imágenes
│   ├── analyze_dataset.py                  # Analizar dataset
│   └── data/
│       ├── carton/
│       ├── metal/
│       ├── papel/
│       ├── plastico/
│       ├── trash/
│       └── vidrio/
│
├── tests/
│   ├── test_prediction.py           # Test clasificador local
│   ├── test_api.py                  # Test endpoints API
│   └── test_comprehensive.py        # Suite completa
│
├── run.py                           # Script para iniciar API
├── .env                             # Configuración
└── requirements.txt                 # Dependencias
```

##  Configuración (.env)

```env
# Nivel de logging: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=DEBUG

# Ruta del modelo
# PyTorch:     models/mobilenetv2_waste_pytorch_best.pth
# TensorFlow:  models/mobilenetv2_waste.h5
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth

# Umbral de confianza para clasificación "confiable"
CONFIDENCE_THRESHOLD=0.7

# Tamaño máximo de archivo en bytes
MAX_FILE_SIZE=5000000

# Habilitar logging de predicciones
LOG_PREDICTIONS=true
```

##  Docker

### Compilar Imagen
```bash
docker build -t waste-classifier:latest .
```

### Ejecutar Contenedor
```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  waste-classifier:latest
```

### Docker Compose
```bash
docker-compose up -d
```

##  Rendimiento

| Métrica | PyTorch | TensorFlow |
|---------|---------|-----------|
| **Precisión** | 91.88% | ~91% |
| **Tiempo Inferencia** | 100-200ms | 150-250ms |
| **Tamaño Modelo** | 13 MB | 15 MB |
| **Entrenamiento (GPU)** | 3-4 min  | 5-6 min |
| **Entrenamiento (CPU)** | 30+ min | 35+ min |

## 🔍 Troubleshooting

### El API no inicia
```bash
# Verificar si el puerto 8000 está en uso
netstat -ano | findstr :8000

# Usar puerto diferente
python -m uvicorn app.main:app --port 8001
```

### GPU no se detecta
```bash
# PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# TensorFlow
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### Errores de modelo
```bash
# Verificar archivo existe
ls models/*.pth models/*.h5

# Probar carga
python tests/test_prediction.py
```

### Out of Memory
```bash
# El código automáticamente cae a CPU si es necesario
# Puedes forzar CPU editando app/models/mobilenet_classifier.py
```

##  Endpoints

### POST `/predict`
Hacer predicción en una imagen

**Request:**
```
Content-Type: multipart/form-data
file: <binary image>
```

**Response (200):**
```json
{
  "code": 1,
  "class_name": "metal",
  "confidence": 0.94,
  "is_confident": true,
  "description": "...",
  "alternative_classes": [
    {"class_name": "vidrio", "confidence": 0.04}
  ],
  "requires_review": false,
  "special_handling": false
}
```

**Response (400, 413, 500):**
```json
{"detail": "Error message"}
```

### GET `/health`
Verificar estado del API

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "logging": {
    "level": "DEBUG",
    "file_logging": true,
    "predictions_logged": true
  }
}
```

### GET `/docs`
Documentación interactiva (Swagger UI)

### GET `/redoc`
Documentación en formato ReDoc

##  Seguridad

-  Validación de tamaño de archivo
-  Validación de formato de imagen
-  CORS configurado
-  Logging de requests
-  Error handling robusto

##  Logging

Los logs se guardan en:
```
logs/
├── app.log          # Logs generales
└── predictions.log  # Registros de predicciones
```

Ver logs en tiempo real:
```bash
# Windows
Get-Content -Path logs/app.log -Tail 20 -Wait

# Linux
tail -f logs/app.log
```

##  Integración con ESP32

El API retorna códigos numéricos para fácil integración:

```cpp
// Ejemplo ESP32 en C++
HTTPClient http;
http.begin("http://192.168.1.100:8000/predict");

// Response JSON:
// {"code": 1, "class_name": "metal", "confidence": 0.94}

if (response.code == 1) {
    Serial.println("Metal");
} else if (response.code == 3) {
    Serial.println("Plastico");
}
```

##  Monitoreo

El sistema loguea automáticamente:
- Tiempo de procesamiento de cada imagen
- Confianza de predicciones
- Errores y excepciones

Ver analytics:
```bash
grep "confidence" logs/predictions.log | tail -10
```

##  Performance Tips

1. **GPU Acceleration**
   - Verificar logs para "cuda"
   - Típicamente 100-200ms por imagen

2. **Batch Processing**
   - Procesar secuencialmente
   - Considera pooling para red

3. **Image Preparation**
   - Tamaño: 224x224 (auto-redimensionado)
   - Formatos: JPG, PNG, BMP
   - Max: 5MB

##  Soporte

### Documentación en Proyecto
- Guías en `training/` directory
- Tests en `tests/` directory

### Problemas Comunes
- Ver sección **Troubleshooting**
- Ejecutar: `python tests/test_comprehensive.py`

##  Licencia

Este proyecto es parte del sistema de clasificación de residuos.

##  Autor

Desarrollado por el equipo de clasificación de residuos.

---

**Última Actualización**: Diciembre 14, 2025  
**Versión**: 1.0  
**Status**:  Production Ready
