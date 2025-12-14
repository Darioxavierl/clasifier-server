# 🔄 Framework Switching Guide

Guía rápida para cambiar entre PyTorch y TensorFlow.

## Vista Rápida

| Aspecto | PyTorch | TensorFlow |
|---------|---------|-----------|
| **Archivo** | `.pth` | `.h5` |
| **SO Ideal** | Windows/Linux | Linux/Servidores |
| **GPU** | ⚡ Rápido en Windows | Más estable en Linux |
| **Instalación** | Fácil | Requiere CUDA completo |
| **Velocidad** | 3-4 min entrenamiento | 5-6 min entrenamiento |
| **Comunidad** | Muy activa | Estable |

## Cambiar a PyTorch

### 1. Editar `.env`
```env
MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
```

### 2. Instalar PyTorch
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. Iniciar API
```bash
python run.py
```

### 4. Verificar
Buscar en logs:
```
Framework: pytorch
Usando dispositivo: cuda  # O cpu si no hay GPU
```

## Cambiar a TensorFlow

### 1. Editar `.env`
```env
MODEL_PATH=models/mobilenetv2_waste.h5
```

### 2. Instalar TensorFlow
```bash
# Opción A: Con CUDA (recomendado para GPU)
pip install tensorflow[and-cuda]

# Opción B: CPU only
pip install tensorflow
```

### 3. Iniciar API
```bash
python run.py
```

### 4. Verificar
Buscar en logs:
```
Framework: tensorflow
Modelo TensorFlow cargado
```

## Entrenar Nuevo Modelo

### Con PyTorch
```bash
cd training
python train_waste_classifier_pytorch.py

# Output: mobilenetv2_waste_pytorch_best.pth
# Actualizar .env con nueva ruta
```

### Con TensorFlow
```bash
cd training
python train_waste_classifier.py

# Output: mobilenetv2_waste.h5
# Actualizar .env con nueva ruta
```

## Tests por Framework

### Probar PyTorch
```bash
# En .env: MODEL_PATH=models/mobilenetv2_waste_pytorch_best.pth
python tests/test_prediction.py
```

### Probar TensorFlow
```bash
# En .env: MODEL_PATH=models/mobilenetv2_waste.h5
python tests/test_prediction.py
```

## Archivos de Modelo

**Incluidos en el proyecto:**
- ✅ `models/mobilenetv2_waste_pytorch_best.pth` - PyTorch (13 MB)
- ✅ `models/mobilenetv2_waste.h5` - TensorFlow (15 MB)

Ambos tienen la misma arquitectura y precisión (~91.88%).

## Código: Auto-Detección

El API detecta automáticamente el framework:

```python
# En app/models/mobilenet_classifier.py
suffix = model_file.suffix.lower()

if suffix in ['.pth', '.pt']:
    self._load_pytorch_model(model_path)
elif suffix in ['.h5', '.keras']:
    self._load_tensorflow_model(model_path)
```

No necesitas cambiar código, solo cambiar `MODEL_PATH`.

## Compatibilidad

### Windows
- **Recomendado**: PyTorch ✅
- Funciona: TensorFlow (requiere CUDA completo)

### Linux
- **Recomendado**: TensorFlow ✅
- Funciona: PyTorch

### macOS
- **Recomendado**: TensorFlow (sin CUDA)
- PyTorch: Usar MPS (Metal Performance Shaders)

## GPU Detectada

### PyTorch
```python
import torch
print(torch.cuda.is_available())  # True/False
print(torch.cuda.get_device_name(0))  # GPU name
```

### TensorFlow
```python
import tensorflow as tf
devices = tf.config.list_physical_devices('GPU')
print(len(devices) > 0)  # True/False
```

## Solución de Problemas

### "Module not found: torch"
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "Module not found: tensorflow"
```bash
pip install tensorflow[and-cuda]
```

### GPU no se detecta
```bash
# Verificar CUDA
nvcc --version

# Reinstalar framework
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Model file not found
```bash
# Verificar ruta en .env
cat .env | grep MODEL_PATH

# Verificar archivo existe
ls models/
```

## Performance Esperado

### PyTorch (GPU GTX 1660)
- Inferencia: 100-200ms
- Entrenamiento: 3-4 min
- Memoria: ~2.5GB

### TensorFlow (GPU similar)
- Inferencia: 150-250ms  
- Entrenamiento: 5-6 min
- Memoria: ~3GB

---

**Nota**: Los modelos son intercambiables en respuesta, solo cambia el archivo de entrada.
