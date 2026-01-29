# TP Administration BDD

## Sujet 3 — Produits alimentaires & qualité nutritionnelle

Pipeline de traitement de données depuis la collecte jusqu'au dashboard.

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
- MongoDB 4.4+ (pour RAW et ENRICHED)
- SQLite (par défaut) ou PostgreSQL

---

## 🏗️ Architecture

```
OpenFoodFacts API
       │
       ▼ ÉTAPE 1: Collecte
┌─────────────┐
│ MongoDB RAW │  ← Données brutes 100%
└──────┬──────┘
       │
       ▼ ÉTAPE 3: Enrichissement  
┌─────────────────┐
│ MongoDB ENRICHED│  ← Score qualité + Catégorisation
└──────┬──────────┘
       │
       ▼ ÉTAPE 4: ETL
┌─────────────┐
│  SQLite/    │  ← Modèle relationnel
│  PostgreSQL │
└──────┬──────┘
       │
       ▼ ÉTAPE 5: API
┌─────────────┐
│   FastAPI   │  ← /items, /items/{id}, /stats
└──────┬──────┘
       │
       ▼ ÉTAPE 6: Dashboard
┌─────────────┐
│  Streamlit  │  ← Interface utilisateur
└─────────────┘
```

---

## 📁 Structure du projet

```
TP_ADMINISTRATION_BDD/
├── config/settings.py       # Configuration centralisée
├── scripts/
│   ├── collect_data.py      # ÉTAPE 1: Collecte CLI
│   ├── enrich_data.py       # ÉTAPE 3: Enrichissement CLI
│   └── run_etl.py           # ÉTAPE 4: ETL CLI
├── src/
│   ├── database/
│   │   └── mongodb_manager.py   # ÉTAPE 2: MongoDB RAW/ENRICHED
│   ├── enrichment/
│   │   └── enricher.py          # ÉTAPE 3: Enrichissement
│   ├── etl/
│   │   ├── models.py            # ÉTAPE 4: Schéma SQL
│   │   └── pipeline.py          # ÉTAPE 4: ETL
│   ├── api/
│   │   └── main.py              # ÉTAPE 5: API FastAPI
│   └── dashboard/
│       └── app.py               # ÉTAPE 6: Dashboard Streamlit
├── tests/
│   ├── conftest.py              # Fixtures
│   ├── test_unit.py             # Tests unitaires
│   └── test_integration.py      # Tests d'intégration
├── schema.sql                   # Schéma SQL
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

Créer un fichier `.env` à la racine :

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
# ou MongoDB Atlas :
# MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/openfoodfacts

MONGODB_DB=openfoodfacts

# SQL (SQLite par défaut)
USE_SQLITE=true
SQLITE_PATH=data/openfoodfacts.db

# PostgreSQL (optionnel)
# USE_SQLITE=false
# POSTGRES_URI=postgresql://user:password@localhost:5432/openfoodfacts
```

---

## 🚀 Commandes (Étape par Étape)

### Pipeline complet (copier-coller)
```bash
# 1. Installation
pip install -r requirements.txt

# 2. Collecte → MongoDB RAW (300 produits minimum)
python scripts/collect_data.py --count 300

# 3. Enrichissement → MongoDB ENRICHED
python scripts/enrich_data.py

# 4. ETL → SQLite
python scripts/run_etl.py

# 5. API (dans un terminal séparé)
python -m uvicorn src.api.main:app --reload --port 8000

# 6. Dashboard (dans un autre terminal)
python -m streamlit run src/dashboard/app.py

# 7. Tests
python -m pytest tests/ -v
```

---

## 🔗 URLs après lancement

| Service | URL |
|---------|-----|
| **API Documentation** | http://localhost:8000/docs |
| **API (Swagger)** | http://localhost:8000/redoc |
| **Dashboard** | http://localhost:8501 |

---

## 📖 Détail des commandes

