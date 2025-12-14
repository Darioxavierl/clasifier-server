# ⚡ Quick Start - 5 Minutos

Guía mínima para empezar en 5 minutos.

## 1️⃣ Activar Entorno (30 seg)

```bash
.venv\Scripts\activate
```

## 2️⃣ Verificar Setup (30 seg)

```bash
python verify_setup.py
```

Busca:
```
✅ All checks passed!
```

## 3️⃣ Ejecutar Test Local (1 min)

```bash
python tests/test_prediction.py
```

Resultado esperado:
```
✅ VALIDATION SUCCESSFUL
```

## 4️⃣ Iniciar API (20 seg)

```bash
python run.py
```

Espera:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 5️⃣ Hacer Predicción (2 min)

Opción A - Web Browser (Recomendado):
1. Abre: http://localhost:8000/docs
2. Click `POST /predict`
3. Click "Try it out"
4. Selecciona una imagen JPG
5. Click "Execute"

Opción B - Python:
```python
import requests

with open('tu_imagen.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/predict',
        files={'file': f}
    )
    print(response.json())
```

Opción C - cURL:
```bash
curl -X POST http://localhost:8000/predict -F "file=@tu_imagen.jpg"
```

---

## Respuesta Esperada

```json
{
  "code": 1,
  "class_name": "metal",
  "confidence": 0.9395,
  "is_confident": true,
  "description": "This image classified as metal"
}
```

---

## 🔧 Cambiar Framework (1 min)

### Usar PyTorch (Default)
```bash
# .env ya apunta a PyTorch
python run.py
```

### Usar TensorFlow
```bash
# Editar .env:
# MODEL_PATH=models/mobilenetv2_waste.h5

python run.py
```

---

## ❓ Si Algo Falla

```bash
# Verificar setup
python verify_setup.py

# Ver logs detallados
tail -f logs/app.log

# Reiniciar API (Ctrl+C, luego)
python run.py
```

---

**¡Listo! Ya tienes la API corriendo 🚀**

Para más detalles: Ver `README.md`
