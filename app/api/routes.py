from fastapi import APIRouter, File, UploadFile, HTTPException, Request
import time
from app.core.preprocessing import decode_image, validate_image
from app.core.postprocessing import PostProcessor
from app.models.mobilenet_classifier import MobileNetClassifier
from app.schemas.prediction import PredictionResponse, ESPResponse
from app.config import settings
from app.utils.logger import logger, LoggerContext, prediction_logger

router = APIRouter()

classifier = MobileNetClassifier()
classifier.load_model(settings.MODEL_PATH)
post_processor = PostProcessor()

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    """Endpoint completo con toda la información"""
    
    request_id = getattr(request.state, 'request_id', 'N/A')
    start_time = time.time()
    
    # Usar context manager para logging con request_id
    with LoggerContext(logger, request_id) as log:
        try:
            log.info(f"Recibiendo imagen: {file.filename}")
            
            # Validar tamaño
            contents = await file.read()
            if len(contents) > settings.MAX_FILE_SIZE:
                log.warning(f"Archivo muy grande: {len(contents)} bytes")
                raise HTTPException(status_code=413, detail="Archivo muy grande")
            
            log.debug(f"Tamaño del archivo: {len(contents)} bytes")
            
            # Preprocesamiento
            image = decode_image(contents)
            validate_image(image)
            log.debug(f"Imagen decodificada: {image.shape}")
            
            # Predicción del modelo
            raw_prediction = classifier.predict(image)
            log.info(
                f"Predicción cruda: {raw_prediction['class_name']} "
                f"({raw_prediction['confidence']:.2%})"
            )
            
            # Postprocesamiento
            processed_result = post_processor.process_prediction(raw_prediction)
            final_result = post_processor.apply_business_rules(processed_result)
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            log.info(
                f"Clasificación exitosa: {final_result['class_name']} | "
                f"Código: {final_result['code']} | "
                f"Tiempo: {processing_time:.3f}s"
            )
            
            # Loggear predicción para análisis
            if settings.LOG_PREDICTIONS:
                prediction_logger.log_prediction(
                    request_id=request_id,
                    class_name=final_result['class_name'],
                    confidence=final_result['confidence'],
                    code=final_result['code'],
                    processing_time=processing_time,
                    image_size=image.shape[:2],
                    is_confident=final_result['is_confident'],
                    alternatives=final_result['alternative_classes']
                )
            
            return final_result
            
        except HTTPException:
            raise
        except Exception as e:
            log.error(f"Error en predicción: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando imagen: {str(e)}"
            )


@router.get("/health")
async def health_check():
    """Health check con info de logging"""
    return {
        "status": "healthy",
        "model_loaded": classifier.model is not None,
        "logging": {
            "level": settings.LOG_LEVEL,
            "file_logging": settings.ENABLE_FILE_LOGGING,
            "predictions_logged": settings.LOG_PREDICTIONS
        }
    }