# 🎓 Training - Entrenamiento de Modelos

Herramientas y scripts para entrenar modelos de clasificación de residuos con **PyTorch** o **TensorFlow**.

## 📚 Documentación Principal

👉 **LEE PRIMERO:** [`TRAINING_GUIDE.md`](TRAINING_GUIDE.md)

Guía completa con:
- ✅ Setup de dependencias
- ✅ Preparación de datos
- ✅ Entrenamiento paso a paso (PyTorch y TensorFlow)
- ✅ Troubleshooting y soluciones
- ✅ Mejoras avanzadas

## 🗂️ Scripts Disponibles

### 1. 📸 Capturar Imágenes
```bash
python capture_dataset.py
```
- Captura imágenes desde tu webcam
- Organiza por clase automáticamente
- Controles interactivos para ajustar brillo
- Genera dataset personalizado

### 2. 📊 Analizar Dataset
```bash
python analyze_dataset.py
```
- Valida integridad de imágenes
- Detecta imágenes corruptas
- Verifica balance de clases
- Proporciona recomendaciones

### 3. ⚡ Entrenar con PyTorch (Recomendado para Windows)
```bash
python train_waste_classifier_pytorch.py --data-dir data --epochs 10
```
**Características:**
- GPU CUDA optimizado
- 2 fases de entrenamiento
- Modelos rápidos (15-20 min)
- Accuracy ~91%

**Opciones:**
```
--data-dir    Directorio de datos (default: data)
--epochs      Número de épocas (default: 10)
--batch-size  Batch size (default: 32)
--lr          Learning rate (default: 0.001)
--output      Nombre del modelo (default: mobilenetv2_waste_pytorch.pth)
--unfreeze    Capas a descongelar (default: 50)
--num-workers Workers para data loading (default: 0)
```

### 4. 🔧 Entrenar con TensorFlow (Alternativa)
```bash
python train_waste_classifier.py --data-dir data --epochs 10
```
**Características:**
- Soporta GPU NVIDIA en Linux
- Early stopping integrado
- 2 fases de entrenamiento
- Accuracy ~89%

**Opciones:**
```
--data-dir    Directorio de datos (default: data)
--epochs      Número de épocas (default: 10)
--batch-size  Batch size (default: 32)
--lr          Learning rate (default: 0.001)
--output      Nombre del modelo (default: mobilenetv2_waste.h5)
--unfreeze    Capas a descongelar (default: 50)
```

### 5. 🎮 Verificar GPU
```bash
python check_gpu.py
```
- Verifica dispositivos disponibles
- Muestra GPU detectadas
- Valida funcionamiento CUDA
- Necesario antes de entrenar con GPU

## 🚀 Inicio Rápido

### Opción A: Capturar tus propias imágenes
```bash
# 1. Capturar imágenes desde cámara
python capture_dataset.py

# 2. Validar dataset
python analyze_dataset.py

# 3. Entrenar modelo
python train_waste_classifier_pytorch.py --epochs 10

# ✅ Modelo listo en: models/mobilenetv2_waste_pytorch_best.pth
```

### Opción B: Usar imágenes existentes
```bash
# 1. Colocar imágenes en data/ por clase
# data/
# ├── plastico/
# ├── papel/
# ├── vidrio/
# ├── metal/
# └── ...

# 2. Validar
python analyze_dataset.py

# 3. Entrenar
python train_waste_classifier_pytorch.py --epochs 10
```

## 📁 Estructura de Carpetas

```
training/
├── README.md                              # Este archivo
├── TRAINING_GUIDE.md                      # Guía completa ⭐
├── capture_dataset.py                     # Capturar imágenes
├── analyze_dataset.py                     # Analizar dataset
├── train_waste_classifier_pytorch.py      # Entrenar PyTorch ⭐
├── train_waste_classifier.py              # Entrenar TensorFlow
├── check_gpu.py                           # Verificar GPU
│
├── data/                                  # Datos (crearás tú)
│   ├── plastico/
│   ├── papel/
│   ├── vidrio/
│   ├── metal/
│   ├── carton/
│   └── trash/
│
└── models/                                # Modelos (se crean aquí)
    ├── mobilenetv2_waste_pytorch_best.pth
    └── mobilenetv2_waste_best.h5
```

## ⚡ Ejemplo de Entrenamiento Completo

```bash
# Paso 1: Capturar datos (~10 min)
python capture_dataset.py
# Selecciona cada clase y captura 100-150 imágenes

# Paso 2: Validar datos (1 min)
python analyze_dataset.py
# Verifica balance, cantidad y corrupción

# Paso 3: Verificar GPU (30 seg)
python check_gpu.py
# Asegúrate que CUDA está disponible

# Paso 4: Entrenar modelo (~15 min con GPU)
python train_waste_classifier_pytorch.py \
  --data-dir data \
  --epochs 20 \
  --batch-size 32 \
  --lr 0.001

# ✅ Listo! Tu modelo está en: models/
```

## 📊 Tiempo de Entrenamiento

| GPU | Tiempo | Accuracy |
|-----|--------|----------|
| NVIDIA GTX 1660 SUPER | 15-20 min | 88-91% |
| NVIDIA RTX 3060 | 8-12 min | 89-92% |
| NVIDIA RTX 4090 | 3-5 min | 90-93% |
| CPU Intel i7 | 45-60 min | 88-91% |

## 🔍 Requisitos

### PyTorch (Recomendado)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### TensorFlow
```bash
pip install tensorflow[and-cuda]
```

### Comunes
```bash
pip install opencv-python-headless numpy pillow
```

## 💡 Tips

- ✅ Usa **PyTorch** en Windows con GPU
- ✅ Captura imágenes en diferentes ángulos y luces
- ✅ Mantén datos balanceados (misma cantidad por clase)
- ✅ Usa `--num-workers 4` en sistemas multi-core para acelerar
- ❌ No uses caracteres especiales en nombres de clases

## 🐛 Problemas Comunes

**"CUDA out of memory"**
```bash
python train_waste_classifier_pytorch.py --batch-size 16
```

**"No module named torch"**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**"Dataset desbalanceado"**
```bash
python capture_dataset.py
# Captura más imágenes de la clase minoritaria
```

**Ver más:** Lee `TRAINING_GUIDE.md` sección Troubleshooting

## ✅ Checklist antes de Entrenar

- [ ] Instalé PyTorch o TensorFlow
- [ ] Verifiqué GPU con `check_gpu.py`
- [ ] Capturé imágenes en `data/`
- [ ] Validé con `analyze_dataset.py`
- [ ] Tengo 100+ imágenes por clase
- [ ] Dataset está balanceado

## 📞 Soporte

Para problemas:
1. Revisa `TRAINING_GUIDE.md`
2. Ejecuta `python check_gpu.py`
3. Ejecuta `python analyze_dataset.py`
4. Verifica versiones:
   ```bash
   python -c "import torch; print(torch.__version__)"
   python -c "import tensorflow; print(tensorflow.__version__)"
   ```

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2024
