import numpy as np
from app.models.base_model import BaseClassifier
from app.config import settings
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Importar frameworks de manera segura (pueden no estar instalados)
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    import torch
    import torchvision.transforms as transforms
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


class MobileNetClassifier(BaseClassifier):
    def __init__(self):
        self.model = None
        self.input_shape = settings.IMG_SIZE
        self.framework = None  # 'tensorflow' o 'pytorch'
        self.device = None  # Para PyTorch
        
    def load_model(self, model_path: str):
        """
        Carga el modelo detectando automáticamente el framework
        Soporta:
        - TensorFlow (.h5, .keras)
        - PyTorch (.pth, .pt)
        
        Args:
            model_path: ruta al archivo del modelo
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            Exception: Si hay error cargando el modelo
        """
        model_file = Path(model_path)
        
        if not model_file.exists():
            error_msg = f"Archivo de modelo no encontrado: {model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Detectar framework por extensión
        suffix = model_file.suffix.lower()
        
        if suffix in ['.pth', '.pt']:
            self._load_pytorch_model(model_path)
        elif suffix in ['.h5', '.keras']:
            self._load_tensorflow_model(model_path)
        else:
            raise ValueError(f"Formato de modelo no soportado: {suffix}")
    
    def _load_tensorflow_model(self, model_path: str):
        """Cargar modelo TensorFlow"""
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow no está instalado")
        
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.framework = 'tensorflow'
            # Detectar número de clases de la última capa
            self.num_classes = self.model.layers[-1].output_shape[-1]
            logger.info(f"Modelo TensorFlow cargado: {model_path}")
            logger.info(f"Forma de entrada: {self.model.input_shape}")
            logger.info(f"Número de capas: {len(self.model.layers)}")
            logger.info(f"Número de clases: {self.num_classes}")
        except Exception as e:
            error_msg = f"Error cargando modelo TensorFlow: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _load_pytorch_model(self, model_path: str):
        """Cargar modelo PyTorch"""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch no está instalado")
        
        try:
            from torchvision import models
            
            # Detectar dispositivo (GPU si disponible, sino CPU)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Usando dispositivo: {self.device}")
            
            # Cargar pesos primero para detectar número de clases
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            # Detectar número de clases del checkpoint
            # Buscar el último layer lineal de salida (classifier.4)
            # Necesitamos el layer FINAL con shape[0] = número de clases
            num_classes = None
            classifier_weights = [k for k in checkpoint.keys() if 'classifier' in k and 'weight' in k]
            
            if classifier_weights:
                # El último layer lineal en la secuencia es el de salida con num_classes
                # classifier.1 tiene shape [128, 1280], classifier.4 tiene shape [6, 128]
                # Buscamos el que tiene el menor shape[1] (entrada) - ese es el final
                final_layer = classifier_weights[-1]  # classifier.4 es el último
                num_classes = checkpoint[final_layer].shape[0]
            
            if num_classes is None:
                raise ValueError("No se pudo detectar número de clases del modelo")
            
            logger.info(f"Detectadas {num_classes} clases en el modelo")
            
            # Crear modelo base con el número correcto de clases
            base_model = models.mobilenet_v2(pretrained=False)
            
            # Reemplazar cabezal (DEBE coincidir con el entrenamiento)
            num_features = base_model.classifier[1].in_features
            base_model.classifier = torch.nn.Sequential(
                torch.nn.Dropout(p=0.5),
                torch.nn.Linear(num_features, 128),
                torch.nn.ReLU(inplace=True),
                torch.nn.Dropout(p=0.5),
                torch.nn.Linear(128, num_classes)  # Usar número de clases del modelo
            )
            
            # Cargar pesos
            base_model.load_state_dict(checkpoint)
            base_model = base_model.to(self.device)
            base_model.eval()
            
            self.model = base_model
            self.framework = 'pytorch'
            self.num_classes = num_classes
            logger.info(f"Modelo PyTorch cargado: {model_path}")
            logger.info(f"Dispositivo: {self.device}")
            logger.info(f"Clases: {num_classes}")
        except Exception as e:
            error_msg = f"Error cargando modelo PyTorch: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocesamiento específico de MobileNet"""
        if self.framework == 'tensorflow':
            return self._preprocess_tensorflow(image)
        elif self.framework == 'pytorch':
            return self._preprocess_pytorch(image)
        else:
            raise ValueError(f"Framework no soportado: {self.framework}")
    
    def _preprocess_tensorflow(self, image: np.ndarray) -> np.ndarray:
        """Preprocesamiento para TensorFlow"""
        import tensorflow as tf
        
        # Redimensionar
        image = tf.image.resize(image, self.input_shape)
        # Normalizar [-1, 1] (MobileNet usa esta normalización)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        # Añadir dimensión batch
        image = np.expand_dims(image, axis=0)
        return image
    
    def _preprocess_pytorch(self, image: np.ndarray) -> torch.Tensor:
        """Preprocesamiento para PyTorch"""
        from PIL import Image
        import torchvision.transforms as transforms
        
        # Convertir numpy a PIL
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image.astype(np.uint8))
        
        # Transformaciones
        transform = transforms.Compose([
            transforms.Resize(self.input_shape),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Aplicar transformaciones y añadir batch
        tensor = transform(pil_image).unsqueeze(0)
        return tensor.to(self.device)
    
    def predict(self, image: np.ndarray) -> dict:
        """Predecir clase - funciona con ambos frameworks"""
        
        if self.framework == 'tensorflow':
            return self._predict_tensorflow(image)
        elif self.framework == 'pytorch':
            return self._predict_pytorch(image)
        else:
            raise ValueError(f"Framework no soportado: {self.framework}")
    
    def _predict_tensorflow(self, image: np.ndarray) -> dict:
        """Predicción TensorFlow"""
        preprocessed = self._preprocess_tensorflow(image)
        predictions = self.model.predict(preprocessed)[0]
        
        class_id = int(np.argmax(predictions))
        confidence = float(predictions[class_id])
        
        return {
            "class_id": class_id,
            "class_name": settings.CLASSES[class_id],
            "confidence": confidence,
            "all_probabilities": predictions.tolist()
        }
    
    def _predict_pytorch(self, image: np.ndarray) -> dict:
        """Predicción PyTorch"""
        preprocessed = self._preprocess_pytorch(image)
        
        with torch.no_grad():
            output = self.model(preprocessed)
            predictions = torch.softmax(output, dim=1)[0].cpu().numpy()
        
        class_id = int(np.argmax(predictions))
        confidence = float(predictions[class_id])
        
        return {
            "class_id": class_id,
            "class_name": settings.CLASSES[class_id],
            "confidence": confidence,
            "all_probabilities": predictions.tolist()
        }