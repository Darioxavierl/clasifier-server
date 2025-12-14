#!/bin/bash
# Script de configuración rápida para desarrollo local
# Uso: bash setup_dev.sh (Linux/Mac) o ejecutar comandos manualmente en Windows

echo "=========================================="
echo "Configuración de Desarrollo - Waste Classifier"
echo "=========================================="
echo ""

# Crear entorno virtual
echo "1. Creando entorno virtual..."
python -m venv venv

# Activar entorno
echo "2. Activando entorno virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Instalar dependencias
echo "3. Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear modelo dummy
echo "4. Creando modelo dummy para pruebas..."
python scripts/create_dummy_model.py

# Crear imagen de prueba
echo "5. Creando imagen de prueba..."
python scripts/create_test_image.py

# Crear directorio de logs
echo "6. Creando directorio de logs..."
mkdir -p logs

# Validar proyecto
echo "7. Validando proyecto..."
python validate.py

echo ""
echo "=========================================="
echo "✓ Configuración completada!"
echo "=========================================="
echo ""
echo "Para iniciar el servidor:"
echo "  python run.py"
echo ""
echo "Para probar los endpoints:"
echo "  python test_api.py"
echo ""
