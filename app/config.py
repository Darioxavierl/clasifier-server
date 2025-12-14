from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Tuple

class Settings(BaseSettings):
    MODEL_PATH: str = "models/mobilenetv2_waste.h5"
    IMG_SIZE: Tuple[int, int] = (224, 224)
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_FILE_SIZE: int = 5_000_000  # 5MB
    
    # Clases del modelo
    CLASSES: List[str] = ["plastico", "papel", "vidrio", "metal", "organico"]

    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    ENABLE_FILE_LOGGING: bool = True
    ENABLE_CONSOLE_LOGGING: bool = True
    LOG_PREDICTIONS: bool = True  # Para análisis posterior
    
    class Config:
        env_file = ".env"

settings = Settings()