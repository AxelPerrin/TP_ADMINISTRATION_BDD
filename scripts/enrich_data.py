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
    from src.database.mongodb_manager import MongoDBManager
    from src.enrichment.enricher import enrich_product
    
    with MongoDBManager() as mongo:
        raw_docs = mongo.get_raw_documents_for_enrichment()
        logger.info(f"📥 {len(raw_docs)} documents RAW à enrichir")
        
        if not raw_docs:
            logger.warning("Aucun document à enrichir")
            return
        
        enriched_docs = []
        stats = {"success": 0, "failed": 0}
        
        for raw_doc in raw_docs:
            enriched = enrich_product(raw_doc)
            enriched_docs.append(enriched)
            stats[enriched["status"]] = stats.get(enriched["status"], 0) + 1
        
        count = mongo.insert_enriched_documents_batch(enriched_docs)
        
        logger.info(f"✅ Success: {stats['success']} | ❌ Failed: {stats['failed']}")
        logger.info(f"💾 {count} documents insérés dans MongoDB (ENRICHED)")


if __name__ == "__main__":
    main()
