#!/usr/bin/env python3
"""
Script para verificar si TensorFlow está usando GPU o CPU
"""

import tensorflow as tf
import sys

print("\n" + "="*60)
print("VERIFICACIÓN DE DISPOSITIVO")
print("="*60)

# 1. Listar dispositivos disponibles
print("\n📱 DISPOSITIVOS DISPONIBLES:")
devices = tf.config.list_physical_devices()
for device in devices:
    print(f"  - {device}")

# 2. Verificar GPUs específicamente
print("\n🎮 GPUs DETECTADAS:")
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"  ✓ {len(gpus)} GPU(s) disponible(s)")
    for gpu in gpus:
        print(f"    - {gpu}")
else:
    print("  ❌ Sin GPUs disponibles")

# 3. Verificar CPUs
print("\n💻 CPUs DETECTADAS:")
cpus = tf.config.list_physical_devices('CPU')
if cpus:
    print(f"  ✓ {len(cpus)} CPU(s) disponible(s)")
    for cpu in cpus:
        print(f"    - {cpu}")
else:
    print("  ❌ Sin CPUs detectadas")

# 4. Verificar cuál está usando TensorFlow
print("\n🔍 DISPOSITIVO ACTUAL DE TensorFlow:")
print(f"  Default: {tf.config.list_logical_devices()}")

# 5. Test simple para ver dónde corre
print("\n⚡ TEST: Crear tensor y ver dónde se procesa:")
try:
    with tf.device('/GPU:0'):
        a = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        b = tf.constant([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        c = tf.matmul(a, b)
        print(f"  ✓ Operación ejecutada en GPU: {c.device}")
except RuntimeError as e:
    print(f"  ❌ No se puede usar GPU: {e}")
    print(f"  ✓ Fallback a CPU")

# 6. Información detallada
print("\n📊 INFORMACIÓN DETALLADA:")
print(f"  TensorFlow version: {tf.__version__}")
print(f"  CUDA disponible: {tf.test.is_built_with_cuda()}")
print(f"  cuDNN disponible: {tf.test.is_built_with_gpu_support()}")

print("\n" + "="*60)

# 7. Recomendación
if gpus:
    print("✅ GPU DISPONIBLE - El entrenamiento usará GPU")
    print("   (Mucho más rápido: ~10x más veloz que CPU)")
else:
    print("⚠️  GPU NO DISPONIBLE - Se usará CPU")
    print("   (Más lento pero funcional)")
    print("\n   Para usar GPU necesitas:")
    print("   - NVIDIA GPU (RTX, GTX, Tesla, etc)")
    print("   - NVIDIA CUDA Toolkit")
    print("   - cuDNN library")

print("="*60 + "\n")
