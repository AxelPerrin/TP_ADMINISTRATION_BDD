import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestParsing:
    def test_parse_product_code(self, sample_raw_payload):
        assert sample_raw_payload.get("code") == "1234567890123"
    
    def test_parse_product_name(self, sample_raw_payload):
        assert sample_raw_payload.get("product_name") == "Céréales Test"
    
    def test_parse_nutriscore(self, sample_raw_payload):
        grade = sample_raw_payload.get("nutriscore_grade", "").lower()
        assert grade in ["a", "b", "c", "d", "e", ""]


class TestEnrichment:
    def test_enrich_product_success(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        
        assert result["status"] == "success"
        assert result["raw_id"] == "abc123"
        assert "data" in result
        assert "enriched_at" in result
    
    def test_enrich_quality_score(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        assert result["data"]["quality_score"] == 80
    
    def test_enrich_categorization(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        
        assert result["data"]["category"] == "Breakfast Cereals"


class TestNormalization:
    def test_normalize_category_name(self):
        from src.enrichment.enricher import _categorize_product
        
        payload = {"main_category": "en:breakfast-cereals"}
        result = _categorize_product(payload)
        
        assert result == "Breakfast Cereals"
    
    def test_normalize_empty_category(self):
        from src.enrichment.enricher import _categorize_product
        
        payload = {}
        result = _categorize_product(payload)
        
        assert result == "Non catégorisé"


class TestMappingETL:
    def test_mapping_enriched_to_sql(self, sample_raw_document):
        from src.enrichment.enricher import enrich_product
        
        enriched = enrich_product(sample_raw_document)
        data = enriched["data"]
        
        # Vérifier que tous les champs nécessaires pour SQL sont présents
        assert "code" in data
        assert "product_name" in data
        assert "brands" in data
        assert "category" in data
        assert "nutriscore_grade" in data
        assert "quality_score" in data
    
    def test_raw_hash_computation(self):
        from src.database.mongodb_manager import compute_raw_hash
        
        payload1 = {"code": "123", "name": "Test"}
        payload2 = {"code": "123", "name": "Test"}
        payload3 = {"code": "456", "name": "Other"}
        
        hash1 = compute_raw_hash(payload1)
        hash2 = compute_raw_hash(payload2)
        hash3 = compute_raw_hash(payload3)
        
        assert hash1 == hash2
        assert hash1 != hash3
