# scripts/create_test_image.py
import numpy as np
from PIL import Image

# Crear imagen de prueba 300x300 con ruido aleatorio
img_array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
img.save("test_image.jpg")
print("✅ Imagen de prueba creada: test_image.jpg")