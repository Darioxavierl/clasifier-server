import cv2
import numpy as np
from fastapi import HTTPException

def decode_image(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes a imagen numpy"""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Imagen corrupta")
            
        # BGR a RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error decodificando imagen: {str(e)}")

def validate_image(image: np.ndarray) -> bool:
    """Validaciones básicas"""
    if image.shape[0] < 50 or image.shape[1] < 50:
        raise HTTPException(status_code=400, detail="Imagen muy pequeña")
    return True