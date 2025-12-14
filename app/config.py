from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Tuple, ClassVar

class Settings(BaseSettings):
    """
    Configuración de la aplicación Waste Classifier.
    
    Variables que se PUEDEN cambiar en .env:
    - MODEL_PATH: Ruta al modelo entrenado
    - CONFIDENCE_THRESHOLD: Umbral de confianza (0.0-1.0)
    - MAX_FILE_SIZE: Tamaño máximo en bytes
    - LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - LOG_DIR: Directorio para logs
    - ENABLE_FILE_LOGGING: true/false
    - ENABLE_CONSOLE_LOGGING: true/false
    - LOG_PREDICTIONS: true/false
    - PORT: Puerto del servidor (requiere restart)
    - HOST: Host del servidor (requiere restart)
    - UID: ID del usuario (informativo, para build args)
    - GID: ID del grupo (informativo, para build args)
    - APP_USER: Nombre del usuario (informativo, para build args)
    
    Variables que NO se pueden cambiar en .env:
    - IMG_SIZE: Tamaño de imagen (hardcoded, depende del modelo)
    - CLASSES: Clases del modelo (hardcoded, depende del modelo)
      Para cambiar estas, edita este archivo directamente.
    """
    
    # Configuración del modelo
    MODEL_PATH: str = "models/mobilenetv2_waste_pytorch_best.pth"
    IMG_SIZE: Tuple[int, int] = (224, 224)
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_FILE_SIZE: int = 5_000_000  # 5MB
    
    # Clases del modelo (no son campos de config, son constantes)
    # ⚠️ Estas NO se pueden cambiar desde .env
    # Si necesitas cambiarlas, edita esta línea o redefine el modelo
    CLASSES: ClassVar[List[str]] = ["carton", "metal", "papel", "plastico", "trash", "vidrio"]

    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True
    LOG_PREDICTIONS: bool = True  # Para análisis posterior
    
    # Configuración del servidor
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Variables de build (informativas, usadas en docker build --build-arg)
    # Estas se pueden consultar en runtime pero no afectan la ejecución
    UID: int = 1000
    GID: int = 1000
    APP_USER: str = "appuser"
    
    class Config:
        env_file = ".env"

settings = Settings()