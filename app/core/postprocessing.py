import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class PostProcessor:
    """
    Procesa y enriquece los resultados del modelo de IA
    """
    
    # Mapeo de clases a códigos para el ESP32
    CLASS_TO_CODE = {
        "plastico": 1,
        "papel": 2,
        "vidrio": 3,
        "metal": 4,
        "organico": 5,
        "indeterminado": 0
    }
    
    # Mensajes descriptivos (opcional para frontend)
    CLASS_DESCRIPTIONS = {
        "plastico": "Residuo plástico reciclable",
        "papel": "Papel y cartón",
        "vidrio": "Vidrio reciclable",
        "metal": "Metal reciclable",
        "organico": "Residuo orgánico",
        "indeterminado": "No se pudo clasificar con confianza"
    }
    
    @staticmethod
    def process_prediction(
        raw_prediction: Dict[str, Any],
        confidence_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Procesa el resultado crudo del modelo y genera respuesta final
        
        Args:
            raw_prediction: {
                "class_id": int,
                "class_name": str,
                "confidence": float,
                "all_probabilities": list
            }
            confidence_threshold: umbral mínimo (usa config si no se especifica)
        
        Returns:
            {
                "code": int,              # Código para ESP32
                "class_name": str,        # Nombre legible
                "confidence": float,      # Confianza [0-1]
                "is_confident": bool,     # Si supera el umbral
                "description": str,       # Mensaje descriptivo
                "alternative_classes": list  # Top 3 alternativas
            }
        """
        threshold = confidence_threshold or settings.CONFIDENCE_THRESHOLD
        
        class_name = raw_prediction["class_name"]
        confidence = raw_prediction["confidence"]
        
        # Determinar si la clasificación es confiable
        is_confident = confidence >= threshold
        
        # Si no es confiable, marcar como indeterminado
        if not is_confident:
            class_name = "indeterminado"
            logger.warning(
                f"Confianza baja ({confidence:.2%}) - "
                f"Clasificado como indeterminado"
            )
        
        # Obtener código para ESP32
        code = PostProcessor.CLASS_TO_CODE.get(class_name, 0)
        
        # Obtener alternativas (top 3)
        alternatives = PostProcessor._get_top_alternatives(
            raw_prediction["all_probabilities"],
            exclude_index=raw_prediction["class_id"] if is_confident else None
        )
        
        result = {
            "code": code,
            "class_name": class_name,
            "confidence": round(confidence, 4),
            "is_confident": is_confident,
            "description": PostProcessor.CLASS_DESCRIPTIONS.get(
                class_name, 
                "Clasificación desconocida"
            ),
            "alternative_classes": alternatives
        }
        
        # Log de la decisión
        logger.info(
            f"Clasificación: {class_name} | "
            f"Código: {code} | "
            f"Confianza: {confidence:.2%}"
        )
        
        return result
    
    @staticmethod
    def _get_top_alternatives(
        probabilities: list, 
        top_k: int = 3,
        exclude_index: Optional[int] = None
    ) -> list:
        """
        Obtiene las top K clases alternativas
        
        Args:
            probabilities: lista de probabilidades
            top_k: cantidad de alternativas a retornar
            exclude_index: índice a excluir (la predicción principal)
        
        Returns:
            [
                {"class_name": "papel", "confidence": 0.23},
                {"class_name": "plastico", "confidence": 0.15},
                ...
            ]
        """
        import numpy as np
        
        # Convertir a numpy para facilitar operaciones
        probs = np.array(probabilities)
        
        # Obtener índices ordenados de mayor a menor
        sorted_indices = np.argsort(probs)[::-1]
        
        alternatives = []
        for idx in sorted_indices:
            # Saltar la clase principal si se especificó
            if exclude_index is not None and idx == exclude_index:
                continue
            
            # Solo incluir clases con confianza > 1%
            if probs[idx] < 0.01:
                break
                
            alternatives.append({
                "class_name": settings.CLASSES[idx],
                "confidence": round(float(probs[idx]), 4)
            })
            
            if len(alternatives) >= top_k:
                break
        
        return alternatives
    
    @staticmethod
    def generate_esp_response(code: int) -> Dict[str, Any]:
        """
        Genera respuesta minimalista para ESP32 (solo el código)
        Útil si quieres un endpoint más ligero
        
        Args:
            code: código de clasificación
        
        Returns:
            {"code": 1}
        """
        return {"code": code}
    
    @staticmethod
    def apply_business_rules(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica reglas de negocio adicionales
        Ejemplo: ciertos residuos requieren validación humana
        
        Args:
            result: resultado procesado
        
        Returns:
            resultado con reglas aplicadas
        """
        # Inicializar valores por defecto
        result["requires_review"] = False
        result["review_reason"] = None
        result["special_handling"] = False
        result["handling_notes"] = None
        
        # Ejemplo: si es metal con baja confianza, marcar para revisión
        if (result["class_name"] == "metal" and 
            result["confidence"] < 0.85):
            result["requires_review"] = True
            result["review_reason"] = "Metal detectado con confianza moderada"
        
        # Ejemplo: vidrio siempre requiere cuidado especial
        if result["class_name"] == "vidrio":
            result["special_handling"] = True
            result["handling_notes"] = "Manipular con precaución - Material frágil"
        
        # Ejemplo: plástico de baja confianza
        if (result["class_name"] == "plastico" and 
            result["confidence"] < 0.6):
            result["requires_review"] = True
            result["review_reason"] = "Plástico identificado con baja confianza"
        
        # Ejemplo: indeterminado siempre requiere revisión
        if result["class_name"] == "indeterminado":
            result["requires_review"] = True
            result["review_reason"] = "Imagen no clasificada con suficiente confianza"
        
        return result