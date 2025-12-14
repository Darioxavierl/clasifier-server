#!/usr/bin/env python3
"""
Script de validación del proyecto Waste Classifier
Verifica que todos los componentes estén correctamente configurados
"""

import sys
from pathlib import Path
import importlib.util
from typing import Tuple, List

class Colors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    OKCYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def check_pass(msg):
    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {msg}")

def check_fail(msg):
    print(f"  {Colors.FAIL}✗{Colors.ENDC} {msg}")

def check_warn(msg):
    print(f"  {Colors.WARNING}⚠{Colors.ENDC} {msg}")

def check_python_version() -> bool:
    """Verificar versión de Python"""
    print_section("1. Verificación de Python")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        check_pass(f"Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        check_fail(f"Python 3.8+ requerido (tienes {version.major}.{version.minor})")
        return False

def check_dependencies() -> bool:
    """Verificar dependencias"""
    print_section("2. Verificación de Dependencias")
    
    required = [
        'fastapi',
        'uvicorn',
        'tensorflow',
        'numpy',
        'pydantic',
        'pydantic_settings',
        'cv2',
        'PIL'
    ]
    
    missing = []
    
    for pkg in required:
        try:
            if pkg == 'cv2':
                importlib.import_module('cv2')
                check_pass(f"{pkg} (opencv-python-headless)")
            elif pkg == 'PIL':
                importlib.import_module('PIL')
                check_pass(f"{pkg} (pillow)")
            else:
                importlib.import_module(pkg)
                check_pass(f"{pkg}")
        except ImportError:
            check_fail(f"{pkg} NO INSTALADO")
            missing.append(pkg)
    
    if missing:
        print(f"\n  Instala con: pip install {' '.join(missing)}")
        return False
    return True

def check_project_structure() -> bool:
    """Verificar estructura de directorios"""
    print_section("3. Verificación de Estructura de Proyecto")
    
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/schemas',
        'app/utils',
        'scripts',
    ]
    
    required_files = [
        'app/__init__.py',
        'app/config.py',
        'app/main.py',
        'app/api/__init__.py',
        'app/api/routes.py',
        'app/core/__init__.py',
        'app/core/preprocessing.py',
        'app/core/postprocessing.py',
        'app/models/__init__.py',
        'app/models/base_model.py',
        'app/models/mobilenet_classifier.py',
        'app/schemas/__init__.py',
        'app/schemas/prediction.py',
        'app/utils/__init__.py',
        'app/utils/logger.py',
        'requirements.txt',
        'run.py',
        'test_api.py',
        'README.md',
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            check_pass(f"Directorio: {dir_path}")
        else:
            check_fail(f"Directorio faltante: {dir_path}")
            all_ok = False
    
    print()
    
    for file_path in required_files:
        if Path(file_path).is_file():
            check_pass(f"Archivo: {file_path}")
        else:
            check_fail(f"Archivo faltante: {file_path}")
            all_ok = False
    
    return all_ok

def check_model_file() -> bool:
    """Verificar archivo del modelo"""
    print_section("4. Verificación de Modelo")
    
    model_path = Path('models/mobilenetv2_waste.h5')
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        check_pass(f"Modelo encontrado: {model_path}")
        check_pass(f"Tamaño: {size_mb:.2f} MB")
        return True
    else:
        check_warn(f"Modelo no encontrado: {model_path}")
        check_warn(f"Ejecuta: python scripts/create_dummy_model.py")
        return False

def check_configurations() -> bool:
    """Verificar archivos de configuración"""
    print_section("5. Verificación de Configuración")
    
    all_ok = True
    
    # Verificar config.py
    try:
        from app.config import settings
        check_pass("app/config.py carga correctamente")
        
        # Verificar variables críticas
        required_settings = [
            ('MODEL_PATH', str),
            ('IMG_SIZE', tuple),
            ('CONFIDENCE_THRESHOLD', float),
            ('CLASSES', list),
            ('LOG_LEVEL', str),
        ]
        
        for attr, expected_type in required_settings:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                if isinstance(value, expected_type):
                    check_pass(f"  {attr} = {value}")
                else:
                    check_fail(f"  {attr} tipo incorrecto (esperado {expected_type})")
                    all_ok = False
            else:
                check_fail(f"  Falta atributo: {attr}")
                all_ok = False
                
    except Exception as e:
        check_fail(f"Error cargando config: {str(e)}")
        all_ok = False
    
    # Verificar .env
    print()
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        check_pass(".env encontrado")
    else:
        if env_example.exists():
            check_warn(".env no encontrado, pero .env.example disponible")
            check_warn("Copia: cp .env.example .env")
        else:
            check_fail(".env.example no encontrado")
            all_ok = False
    
    return all_ok

def check_imports() -> bool:
    """Verificar que todos los imports funcionan"""
    print_section("6. Verificación de Imports")
    
    modules_to_check = [
        ('app.config', ['Settings', 'settings']),
        ('app.main', ['app']),
        ('app.api.routes', ['router']),
        ('app.core.preprocessing', ['decode_image', 'validate_image']),
        ('app.core.postprocessing', ['PostProcessor']),
        ('app.models.base_model', ['BaseClassifier']),
        ('app.models.mobilenet_classifier', ['MobileNetClassifier']),
        ('app.schemas.prediction', ['PredictionResponse', 'ESPResponse']),
        ('app.utils.logger', ['setup_logger', 'logger', 'LoggerContext']),
    ]
    
    all_ok = True
    
    for module_name, exports in modules_to_check:
        try:
            module = importlib.import_module(module_name)
            check_pass(f"Módulo: {module_name}")
            
            for export in exports:
                if hasattr(module, export):
                    check_pass(f"  ✓ {export}")
                else:
                    check_fail(f"  ✗ Falta: {export}")
                    all_ok = False
                    
        except ImportError as e:
            check_fail(f"Módulo: {module_name}")
            check_fail(f"  Error: {str(e)}")
            all_ok = False
        except Exception as e:
            check_fail(f"Módulo: {module_name}")
            check_fail(f"  Error: {str(e)}")
            all_ok = False
    
    return all_ok

def check_logs_dir() -> bool:
    """Verificar directorio de logs"""
    print_section("7. Verificación de Directorio de Logs")
    
    logs_dir = Path('logs')
    
    if logs_dir.exists():
        check_pass(f"Directorio 'logs' existe")
    else:
        try:
            logs_dir.mkdir(exist_ok=True)
            check_pass(f"Directorio 'logs' creado")
        except Exception as e:
            check_fail(f"No se pudo crear 'logs': {str(e)}")
            return False
    
    return True

def main():
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
    print("╔" + "="*58 + "╗")
    print("║" + "  VALIDACIÓN DE PROYECTO WASTE CLASSIFIER".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print(Colors.ENDC)
    
    checks = [
        ("Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Estructura", check_project_structure),
        ("Modelo", check_model_file),
        ("Configuración", check_configurations),
        ("Imports", check_imports),
        ("Logs", check_logs_dir),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            check_fail(f"Error en {check_name}: {str(e)}")
            results[check_name] = False
    
    # Resumen
    print_section("RESUMEN")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = f"{Colors.OKGREEN}PASÓ{Colors.ENDC}" if result else f"{Colors.FAIL}FALLÓ{Colors.ENDC}"
        symbol = "✓" if result else "✗"
        print(f"  {Colors.OKGREEN if result else Colors.FAIL}{symbol}{Colors.ENDC} {check_name:.<40} {status}")
    
    print(f"\n  {Colors.BOLD}Total: {passed}/{total} validaciones pasadas{Colors.ENDC}\n")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ Proyecto validado correctamente!{Colors.ENDC}\n")
        print("  Próximos pasos:")
        print("  1. python scripts/create_dummy_model.py  # Si aún no tienes modelo")
        print("  2. python run.py                         # Iniciar servidor")
        print("  3. python test_api.py                    # Probar endpoints")
        print()
        return 0
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ Hay problemas que necesitan solución{Colors.ENDC}\n")
        print("  Revisa los errores arriba y sigue las instrucciones")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
