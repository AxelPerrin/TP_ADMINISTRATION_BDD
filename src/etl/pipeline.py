from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

from src.database.mongodb_manager import MongoDBManager
from src.etl.models import get_session, create_tables, Product, Brand, Category


class ETLPipeline:
    def __init__(self):
        self.session: Optional[Session] = None
        self.brands_cache = {}
        self.categories_cache = {}
    
    def run(self):
        logger.info("Démarrage ETL")
        
        create_tables()
        self.session = get_session()
        
        try:
            with MongoDBManager() as mongo:
                enriched_docs = mongo.get_enriched_documents(status="success", limit=10000)
            
            logger.info(f"📥 {len(enriched_docs)} documents extraits")
            
            loaded = 0
            for doc in enriched_docs:
                if self._load_product(doc):
                    loaded += 1
            
            self.session.commit()
            logger.info(f"✅ {loaded} produits chargés en SQL")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Erreur ETL: {e}")
            raise
        finally:
            self.session.close()
    
    def _get_or_create_brand(self, name: str) -> Optional[Brand]:
        if not name:
            return None
        
        name = name.strip()[:255]
        
        if name in self.brands_cache:
            return self.brands_cache[name]
        
        brand = self.session.query(Brand).filter_by(name=name).first()
        if not brand:
            brand = Brand(name=name)
            self.session.add(brand)
            self.session.flush()
        
        self.brands_cache[name] = brand
        return brand
    
    def _get_or_create_category(self, name: str) -> Optional[Category]:
        if not name:
            return None
        
        name = name.strip()[:255]
        
        if name in self.categories_cache:
            return self.categories_cache[name]
        
        category = self.session.query(Category).filter_by(name=name).first()
        if not category:
            category = Category(name=name)
            self.session.add(category)
            self.session.flush()
        
        self.categories_cache[name] = category
        return category
    
    def _load_product(self, enriched_doc: dict) -> bool:
        """Charge un produit en SQL (idempotent)."""
        data = enriched_doc.get("data", {})
        code = data.get("code")
        
        if not code:
            return False
        
        existing = self.session.query(Product).filter_by(code=code).first()
        
        if existing:
            existing.product_name = data.get("product_name", "")[:500]
            existing.nutriscore_grade = (data.get("nutriscore_grade") or "")[:1]
            existing.nova_group = data.get("nova_group")
            existing.quality_score = data.get("quality_score")
            
            brand = self._get_or_create_brand(data.get("brands", ""))
            category = self._get_or_create_category(data.get("category", ""))
            existing.brand = brand
            existing.category = category
        else:
            brand = self._get_or_create_brand(data.get("brands", ""))
            category = self._get_or_create_category(data.get("category", ""))
            
            product = Product(
                code=code,
                product_name=data.get("product_name", "")[:500],
                brand=brand,
                category=category,
                nutriscore_grade=(data.get("nutriscore_grade") or "")[:1],
                nova_group=data.get("nova_group"),
                quality_score=data.get("quality_score")
            )
            self.session.add(product)
        
        return True
