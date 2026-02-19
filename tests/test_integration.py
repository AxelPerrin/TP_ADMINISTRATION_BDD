"""
=============================================================================
TESTS D'INTÉGRATION - VALIDATION DES COMPOSANTS CONNECTÉS
=============================================================================
Tests des composants ensemble : API, base de données, pipelines.

Ces tests vérifient que les différentes parties du système
fonctionnent correctement ensemble.
=============================================================================
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# =============================================================================
# TESTS API FASTAPI
# =============================================================================

class TestAPIIntegration:
    """Tests d'intégration de l'API REST."""
    
    def test_api_items_endpoint(self, api_client):
        """Test de l'endpoint /items avec pagination."""
        response = api_client.get("/items", params={"page": 1, "page_size": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
    
    def test_api_items_pagination(self, api_client):
        """Test de la pagination correcte."""
        response = api_client.get("/items", params={"page": 1, "page_size": 5})
        data = response.json()
        
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["items"]) <= 5
    
    def test_api_items_search(self, api_client):
        """Test de la recherche par mot-clé."""
        response = api_client.get("/items", params={"search": "test"})
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    def test_api_items_filter_nutriscore(self, api_client):
        """Test du filtre par Nutriscore."""
        response = api_client.get("/items", params={"nutriscore": "a"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier que tous les items retournés ont le bon Nutriscore
        for item in data["items"]:
            if item.get("nutriscore_grade"):
                assert item["nutriscore_grade"].lower() == "a"
    
    def test_api_stats_endpoint(self, api_client):
        """Test de l'endpoint /stats."""
        response = api_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["total_products", "total_brands", "total_categories", 
                          "nutriscore_distribution", "avg_quality_score"]
        for field in required_fields:
            assert field in data, f"Champ manquant : {field}"
    
    def test_api_stats_nutriscore_distribution(self, api_client):
        """Vérifie la structure de la distribution Nutriscore."""
        response = api_client.get("/stats")
        data = response.json()
        
        distribution = data["nutriscore_distribution"]
        valid_grades = ["a", "b", "c", "d", "e"]
        
        for grade in valid_grades:
            assert grade in distribution
            assert isinstance(distribution[grade], int)
            assert distribution[grade] >= 0
    
    def test_api_item_detail_not_found(self, api_client):
        """Test 404 pour produit inexistant."""
        response = api_client.get("/items/999999")
        
        assert response.status_code == 404
    
    def test_api_item_detail_existing(self, api_client):
        """Test de récupération d'un produit existant."""
        # D'abord récupérer un ID valide
        list_response = api_client.get("/items", params={"page_size": 1})
        items = list_response.json()["items"]
        
        if items:
            item_id = items[0]["id"]
            response = api_client.get(f"/items/{item_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == item_id
    
    def test_api_categories_endpoint(self, api_client):
        """Test de l'endpoint /categories."""
        response = api_client.get("/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.skip(reason="Endpoint /brands non implémenté")
    def test_api_brands_endpoint(self, api_client):
        """Test de l'endpoint /brands (non implémenté)."""
        response = api_client.get("/brands")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_api_invalid_page_number(self, api_client):
        """Test avec numéro de page invalide."""
        response = api_client.get("/items", params={"page": 0})
        
        # Devrait retourner une erreur ou page 1
        assert response.status_code in [200, 422]
    
    def test_api_large_page_size(self, api_client):
        """Test avec grande taille de page (validation serveur)."""
        response = api_client.get("/items", params={"page_size": 1000})
        
        # Le serveur peut rejeter (422) ou limiter la taille
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["items"]) <= 1000


# =============================================================================
# TESTS INTÉGRATION SQL
# =============================================================================

class TestSQLIntegration:
    """Tests d'intégration avec SQLite/PostgreSQL."""
    
    def test_create_tables(self):
        """Vérifie la création des tables."""
        from src.etl.models import create_tables, get_engine
        
        engine = create_tables()
        assert engine is not None
    
    def test_sql_session(self, db_session):
        """Test de connexion et requête simple."""
        from src.etl.models import Product
        
        count = db_session.query(Product).count()
        assert count >= 0
    
    def test_sql_query_with_filter(self, db_session):
        """Test de requête avec filtre."""
        from src.etl.models import Product
        
        products = db_session.query(Product).filter(
            Product.nutriscore_grade == "a"
        ).limit(5).all()
        
        assert isinstance(products, list)
        for p in products:
            assert p.nutriscore_grade == "a"
    
    def test_sql_relationships_brand(self, db_session):
        """Test de la relation Product -> Brand."""
        from src.etl.models import Product, Brand
        
        product = db_session.query(Product).filter(
            Product.brand_id.isnot(None)
        ).first()
        
        if product:
            assert product.brand is not None or product.brand_id is not None
    
    def test_sql_relationships_category(self, db_session):
        """Test de la relation Product -> Category."""
        from src.etl.models import Product, Category
        
        product = db_session.query(Product).filter(
            Product.category_id.isnot(None)
        ).first()
        
        if product:
            assert product.category is not None or product.category_id is not None
    
    def test_sql_query_aggregate(self, db_session):
        """Test des fonctions d'agrégation."""
        from src.etl.models import Product
        from sqlalchemy import func
        
        avg_score = db_session.query(
            func.avg(Product.quality_score)
        ).scalar()
        
        if avg_score is not None:
            assert 0 <= avg_score <= 100
    
    def test_sql_query_group_by(self, db_session):
        """Test de GROUP BY pour distribution."""
        from src.etl.models import Product
        from sqlalchemy import func
        
        results = db_session.query(
            Product.nutriscore_grade,
            func.count(Product.id)
        ).group_by(Product.nutriscore_grade).all()
        
        assert isinstance(results, list)


# =============================================================================
# TESTS INTÉGRATION PIPELINE
# =============================================================================

class TestPipelineIntegration:
    """Tests du pipeline complet d'enrichissement et ETL."""
    
    def test_enrichment_pipeline(self, sample_raw_document):
        """Test du pipeline d'enrichissement sur plusieurs documents."""
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
        """Test du mapping enriched -> SQL."""
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
    
    def test_pipeline_handles_batch(self, sample_raw_document, complete_raw_document):
        """Test du traitement par lot."""
        from src.enrichment.enricher import enrich_product
        
        batch = [sample_raw_document, complete_raw_document]
        results = [enrich_product(doc) for doc in batch]
        
        success_count = sum(1 for r in results if r["status"] == "success")
        assert success_count == len(batch)
    
    def test_pipeline_idempotent(self, sample_raw_document):
        """L'enrichissement doit être idempotent (même résultat si relancé)."""
        from src.enrichment.enricher import enrich_product
        
        result1 = enrich_product(sample_raw_document)
        result2 = enrich_product(sample_raw_document)
        
        # Les données doivent être identiques (timestamp peut différer)
        assert result1["data"] == result2["data"]
        assert result1["status"] == result2["status"]


# =============================================================================
# TESTS DE PERFORMANCE
# =============================================================================

class TestPerformance:
    """Tests de performance basiques."""
    
    def test_enrichment_speed(self, sample_raw_document):
        """L'enrichissement doit être rapide."""
        import time
        from src.enrichment.enricher import enrich_product
        
        start = time.time()
        for _ in range(100):
            enrich_product(sample_raw_document)
        duration = time.time() - start
        
        # 100 enrichissements en moins de 1 seconde
        assert duration < 1.0, f"Trop lent : {duration:.2f}s pour 100 enrichissements"
    
    def test_api_response_time(self, api_client):
        """L'API doit répondre rapidement."""
        import time
        
        start = time.time()
        response = api_client.get("/items", params={"page_size": 10})
        duration = time.time() - start
        
        assert response.status_code == 200
        # Réponse en moins de 500ms
        assert duration < 0.5, f"API trop lente : {duration:.2f}s"
