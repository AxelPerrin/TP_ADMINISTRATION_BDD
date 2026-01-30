"""
=============================================================================
API REST FASTAPI - BACKEND DU PROJET
=============================================================================
Ce fichier définit l'API REST qui expose les données aux applications clientes.

FastAPI est un framework moderne pour créer des APIs en Python :
- Très performant (asynchrone par défaut)
- Documentation automatique (Swagger UI)
- Validation automatique des données (Pydantic)

ENDPOINTS DISPONIBLES :
- GET /items : Liste paginée des produits avec filtres
- GET /items/{id} : Détail d'un produit spécifique
- GET /stats : Statistiques globales (comptages, distributions)

Lancez l'API avec : python -m uvicorn src.api.main:app --reload
Documentation auto : http://localhost:8000/docs
=============================================================================
"""

from typing import Optional, List
# FastAPI : framework web pour créer des APIs REST
from fastapi import FastAPI, HTTPException, Query, Depends
# Middleware CORS : permet aux sites web d'appeler notre API
from fastapi.middleware.cors import CORSMiddleware
# Pydantic : validation et sérialisation des données
from pydantic import BaseModel
# SQLAlchemy : ORM pour interagir avec la base SQL
from sqlalchemy.orm import Session
from sqlalchemy import func  # Fonctions SQL (AVG, COUNT, etc.)

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

# Import des modèles et fonctions de connexion SQL
from src.etl.models import get_session, Product, Brand, Category


# =============================================================================
# MODÈLES PYDANTIC (Schémas de données pour l'API)
# =============================================================================
# Ces classes définissent la structure des données échangées avec l'API.
# Pydantic valide automatiquement les données entrantes et sortantes.

class ItemSummary(BaseModel):
    """
    Résumé d'un produit pour les listes.
    
    Contient les informations essentielles affichées dans les listes
    sans surcharger la réponse avec tous les détails.
    """
    id: int                           # ID unique du produit en base
    code: str                         # Code-barres du produit
    product_name: str                 # Nom du produit
    brand: Optional[str]              # Nom de la marque (peut être null)
    category: Optional[str]           # Nom de la catégorie (peut être null)
    nutriscore_grade: Optional[str]   # Note Nutriscore (a-e)
    quality_score: Optional[int]      # Score qualité calculé (0-100)


class ItemDetail(ItemSummary):
    """
    Détail complet d'un produit.
    
    Hérite de ItemSummary et ajoute des champs supplémentaires
    affichés uniquement sur la page de détail.
    """
    nova_group: Optional[int]  # Groupe NOVA (1-4) : niveau de transformation


class ItemListResponse(BaseModel):
    """
    Réponse paginée pour la liste des produits.
    
    Contient les produits + les métadonnées de pagination
    pour permettre la navigation dans les résultats.
    """
    items: List[ItemSummary]  # Liste des produits de la page courante
    total: int                # Nombre total de produits (toutes pages)
    page: int                 # Numéro de page actuelle (1-indexed)
    page_size: int            # Nombre de produits par page
    total_pages: int          # Nombre total de pages


class StatsResponse(BaseModel):
    """
    Statistiques globales sur les données.
    
    Utilisé pour le dashboard et les métriques générales.
    """
    total_products: int                # Nombre total de produits
    total_brands: int                  # Nombre de marques différentes
    total_categories: int              # Nombre de catégories différentes
    avg_quality_score: Optional[float] # Score qualité moyen
    nutriscore_distribution: dict      # Répartition des Nutriscore {"a": 150, "b": 200, ...}


# =============================================================================
# CONFIGURATION DE L'APPLICATION FASTAPI
# =============================================================================

# Création de l'application FastAPI avec métadonnées
app = FastAPI(
    title="API Backend",  # Titre affiché dans la doc Swagger
    version="1.0.0"       # Version de l'API
)

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet aux navigateurs web d'appeler notre API depuis d'autres domaines
# ATTENTION: allow_origins=["*"] autorise TOUT le monde (ok pour dev, pas pour prod!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Domaines autorisés (* = tous)
    allow_methods=["*"],     # Méthodes HTTP autorisées (GET, POST, etc.)
    allow_headers=["*"],     # En-têtes HTTP autorisés
)


# =============================================================================
# GESTION DES SESSIONS DE BASE DE DONNÉES
# =============================================================================

def get_db():
    """
    Générateur de session de base de données.
    
    Cette fonction est utilisée comme "dépendance" FastAPI.
    Elle crée une session SQL, la fournit à l'endpoint, puis la ferme.
    
    Le pattern "yield" permet de :
    1. Créer la session AVANT l'exécution de l'endpoint
    2. La fournir à l'endpoint via Depends()
    3. La fermer APRÈS l'exécution (même en cas d'erreur)
    
    Yields:
        Session: Session SQLAlchemy prête à l'emploi
    """
    db = get_session()  # Créer une nouvelle session
    try:
        yield db  # Fournir la session à l'endpoint
    finally:
        db.close()  # Toujours fermer la session (libère les ressources)


# =============================================================================
# ENDPOINTS DE L'API
# =============================================================================

