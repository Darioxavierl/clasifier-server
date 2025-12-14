import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """
    Formatter con colores para consola (facilita debugging)
    """
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Añadir color al nivel de log
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        return super().format(record)


class RequestIdFilter(logging.Filter):
    """
    Filtro para añadir request_id a los logs (útil para rastrear requests)
    """
    def filter(self, record):
        # Si no existe request_id, usar 'N/A'
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        return True


def setup_logger(
    name: str = "waste_classifier",
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configura el sistema de logging del servidor
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde guardar logs (default: ./logs)
        enable_file_logging: Si guardar logs en archivo
        enable_console_logging: Si mostrar logs en consola
        max_bytes: Tamaño máximo por archivo de log
        backup_count: Cantidad de archivos de backup a mantener
    
    Returns:
        Logger configurado
    """
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Añadir filtro de request_id
    logger.addFilter(RequestIdFilter())
    
    # Formato detallado para archivos
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(request_id)s | '
            '%(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato más simple y colorido para consola
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # ================== HANDLER DE CONSOLA ==================
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # ================== HANDLERS DE ARCHIVO ==================
    if enable_file_logging:
        # Crear directorio de logs si no existe
        if log_dir is None:
            log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 1. Log general con rotación por tamaño
        general_log_path = log_dir / "app.log"
        general_handler = RotatingFileHandler(
            filename=general_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(file_formatter)
        logger.addHandler(general_handler)
        
        # 2. Log de errores separado
        error_log_path = log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            filename=error_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        # 3. Log diario para análisis (rotación por tiempo)
        daily_log_path = log_dir / "daily.log"
        daily_handler = TimedRotatingFileHandler(
            filename=daily_log_path,
            when='midnight',
            interval=1,
            backupCount=30,  # Mantener 30 días
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        logger.addHandler(daily_handler)
    
    logger.info(f"Logger '{name}' configurado correctamente")
    return logger


class LoggerContext:
    """
    Context manager para logging con request_id
    Útil para rastrear requests individuales
    """
    
    def __init__(self, logger: logging.Logger, request_id: str):
        self.logger = logger
        self.request_id = request_id
    
    def __enter__(self):
        # Retorna el logger, que ya tiene el filtro RequestIdFilter
        # que añade request_id a cada record
        return self._create_logger_with_request_id()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def _create_logger_with_request_id(self):
        """Envuelve el logger para inyectar request_id automáticamente"""
        import functools
        
        class LoggerWrapper:
            def __init__(self, logger, request_id):
                self._logger = logger
                self._request_id = request_id
            
            def _log(self, level_name, msg, *args, **kwargs):
                method = getattr(self._logger, level_name)
                kwargs['extra'] = {'request_id': self._request_id}
                return method(msg, *args, **kwargs)
            
            def debug(self, msg, *args, **kwargs):
                return self._log('debug', msg, *args, **kwargs)
            
            def info(self, msg, *args, **kwargs):
                return self._log('info', msg, *args, **kwargs)
            
            def warning(self, msg, *args, **kwargs):
                return self._log('warning', msg, *args, **kwargs)
            
            def error(self, msg, *args, **kwargs):
                return self._log('error', msg, *args, **kwargs)
            
            def critical(self, msg, *args, **kwargs):
                return self._log('critical', msg, *args, **kwargs)
        
        return LoggerWrapper(self.logger, self.request_id)


class PredictionLogger:
    """
    Logger especializado para registrar predicciones
    Útil para análisis posterior y mejora del modelo
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.predictions_log = log_dir / "predictions.jsonl"
        
    def log_prediction(
        self,
        request_id: str,
        class_name: str,
        confidence: float,
        code: int,
        processing_time: float,
        image_size: tuple,
        is_confident: bool,
        alternatives: list = None
    ):
        """
        Registra una predicción en formato JSON Lines
        Perfecto para análisis posterior con pandas
        """
        import json
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "prediction": {
                "class_name": class_name,
                "confidence": confidence,
                "code": code,
                "is_confident": is_confident,
                "alternatives": alternatives or []
            },
            "metadata": {
                "processing_time_ms": round(processing_time * 1000, 2),
                "image_size": f"{image_size[0]}x{image_size[1]}"
            }
        }
        
        with open(self.predictions_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


# ================== INSTANCIA GLOBAL ==================
# Configuración por defecto para desarrollo
logger = setup_logger(
    name="waste_classifier",
    log_level="INFO",
    enable_console_logging=True,
    enable_file_logging=True
)

# Logger de predicciones
prediction_logger = PredictionLogger()