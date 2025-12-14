#!/usr/bin/env python3
"""
Capturador de imágenes para crear dataset personalizado
Usa tu webcam para capturar imágenes de diferentes tipos de residuos

Uso: python capture_dataset.py
"""

import cv2
import os
from pathlib import Path
from datetime import datetime
import argparse


class DatasetCapture:
    """Capturador de imágenes para crear dataset"""
    
    def __init__(self, output_dir='data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def capture_class(self, class_name, count=100, size=(224, 224)):
        """
        Capturar imágenes de una clase específica
        
        Controles:
        - ESPACIO: Capturar imagen
        - FLECHA ARRIBA: Aumentar brillo
        - FLECHA ABAJO: Disminuir brillo
        - D: Mostrar/ocultar descripción
        - Q: Salir
        
        Args:
            class_name: Nombre de la clase (ej: 'plastico')
            count: Número de imágenes a capturar
            size: Tamaño de redimensionamiento
        """
        
        # Crear directorio para la clase
        class_dir = self.output_dir / class_name
        class_dir.mkdir(exist_ok=True)
        
        # Contar imágenes existentes
        existing = len(list(class_dir.glob('*.jpg')))
        
        print("\n" + "="*60)
        print(f"CAPTURANDO: {class_name.upper()}")
        print("="*60)
        print(f"Directorio: {class_dir}")
        print(f"Imágenes existentes: {existing}")
        print(f"Target: {count} imágenes")
        print(f"Tamaño: {size}")
        
        print("\nCONTROLES:")
        print("  ESPACIO  - Capturar imagen")
        print("  ↑↓       - Ajustar brillo")
        print("  D        - Mostrar/ocultar info")
        print("  Q        - Salir")
        print("\nPresiona una tecla para iniciar...")
        
        # Abrir cámara
        cap = cv2.VideoCapture(0)
        
        # Configurar cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        captured = existing
        brightness_offset = 0
        show_info = True
        
        print(f"\n✓ Cámara iniciada")
        
        while captured < count + existing:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Error: No se puede leer de la cámara")
                break
            
            # Aplicar brillo
            if brightness_offset != 0:
                frame = cv2.convertScaleAbs(frame, alpha=1, beta=brightness_offset)
            
            # Voltear horizontalmente para espejo
            frame = cv2.flip(frame, 1)
            
            # Mostrar información
            if show_info:
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (10, 10), (w-10, 150), (0, 0, 0), -1)
                cv2.rectangle(frame, (10, 10), (w-10, 150), (0, 255, 0), 2)
                
                cv2.putText(
                    frame,
                    f"Clase: {class_name.upper()}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                cv2.putText(
                    frame,
                    f"Capturadas: {captured - existing}/{count}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                cv2.putText(
                    frame,
                    f"Brillo: {brightness_offset:+d}",
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                cv2.putText(
                    frame,
                    "ESPACIO=Capturar, Flechas=Brillo, D=Info, Q=Salir",
                    (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (200, 200, 0),
                    1
                )
            
            # Mostrar preview
            cv2.imshow(f'Capturador - {class_name}', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):
                # Capturar imagen
                filename = class_dir / f"{captured:04d}.jpg"
                
                # Redimensionar a tamaño standard
                resized = cv2.resize(frame, size)
                cv2.imwrite(str(filename), resized)
                
                captured += 1
                
                # Feedback visual
                print(f"✓ Imagen {captured - existing}/{count} guardada: {filename.name}")
                
                # Mostrar confirmación en pantalla
                frame_copy = frame.copy()
                cv2.rectangle(frame_copy, (0, 0), frame_copy.shape[1::-1], (0, 255, 0), 3)
                cv2.imshow(f'Capturador - {class_name}', frame_copy)
                cv2.waitKey(200)  # Mostrar confirmación 200ms
                
            elif key == 82:  # Flecha arriba
                brightness_offset = min(brightness_offset + 10, 100)
                print(f"  Brillo: {brightness_offset:+d}")
                
            elif key == 84:  # Flecha abajo
                brightness_offset = max(brightness_offset - 10, -100)
                print(f"  Brillo: {brightness_offset:+d}")
                
            elif key == ord('d'):
                show_info = not show_info
                
            elif key == ord('q'):
                print(f"\n⚠️  Captura cancelada. Imágenes capturadas: {captured - existing}")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n✓ Completado: {captured - existing}/{count} imágenes capturadas")
        print(f"✓ Guardadas en: {class_dir}")
        
        return captured - existing
    
    def capture_all_classes(self, classes, count_per_class=100):
        """
        Capturar imágenes para todas las clases
        
        Args:
            classes: Lista de nombres de clases
            count_per_class: Imágenes por clase
        """
        
        print("\n" + "="*60)
        print("CREADOR DE DATASET")
        print("="*60)
        print(f"Clases: {', '.join(classes)}")
        print(f"Target por clase: {count_per_class} imágenes")
        print(f"Total target: {len(classes) * count_per_class} imágenes")
        print("="*60)
        
        total_captured = 0
        
        for i, class_name in enumerate(classes, 1):
            print(f"\n[{i}/{len(classes)}] Preparando captura de '{class_name}'")
            input("Presiona ENTER para continuar...")
            
            captured = self.capture_class(class_name, count=count_per_class)
            total_captured += captured
        
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        print(f"Total de imágenes capturadas: {total_captured}")
        print(f"Directorio: {self.output_dir}")
        
        # Mostrar resumen por clase
        print("\nImágenes por clase:")
        for class_name in classes:
            class_dir = self.output_dir / class_name
            count = len(list(class_dir.glob('*.jpg')))
            print(f"  {class_name}: {count} imágenes")
        
        print("\n✓ Dataset creado exitosamente")
        print("\nPróximos pasos:")
        print("1. Ejecuta: python train_waste_classifier.py --epochs 10")
        print("2. El modelo se guardará en: models/mobilenetv2_waste.h5")
        print("3. Actualiza app/config.py con el nuevo modelo")
        print("4. Ejecuta: python run.py")


def main():
    parser = argparse.ArgumentParser(
        description="Capturador de imágenes para crear dataset de residuos"
    )
    
    parser.add_argument(
        '--output',
        default='data',
        help='Directorio de salida'
    )
    
    parser.add_argument(
        '--per-class',
        type=int,
        default=100,
        help='Imágenes por clase'
    )
    
    parser.add_argument(
        '--size',
        nargs=2,
        type=int,
        default=[224, 224],
        help='Tamaño de imagen (ancho alto)'
    )
    
    parser.add_argument(
        '--class',
        dest='class_name',
        help='Capturar una sola clase'
    )
    
    args = parser.parse_args()
    
    # Verificar disponibilidad de cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: No se puede acceder a la cámara")
        print("Verifica que tu cámara esté conectada y disponible")
        return
    
    cap.release()
    
    # Crear capturador
    capturer = DatasetCapture(output_dir=args.output)
    
    # Capturar
    if args.class_name:
        # Capturar una sola clase
        capturer.capture_class(
            args.class_name,
            count=args.per_class,
            size=tuple(args.size)
        )
    else:
        # Capturar todas las clases
        classes = ['plastico', 'papel', 'vidrio', 'metal', 'organico']
        capturer.capture_all_classes(classes, count_per_class=args.per_class)


if __name__ == "__main__":
    main()
