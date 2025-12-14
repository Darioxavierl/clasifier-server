#!/usr/bin/env python3
"""
Fine-tuning de MobileNetV2 para clasificación de residuos
Uso: python train_waste_classifier.py
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pathlib import Path
import argparse
import sys
from datetime import datetime


class WasteClassifierTrainer:
    """Entrenador de modelo para clasificación de residuos"""
    
    def __init__(self, 
                 img_size=(224, 224),
                 num_classes=5,
                 model_name="mobilenetv2_waste",
                 verbose=True):
        
        self.img_size = img_size
        self.num_classes = num_classes
        self.model_name = model_name
        self.verbose = verbose
        self.model = None
        self.base_model = None
        
    def create_model(self):
        """
        Crear modelo MobileNetV2 con custom head
        
        Arquitectura:
        - Input: 224x224x3
        - MobileNetV2 (preentrenado en ImageNet, congelado)
        - GlobalAveragePooling2D
        - Dense(128, relu)
        - Dropout(0.5)
        - Dense(5, softmax)
        """
        
        if self.verbose:
            print("\n" + "="*60)
            print("CREANDO MODELO")
            print("="*60)
            print(f"Tamaño entrada: {self.img_size}")
            print(f"Número de clases: {self.num_classes}")
        
        # Cargar MobileNetV2 preentrenado
        self.base_model = tf.keras.applications.MobileNetV2(
            input_shape=(self.img_size[0], self.img_size[1], 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Congelar modelo base inicialmente
        self.base_model.trainable = False
        
        # Construir modelo completo
        self.model = keras.Sequential([
            keras.layers.InputLayer(input_shape=(self.img_size[0], self.img_size[1], 3)),
            
            # Preprocesamiento MobileNetV2 (envuelto en Lambda)
            keras.layers.Lambda(tf.keras.applications.mobilenet_v2.preprocess_input),
            
            # Modelo base congelado
            self.base_model,
            
            # Capas personalizadas
            keras.layers.GlobalAveragePooling2D(),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        
        if self.verbose:
            print("✓ Modelo creado exitosamente")
        
        return self.model
    
    def compile_model(self, learning_rate=1e-3):
        """Compilar modelo inicial (entrenando solo custom head)"""
        
        if self.verbose:
            print("\n" + "="*60)
            print("COMPILANDO MODELO")
            print("="*60)
            print(f"Learning rate: {learning_rate}")
            print("Entrenando: Solo custom head (base congelado)")
        
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_acc')
            ]
        )
        
        if self.verbose:
            print("✓ Modelo compilado")
    
    def unfreeze_and_compile(self, unfreeze_layers=50, learning_rate=1e-4):
        """
        Descongelar últimas capas del modelo base
        para fine-tuning más agresivo
        """
        
        if self.verbose:
            print("\n" + "="*60)
            print("DESCONGELANDO MODELO BASE")
            print("="*60)
            print(f"Últimas capas a descongelar: {unfreeze_layers}")
            print(f"Nuevo learning rate: {learning_rate}")
        
        # Descongelar últimas capas del base model
        for layer in self.base_model.layers[:-unfreeze_layers]:
            layer.trainable = False
        
        for layer in self.base_model.layers[-unfreeze_layers:]:
            layer.trainable = True
        
        # Recompilar con learning rate más bajo
        optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        trainable_count = sum(1 for layer in self.model.layers if layer.trainable)
        total_count = len(self.model.layers)
        
        if self.verbose:
            print(f"✓ Capas entrenables: {trainable_count}/{total_count}")
    
    def prepare_data(self, data_dir, validation_split=0.2, batch_size=32):
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
        
        # Data augmentation para entrenamiento
        train_datagen = ImageDataGenerator(
            preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            validation_split=validation_split
        )
        
        # Sin augmentation para validación
        val_datagen = ImageDataGenerator(
            preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
            validation_split=validation_split
        )
        
        # Cargar generadores
        train_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical',
            subset='training'
        )
        
        val_generator = val_datagen.flow_from_directory(
            data_dir,
            target_size=self.img_size,
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation'
        )
        
        if self.verbose:
            print(f"✓ Datos cargados")
            print(f"  - Entrenamientos: {train_generator.samples} imágenes")
            print(f"  - Validación: {val_generator.samples} imágenes")
            print(f"  - Clases: {list(train_generator.class_indices.keys())}")
        
        return train_generator, val_generator
    
    def train(self, 
              train_generator, 
              val_generator,
              epochs=10,
              steps_per_epoch=None):
        """
        Entrenar el modelo
        
        Args:
            train_generator: Generador de datos de entrenamiento
            val_generator: Generador de datos de validación
            epochs: Número de épocas
            steps_per_epoch: Pasos por época (None = todo el dataset)
        """
        
        if self.verbose:
            print("\n" + "="*60)
            print("INICIANDO ENTRENAMIENTO")
            print("="*60)
            print(f"Épocas: {epochs}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Usando dispositivo: {tf.config.list_logical_devices()}")
        
        # Crear directorio para logs
        Path('logs').mkdir(exist_ok=True)
        Path('models').mkdir(exist_ok=True)
        
        # Callbacks
        callbacks = [
            # Guardar mejor modelo
            keras.callbacks.ModelCheckpoint(
                f'models/{self.model_name}_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1 if self.verbose else 0
            ),
            
            # Reducir learning rate si no mejora
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=2,
                min_lr=1e-7,
                verbose=1 if self.verbose else 0
            ),
            
            # Early stopping
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True,
                verbose=1 if self.verbose else 0
            ),
            
            # TensorBoard (opcional)
            keras.callbacks.TensorBoard(
                log_dir='./logs',
                histogram_freq=0,
                write_graph=False
            )
        ]
        
        # Entrenar
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
            verbose=1 if self.verbose else 0
        )
        
        return history
    
    def save_model(self, path=None):
        """Guardar modelo entrenado"""
        if path is None:
            path = f'models/{self.model_name}.h5'
        
        self.model.save(path)
        
        if self.verbose:
            print(f"✓ Modelo guardado: {path}")
    
    def evaluate(self, val_generator):
        """Evaluar modelo en datos de validación"""
        
        results = self.model.evaluate(val_generator, verbose=0)
        
        if self.verbose:
            print("\n" + "="*60)
            print("RESULTADOS DE EVALUACIÓN")
            print("="*60)
            print(f"Loss: {results[0]:.4f}")
            print(f"Accuracy: {results[1]:.4f} ({results[1]*100:.2f}%)")
            if len(results) > 2:
                print(f"Top-2 Accuracy: {results[2]:.4f} ({results[2]*100:.2f}%)")
            print("="*60)
        
        return results
    
    def get_model_summary(self):
        """Obtener resumen del modelo"""
        return self.model.summary()


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tuning de MobileNetV2 para clasificación de residuos"
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
        default='mobilenetv2_waste.h5',
        help='Nombre del modelo de salida'
    )
    
    parser.add_argument(
        '--unfreeze',
        type=int,
        default=50,
        help='Capas a descongelar del modelo base'
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
    
    # Crear trainer con número de clases automático
    trainer = WasteClassifierTrainer(num_classes=num_classes, verbose=True)
    
    # Crear modelo
    trainer.create_model()
    trainer.get_model_summary()
    
    # Compilar para primer entrenamiento (solo custom head)
    trainer.compile_model(learning_rate=args.lr)
    
    # Preparar datos
    train_gen, val_gen = trainer.prepare_data(
        args.data_dir,
        batch_size=args.batch_size
    )
    
    # FASE 1: Entrenar solo custom head
    print("\n" + "🔄"*30)
    print("FASE 1: Entrenar custom head (modelo base congelado)")
    print("🔄"*30)
    
    trainer.train(
        train_gen,
        val_gen,
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
        train_gen,
        val_gen,
        epochs=args.epochs//2 if args.epochs > 1 else 1
    )
    
    # Guardar modelo
    output_path = f'models/{args.output}'
    trainer.save_model(output_path)
    
    # Evaluar
    trainer.evaluate(val_gen)
    
    print("\n✅ Entrenamiento completado exitosamente")
    print(f"📁 Modelo guardado: {output_path}")
    print("\nPróximos pasos:")
    print(f"1. Actualizar app/config.py: MODEL_PATH = '{output_path}'")
    print("2. Ejecutar: python run.py")
    print("3. Probar: python test_api.py")


if __name__ == "__main__":
    main()
