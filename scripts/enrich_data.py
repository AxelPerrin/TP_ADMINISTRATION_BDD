"""
=============================================================================
SCRIPT D'ENRICHISSEMENT DES DONNÉES
=============================================================================
Ce script transforme les données brutes (RAW) en données enrichies (ENRICHED).

L'enrichissement ajoute des informations calculées :
- Score de qualité (0-100) basé sur le Nutriscore et la complétude
- Catégorie normalisée et formatée

FLUX DE DONNÉES :
MongoDB (products_raw) → enricher.py → MongoDB (products_enriched)

UTILISATION :
    python scripts/enrich_data.py

Ce script lit tous les documents de products_raw, les enrichit un par un,
et stocke les résultats dans products_enriched.
=============================================================================
"""

import sys
from pathlib import Path

from loguru import logger  # Librairie de logging avancée

# Ajouter le chemin racine au path Python
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configuration des logs avec format coloré
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")


def main():
    """
    Fonction principale du script d'enrichissement.
    
    Étapes :
    1. Se connecte à MongoDB
    2. Récupère tous les documents RAW
    3. Enrichit chaque document (calcul du score, catégorisation)
    4. Sauvegarde les documents enrichis dans la collection ENRICHED
    """
    # Import des modules nécessaires
    from src.database.mongodb_manager import MongoDBManager
    from src.enrichment.enricher import enrich_product
    
    # Utiliser le context manager pour gérer la connexion MongoDB
    with MongoDBManager() as mongo:
        # ÉTAPE 1 : Récupérer tous les documents bruts
        raw_docs = mongo.get_raw_documents_for_enrichment()
        logger.info(f"📥 {len(raw_docs)} documents RAW à enrichir")
        
        # Vérifier qu'il y a des documents à traiter
        if not raw_docs:
            logger.warning("Aucun document à enrichir")
            return
        
        # Listes et compteurs pour le traitement
        enriched_docs = []  # Documents enrichis à sauvegarder
        stats = {"success": 0, "failed": 0}  # Statistiques
        
        # ÉTAPE 2 : Enrichir chaque document
        for raw_doc in raw_docs:
            # Appeler la fonction d'enrichissement
            enriched = enrich_product(raw_doc)
            enriched_docs.append(enriched)
            # Mettre à jour les statistiques selon le statut
            stats[enriched["status"]] = stats.get(enriched["status"], 0) + 1
        
        # ÉTAPE 3 : Sauvegarder tous les documents enrichis en batch
        count = mongo.insert_enriched_documents_batch(enriched_docs)
        
        # Afficher le résumé
        logger.info(f"✅ Success: {stats['success']} | ❌ Failed: {stats['failed']}")
        logger.info(f"💾 {count} documents insérés dans MongoDB (ENRICHED)")


if __name__ == "__main__":
    main()
