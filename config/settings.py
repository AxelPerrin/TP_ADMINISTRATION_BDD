"""
=============================================================================
FICHIER DE CONFIGURATION CENTRALISÉ DU PROJET
=============================================================================
Ce fichier contient TOUTES les configurations du projet :
- Connexions aux bases de données (MongoDB, PostgreSQL, SQLite)
- URLs de l'API OpenFoodFacts
- Paramètres de collecte de données
- Configuration du serveur API et du Dashboard
- Constantes métier (Nutriscore, catégories)

Les valeurs peuvent être surchargées via des variables d'environnement
ou un fichier .env à la racine du projet.
=============================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv  # Permet de charger les variables depuis un fichier .env

# Charge les variables d'environnement depuis le fichier .env (s'il existe)
# Cela permet de ne pas mettre les mots de passe en dur dans le code
load_dotenv()

# =============================================================================
# CHEMINS DE BASE DU PROJET
# =============================================================================
# BASE_DIR = Dossier racine du projet (parent du dossier config/)
# DATA_DIR = Dossier où sont stockées les données (fichiers JSON, SQLite, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# =============================================================================
# CONFIGURATION MONGODB (Base de données NoSQL)
# =============================================================================
# MongoDB est utilisé pour stocker les données brutes (RAW) de l'API OpenFoodFacts
# et les données enrichies (ENRICHED) après traitement.
# C'est une base orientée documents (JSON) très flexible.

# Adresse du serveur MongoDB (par défaut: localhost = sur ta machine)
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
# Port de MongoDB (par défaut: 27017, c'est le port standard de MongoDB)
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
# Nom de la base de données dans MongoDB
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "openfoodfacts")
# URI de connexion complète (format: mongodb://host:port)
MONGODB_URI = os.getenv("MONGODB_URI", f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}")

# Noms des collections MongoDB (équivalent des "tables" en SQL)
# products_raw = données brutes telles que récupérées de l'API
# products_enriched = données après calcul du score qualité et catégorisation
COLLECTION_RAW = "products_raw"
COLLECTION_ENRICHED = "products_enriched"

# =============================================================================
# CONFIGURATION POSTGRESQL (Base de données SQL relationnelle)
# =============================================================================
# PostgreSQL est une base SQL performante utilisée pour les données finales
# Elle permet des requêtes complexes, des jointures, et des analyses.

# Adresse du serveur PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
# Port PostgreSQL (par défaut: 5432)
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
# Nom d'utilisateur pour se connecter
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
# Mot de passe (⚠️ À changer en production!)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
# Nom de la base de données
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "openfoodfacts_analytics")

# URI de connexion PostgreSQL (format standard SQLAlchemy)
# Format: postgresql://utilisateur:motdepasse@host:port/base
POSTGRES_URI = os.getenv(
    "POSTGRES_URI",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

# =============================================================================
# CONFIGURATION SQLITE (Base de données légère en fichier)
# =============================================================================
# SQLite est une alternative simple à PostgreSQL qui stocke tout dans UN fichier.
# Parfait pour le développement et les tests, pas besoin d'installer de serveur!

# Chemin du fichier SQLite (sera créé automatiquement dans data/)
SQLITE_PATH = DATA_DIR / "openfoodfacts.db"
# Si True, on utilise SQLite au lieu de PostgreSQL (plus simple pour débuter)
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

# =============================================================================
# CONFIGURATION API OPENFOODFACTS (Source des données)
# =============================================================================
# OpenFoodFacts est une base de données ouverte sur les produits alimentaires.
# On utilise leur API pour récupérer les informations nutritionnelles.

# URL de base de l'API OpenFoodFacts
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org"
# URL pour rechercher des produits (avec filtres par catégorie, pays, etc.)
OPENFOODFACTS_SEARCH_URL = f"{OPENFOODFACTS_API_URL}/cgi/search.pl"
# URL pour récupérer un produit spécifique par son code-barres
OPENFOODFACTS_PRODUCT_URL = f"{OPENFOODFACTS_API_URL}/api/v2/product"

# =============================================================================
# PARAMÈTRES DE COLLECTE DE DONNÉES
# =============================================================================
# Ces paramètres contrôlent comment on récupère les données de l'API

# Nombre de produits par page lors de la recherche (max 100 pour OpenFoodFacts)
COLLECT_PAGE_SIZE = 100
# Nombre maximum de produits à collecter au total
COLLECT_MAX_PRODUCTS = 1000
# Délai entre chaque requête (en secondes) pour ne pas surcharger l'API
# C'est important d'être "poli" avec les APIs publiques!
COLLECT_DELAY_SECONDS = 1

# =============================================================================
# CONFIGURATION DU SERVEUR API FASTAPI
# =============================================================================
# Notre propre API REST qui expose les données aux applications clientes

# Adresse d'écoute (0.0.0.0 = toutes les interfaces réseau)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
# Port du serveur API (accessible via http://localhost:8000)
API_PORT = int(os.getenv("API_PORT", 8000))
# Mode debug (recharge automatique du code, messages d'erreur détaillés)
API_DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"

# =============================================================================
# CONFIGURATION DU DASHBOARD STREAMLIT
# =============================================================================
# Interface web de visualisation des données

# Adresse d'écoute du dashboard
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
# Port du dashboard (accessible via http://localhost:8501)
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8501))

# =============================================================================
# CONSTANTES MÉTIER - NUTRISCORE
# =============================================================================
# Le Nutriscore est une note nutritionnelle de A (meilleur) à E (moins bon)
# qui aide les consommateurs à faire des choix alimentaires plus sains.

# Liste des grades Nutriscore possibles (de meilleur à moins bon)
NUTRISCORE_GRADES = ["a", "b", "c", "d", "e"]

# Couleurs officielles du Nutriscore pour l'affichage
# A = vert foncé (excellent), E = rouge (à limiter)
NUTRISCORE_COLORS = {
    "a": "#038141",  # Vert foncé - Excellent
    "b": "#85BB2F",  # Vert clair - Bon
    "c": "#FECB02",  # Jaune - Moyen
    "d": "#EE8100",  # Orange - Limiter
    "e": "#E63E11"   # Rouge - À éviter
}

# =============================================================================
# CATÉGORIES DE PRODUITS À COLLECTER
# =============================================================================
# Liste des catégories alimentaires qu'on veut récupérer de OpenFoodFacts.
# Ces noms correspondent aux tags utilisés par l'API.

MAIN_CATEGORIES = [
    "breakfast-cereals",  # Céréales du petit-déjeuner
    "dairy",              # Produits laitiers
    "beverages",          # Boissons
    "snacks",             # Snacks et grignotages
    "bread",              # Pains et viennoiseries
    "fruits",             # Fruits
    "vegetables",         # Légumes
    "meat",               # Viandes
    "fish",               # Poissons et fruits de mer
    "frozen-foods"        # Produits surgelés
]
