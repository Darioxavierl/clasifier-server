# 📚 Guía Completa de Entrenamiento - Clasificador de Residuos

Documentación completa para entrenar modelos de clasificación de residuos usando **PyTorch** o **TensorFlow**.

---

## 🎯 Tabla de Contenidos

1. [Prerequisitos](#-prerequisitos)
2. [Preparación de Datos](#-preparación-de-datos)
3. [Entrenamiento con PyTorch](#-entrenamiento-con-pytorch)
4. [Entrenamiento con TensorFlow](#-entrenamiento-con-tensorflow)
5. [Estructura de Datos Esperada](#-estructura-de-datos-esperada)
6. [Utilidades de Entrenamiento](#-utilidades-de-entrenamiento)
7. [Troubleshooting](#-troubleshooting)

---

## ✅ Prerequisitos

### Dependencias Requeridas

Según el framework que uses, instala las dependencias:

#### **Para PyTorch (GPU Recomendado)**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install opencv-python-headless numpy pillow tqdm
```

**Verificar instalación:**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'GPU: {torch.cuda.is_available()}')"
```

#### **Para TensorFlow (CPU o GPU)**
```bash
pip install tensorflow[and-cuda]
pip install opencv-python-headless numpy pillow
```

**Verificar instalación:**
```bash
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}'); print(f'GPUs: {len(tf.config.list_physical_devices(\"GPU\"))}')"
```

### Hardware Recomendado

| Framework | CPU Mínimo | GPU Recomendada | VRAM Mínima |
|-----------|-----------|-----------------|------------|
| **PyTorch** | Intel i5 / AMD Ryzen 5 | NVIDIA RTX 3060 | 6GB |
| **TensorFlow** | Intel i7 / AMD Ryzen 7 | NVIDIA RTX 3080 | 8GB |

---

## 🖼️ Preparación de Datos

### Opción 1: Capturar Imágenes con tu Cámara

```bash
python training/capture_dataset.py
```

**Controles:**
- **ESPACIO** - Capturar imagen
- **↑ / ↓** - Ajustar brillo
- **D** - Mostrar/ocultar información
- **Q** - Salir y siguiente clase

**Pasos:**
1. Selecciona clase (ej: "plastico")
2. Captura ~100-150 imágenes por clase
3. Varía ángulos, distancia y rotación
4. Repite para todas las clases

**Ejemplo:**
```bash
# Capturar imágenes de plástico
python training/capture_dataset.py
# Luego selecciona "plastico" y captura imágenes

# Luego papel
# Luego vidrio
# Etc...
```

### Opción 2: Usar Dataset Existente

Coloca tus imágenes en `training/data/` con estructura:
```
training/data/
├── plastico/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
├── papel/
├── vidrio/
├── metal/
├── carton/
└── trash/
```

### Validar Dataset

```bash
python training/analyze_dataset.py
```

**Salida esperada:**
```
📊 CONTEO DE IMÁGENES
- plastico................. 145 imágenes
- papel.................... 142 imágenes
- vidrio................... 148 imágenes
- metal.................... 146 imágenes
- carton................... 143 imágenes
- trash.................... 141 imágenes
------
TOTAL...................... 865 imágenes

⚖️ BALANCE DE CLASES
✓ Dataset está bien balanceado
✓ No hay imágenes corruptas
```

**Recomendaciones:**
- ✅ Mínimo 100 imágenes por clase
- ✅ Mínimo 500 imágenes totales
- ✅ Imágenes bien balanceadas
- ✅ Variación en ángulos y condiciones de luz

---

## ⚡ Entrenamiento con PyTorch

### Configuración Rápida

```bash
cd training
python train_waste_classifier_pytorch.py --data-dir data --epochs 10
```

### Opciones Disponibles

```bash
python train_waste_classifier_pytorch.py \
  --data-dir data \           # Directorio de datos (default: data)
  --epochs 10 \               # Número de épocas (default: 10)
  --batch-size 32 \           # Batch size (default: 32)
  --lr 0.001 \                # Learning rate (default: 0.001)
  --output mobilenetv2_waste_pytorch_best.pth \  # Nombre salida
  --unfreeze 50 \             # Capas a descongelar (default: 50)
  --num-workers 4             # Workers para data loading (default: 0)
```

### Proceso de Entrenamiento (2 Fases)

```
FASE 1: Entrenar custom head (30-50% de épocas)
├── Modelo base (MobileNetV2) CONGELADO
├── Solo entrena custom head (cabezal personalizado)
├── Learning rate: 1e-3 (alto)
└── Aproximadamente 3-5 minutos

FASE 2: Fine-tune del modelo base (50-70% de épocas)
├── Descongelan últimas 50 capas del modelo base
├── Todo el modelo se entrena
├── Learning rate: 1e-4 (bajo)
└── Aproximadamente 10-15 minutos
```

### Ejemplo Completo

```bash
# 1. Ir a carpeta training
cd training

# 2. Capturar/preparar datos
python capture_dataset.py
# O colocar datos en data/

# 3. Validar dataset
python analyze_dataset.py

# 4. Entrenar modelo
python train_waste_classifier_pytorch.py \
  --data-dir data \
  --epochs 20 \
  --batch-size 32 \
  --lr 0.001

# 5. Resultado final
# ✅ Modelo guardado: models/mobilenetv2_waste_pytorch.pth
# 🎯 Accuracy: 91.88%
```

### Monitoreo en Tiempo Real

Durante el entrenamiento verás:
```
Epoch [1/20] Train Loss: 0.8234, Acc: 72.45% | Val Loss: 0.5123, Acc: 85.32%
Epoch [2/20] Train Loss: 0.5123, Acc: 82.15% | Val Loss: 0.3456, Acc: 89.12%
Epoch [3/20] Train Loss: 0.3456, Acc: 89.67% | Val Loss: 0.2123, Acc: 91.88%
...
✅ Entrenamiento completado
📁 Modelo guardado: models/mobilenetv2_waste_pytorch_best.pth
🎯 Accuracy: 91.88%
```

### Parámetros Recomendados por Escenario

#### Dataset Pequeño (< 500 imágenes)
```bash
python train_waste_classifier_pytorch.py \
  --epochs 5 \
  --batch-size 16 \
  --lr 0.0005
```

#### Dataset Mediano (500-1000 imágenes)
```bash
python train_waste_classifier_pytorch.py \
  --epochs 10 \
  --batch-size 32 \
  --lr 0.001
```

#### Dataset Grande (> 1000 imágenes)
```bash
python train_waste_classifier_pytorch.py \
  --epochs 20 \
  --batch-size 64 \
  --lr 0.001 \
  --unfreeze 100
```

### Tiempo de Entrenamiento Estimado

| GPU | Batch=32 | Batch=64 |
|-----|----------|----------|
| NVIDIA GTX 1660 SUPER | 15-20 min | 12-18 min |
| NVIDIA RTX 3060 | 8-12 min | 6-10 min |
| NVIDIA RTX 4090 | 3-5 min | 2-4 min |
| CPU (Intel i7) | 45-60 min | 60-90 min |

---

## 🔧 Entrenamiento con TensorFlow

### Configuración Rápida

```bash
cd training
python train_waste_classifier.py --data-dir data --epochs 10
```

### Opciones Disponibles

```bash
python train_waste_classifier.py \
  --data-dir data \           # Directorio de datos (default: data)
  --epochs 10 \               # Número de épocas (default: 10)
  --batch-size 32 \           # Batch size (default: 32)
  --lr 0.001 \                # Learning rate (default: 0.001)
  --output mobilenetv2_waste.h5 \  # Nombre salida
  --unfreeze 50               # Capas a descongelar (default: 50)
```

### Proceso de Entrenamiento (2 Fases)

```
FASE 1: Entrenar custom head (30-50% de épocas)
├── Modelo base (MobileNetV2) CONGELADO
├── Solo entrena custom head
├── Learning rate: 1e-3 (alto)
└── Early stopping: sí (detiene si no mejora)

FASE 2: Fine-tune del modelo base (50-70% de épocas)
├── Descongelan últimas 50 capas
├── Todo el modelo se entrena
├── Learning rate: 1e-4 (bajo)
└── Aproximadamente 15-20 minutos
```

### Ejemplo Completo

```bash
# 1. Ir a carpeta training
cd training

# 2. Capturar/preparar datos
python capture_dataset.py
# O colocar datos en data/

# 3. Validar dataset
python analyze_dataset.py

# 4. Entrenar modelo
python train_waste_classifier.py \
  --data-dir data \
  --epochs 20 \
  --batch-size 32 \
  --lr 0.001

# 5. Resultado final
# ✅ Modelo guardado: models/mobilenetv2_waste_best.h5
# 🎯 Accuracy: 89.45%
```

### Monitoreo en Tiempo Real

Durante el entrenamiento verás:
```
Epoch 1/20
125/125 [==============================] - 45s 360ms/step - loss: 0.8234 - accuracy: 0.7245 - val_loss: 0.5123 - val_accuracy: 0.8532
Epoch 2/20
125/125 [==============================] - 42s 336ms/step - loss: 0.5123 - accuracy: 0.8215 - val_loss: 0.3456 - val_accuracy: 0.8912
...
✅ Entrenamiento completado
📁 Modelo guardado: models/mobilenetv2_waste_best.h5
🎯 Accuracy: 89.45%
```

### Parámetros Recomendados por Escenario

#### Dataset Pequeño (< 500 imágenes)
```bash
python train_waste_classifier.py \
  --epochs 5 \
  --batch-size 16 \
  --lr 0.0005
```

#### Dataset Mediano (500-1000 imágenes)
```bash
python train_waste_classifier.py \
  --epochs 10 \
  --batch-size 32 \
  --lr 0.001
```

#### Dataset Grande (> 1000 imágenes)
```bash
python train_waste_classifier.py \
  --epochs 20 \
  --batch-size 64 \
  --lr 0.001 \
  --unfreeze 100
```

### Tiempo de Entrenamiento Estimado

| GPU | Batch=32 | Batch=64 |
|-----|----------|----------|
| NVIDIA RTX 3080 | 20-25 min | 15-20 min |
| NVIDIA A100 | 8-10 min | 5-8 min |
| TPU v4 | 3-5 min | 2-3 min |
| CPU (Intel i7) | 60-90 min | 90-120 min |

---

## 📁 Estructura de Datos Esperada

### Estructura de Carpetas Requerida

```
training/
├── capture_dataset.py           # Script para capturar imágenes
├── analyze_dataset.py           # Análisis de dataset
├── train_waste_classifier_pytorch.py    # Entrenador PyTorch
├── train_waste_classifier.py            # Entrenador TensorFlow
├── check_gpu.py                 # Verificar GPU
│
├── data/                        # 📁 DATOS (creas tú)
│   ├── plastico/
│   │   ├── 000001.jpg
│   │   ├── 000002.jpg
│   │   └── ...
│   ├── papel/
│   │   ├── 000001.jpg
│   │   └── ...
│   ├── vidrio/
│   ├── metal/
│   ├── carton/
│   └── trash/
│
└── models/                      # 📁 MODELOS (se crean aquí)
    ├── mobilenetv2_waste_pytorch_best.pth
    ├── mobilenetv2_waste.h5
    └── ...
```

### Nombres de Clases Soportadas

El script detecta automáticamente las clases desde los directorios:

```
✅ Soportadas automáticamente:
  - plastico
  - papel
  - vidrio
  - metal
  - carton
  - organico
  - trash
  - (cualquier nombre de directorio)

❌ NO usar espacios ni caracteres especiales en nombres
```

---

## 🛠️ Utilidades de Entrenamiento

### 1. Verificar GPU

```bash
python training/check_gpu.py
```

**Salida esperada (PyTorch disponible):**
```
✓ 1 GPU(s) disponible(s)
  - /physical_device:GPU:0 (NVIDIA GeForce GTX 1660 SUPER)
✓ GPU detectada para TensorFlow
```

### 2. Analizar Dataset

```bash
python training/analyze_dataset.py --data-dir data
```

**Información que proporciona:**
- Cantidad de imágenes por clase
- Tamaños de imágenes
- Imágenes corruptas (si las hay)
- Balance de clases
- Recomendaciones

### 3. Capturar Imágenes

```bash
python training/capture_dataset.py --output-dir data
```

**Ejemplo interactivo:**
```
CAPTURANDO: PLASTICO
Directorio: data/plastico
Imágenes existentes: 0
Target: 100 imágenes

CONTROLES:
  ESPACIO  - Capturar imagen
  ↑↓       - Ajustar brillo
  D        - Mostrar/ocultar info
  Q        - Salir

✓ Cámara iniciada
Capturadas: 1/100 | Brillo: 0
Capturadas: 2/100 | Brillo: 0
...
✅ Completado: 100/100 imágenes
```

---

## 📊 Comparación de Frameworks

| Aspecto | PyTorch | TensorFlow |
|--------|---------|-----------|
| **Velocidad (GPU)** | 🟢 Rápido | 🟡 Medio |
| **Velocidad (CPU)** | 🟡 Medio | 🔴 Lento |
| **Curva de aprendizaje** | 🟢 Fácil | 🟡 Medio |
| **GPU Support Windows** | 🟢 Excelente | 🔴 Limitado |
| **GPU Support Linux** | 🟢 Excelente | 🟢 Excelente |
| **Tamaño modelo** | 🟢 Pequeño (~13MB) | 🟡 Medio (~30MB) |
| **Memoria RAM** | 🟢 Poco | 🟡 Más |
| **Facilidad debugar** | 🟢 Muy fácil | 🟡 Medio |
| **Producción** | 🟢 Excelente | 🟢 Excelente |

**Recomendación:**
- 🎯 **Windows + GPU** → PyTorch ⭐
- 🎯 **Linux + GPU** → TensorFlow o PyTorch
- 🎯 **CPU only** → PyTorch (más rápido)

---

## 🔍 Resultados y Evaluación

### Métricas Esperadas

**Después de entrenamiento completo (20 épocas):**

| Framework | Accuracy | Loss | Tiempo |
|-----------|----------|------|--------|
| PyTorch | 88-93% | 0.15-0.25 | 15-20 min |
| TensorFlow | 85-91% | 0.18-0.30 | 20-25 min |

### Interpretación de Resultados

```
✅ EXCELENTE (>90% accuracy)
├── Modelo listo para producción
├── Mínimo overfitting detectado
└── Usar para aplicaciones críticas

⚠️ BUENO (85-90% accuracy)
├── Aceptable para mayoría de casos
├── Posible overfitting moderado
└── Considera recolectar más datos si es crítico

⚠️ REGULAR (80-85% accuracy)
├── Necesita mejora
├── Probable bajo balance de datos
└── Captura más imágenes por clase

🔴 MALO (<80% accuracy)
├── Revisar calidad de datos
├── Dataset muy pequeño
├── Aumentar épocas de entrenamiento
└── Usar diferentes parámetros
```

---

## 🚀 Integración en la Aplicación

Después de entrenar, integra el modelo en FastAPI:

### 1. Actualizar Configuración

Edita `.env`:
```env
# Para PyTorch
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
MODEL_FRAMEWORK=pytorch

# O para TensorFlow
MODEL_PATH=models/mobilenetv2_waste.h5
MODEL_FRAMEWORK=tensorflow
```

### 2. Iniciar API

```bash
cd .. && python run.py
```

### 3. Probar Predicción

```bash
# En otra terminal
curl -X POST "http://localhost:8000/predict" \
  -F "file=@test_image.jpg"
```

---

## 🐛 Troubleshooting

### PyTorch - Errores Comunes

#### Error: "CUDA out of memory"
```bash
# Reducir batch size
python train_waste_classifier_pytorch.py --batch-size 16

# O usar CPU
export CUDA_VISIBLE_DEVICES=''  # Windows: set CUDA_VISIBLE_DEVICES=
python train_waste_classifier_pytorch.py
```

#### Error: "No CUDA devices available"
```bash
# Verificar instalación CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### Error: "No module named torch"
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### TensorFlow - Errores Comunes

#### Error: "CUDA out of memory"
```bash
# Reduce batch size
python train_waste_classifier.py --batch-size 16

# O limitador de memoria GPU
export TF_FORCE_GPU_ALLOW_GROWTH=true
python train_waste_classifier.py
```

#### Error: "Could not load dynamic library 'nvcuda.dll'"
Instala NVIDIA CUDA Toolkit desde: https://developer.nvidia.com/cuda-downloads

#### Error: "No module named tensorflow"
```bash
pip install tensorflow[and-cuda]
```

### Problemas de Datos

#### Error: "No subdirectories of classes"
```bash
# Estructura incorrecta. Debe ser:
training/data/
├── plastico/
├── papel/
└── ...

# NO:
training/data/
└── todas_mis_fotos.jpg
```

#### Advertencia: "Dataset está desbalanceado"
```bash
# Captura más imágenes de clases minoritarias
python capture_dataset.py
# Luego selecciona la clase con menos imágenes
```

### Lentitud General

#### El entrenamiento es muy lento (>2 min/época)
```bash
# 1. Verificar GPU
python training/check_gpu.py

# 2. Aumentar workers si usas PyTorch
python train_waste_classifier_pytorch.py --num-workers 4

# 3. Aumentar batch size (si memoria lo permite)
python train_waste_classifier_pytorch.py --batch-size 64

# 4. Usar CPU en lugar de GPU (para comparar)
export CUDA_VISIBLE_DEVICES=''
python train_waste_classifier_pytorch.py
```

---

## 📈 Mejoras Avanzadas

### Aumentar Accuracy Existente

1. **Capturar más datos**
   ```bash
   python capture_dataset.py
   # +200 imágenes adicionales
   ```

2. **Data Augmentation más agresivo**
   - Editar `train_waste_classifier_pytorch.py` línea ~155
   - Aumentar `RandomRotation`, `RandomAffine`, etc.

3. **Fine-tuning más agresivo**
   ```bash
   python train_waste_classifier_pytorch.py \
     --epochs 30 \
     --unfreeze 100 \
     --lr 0.0005
   ```

4. **Usar modelo más grande**
   - Editar script para usar `ResNet50` en lugar de `MobileNetV2`

### Transfer Learning con Datos Externos

Si tienes un dataset pequeño, usar un modelo preentrenado mejor:

```python
# En train_waste_classifier_pytorch.py
# Cambiar línea ~50
base_model = models.resnet50(pretrained=True)  # Más preciso
# base_model = models.mobilenet_v2(pretrained=True)  # Más rápido
```

---

## ✅ Checklist Final

Antes de usar el modelo en producción:

- [ ] Dataset tiene 100+ imágenes por clase
- [ ] Dataset está bien balanceado
- [ ] Accuracy > 85% en validación
- [ ] Loss < 0.5
- [ ] Modelo guardado correctamente
- [ ] Modelo cargado correctamente en app
- [ ] API responde correctamente
- [ ] Test de predicción exitoso

---

## 📞 Soporte

Para problemas:

1. Revisa logs en `logs/` si existen
2. Ejecuta `python training/check_gpu.py`
3. Ejecuta `python training/analyze_dataset.py`
4. Prueba con dataset pequeño primero
5. Revisa versiones de dependencias

```bash
# Ver versiones instaladas
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import tensorflow; print(f'TensorFlow: {tensorflow.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
```

---

**Última actualización:** Diciembre 2024  
**Versión:** 1.0
