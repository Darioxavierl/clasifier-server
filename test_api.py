#!/usr/bin/env python3
"""
Script para probar los endpoints de la API de Waste Classifier
Simula requests que vendría un ESP32 o cliente similar
"""

import requests
import json
from pathlib import Path
import argparse
from typing import Optional
import time

# Configurar colors para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_response(response):
    """Imprime la respuesta de forma legible"""
    print(f"\n{Colors.OKBLUE}Status Code: {response.status_code}{Colors.ENDC}")
    
    try:
        data = response.json()
        print(f"\n{Colors.BOLD}Response JSON:{Colors.ENDC}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f"\n{Colors.BOLD}Response Text:{Colors.ENDC}")
        print(response.text)

def test_health_check(base_url: str) -> bool:
    """
    Prueba el endpoint de health check
    """
    print_header("PRUEBA 1: Health Check")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            print_success("Health check exitoso")
            return True
        else:
            print_error(f"Health check falló con status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al servidor. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_root(base_url: str) -> bool:
    """
    Prueba el endpoint raíz
    """
    print_header("PRUEBA 2: Endpoint Raíz")
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            print_success("Endpoint raíz respondiendo")
            return True
        else:
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_predict(base_url: str, image_path: Optional[str] = None) -> bool:
    """
    Prueba el endpoint de predicción con una imagen
    """
    print_header("PRUEBA 3: Predicción con Imagen")
    
    # Crear imagen de prueba si no existe
    if image_path is None:
        image_path = "test_image.jpg"
    
    image_file = Path(image_path)
    
    if not image_file.exists():
        print_warning(f"Archivo {image_path} no encontrado")
        print_info(f"Creando imagen de prueba...")
        
        try:
            import numpy as np
            from PIL import Image
            
            # Crear imagen aleatoria
            img_array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(image_path)
            print_success(f"Imagen de prueba creada: {image_path}")
            
        except ImportError:
            print_error("Se necesita PIL/Pillow y numpy para crear la imagen")
            print_info("Instala con: pip install pillow numpy")
            return False
        except Exception as e:
            print_error(f"Error creando imagen: {str(e)}")
            return False
    
    # Enviar predicción
    try:
        with open(image_file, 'rb') as f:
            files = {'file': f}
            
            print_info(f"Enviando imagen: {image_path}")
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/predict",
                files=files,
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            print_response(response)
            print_info(f"Tiempo de procesamiento: {elapsed:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Predicción exitosa: {data.get('class_name', 'N/A')}")
                print_info(f"Código para ESP32: {data.get('code', 'N/A')}")
                print_info(f"Confianza: {data.get('confidence', 'N/A')}")
                return True
            else:
                return False
                
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_invalid_request(base_url: str) -> bool:
    """
    Prueba manejo de errores con request inválido
    """
    print_header("PRUEBA 4: Manejo de Errores (Archivo Inválido)")
    
    try:
        files = {'file': ('invalid.jpg', b'not a real image')}
        response = requests.post(
            f"{base_url}/predict",
            files=files,
            timeout=5
        )
        
        print_response(response)
        
        if response.status_code >= 400:
            print_success("Servidor rechaza archivos inválidos correctamente")
            return True
        else:
            print_warning("Servidor aceptó archivo inválido (comportamiento inesperado)")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_multiple_predictions(base_url: str, count: int = 3) -> bool:
    """
    Prueba múltiples predicciones para verificar estabilidad
    """
    print_header(f"PRUEBA 5: {count} Predicciones Consecutivas")
    
    image_path = "test_image.jpg"
    image_file = Path(image_path)
    
    if not image_file.exists():
        print_info("Creando imagen de prueba...")
        try:
            import numpy as np
            from PIL import Image
            
            img_array = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(image_path)
            
        except Exception as e:
            print_error(f"Error creando imagen: {str(e)}")
            return False
    
    success_count = 0
    total_time = 0
    
    try:
        for i in range(count):
            with open(image_file, 'rb') as f:
                files = {'file': f}
                print_info(f"Predicción {i+1}/{count}...", end=" ")
                
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/predict",
                    files=files,
                    timeout=30
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"{data.get('class_name')} ({elapsed:.2f}s)")
                    success_count += 1
                    total_time += elapsed
                else:
                    print_error(f"Status {response.status_code}")
        
        if success_count == count:
            print_success(f"\n✓ Todas {count} predicciones exitosas")
            print_info(f"Tiempo promedio: {total_time/count:.2f}s")
            return True
        else:
            print_error(f"\n✗ Solo {success_count}/{count} predicciones exitosas")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(
        description="Probar API de Waste Classifier"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="URL base de la API (default: http://127.0.0.1:8000)"
    )
    parser.add_argument(
        "--image",
        help="Ruta a imagen para predicción (default: test_image.jpg)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecutar todas las pruebas"
    )
    
    args = parser.parse_args()
    
    print_header("PRUEBAS DE API - WASTE CLASSIFIER")
    print_info(f"URL Base: {args.url}\n")
    
    # Ejecutar pruebas
    results = {}
    
    # Pruebas básicas (siempre)
    results["Health Check"] = test_health_check(args.url)
    if not results["Health Check"]:
        print_error("No se puede continuar sin conexión al servidor")
        return
    
    results["Root Endpoint"] = test_root(args.url)
    results["Predicción"] = test_predict(args.url, args.image)
    results["Validación de Errores"] = test_invalid_request(args.url)
    
    # Pruebas adicionales si se especifica --all
    if args.all:
        results["Predicciones Múltiples"] = test_multiple_predictions(args.url, count=5)
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.OKGREEN}✓ PASÓ{Colors.ENDC}" if passed_test else f"{Colors.FAIL}✗ FALLÓ{Colors.ENDC}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} pruebas pasadas{Colors.ENDC}\n")
    
    if passed == total:
        print_success("¡Todas las pruebas pasaron!")
    else:
        print_error(f"Algunas pruebas fallaron ({total - passed})")

if __name__ == "__main__":
    main()