### ÉTAPE 1 & 2 : Collecte des données
```bash
# Collecte 300 produits (minimum requis)
python scripts/collect_data.py --count 300

# Options disponibles :
python scripts/collect_data.py --count 500                    # Plus de produits
python scripts/collect_data.py --categories "snacks,beverages" # Catégories spécifiques
python scripts/collect_data.py --no-mongodb                   # Sans stockage MongoDB
```

### ÉTAPE 3 : Enrichissement
```bash
python scripts/enrich_data.py
# → Ajoute quality_score et category_group à chaque produit
```

### ÉTAPE 4 : ETL vers SQL
```bash
python scripts/run_etl.py
# → Transfert MongoDB ENRICHED → SQLite (tables: products, brands, categories)
```

### ÉTAPE 5 : API FastAPI
```bash
uvicorn src.api.main:app --reload --port 8000
# → Documentation: http://localhost:8000/docs
```

### ÉTAPE 6 : Dashboard Streamlit
```bash
streamlit run src/dashboard/app.py
# → Interface: http://localhost:8501
```

### ÉTAPE 7 : Tests
```bash
# Tous les tests
pytest tests/ -v

# Tests unitaires uniquement
pytest tests/test_unit.py -v

# Tests d'intégration uniquement
pytest tests/test_integration.py -v

# Avec couverture
pytest tests/ -v --cov=src
```

---

## 🔍 Vérification des données

```bash
# Vérifier MongoDB
python -c "from src.database.mongodb_manager import MongoDBManager; m=MongoDBManager(); print(f'RAW: {m.raw_collection.count_documents({})}'); print(f'ENRICHED: {m.enriched_collection.count_documents({})}')"

# Vérifier SQLite
python -c "from src.etl.models import get_session, Product, Brand, Category; s=get_session(); print(f'Produits: {s.query(Product).count()}'); print(f'Marques: {s.query(Brand).count()}'); print(f'Categories: {s.query(Category).count()}')"
```

---

## 🔧 Choix techniques

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Collecte** | `requests` | Simple, fiable |
| **Stockage RAW** | MongoDB | Flexible, JSON natif, données hétérogènes |
| **Stockage SQL** | SQLite/PostgreSQL | Jointures, index, agrégations performantes |
| **ORM** | SQLAlchemy | Abstraction, migrations, relations |
| **API** | FastAPI | Performant, async, documentation auto |
| **Dashboard** | Streamlit | Rapide à développer, interactif |
| **Tests** | pytest | Standard Python, fixtures |

---

## 📊 Schéma SQL

```sql
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   brands    │     │  products   │     │ categories  │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │◄────│ brand_id(FK)│     │ id (PK)     │
│ name (UQ)   │     │ code (UQ)   │────►│ name (UQ)   │
└─────────────┘     │ product_name│     └─────────────┘
                    │ category_id │
                    │ nutriscore  │
                    │ nova_group  │
                    │ quality_score│
                    │ created_at  │
                    └─────────────┘
```

Voir [schema.sql](schema.sql) pour le script complet.

---

## ⚠️ Limites du projet

1. **Données** : Dépendance à l'API OpenFoodFacts (disponibilité, rate limiting)
2. **Enrichissements** : Seulement 2 enrichissements basiques (score qualité, catégorisation)
3. **Stockage** : SQLite en local, pas adapté à la production multi-utilisateurs
4. **Dashboard** : Interface simple, pas de gestion d'authentification
5. **Tests** : Couverture limitée aux cas principaux
6. **Scalabilité** : Pas de cache, pas de pagination optimisée côté MongoDB

---

## 📝 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/items` | GET | Liste paginée avec filtres |
| `/items/{id}` | GET | Détail d'un produit |
| `/stats` | GET | Statistiques globales |

### Filtres disponibles
- `category` : Filtre par catégorie
- `brand` : Filtre par marque
- `nutriscore` : Filtre par grade (a,b,c,d,e)
- `min_quality` : Score qualité minimum (0-100)
- `page` / `page_size` : Pagination

---

## 👤 Auteur

TP Administration BDD - Axel PERRIN - 2026
