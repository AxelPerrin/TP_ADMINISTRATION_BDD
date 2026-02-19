"""
=============================================================================
TESTS UNITAIRES - VALIDATION DES COMPOSANTS INDIVIDUELS
=============================================================================
Tests des fonctions et modules individuellement, sans dépendances externes.

Ces tests vérifient que chaque composant fonctionne correctement en isolation.
=============================================================================
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# =============================================================================
# TESTS DE PARSING DES DONNÉES
# =============================================================================

class TestParsing:
    """Tests de parsing et extraction des données produit."""
    
    def test_parse_product_code(self, sample_raw_payload):
        """Vérifie l'extraction du code-barres."""
        assert sample_raw_payload.get("code") == "1234567890123"
    
    def test_parse_product_name(self, sample_raw_payload):
        """Vérifie l'extraction du nom produit."""
        assert sample_raw_payload.get("product_name") == "Céréales Test"
    
    def test_parse_nutriscore(self, sample_raw_payload):
        """Vérifie que le Nutriscore est valide."""
        grade = sample_raw_payload.get("nutriscore_grade", "").lower()
        assert grade in ["a", "b", "c", "d", "e", ""]
    
    def test_parse_empty_payload(self):
        """Test avec payload vide."""
        empty = {}
        assert empty.get("code", "") == ""
        assert empty.get("product_name", "Inconnu") == "Inconnu"
    
    def test_parse_nova_group_range(self, sample_raw_payload):
        """Vérifie que NOVA est dans la plage valide 1-4."""
        nova = sample_raw_payload.get("nova_group")
        if nova is not None:
            assert 1 <= nova <= 4
    
    def test_parse_completeness_range(self, sample_raw_payload):
        """Vérifie que la complétude est entre 0 et 1."""
        completeness = sample_raw_payload.get("completeness", 0)
        assert 0 <= completeness <= 1


# =============================================================================
# TESTS D'ENRICHISSEMENT
# =============================================================================

