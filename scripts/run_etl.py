#!/usr/bin/env python
"""
=============================================================================
SCRIPT ETL - CHARGEMENT DES DONNÉES VERS SQL
=============================================================================
Ce script exécute le pipeline ETL (Extract-Transform-Load) qui transfère
les données enrichies de MongoDB vers la base de données SQL.

ETL = Extract-Transform-Load :
- EXTRACT : Lit les données depuis MongoDB (products_enriched)
- TRANSFORM : Adapte les données au schéma SQL (normalisation)
- LOAD : Insère les données dans les tables SQL (products, brands, categories)

FLUX DE DONNÉES :
MongoDB (products_enriched) → ETL Pipeline → SQL (SQLite ou PostgreSQL)

UTILISATION :
    python scripts/run_etl.py

Après exécution, les données sont accessibles via l'API FastAPI
et le dashboard Streamlit.
=============================================================================
"""

import sys
from pathlib import Path

from loguru import logger  # Librairie de logging avancée

# Ajouter le chemin racine au path Python
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configuration des logs avec format coloré et timestamp
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")


def main():
    """
    Fonction principale qui exécute le pipeline ETL.
    
    Étapes :
    1. Importe et instancie le pipeline ETL
    2. Exécute le pipeline (extraction, transformation, chargement)
    3. Affiche un message de succès
    
    Le pipeline gère automatiquement :
    - La création des tables SQL si elles n'existent pas
    - La mise à jour des produits existants (idempotent)
    - Les rollbacks en cas d'erreur
    """
    # Import du pipeline ETL
    from src.etl.pipeline import ETLPipeline
    
    # Créer une instance du pipeline
    pipeline = ETLPipeline()
    
    # Exécuter le pipeline (extraction MongoDB → chargement SQL)
    pipeline.run()
    
    # Message de succès final
    logger.success("✅ ETL terminé")


if __name__ == "__main__":
    main()
