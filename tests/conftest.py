import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_raw_payload():
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
    return {
        "_id": "abc123",
        "source": "openfoodfacts",
        "fetched_at": "2026-01-29T10:00:00Z",
        "raw_hash": "hash123",
        "payload": sample_raw_payload
    }
