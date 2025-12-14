#!/usr/bin/env python3
"""
Fine-tuning de MobileNetV2 para clasificación de residuos - PyTorch Edition
Optimizado para GPU NVIDIA con CUDA
Uso: python train_waste_classifier_pytorch.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import models, transforms, datasets
from pathlib import Path
import argparse
import sys
from datetime import datetime
import json


class WasteClassifierPyTorch:
    """Entrenador PyTorch para clasificación de residuos"""
    
    def __init__(self, 
                 img_size=(224, 224),
                 num_classes=5,
                 model_name="mobilenetv2_waste_pytorch",
                 verbose=True,
                 device=None):
        
        self.img_size = img_size
        self.num_classes = num_classes
        self.model_name = model_name
        self.verbose = verbose
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.best_accuracy = 0.0
        
        if self.verbose:
            print(f"Dispositivo: {self.device}")
            if torch.cuda.is_available():
                print(f"GPU: {torch.cuda.get_device_name(0)}")
        
    def create_model(self):
        """
        Crear modelo MobileNetV2 con custom head
        
        Arquitectura:
        - Input: 224x224x3
        - MobileNetV2 (preentrenado en ImageNet, congelado)
        - Adaptative Avg Pool
        - Linear(128, relu)
        - Dropout(0.5)
        - Linear(num_classes, softmax)
        """
        
        if self.verbose:
            print("\n" + "="*60)
            print("CREANDO MODELO")
            print("="*60)
            print(f"Tamaño entrada: {self.img_size}")
            print(f"Número de clases: {self.num_classes}")
        
        # Cargar MobileNetV2 preentrenado
        base_model = models.mobilenet_v2(pretrained=True)
        
        # Congelar modelo base inicialmente
        for param in base_model.parameters():
            param.requires_grad = False
        
        # Reemplazar cabezal de clasificación
        num_features = base_model.classifier[1].in_features
        base_model.classifier = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(num_features, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(128, self.num_classes)
        )
        
        self.model = base_model.to(self.device)
        
        if self.verbose:
            print("✓ Modelo creado exitosamente")
        
        return self.model
    
    def compile_model(self, learning_rate=1e-3):
        """Configurar optimizer y loss"""
        
        if self.verbose:
            print("\n" + "="*60)
            print("COMPILANDO MODELO")
            print("="*60)
            print(f"Learning rate: {learning_rate}")
            print("Entrenando: Solo custom head (base congelado)")
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=2, verbose=self.verbose
        )
        
        if self.verbose:
            print("✓ Modelo compilado")
    
    def unfreeze_and_compile(self, unfreeze_layers=50, learning_rate=1e-4):
        """Descongelar últimas capas del modelo base"""
        
        if self.verbose:
            print("\n" + "="*60)
            print("DESCONGELANDO MODELO BASE")
            print("="*60)
            print(f"Últimas capas a descongelar: {unfreeze_layers}")
            print(f"Nuevo learning rate: {learning_rate}")
        
        # Contar capas totales
        all_params = list(self.model.features.parameters())
        
        # Descongelar últimas N capas
        for param in all_params[-unfreeze_layers:]:
            param.requires_grad = True
        
        # Recompilar con learning rate más bajo
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=2, verbose=self.verbose
        )
        
        trainable = sum(1 for p in self.model.parameters() if p.requires_grad)
        total = sum(1 for p in self.model.parameters())
        
        if self.verbose:
            print(f"✓ Parámetros entrenables: {trainable}/{total}")
    
    def prepare_data(self, data_dir, validation_split=0.2, batch_size=32, num_workers=0):
        """
        Preparar datos con aumento de imágenes
        
        Estructura esperada:
        data_dir/
        ├── plastico/
        ├── papel/
        ├── vidrio/
        ├── metal/
        └── organico/
        """
        
        if self.verbose:
            print("\n" + "="*60)
            print("PREPARANDO DATOS")
            print("="*60)
            print(f"Directorio: {data_dir}")
            print(f"Validación split: {validation_split*100:.0f}%")
            print(f"Batch size: {batch_size}")
            print(f"Workers: {num_workers}")
        
        # Transformaciones para entrenamiento
        train_transform = transforms.Compose([
            transforms.Resize((self.img_size[0], self.img_size[1])),
            transforms.RandomRotation(20),
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Transformaciones para validación
        val_transform = transforms.Compose([
            transforms.Resize((self.img_size[0], self.img_size[1])),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Cargar datasets
        full_dataset = datasets.ImageFolder(data_dir, transform=train_transform)
        
        # Split manual
        val_size = int(len(full_dataset) * validation_split)
        train_size = len(full_dataset) - val_size
        
        train_dataset, val_dataset = random_split(
            full_dataset, [train_size, val_size]
        )
        
        # Aplicar transformación correcta a validación
        val_dataset.dataset.transform = val_transform
        
        # Data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers
        )
        
        # Obtener nombres de clases
        classes = full_dataset.classes
        
        if self.verbose:
            print(f"✓ Datos cargados")
            print(f"  - Entrenamientos: {train_size} imágenes")
            print(f"  - Validación: {val_size} imágenes")
            print(f"  - Clases: {classes}")
        
        return train_loader, val_loader, classes
    
    def train_epoch(self, train_loader):
        """Entrenar una época"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward
            loss.backward()
            self.optimizer.step()
            
            # Stats
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        epoch_loss = total_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader):
        """Validar modelo"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        epoch_loss = total_loss / len(val_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, train_loader, val_loader, epochs=10):
        """Entrenar el modelo"""
        
        if self.verbose:
            print("\n" + "="*60)
            print("INICIANDO ENTRENAMIENTO")
            print("="*60)
            print(f"Épocas: {epochs}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Crear directorios
        Path('models').mkdir(exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
        history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.validate(val_loader)
            
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            # Scheduler step
            self.scheduler.step(val_loss)
            
            # Guardar mejor modelo
            if val_acc > self.best_accuracy:
                self.best_accuracy = val_acc
                self.save_model(f'models/{self.model_name}_best.pth')
            
            if self.verbose:
                print(f'Epoch [{epoch+1}/{epochs}] '
                      f'Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}% | '
                      f'Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%')
        
        return history
    
    def save_model(self, path=None):
        """Guardar modelo"""
        if path is None:
            path = f'models/{self.model_name}.pth'
        
        torch.save(self.model.state_dict(), path)
        
        if self.verbose:
            print(f"✓ Modelo guardado: {path}")
    
    def evaluate(self, val_loader):
        """Evaluar modelo"""
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        
        if self.verbose:
            print("\n" + "="*60)
            print("RESULTADOS DE EVALUACIÓN")
            print("="*60)
            print(f"Accuracy: {accuracy:.2f}% ({correct}/{total})")
            print("="*60)
        
        return accuracy


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tuning de MobileNetV2 para clasificación de residuos (PyTorch)"
    )
    
    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directorio con datos de entrenamiento'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Número de épocas'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Tamaño de batch'
    )
    
    parser.add_argument(
        '--lr',
        type=float,
        default=0.001,
        help='Learning rate inicial'
    )
    
    parser.add_argument(
        '--output',
        default='mobilenetv2_waste_pytorch.pth',
        help='Nombre del modelo de salida'
    )
    
    parser.add_argument(
        '--unfreeze',
        type=int,
        default=50,
        help='Capas a descongelar del modelo base'
    )
    
    parser.add_argument(
        '--num-workers',
        type=int,
        default=0,
        help='Workers para data loading (0=no multiprocessing, 4+=recomendado)'
    )
    
    args = parser.parse_args()
    
    # Verificar que existan los datos
    data_path = Path(args.data_dir)
    if not data_path.exists():
        print(f"❌ Error: Directorio '{args.data_dir}' no existe")
        print("\nCrea la estructura de datos:")
        print(f"{args.data_dir}/")
        print("├── plastico/")
        print("├── papel/")
        print("├── vidrio/")
        print("├── metal/")
        print("└── organico/")
        sys.exit(1)
    
    # Detectar automáticamente el número de clases
    class_dirs = sorted([d for d in data_path.iterdir() if d.is_dir()])
    num_classes = len(class_dirs)
    
    if num_classes == 0:
        print(f"❌ Error: No hay subdirectorios de clases en '{args.data_dir}'")
        sys.exit(1)
    
    print(f"\n✓ Detectadas {num_classes} clases: {[d.name for d in class_dirs]}")
    
    # Crear trainer
    trainer = WasteClassifierPyTorch(num_classes=num_classes, verbose=True)
    
    # Crear modelo
    trainer.create_model()
    
    # Compilar para primer entrenamiento
    trainer.compile_model(learning_rate=args.lr)
    
    # Preparar datos
    train_loader, val_loader, classes = trainer.prepare_data(
        args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # FASE 1: Entrenar solo custom head
    print("\n" + "🔄"*30)
    print("FASE 1: Entrenar custom head (modelo base congelado)")
    print("🔄"*30)
    
    trainer.train(
        train_loader,
        val_loader,
        epochs=args.epochs//2 if args.epochs > 1 else 1
    )
    
    # FASE 2: Fine-tune del modelo base
    print("\n" + "🔄"*30)
    print("FASE 2: Fine-tune del modelo base")
    print("🔄"*30)
    
    trainer.unfreeze_and_compile(
        unfreeze_layers=args.unfreeze,
        learning_rate=args.lr / 10
    )
    
    trainer.train(
        train_loader,
        val_loader,
        epochs=args.epochs//2 if args.epochs > 1 else 1
    )
    
    # Guardar modelo final
    output_path = f'models/{args.output}'
    trainer.save_model(output_path)
    
    # Evaluar
    trainer.evaluate(val_loader)
    
    print("\n✅ Entrenamiento completado exitosamente")
    print(f"📁 Modelo guardado: {output_path}")
    print(f"🎯 Accuracy: {trainer.best_accuracy:.2f}%")
    print("\nPróximos pasos:")
    print(f"1. Convertir modelo PyTorch a ONNX o TensorFlow si lo necesitas")
    print("2. Integrar en tu aplicación FastAPI")
    print("3. Ejecutar: python run.py")
    print("4. Probar: python test_api.py")


if __name__ == "__main__":
    main()
