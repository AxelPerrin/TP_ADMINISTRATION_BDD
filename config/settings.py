import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# MongoDB
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "openfoodfacts")
MONGODB_URI = os.getenv("MONGODB_URI", f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}")

COLLECTION_RAW = "products_raw"
COLLECTION_ENRICHED = "products_enriched"

# PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "openfoodfacts_analytics")

POSTGRES_URI = os.getenv(
    "POSTGRES_URI",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

# SQLite
SQLITE_PATH = DATA_DIR / "openfoodfacts.db"
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

# OpenFoodFacts API
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org"
OPENFOODFACTS_SEARCH_URL = f"{OPENFOODFACTS_API_URL}/cgi/search.pl"
OPENFOODFACTS_PRODUCT_URL = f"{OPENFOODFACTS_API_URL}/api/v2/product"

# Collecte
COLLECT_PAGE_SIZE = 100
COLLECT_MAX_PRODUCTS = 1000
COLLECT_DELAY_SECONDS = 1

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"

# Dashboard
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8501))

NUTRISCORE_GRADES = ["a", "b", "c", "d", "e"]
NUTRISCORE_COLORS = {
    "a": "#038141",
    "b": "#85BB2F",
    "c": "#FECB02",
    "d": "#EE8100",
    "e": "#E63E11"
}

MAIN_CATEGORIES = [
    "breakfast-cereals",
    "dairy",
    "beverages",
    "snacks",
    "bread",
    "fruits",
    "vegetables",
    "meat",
    "fish",
    "frozen-foods"
]
