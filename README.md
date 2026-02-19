# TP Administration BDD

## Sujet 3 — Produits alimentaires & qualité nutritionnelle

Pipeline de traitement de données alimentaires : collecte depuis OpenFoodFacts, enrichissement, stockage relationnel et visualisation via dashboard.

---

## 📦 Installation

```bash
# Cloner le dépôt
git clone https://github.com/[user]/TP_ADMINISTRATION_BDD.git
cd TP_ADMINISTRATION_BDD

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
```

### Prérequis
- Python 3.9+
- MongoDB 4.4+ (stockage RAW et ENRICHED)
- PostgreSQL 17 (base analytique)

---

## 🏗️ Architecture

```
┌──────────────────┐
│ OpenFoodFacts API│
└────────┬─────────┘
         │ collect_data.py
         ▼
┌──────────────────┐
│   MongoDB RAW    │  ← Données brutes JSON
└────────┬─────────┘
         │ enrich_data.py
         ▼
┌──────────────────┐
│ MongoDB ENRICHED │  ← + quality_score, image_url, nutrition
└────────┬─────────┘
         │ run_etl.py
         ▼
┌──────────────────┐
│   PostgreSQL     │  ← Modèle relationnel normalisé (3NF)
│   4 tables       │     products, brands, categories, nutrition_facts
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    FastAPI       │  ← REST API (port 8000)
│    /items, /stats│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Streamlit     │  ← Dashboard interactif (port 8501)
└──────────────────┘
```

---

## 📁 Structure du projet

```
TP_ADMINISTRATION_BDD/
├── config/settings.py           # Configuration centralisée
├── scripts/
│   ├── collect_data.py          # Collecte depuis OpenFoodFacts
│   ├── enrich_data.py           # Enrichissement des données
│   └── run_etl.py               # ETL MongoDB → PostgreSQL
├── src/
│   ├── database/
│   │   └── mongodb_manager.py   # Gestionnaire MongoDB (RAW/ENRICHED)
│   ├── enrichment/
│   │   └── enricher.py          # Calcul quality_score, extraction nutrition
│   ├── etl/
│   │   ├── models.py            # Modèles SQLAlchemy (4 tables)
│   │   └── pipeline.py          # Pipeline ETL
│   ├── api/
│   │   └── main.py              # API REST FastAPI
│   └── dashboard/
│       └── app.py               # Dashboard Streamlit
├── tests/
│   ├── conftest.py              # Fixtures pytest
│   ├── test_unit.py             # Tests unitaires
│   └── test_integration.py      # Tests d'intégration
├── schema.sql                   # Schéma SQL de référence
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

Créer un fichier `.env` à la racine :

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=openfoodfacts

# PostgreSQL (requis)
USE_SQLITE=false
POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/openfoodfacts_analytics
```

---

## 🚀 Commandes

### Pipeline complet
```bash
# 1. Collecte → MongoDB RAW (300 produits minimum)
python scripts/collect_data.py --count 300

# 2. Enrichissement → MongoDB ENRICHED
python scripts/enrich_data.py

# 3. ETL → PostgreSQL
python scripts/run_etl.py

# 4. API (terminal séparé)
uvicorn src.api.main:app --reload --port 8000

# 5. Dashboard (terminal séparé)
streamlit run src/dashboard/app.py

# 6. Tests
pytest tests/ -v
```

---

## 🔗 URLs après lancement

| Service | URL |
|---------|-----|
| **API Documentation** | http://localhost:8000/docs |
| **API (Swagger)** | http://localhost:8000/redoc |
| **Dashboard** | http://localhost:8501 |

---

## 📖 Détail des scripts

### collect_data.py
```bash
python scripts/collect_data.py --count 300           # Collecte 300 produits
python scripts/collect_data.py --categories "snacks" # Catégorie spécifique
```

### enrich_data.py
```bash
python scripts/enrich_data.py
# → Ajoute quality_score, image_url et nutrition à chaque produit
```

### run_etl.py
```bash
python scripts/run_etl.py
# → Transfère MongoDB ENRICHED → PostgreSQL (4 tables normalisées)
```

---

## 🔍 Vérification des données

```bash
# Vérifier MongoDB
python -c "from src.database.mongodb_manager import MongoDBManager; m=MongoDBManager(); print(f'RAW: {m.raw_collection.count_documents({})}'); print(f'ENRICHED: {m.enriched_collection.count_documents({})}')"

# Vérifier PostgreSQL
python -c "from src.etl.models import get_session, Product, Brand, Category, NutritionFacts; s=get_session(); print(f'Produits: {s.query(Product).count()}'); print(f'Marques: {s.query(Brand).count()}'); print(f'Categories: {s.query(Category).count()}'); print(f'Nutrition: {s.query(NutritionFacts).count()}')"
```

---

## 🔧 Choix techniques

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Collecte** | `requests` | Simple, fiable |
| **Stockage RAW** | MongoDB | Flexible, JSON natif, données hétérogènes |
| **Stockage SQL** | PostgreSQL 17 | Jointures, index, agrégations performantes |
| **ORM** | SQLAlchemy | Abstraction, migrations, relations |
| **API** | FastAPI | Performant, async, documentation auto |
| **Dashboard** | Streamlit | Rapide à développer, interactif |
| **Tests** | pytest | Standard Python, fixtures |

---

## 📊 Schéma SQL (PostgreSQL)

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   brands    │       │    products     │       │ nutrition_facts │
├─────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)     │◄──────│ brand_id (FK)   │       │ id (PK)         │
│ name (UQ)   │       │ category_id(FK) │──────►│ product_id (FK) │
└─────────────┘       │ code (UQ)       │       │ energy_kcal     │
                      │ product_name    │       │ fat             │
┌─────────────┐       │ image_url       │       │ saturated_fat   │
│ categories  │       │ nutriscore_grade│       │ carbohydrates   │
├─────────────┤       │ nova_group      │       │ sugars          │
│ id (PK)     │◄──────│ quality_score   │       │ fiber           │
│ name (UQ)   │       │ created_at      │       │ proteins        │
└─────────────┘       └─────────────────┘       │ salt            │
                                                └─────────────────┘
```

### Normalisation 3NF
| Table | Rôle | Relation |
|-------|------|----------|
| `brands` | Référentiel marques | 1:N avec products |
| `categories` | Référentiel catégories | 1:N avec products |
| `products` | Données principales | Table centrale |
| `nutrition_facts` | Valeurs nutritionnelles | 1:1 avec products |

Voir [schema.sql](schema.sql) pour le script complet.

---

## ⚠️ Limites du projet

1. **Données** : Dépendance à l'API OpenFoodFacts (disponibilité, rate limiting)
2. **Enrichissements** : Score qualité + extraction nutrition (extensible)
3. **Dashboard** : Interface simple, pas de gestion d'authentification
4. **Tests** : Couverture limitée aux cas principaux
5. **Scalabilité** : Pas de cache Redis, pagination côté serveur uniquement

---

## 📝 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/items` | GET | Liste paginée avec filtres |
| `/items/{id}` | GET | Détail d'un produit |
| `/stats` | GET | Statistiques globales |
| `/categories` | GET | Liste des catégories |
| `/brands` | GET | Liste des marques |
| `/health` | GET | État de l'API |

### Filtres disponibles sur `/items`
- `category` : Filtre par catégorie
- `brand` : Filtre par marque  
- `nutriscore` : Filtre par grade (a,b,c,d,e)
- `min_quality` : Score qualité minimum (0-100)
- `page` / `page_size` : Pagination

---

## 👤 Auteur

TP Administration BDD - Axel PERRIN - 2026
