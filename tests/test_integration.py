import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestAPIIntegration:
    def test_api_items_endpoint(self):
        from fastapi.testclient import TestClient
        from src.api.main import app
        
        client = TestClient(app)
        response = client.get("/items", params={"page": 1, "page_size": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
    
    def test_api_stats_endpoint(self):
        from fastapi.testclient import TestClient
        from src.api.main import app
        
        client = TestClient(app)
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "nutriscore_distribution" in data
    
    def test_api_item_detail_not_found(self):
        from fastapi.testclient import TestClient
        from src.api.main import app
        
        client = TestClient(app)
        response = client.get("/items/999999")
        
        assert response.status_code == 404


class TestSQLIntegration:
    def test_create_tables(self):
        from src.etl.models import create_tables, get_engine
        
        engine = create_tables()
        
        assert engine is not None
    
    def test_sql_session(self):
        from src.etl.models import get_session, Product
        
        session = get_session()
        count = session.query(Product).count()
        assert count >= 0
        session.close()
    
    def test_sql_query_with_filter(self):
        from src.etl.models import get_session, Product
        
        session = get_session()
        products = session.query(Product).filter(
            Product.nutriscore_grade == "a"
        ).limit(5).all()
        assert isinstance(products, list)
        session.close()


class TestPipelineIntegration:
    def test_enrichment_pipeline(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        raw_docs = [
            sample_raw_document,
            {
                "_id": "def456",
                "source": "openfoodfacts",
                "fetched_at": "2026-01-29T10:00:00Z",
                "raw_hash": "hash456",
                "payload": {
                    "code": "9876543210",
                    "product_name": "Produit Test 2",
                    "brands": "MarqueTest",
                    "nutriscore_grade": "c",
                    "completeness": 0.5
                }
            }
        ]
        
        enriched_docs = [enrich_product(doc) for doc in raw_docs]
        
        assert len(enriched_docs) == 2
        assert all(doc["status"] == "success" for doc in enriched_docs)
    
    def test_etl_pipeline_mapping(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        enriched = enrich_product(sample_raw_document)
        data = enriched["data"]
        
        sql_product = {
            "code": data["code"],
            "product_name": data["product_name"],
            "brand_name": data["brands"],
            "category_name": data["category"],
            "nutriscore_grade": data["nutriscore_grade"],
            "quality_score": data["quality_score"]
        }
        
        assert sql_product["code"] == "1234567890123"
        assert sql_product["quality_score"] == 80
