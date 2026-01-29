#!/usr/bin/env python
import sys
from pathlib import Path

from loguru import logger

# Ajouter le chemin racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configuration des logs
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")


def main():
    from src.etl.pipeline import ETLPipeline
    
    pipeline = ETLPipeline()
    pipeline.run()
    
    logger.success("✅ ETL terminé")


if __name__ == "__main__":
    main()
