# scripts/create_dummy_model.py
import tensorflow as tf
from pathlib import Path

# Crear directorio
Path("models").mkdir(exist_ok=True)

# Crear modelo dummy simple
model = tf.keras.Sequential([
    tf.keras.layers.InputLayer(input_shape=(224, 224, 3)),
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(5, activation='softmax')  # 5 clases
])

# Guardar
model.save("models/mobilenetv2_waste.h5")
print("Modelo dummy creado en models/mobilenetv2_waste.h5")