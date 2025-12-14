#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Waste Classifier localmente
Uso: python run.py [--host HOST] [--port PORT] [--reload] [--workers WORKERS]

Si no especificas --host o --port, se usan los valores de .env o defaults
"""

import uvicorn
import argparse
import logging
from pathlib import Path
from app.config import settings

# Configurar logging básico antes de importar la app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Ejecutar Waste Classifier API localmente"
    )
    parser.add_argument(
        "--host",
        default=None,  # None = usar valor de .env o settings default
        help=f"Host donde escuchar (default: {settings.HOST} desde .env)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,  # None = usar valor de .env o settings default
        help=f"Puerto donde escuchar (default: {settings.PORT} desde .env)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Habilitar auto-reload en cambios de código"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Número de workers (default: 1 para desarrollo)"
    )
    
    args = parser.parse_args()
    
    # Usar valores de CLI, o si no se proporcionan, usar settings de .env
    host = args.host if args.host is not None else settings.HOST
    port = args.port if args.port is not None else settings.PORT
    reload = args.reload
    workers = args.workers
    
    logger.info("=" * 60)
    logger.info("Iniciando Waste Classifier API")
    logger.info("=" * 60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Workers: {workers}")
    logger.info("=" * 60)
    logger.info(f"Accede a: http://{host}:{port}")
    logger.info(f"Docs: http://{host}:{port}/docs")
    logger.info("=" * 60)
    
    # Ejecutar servidor
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()
