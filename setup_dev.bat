@echo off
REM Script de configuración rápida para desarrollo local (Windows)
REM Uso: setup_dev.bat

echo.
echo ==========================================
echo Configuracion de Desarrollo - Waste Classifier
echo ==========================================
echo.

REM Crear entorno virtual
echo 1. Creando entorno virtual...
python -m venv venv

REM Activar entorno
echo 2. Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 3. Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Crear modelo dummy
echo 4. Creando modelo dummy para pruebas...
python scripts\create_dummy_model.py

REM Crear imagen de prueba
echo 5. Creando imagen de prueba...
python scripts\create_test_image.py

REM Crear directorio de logs
echo 6. Creando directorio de logs...
if not exist logs mkdir logs

REM Validar proyecto
echo 7. Validando proyecto...
python validate.py

echo.
echo ==========================================
echo Configuracion completada!
echo ==========================================
echo.
echo Para iniciar el servidor:
echo   python run.py
echo.
echo Para probar los endpoints:
echo   python test_api.py
echo.
pause
