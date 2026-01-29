from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])


# Mapping Nutriscore vers score numérique
NUTRISCORE_SCORES = {"a": 100, "b": 80, "c": 60, "d": 40, "e": 20}


def enrich_product(raw_doc: dict, max_retries: int = 2) -> dict:
    """Enrichit un document RAW et retourne le document enrichi."""
    raw_id = str(raw_doc.get("_id", ""))
    payload = raw_doc.get("payload", {})
    
    for attempt in range(max_retries + 1):
        try:
            quality_score = _calculate_quality_score(payload)
            category = _categorize_product(payload)
            
            return {
                "raw_id": raw_id,
                "status": "success",
                "enriched_at": datetime.utcnow().isoformat() + "Z",
                "data": {
                    "code": payload.get("code", ""),
                    "product_name": payload.get("product_name", ""),
                    "brands": payload.get("brands", ""),
                    "quality_score": quality_score,
                    "category": category,
                    "nutriscore_grade": payload.get("nutriscore_grade", ""),
                    "nova_group": payload.get("nova_group"),
                }
            }
            
        except Exception as e:
            if attempt == max_retries:
                return {
                    "raw_id": raw_id,
                    "status": "failed",
                    "enriched_at": datetime.utcnow().isoformat() + "Z",
                    "data": {},
                    "error": {
                        "code": type(e).__name__,
                        "message": str(e)
                    }
                }
    
    # Fallback (ne devrait pas arriver)
    return {"raw_id": raw_id, "status": "pending", "enriched_at": None, "data": {}}


def _calculate_quality_score(payload: dict) -> int:
    """Score qualité (0-100) = nutriscore 50% + complétude 50%."""
    score = 0
    
    nutriscore = payload.get("nutriscore_grade", "").lower()
    score += NUTRISCORE_SCORES.get(nutriscore, 0) * 0.5
    
    completeness = payload.get("completeness", 0) or 0
    score += completeness * 50
    
    return int(min(score, 100))


def _categorize_product(payload: dict) -> str:
    """Détermine la catégorie principale."""
    main_cat = payload.get("main_category", "")
    if main_cat:
        return main_cat.replace("en:", "").replace("-", " ").title()
    
    categories = payload.get("categories_tags", [])
    if categories:
        return categories[0].replace("en:", "").replace("-", " ").title()
    
    return "Non catégorisé"
