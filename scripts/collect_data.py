import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import requests
from loguru import logger

# Ajouter le chemin racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configuration des logs
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")


class Collector:
    REQUIRED_FIELDS = ["code", "product_name"]
    
    def __init__(self, page_size: int = 100, delay: float = 1.0, timeout: int = 30, max_retries: int = 3):
        self.page_size = page_size
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.stats = {"collected": 0, "errors": 0, "timeouts": 0, "invalid_format": 0, "missing_data": 0}
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TP_BDD_Collector/1.0"})
    
    def _request(self, url: str, params: dict) -> Optional[dict]:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                self.stats["timeouts"] += 1
                self.stats["errors"] += 1
                logger.warning(f"Timeout (tentative {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    time.sleep(attempt * 2)
            except json.JSONDecodeError:
                self.stats["invalid_format"] += 1
                self.stats["errors"] += 1
                logger.warning("Format JSON invalide")
                return None
            except requests.exceptions.RequestException as e:
                self.stats["errors"] += 1
                logger.error(f"Erreur requête: {e}")
                if attempt < self.max_retries:
                    time.sleep(attempt * 2)
        return None
    
    def _is_valid(self, product: dict) -> bool:
        for field in self.REQUIRED_FIELDS:
            if not product.get(field):
                return False
        return True
    
    def collect(self, target_count: int = 300, categories: Optional[List[str]] = None, country: str = "france") -> List[dict]:
        from config.settings import MAIN_CATEGORIES, OPENFOODFACTS_SEARCH_URL
        
        if categories is None:
            categories = MAIN_CATEGORIES
        
        collected = []
        seen_codes = set()
        products_per_category = max(target_count // len(categories) + 10, 50)
        
        logger.info(f"🎯 Objectif: {target_count} produits")
        
        for category in categories:
            if len(collected) >= target_count:
                break
            
            logger.info(f"📂 Catégorie: {category}")
            page = 1
            category_count = 0
            
            while category_count < products_per_category and len(collected) < target_count:
                params = {
                    "action": "process",
                    "json": 1,
                    "page_size": self.page_size,
                    "page": page,
                    "tagtype_0": "categories",
                    "tag_contains_0": "contains",
                    "tag_0": category,
                    "tagtype_1": "countries",
                    "tag_contains_1": "contains",
                    "tag_1": country
                }
                
                data = self._request(OPENFOODFACTS_SEARCH_URL, params)
                if not data or not isinstance(data, dict):
                    break
                
                products = data.get("products", [])
                if not products:
                    break
                
                for raw_product in products:
                    if len(collected) >= target_count:
                        break
                    
                    if not isinstance(raw_product, dict):
                        self.stats["invalid_format"] += 1
                        continue
                    
                    code = raw_product.get("code", "")
                    if code in seen_codes:
                        continue
                    
                    if not self._is_valid(raw_product):
                        self.stats["missing_data"] += 1
                        continue
                    
                    collected.append(raw_product)
                    seen_codes.add(code)
                    category_count += 1
                    self.stats["collected"] += 1
                
                page += 1
                time.sleep(self.delay)
        
        logger.info(f"✅ Collectés: {self.stats['collected']} | Erreurs: {self.stats['errors']} | Timeouts: {self.stats['timeouts']} | Format invalide: {self.stats['invalid_format']} | Données manquantes: {self.stats['missing_data']}")
        return collected
    
    def save_to_mongodb(self, raw_products: List[dict]) -> int:
        from src.database.mongodb_manager import MongoDBManager
        
        with MongoDBManager() as mongo:
            count = mongo.insert_raw_documents_batch(raw_products, source="openfoodfacts")
            logger.info(f"💾 {count} documents insérés dans MongoDB (RAW)")
            return count


def main():
    parser = argparse.ArgumentParser(description="Collecte OpenFoodFacts")
    parser.add_argument("--count", "-n", type=int, default=300, help="Nombre minimum de produits (défaut: 300)")
    parser.add_argument("--categories", "-c", nargs="+", default=None, help="Catégories à collecter")
    parser.add_argument("--country", default="france", help="Pays cible (défaut: france)")
    parser.add_argument("--no-mongodb", action="store_true", help="Ne pas sauvegarder dans MongoDB")
    parser.add_argument("--output", "-o", type=str, default=None, help="Fichier JSON de sortie")
    
    args = parser.parse_args()
    
    collector = Collector()
    
    try:
        products = collector.collect(target_count=args.count, categories=args.categories, country=args.country)
        
        if not products:
            logger.error("Aucun produit collecté!")
            sys.exit(1)
        
        if args.output:
            output_path = Path(args.output) if Path(args.output).is_absolute() else ROOT_DIR / args.output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Sauvegardé dans: {output_path}")
        
        if not args.no_mongodb:
            try:
                collector.save_to_mongodb(products)
            except Exception as e:
                logger.warning(f"MongoDB non disponible: {e}")
        
        logger.success(f"✅ Collecte terminée: {len(products)} produits")
        
    except KeyboardInterrupt:
        logger.warning("Collecte interrompue")
        sys.exit(1)


if __name__ == "__main__":
    main()
