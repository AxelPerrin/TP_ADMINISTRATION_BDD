"""
=============================================================================
FIXTURES PYTEST - DONNÉES DE TEST RÉUTILISABLES
=============================================================================
Ce fichier définit les fixtures partagées entre tous les tests.

Les fixtures sont des fonctions qui fournissent des données ou des objets
pré-configurés aux tests. Elles permettent d'éviter la duplication de code
et de garantir des données cohérentes.
=============================================================================
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# =============================================================================
# FIXTURES DE DONNÉES PRODUIT
# =============================================================================

@pytest.fixture
def sample_raw_payload():
    """Payload brut typique d'un produit OpenFoodFacts."""
    return {
        "code": "1234567890123",
        "product_name": "Céréales Test",
        "brands": "TestBrand",
        "categories_tags": ["en:breakfast-cereals"],
        "main_category": "en:breakfast-cereals",
        "nutriscore_grade": "b",
        "nova_group": 3,
        "completeness": 0.8
    }


@pytest.fixture
def sample_raw_document(sample_raw_payload):
    """Document MongoDB RAW complet avec payload."""
    return {
        "_id": "abc123",
        "source": "openfoodfacts",
        "fetched_at": "2026-01-29T10:00:00Z",
        "raw_hash": "hash123",
        "payload": sample_raw_payload
    }


@pytest.fixture
def minimal_raw_document():
    """Document RAW avec données minimales (edge case)."""
    return {
        "_id": "minimal123",
        "source": "openfoodfacts",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_hash": "hash_minimal",
        "payload": {
            "code": "0000000000000",
            "product_name": ""
        }
    }


@pytest.fixture
def complete_raw_document():
    """Document RAW avec toutes les données possibles."""
    return {
        "_id": "complete456",
        "source": "openfoodfacts",
        "fetched_at": "2026-01-29T12:00:00Z",
        "raw_hash": "hash_complete",
        "payload": {
            "code": "9876543210123",
            "product_name": "Produit Complet Premium",
            "brands": "MarqueComplete",
            "categories_tags": ["en:beverages", "en:sodas"],
            "main_category": "en:beverages",
            "nutriscore_grade": "a",
            "nova_group": 1,
            "completeness": 1.0,
            "ecoscore_grade": "a",
            "ingredients_text": "Eau, sucre, arômes naturels"
        }
    }


@pytest.fixture
def invalid_nutriscore_document():
    """Document avec Nutriscore invalide."""
    return {
        "_id": "invalid789",
        "source": "openfoodfacts",
        "fetched_at": "2026-01-29T14:00:00Z",
        "raw_hash": "hash_invalid",
        "payload": {
            "code": "1111111111111",
            "product_name": "Produit Sans Nutriscore",
            "brands": "MarqueX",
            "nutriscore_grade": "z",  # Invalide
            "completeness": 0.3
        }
    }


# =============================================================================
# FIXTURES POUR LES TESTS API
# =============================================================================

@pytest.fixture
def api_client():
    """Client de test FastAPI."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)


# =============================================================================
# FIXTURES POUR LES TESTS SQL
# =============================================================================

@pytest.fixture
def db_session():
    """Session SQLAlchemy pour les tests."""
    from src.etl.models import get_session
    session = get_session()
    yield session
    session.close()


# =============================================================================
# PARAMÈTRES DE TEST
# =============================================================================

@pytest.fixture(params=["a", "b", "c", "d", "e"])
def valid_nutriscore(request):
    """Tous les nutriscores valides."""
    return request.param


@pytest.fixture(params=[0.0, 0.25, 0.5, 0.75, 1.0])
def valid_completeness(request):
    """Différentes valeurs de complétude."""
    return request.param