class TestEnrichment:
    """Tests du module d'enrichissement des données."""
    
    def test_enrich_product_success(self, sample_raw_document):
        """Vérifie l'enrichissement réussi d'un produit standard."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        
        assert result["status"] == "success"
        assert result["raw_id"] == "abc123"
        assert "data" in result
        assert "enriched_at" in result
    
    def test_enrich_quality_score(self, sample_raw_document):
        """Vérifie le calcul du score qualité."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        assert result["data"]["quality_score"] == 80
    
    def test_enrich_quality_score_range(self, sample_raw_document):
        """Vérifie que le score qualité est entre 0 et 100."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        score = result["data"]["quality_score"]
        assert 0 <= score <= 100
    
    def test_enrich_categorization(self, sample_raw_document):
        """Vérifie la catégorisation du produit."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        assert result["data"]["category"] == "Breakfast Cereals"
    
    def test_enrich_minimal_document(self, minimal_raw_document):
        """Test d'enrichissement avec données minimales."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(minimal_raw_document)
        
        # Doit réussir même avec données minimales
        assert result["status"] == "success"
        assert result["data"]["code"] == "0000000000000"
    
    def test_enrich_complete_document(self, complete_raw_document):
        """Test d'enrichissement avec données complètes."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(complete_raw_document)
        
        assert result["status"] == "success"
        # Nutriscore A + completeness 1.0 = score élevé
        assert result["data"]["quality_score"] >= 90
    
    def test_enrich_preserves_original_data(self, sample_raw_document):
        """Vérifie que les données originales sont préservées."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        data = result["data"]
        
        assert data["code"] == sample_raw_document["payload"]["code"]
        assert data["product_name"] == sample_raw_document["payload"]["product_name"]
        assert data["brands"] == sample_raw_document["payload"]["brands"]
    
    def test_enrich_timestamp_format(self, sample_raw_document):
        """Vérifie le format ISO 8601 du timestamp."""
        from src.enrichment.enricher import enrich_product
        
        result = enrich_product(sample_raw_document)
        timestamp = result["enriched_at"]
        
        assert timestamp.endswith("Z")
        assert "T" in timestamp


# =============================================================================
# TESTS DE NORMALISATION
# =============================================================================

class TestNormalization:
    """Tests de normalisation des données."""
    
    def test_normalize_category_name(self):
        """Vérifie la normalisation du nom de catégorie."""
        from src.enrichment.enricher import _categorize_product
        
        payload = {"main_category": "en:breakfast-cereals"}
        result = _categorize_product(payload)
        
        assert result == "Breakfast Cereals"
    
    def test_normalize_empty_category(self):
        """Test avec catégorie vide."""
        from src.enrichment.enricher import _categorize_product
        
        payload = {}
        result = _categorize_product(payload)
        
        assert result == "Non catégorisé"
    
    def test_normalize_various_categories(self):
        """Test de normalisation de différentes catégories."""
        from src.enrichment.enricher import _categorize_product
        
        test_cases = [
            ({"main_category": "en:beverages"}, "Beverages"),
            ({"main_category": "en:dairy"}, "Dairy"),
            ({"main_category": "en:snacks"}, "Snacks"),
            ({"main_category": ""}, "Non catégorisé"),
        ]
        
        for payload, expected in test_cases:
            result = _categorize_product(payload)
            assert result == expected, f"Failed for {payload}"
    
    def test_normalize_category_with_prefix(self):
        """Vérifie que le préfixe 'en:' est bien supprimé."""
        from src.enrichment.enricher import _categorize_product
        
        payload = {"main_category": "en:test-category"}
        result = _categorize_product(payload)
        
        assert not result.startswith("en:")


# =============================================================================
# TESTS DE CALCUL DU SCORE QUALITÉ
# =============================================================================

class TestQualityScore:
    """Tests du calcul du score qualité."""
    
    def test_quality_score_nutriscore_a(self):
        """Nutriscore A devrait donner un score élevé."""
        from src.enrichment.enricher import _calculate_quality_score
        
        payload = {"nutriscore_grade": "a", "completeness": 1.0}
        score = _calculate_quality_score(payload)
        
        assert score >= 90
    
    def test_quality_score_nutriscore_e(self):
        """Nutriscore E devrait donner un score plus bas que A."""
        from src.enrichment.enricher import _calculate_quality_score
        
        payload_e = {"nutriscore_grade": "e", "completeness": 1.0}
        payload_a = {"nutriscore_grade": "a", "completeness": 1.0}
        
        score_e = _calculate_quality_score(payload_e)
        score_a = _calculate_quality_score(payload_a)
        
        # E doit être inférieur à A
        assert score_e < score_a
        assert score_e <= 70  # Score E avec complétude 1.0
    
    def test_quality_score_completeness_impact(self):
        """La complétude doit impacter le score."""
        from src.enrichment.enricher import _calculate_quality_score
        
        high_completeness = {"nutriscore_grade": "b", "completeness": 1.0}
        low_completeness = {"nutriscore_grade": "b", "completeness": 0.2}
        
        score_high = _calculate_quality_score(high_completeness)
        score_low = _calculate_quality_score(low_completeness)
        
        assert score_high >= score_low
    
    @pytest.mark.parametrize("nutriscore,min_expected", [
        ("a", 80),
        ("b", 60),
        ("c", 45),
        ("d", 30),
        ("e", 15),
    ])
    def test_quality_score_by_nutriscore(self, nutriscore, min_expected):
        """Test paramétré du score par Nutriscore."""
        from src.enrichment.enricher import _calculate_quality_score
        
        payload = {"nutriscore_grade": nutriscore, "completeness": 0.8}
        score = _calculate_quality_score(payload)
        
        assert score >= min_expected


# =============================================================================
# TESTS DU MAPPING ETL
# =============================================================================

class TestMappingETL:
    """Tests du mapping entre MongoDB et SQL."""
    
    def test_mapping_enriched_to_sql(self, sample_raw_document):
        """Vérifie que tous les champs SQL sont présents."""
        from src.enrichment.enricher import enrich_product
        
        enriched = enrich_product(sample_raw_document)
        data = enriched["data"]
        
        required_fields = ["code", "product_name", "brands", "category", 
                          "nutriscore_grade", "quality_score"]
        
        for field in required_fields:
            assert field in data, f"Champ manquant : {field}"
    
    def test_raw_hash_computation(self):
        """Vérifie la cohérence du calcul de hash."""
        from src.database.mongodb_manager import compute_raw_hash
        
        payload1 = {"code": "123", "name": "Test"}
        payload2 = {"code": "123", "name": "Test"}
        payload3 = {"code": "456", "name": "Other"}
        
        hash1 = compute_raw_hash(payload1)
        hash2 = compute_raw_hash(payload2)
        hash3 = compute_raw_hash(payload3)
        
        # Même payload = même hash
        assert hash1 == hash2
        # Payload différent = hash différent
        assert hash1 != hash3
    
    def test_raw_hash_deterministic(self):
        """Le hash doit être déterministe."""
        from src.database.mongodb_manager import compute_raw_hash
        
        payload = {"code": "123", "data": {"nested": "value"}}
        
        hashes = [compute_raw_hash(payload) for _ in range(5)]
        assert len(set(hashes)) == 1  # Tous identiques
    
    def test_mapping_handles_missing_fields(self):
        """Test de mapping avec champs manquants."""
        from src.enrichment.enricher import enrich_product
        
        incomplete_doc = {
            "_id": "incomplete",
            "source": "test",
            "fetched_at": "2026-01-01T00:00:00Z",
            "raw_hash": "hash",
            "payload": {"code": "123"}
        }
        
        result = enrich_product(incomplete_doc)
        
        # Ne doit pas crasher, doit retourner des valeurs par défaut
        assert result["status"] == "success"
        assert result["data"]["product_name"] == ""
        assert result["data"]["brands"] == ""


# =============================================================================
# TESTS DE VALIDATION DES DONNÉES
# =============================================================================

class TestDataValidation:
    """Tests de validation des formats de données."""
    
    def test_code_format_13_digits(self, sample_raw_payload):
        """Le code-barres doit avoir 13 chiffres (EAN-13)."""
        code = sample_raw_payload.get("code", "")
        assert len(code) == 13
        assert code.isdigit()
    
    def test_nutriscore_lowercase(self, sample_raw_payload):
        """Le Nutriscore doit être en minuscules."""
        grade = sample_raw_payload.get("nutriscore_grade", "")
        if grade:
            assert grade == grade.lower()
    
    def test_brands_not_empty_if_present(self, sample_raw_payload):
        """Si brands est présent, il ne doit pas être vide."""
        brands = sample_raw_payload.get("brands")
        if brands is not None:
            assert len(brands) > 0
