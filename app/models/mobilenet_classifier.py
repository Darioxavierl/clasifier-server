import tensorflow as tf
import numpy as np
from app.models.base_model import BaseClassifier
from app.config import settings
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MobileNetClassifier(BaseClassifier):
    def __init__(self):
        self.model = None
        self.input_shape = settings.IMG_SIZE
        
    def load_model(self, model_path: str):
        """
        Carga el modelo con validación de archivo
        
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
        
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Modelo cargado exitosamente: {model_path}")
            logger.info(f"Forma de entrada: {self.model.input_shape}")
            logger.info(f"Número de capas: {len(self.model.layers)}")
        except Exception as e:
            error_msg = f"Error cargando modelo: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocesamiento específico de MobileNet"""
        # Redimensionar
        image = tf.image.resize(image, self.input_shape)
        # Normalizar [-1, 1] (MobileNet usa esta normalización)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        # Añadir dimensión batch
        image = np.expand_dims(image, axis=0)
        return image
    
    def predict(self, image: np.ndarray) -> dict:
        preprocessed = self.preprocess(image)
        predictions = self.model.predict(preprocessed)[0]
        
        class_id = int(np.argmax(predictions))
        confidence = float(predictions[class_id])
        
        return {
            "class_id": class_id,
            "class_name": settings.CLASSES[class_id],
            "confidence": confidence,
            "all_probabilities": predictions.tolist()
        }