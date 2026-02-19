"""Module d'enrichissement des données."""

from datetime import datetime, timezone
from typing import Optional

NUTRISCORE_SCORES = {"a": 100, "b": 80, "c": 60, "d": 40, "e": 20}


def enrich_product(raw_doc: dict, max_retries: int = 2) -> dict:
    """Enrichit un document brut avec score qualité, catégorie, image et nutrition."""
    raw_id = str(raw_doc.get("_id", ""))
    payload = raw_doc.get("payload", {})
    
    for attempt in range(max_retries + 1):
        try:
            return {
                "raw_id": raw_id,
                "status": "success",
                "enriched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "data": {
                    "code": payload.get("code", ""),
                    "product_name": payload.get("product_name", ""),
                    "brands": payload.get("brands", ""),
                    "quality_score": _calculate_quality_score(payload),
                    "category": _categorize_product(payload),
                    "nutriscore_grade": payload.get("nutriscore_grade", ""),
                    "nova_group": payload.get("nova_group"),
                    "image_url": _extract_image_url(payload),
                    "nutrition": _extract_nutrition(payload),
                }
            }
        except Exception as e:
            if attempt == max_retries:
                return {
                    "raw_id": raw_id,
                    "status": "failed",
                    "enriched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "data": {},
                    "error": {"code": type(e).__name__, "message": str(e)}
                }
    
    return {"raw_id": raw_id, "status": "pending", "enriched_at": None, "data": {}}


def _calculate_quality_score(payload: dict) -> int:
    """Calcule le score qualité (0-100) basé sur Nutriscore + complétude."""
    nutriscore = payload.get("nutriscore_grade", "").lower()
    score = NUTRISCORE_SCORES.get(nutriscore, 0) * 0.5
    score += (payload.get("completeness", 0) or 0) * 50
    return int(min(score, 100))


def _categorize_product(payload: dict) -> str:
    """Détermine la catégorie principale du produit."""
    main_cat = payload.get("main_category", "")
    if main_cat:
        return main_cat.replace("en:", "").replace("-", " ").title()
    
    categories = payload.get("categories_tags", [])
    if categories:
        return categories[0].replace("en:", "").replace("-", " ").title()
    
    return "Non catégorisé"


def _extract_image_url(payload: dict) -> Optional[str]:
    """Extrait l'URL de l'image du produit."""
    return (
        payload.get("image_front_small_url") or
        payload.get("image_front_url") or
        payload.get("image_url") or
        payload.get("image_small_url")
    )


def _extract_nutrition(payload: dict) -> dict:
    """Extrait les données nutritionnelles pour 100g."""
    n = payload.get("nutriments", {})
    return {
        "energy_kcal": n.get("energy-kcal_100g"),
        "fat": n.get("fat_100g"),
        "saturated_fat": n.get("saturated-fat_100g"),
        "carbohydrates": n.get("carbohydrates_100g"),
        "sugars": n.get("sugars_100g"),
        "fiber": n.get("fiber_100g"),
        "proteins": n.get("proteins_100g"),
        "salt": n.get("salt_100g"),
    }
