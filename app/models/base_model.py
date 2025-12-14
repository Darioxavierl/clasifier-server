from abc import ABC, abstractmethod
import numpy as np

class BaseClassifier(ABC):
    """Clase base para cualquier modelo de clasificación"""
    
    @abstractmethod
    def load_model(self, model_path: str):
        """Cargar modelo desde archivo"""
        pass
    
    @abstractmethod
    def predict(self, image: np.ndarray) -> dict:
        """
        Ejecutar predicción
        Returns:
            {
                "class_id": int,
                "class_name": str,
                "confidence": float,
                "all_probabilities": list
            }
        """
        pass
    
    @abstractmethod
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocesamiento específico del modelo"""
        pass