@app.get("/items", response_model=ItemListResponse)
def get_items(
    # Paramètres de pagination
    page: int = Query(1, ge=1),              # Numéro de page (min: 1)
    page_size: int = Query(20, ge=1, le=100), # Taille de page (1-100)
    # Paramètres de filtrage
    category: Optional[str] = Query(None),   # Filtre par catégorie
    brand: Optional[str] = Query(None),      # Filtre par marque
    nutriscore: Optional[str] = Query(None), # Filtre par Nutriscore
    min_quality: Optional[int] = Query(None, ge=0, le=100),  # Score minimum
    # Injection de dépendance : session SQL
    db: Session = Depends(get_db)
):
    """
    Liste paginée des produits avec filtres optionnels.
    
    Permet de parcourir tous les produits avec :
    - Pagination (page, page_size)
    - Filtrage par catégorie, marque, nutriscore
    - Filtrage par score qualité minimum
    
    Les produits sont triés par score qualité décroissant
    (les meilleurs produits en premier).
    
    Returns:
        ItemListResponse: Liste paginée avec métadonnées
    """
    # Commencer la requête sur la table Product
    query = db.query(Product)
    
    # === APPLICATION DES FILTRES ===
    # Chaque filtre est optionnel et s'applique seulement si fourni
    
    if category:
        # Filtre par catégorie avec recherche partielle (LIKE %category%)
        # Le join() lie la table categories pour accéder au nom
        query = query.join(Category).filter(Category.name.ilike(f"%{category}%"))
    
    if brand:
        # Filtre par marque avec recherche partielle
        query = query.join(Brand).filter(Brand.name.ilike(f"%{brand}%"))
    
    if nutriscore:
        # Filtre par Nutriscore exact (a, b, c, d ou e)
        query = query.filter(Product.nutriscore_grade == nutriscore.lower())
    
    if min_quality is not None:
        # Filtre par score qualité minimum
        query = query.filter(Product.quality_score >= min_quality)
    
    # === CALCUL DE LA PAGINATION ===
    
    # Compter le total de résultats (avant pagination)
    total = query.count()
    # Calculer le nombre total de pages (arrondi supérieur)
    total_pages = (total + page_size - 1) // page_size
    
    # Calculer l'offset (combien de résultats sauter)
    # Page 1 → offset 0, Page 2 → offset page_size, etc.
    offset = (page - 1) * page_size
    
    # Exécuter la requête avec tri, offset et limite
    products = query.order_by(Product.quality_score.desc()).offset(offset).limit(page_size).all()
    
    # === TRANSFORMATION EN RÉPONSE API ===
    
    # Convertir les objets Product en ItemSummary
    items = [
        ItemSummary(
            id=p.id,
            code=p.code,
            product_name=p.product_name,
            # Accéder au nom de la marque via la relation ORM
            brand=p.brand.name if p.brand else None,
            # Accéder au nom de la catégorie via la relation ORM
            category=p.category.name if p.category else None,
            nutriscore_grade=p.nutriscore_grade,
            quality_score=p.quality_score
        )
        for p in products
    ]
    
    # Retourner la réponse paginée complète
    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@app.get("/items/{item_id}", response_model=ItemDetail)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails complets d'un produit.
    
    Args:
        item_id: ID du produit à récupérer
        
    Returns:
        ItemDetail: Détails complets du produit
        
    Raises:
        HTTPException 404: Si le produit n'existe pas
    """
    # Chercher le produit par son ID
    product = db.query(Product).filter(Product.id == item_id).first()
    
    # Si le produit n'existe pas, renvoyer une erreur 404
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Construire et retourner le détail du produit
    return ItemDetail(
        id=product.id,
        code=product.code,
        product_name=product.product_name,
        brand=product.brand.name if product.brand else None,
        category=product.category.name if product.category else None,
        nutriscore_grade=product.nutriscore_grade,
        quality_score=product.quality_score,
        nova_group=product.nova_group  # Champ supplémentaire par rapport à ItemSummary
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Retourne les statistiques globales sur les données.
    
    Calcule différentes métriques utiles pour le dashboard :
    - Comptages (produits, marques, catégories)
    - Score qualité moyen
    - Distribution des Nutriscore
    
    Returns:
        StatsResponse: Statistiques agrégées
    """
    # === COMPTAGES ===
    
    # Nombre total de produits
    total_products = db.query(Product).count()
    # Nombre de marques uniques
    total_brands = db.query(Brand).count()
    # Nombre de catégories uniques
    total_categories = db.query(Category).count()
    
    # === MOYENNE DU SCORE QUALITÉ ===
    
    # func.avg calcule la moyenne SQL
    # .scalar() retourne une seule valeur (pas une liste)
    avg_quality = db.query(func.avg(Product.quality_score)).scalar()
    
    # === DISTRIBUTION DES NUTRISCORE ===
    
    # Compter combien de produits ont chaque grade
    nutriscore_dist = {}
    for grade in ["a", "b", "c", "d", "e"]:
        count = db.query(Product).filter(Product.nutriscore_grade == grade).count()
        nutriscore_dist[grade] = count
    
    # Retourner toutes les statistiques
    return StatsResponse(
        total_products=total_products,
        total_brands=total_brands,
        total_categories=total_categories,
        # Arrondir la moyenne à 1 décimale, ou None si pas de données
        avg_quality_score=round(avg_quality, 1) if avg_quality else None,
        nutriscore_distribution=nutriscore_dist
    )


# =============================================================================
# POINT D'ENTRÉE POUR EXÉCUTION DIRECTE
# =============================================================================

if __name__ == "__main__":
    # Si on exécute ce fichier directement (python main.py),
    # on lance le serveur Uvicorn
    import uvicorn
    # Uvicorn est un serveur ASGI performant pour FastAPI
    # host="0.0.0.0" : écoute sur toutes les interfaces réseau
    # port=8000 : accessible via http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
