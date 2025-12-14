#!/usr/bin/env python3
"""
Análisis de dataset y validación de datos
Verifica integridad, balance de clases y calidad de imágenes

Uso: python analyze_dataset.py --data-dir data
"""

import cv2
import numpy as np
from pathlib import Path
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt


class DatasetAnalyzer:
    """Analizador de dataset de imágenes"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.classes = {}
        self.stats = defaultdict(dict)
        
    def analyze(self):
        """Realizar análisis completo del dataset"""
        
        print("\n" + "="*60)
        print("ANÁLISIS DE DATASET")
        print("="*60)
        print(f"Directorio: {self.data_dir}")
        
        if not self.data_dir.exists():
            print(f"❌ Directorio no encontrado: {self.data_dir}")
            return False
        
        # Contar imágenes por clase
        print("\n📊 CONTEO DE IMÁGENES")
        print("-"*60)
        
        total_images = 0
        
        for class_dir in sorted(self.data_dir.iterdir()):
            if class_dir.is_dir():
                images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
                count = len(images)
                
                if count > 0:
                    self.classes[class_dir.name] = images
                    total_images += count
                    
                    status = "✓" if count >= 50 else "⚠"
                    print(f"{status} {class_dir.name:.<30} {count:>4} imágenes")
        
        print("-"*60)
        print(f"{'TOTAL':.<30} {total_images:>4} imágenes")
        
        if total_images == 0:
            print("\n❌ No se encontraron imágenes")
            return False
        
        # Analizar tamaños y formato
        print("\n📐 ANÁLISIS DE IMÁGENES")
        print("-"*60)
        
        sizes = defaultdict(int)
        corrupted = []
        
        for class_name, images in self.classes.items():
            for img_path in images:
                try:
                    img = cv2.imread(str(img_path))
                    
                    if img is None:
                        corrupted.append(img_path)
                        continue
                    
                    h, w = img.shape[:2]
                    size_key = f"{w}x{h}"
                    sizes[size_key] += 1
                    
                    if class_name not in self.stats:
                        self.stats[class_name] = {
                            'sizes': defaultdict(int),
                            'total': 0
                        }
                    
                    self.stats[class_name]['sizes'][size_key] += 1
                    self.stats[class_name]['total'] += 1
                    
                except Exception as e:
                    corrupted.append(img_path)
        
        # Mostrar tamaños
        print("Tamaños más comunes:")
        for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total_images) * 100
            print(f"  {size:.<20} {count:>4} ({percentage:>5.1f}%)")
        
        # Imágenes corruptas
        if corrupted:
            print(f"\n⚠️  Imágenes corruptas: {len(corrupted)}")
            for img in corrupted[:5]:
                print(f"  - {img.name}")
            if len(corrupted) > 5:
                print(f"  ... y {len(corrupted) - 5} más")
        else:
            print("\n✓ No hay imágenes corruptas")
        
        # Balance de clases
        print("\n⚖️  BALANCE DE CLASES")
        print("-"*60)
        
        counts = {name: len(images) for name, images in self.classes.items()}
        min_count = min(counts.values())
        max_count = max(counts.values())
        avg_count = np.mean(list(counts.values()))
        
        for class_name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_images) * 100
            bar_length = int(count / max_count * 30)
            bar = "█" * bar_length
            
            status = "✓" if 0.8 * avg_count <= count <= 1.2 * avg_count else "⚠"
            print(f"{status} {class_name:.<15} {count:>3} ({percentage:>5.1f}%) {bar}")
        
        # Estadísticas de balance
        print("\n📈 ESTADÍSTICAS DE BALANCE")
        print("-"*60)
        print(f"Mínimo por clase: {min_count}")
        print(f"Máximo por clase: {max_count}")
        print(f"Promedio por clase: {avg_count:.1f}")
        print(f"Desviación estándar: {np.std(list(counts.values())):.1f}")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES")
        print("-"*60)
        
        if min_count < 50:
            print("⚠️  Algunas clases tienen menos de 50 imágenes")
            print("   Captura más imágenes para mejor entrenamiento")
        
        if max_count / min_count > 2:
            print("⚠️  El dataset está desbalanceado")
            print("   Considera capturar más imágenes de las clases minoritarias")
        else:
            print("✓ Dataset está bien balanceado")
        
        if len(corrupted) > 0:
            print(f"⚠️  Hay {len(corrupted)} imágenes corruptas")
            print("   Considera eliminarlas para mejor calidad")
        else:
            print("✓ Todas las imágenes están íntegras")
        
        if total_images >= 300:
            print("✓ Suficientes imágenes para entrenamiento")
        elif total_images >= 150:
            print("⚠️  Mínimo de imágenes alcanzado (recomendado: 300+)")
        else:
            print("❌ Muy pocas imágenes (mínimo recomendado: 150)")
        
        # Resumen final
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        
        print(f"Total de imágenes: {total_images}")
        print(f"Número de clases: {len(self.classes)}")
        print(f"Imágenes corruptas: {len(corrupted)}")
        
        ready = (
            total_images >= 150 and
            len(self.classes) >= 4 and
            len(corrupted) == 0
        )
        
        if ready:
            print("\n✅ Dataset listo para entrenamiento")
            print("\nEjecuta: python train_waste_classifier.py --epochs 10")
        else:
            print("\n⚠️  Dataset necesita mejoras antes del entrenamiento")
        
        return ready
    
    def check_image_quality(self, min_brightness=50, max_brightness=200):
        """
        Verificar calidad de imágenes
        (brillo, contraste, etc.)
        """
        
        print("\n" + "="*60)
        print("VERIFICACIÓN DE CALIDAD DE IMÁGENES")
        print("="*60)
        
        quality_issues = defaultdict(list)
        
        for class_name, images in self.classes.items():
            print(f"\nAnalizando {class_name}...")
            
            for img_path in images:
                try:
                    img = cv2.imread(str(img_path))
                    if img is None:
                        continue
                    
                    # Convertir a escala de grises
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Calcular brillo promedio
                    brightness = np.mean(gray)
                    
                    # Calcular contraste (desviación estándar)
                    contrast = np.std(gray)
                    
                    # Detectar problemas
                    if brightness < min_brightness:
                        quality_issues[class_name].append({
                            'file': img_path.name,
                            'issue': 'Demasiado oscura',
                            'brightness': brightness
                        })
                    elif brightness > max_brightness:
                        quality_issues[class_name].append({
                            'file': img_path.name,
                            'issue': 'Demasiado clara',
                            'brightness': brightness
                        })
                    
                    if contrast < 20:
                        quality_issues[class_name].append({
                            'file': img_path.name,
                            'issue': 'Bajo contraste',
                            'contrast': contrast
                        })
                
                except Exception as e:
                    pass
        
        # Mostrar problemas
        total_issues = sum(len(v) for v in quality_issues.values())
        
        if total_issues == 0:
            print("✓ Todas las imágenes tienen buena calidad")
        else:
            print(f"\n⚠️  Se encontraron {total_issues} problemas de calidad")
            
            for class_name, issues in quality_issues.items():
                print(f"\n{class_name}:")
                for issue in issues[:5]:
                    print(f"  - {issue['file']}: {issue['issue']}")
                
                if len(issues) > 5:
                    print(f"  ... y {len(issues) - 5} más")


def main():
    parser = argparse.ArgumentParser(
        description="Analizar dataset de imágenes"
    )
    
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directorio con datos'
    )
    
    parser.add_argument(
        '--quality',
        action='store_true',
        help='Analizar calidad de imágenes'
    )
    
    args = parser.parse_args()
    
    analyzer = DatasetAnalyzer(args.data_dir)
    ready = analyzer.analyze()
    
    if args.quality:
        analyzer.check_image_quality()
    
    return 0 if ready else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
