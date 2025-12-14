#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Waste Classifier localmente
Uso: python run.py [--host HOST] [--port PORT] [--reload]
"""

import uvicorn
import argparse
import logging
from pathlib import Path

# Configurar logging básico antes de importar la app
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Ejecutar Waste Classifier API localmente"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host donde escuchar (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Puerto donde escuchar (default: 8000)"
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
    
    logger.info("=" * 60)
    logger.info("Iniciando Waste Classifier API")
    logger.info("=" * 60)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Workers: {args.workers}")
    logger.info("=" * 60)
    logger.info(f"Accede a: http://{args.host}:{args.port}")
    logger.info(f"Docs: http://{args.host}:{args.port}/docs")
    logger.info("=" * 60)
    
    # Ejecutar servidor
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()
