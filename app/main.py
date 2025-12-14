from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from app.api.routes import router
from app.config import settings
from app.utils.logger import setup_logger, logger

# Reconfigurar logger con settings
logger = setup_logger(
    name="waste_classifier",
    log_level=settings.LOG_LEVEL,
    log_dir=settings.LOG_DIR,
    enable_file_logging=settings.ENABLE_FILE_LOGGING,
    enable_console_logging=settings.ENABLE_CONSOLE_LOGGING
)

app = FastAPI(
    title="Waste Classifier API",
    version="1.0.0"
)

# ================== CONFIGURAR CORS ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo local. En producción especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== MIDDLEWARE DE LOGGING ==================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para loggear todas las requests
    """
    # Generar ID único para el request
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    # Timestamp de inicio
    start_time = time.time()
    
    # Log de request entrante
    logger.info(
        f"[{request_id}] {request.method} {request.url.path}",
        extra={'request_id': request_id}
    )
    
    # Procesar request
    try:
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Log de respuesta
        logger.info(
            f"[{request_id}] Status: {response.status_code} | "
            f"Time: {process_time:.3f}s",
            extra={'request_id': request_id}
        )
        
        # Añadir headers de debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Error: {str(e)} | Time: {process_time:.3f}s",
            exc_info=True,
            extra={'request_id': request_id}
        )
        raise

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Iniciando Waste Classifier API")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Log Directory: {settings.LOG_DIR}")
    logger.info(f"Modelo: {settings.MODEL_PATH}")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Apagando Waste Classifier API")

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "online", "service": "waste-classifier"}