"""
=============================================================================
MODÈLES ORM SQLALCHEMY - DÉFINITION DES TABLES SQL
=============================================================================
Ce fichier définit la structure de la base de données SQL (SQLite ou PostgreSQL).

SQLAlchemy est un ORM (Object-Relational Mapper) qui permet de :
- Définir les tables comme des classes Python
- Manipuler les données avec des objets au lieu d'écrire du SQL brut
- Gérer automatiquement les relations entre tables

ARCHITECTURE DES DONNÉES :
- Brand (Marques) : Table des marques de produits (ex: Nestlé, Danone)
- Category (Catégories) : Table des catégories (ex: Céréales, Boissons)
- Product (Produits) : Table principale avec toutes les infos produits

Relations :
- Un produit appartient à UNE marque (relation N:1)
- Un produit appartient à UNE catégorie (relation N:1)
- Une marque peut avoir PLUSIEURS produits (relation 1:N)
- Une catégorie peut avoir PLUSIEURS produits (relation 1:N)
=============================================================================
"""

from datetime import datetime
# SQLAlchemy : librairie Python pour gérer les bases de données SQL
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base  # Pour créer la classe de base des modèles
from sqlalchemy.orm import relationship, sessionmaker  # Pour les relations et les sessions

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

# Import des configurations de connexion à la base de données
from config.settings import SQLITE_PATH, POSTGRES_URI, USE_SQLITE

# Base = classe parente de tous nos modèles (tables)
# Tous les modèles doivent hériter de cette classe
Base = declarative_base()


# =============================================================================
# TABLE DES MARQUES (BRANDS)
# =============================================================================
class Brand(Base):
    """
    Table des marques de produits alimentaires.
    
    Exemples de marques : Nestlé, Danone, Kellogg's, etc.
    
    Cette table est séparée pour éviter la redondance des données :
    au lieu de stocker "Nestlé" 1000 fois dans la table produits,
    on stocke juste l'ID de la marque (normalisation de la BDD).
    """
    # Nom de la table dans la base de données
    __tablename__ = 'brands'
    
    # Colonnes de la table :
    # id = Clé primaire auto-incrémentée (1, 2, 3, ...)
    id = Column(Integer, primary_key=True, autoincrement=True)
    # name = Nom de la marque, unique (pas de doublons), obligatoire, indexé pour recherche rapide
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    # Relation : une marque a plusieurs produits
    # back_populates crée le lien bidirectionnel (produit.brand ↔ brand.products)
    products = relationship("Product", back_populates="brand")


# =============================================================================
# TABLE DES CATÉGORIES (CATEGORIES)
# =============================================================================
class Category(Base):
    """
    Table des catégories de produits alimentaires.
    
    Exemples de catégories : Céréales, Boissons, Produits laitiers, etc.
    
    Même principe que les marques : normalisation pour éviter la redondance.
    """
    __tablename__ = 'categories'
    
    # Clé primaire
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Nom de la catégorie (unique, obligatoire, indexé)
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    # Relation : une catégorie contient plusieurs produits
    products = relationship("Product", back_populates="category")


# =============================================================================
# TABLE DES PRODUITS (PRODUCTS) - TABLE PRINCIPALE
# =============================================================================
class Product(Base):
    """
    Table principale contenant tous les produits alimentaires.
    
    Chaque ligne représente un produit avec :
    - Son code-barres unique (code)
    - Son nom
    - Sa marque (via brand_id → table brands)
    - Sa catégorie (via category_id → table categories)
    - Son Nutriscore (a, b, c, d, e)
    - Son groupe NOVA (1-4, niveau de transformation)
    - Son score qualité calculé (0-100)
    """
    __tablename__ = 'products'
    
    # === COLONNES PRINCIPALES ===
    
    # Clé primaire auto-incrémentée
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Code-barres du produit (unique, sert d'identifiant métier)
    # index=True permet des recherches rapides par code
    code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Nom du produit (ex: "Chocapic Céréales")
    product_name = Column(String(500), nullable=False)
    
    # === CLÉS ÉTRANGÈRES (liens vers d'autres tables) ===
    
    # ID de la marque (référence vers brands.id)
    # ForeignKey crée une contrainte : la valeur doit exister dans brands.id
    brand_id = Column(Integer, ForeignKey('brands.id'), index=True)
    
    # ID de la catégorie (référence vers categories.id)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    
    # === DONNÉES NUTRITIONNELLES ===
    
    # Nutriscore : a (meilleur) à e (moins bon), une seule lettre
    nutriscore_grade = Column(String(1), index=True)
    
    # Groupe NOVA : niveau de transformation des aliments
    # 1 = non transformé, 2 = ingrédients culinaires, 3 = transformé, 4 = ultra-transformé
    nova_group = Column(Integer)
    
    # Score qualité calculé par nous (0-100)
    # Combine le Nutriscore et la complétude des données
    quality_score = Column(Integer, index=True)
    
    # Date de création de l'enregistrement
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # === RELATIONS ORM ===
    
    # Accès direct à l'objet Brand associé (ex: product.brand.name)
    brand = relationship("Brand", back_populates="products")
    # Accès direct à l'objet Category associé (ex: product.category.name)
    category = relationship("Category", back_populates="products")
    
    # === INDEX COMPOSITE ===
    # Index sur plusieurs colonnes pour optimiser les requêtes combinées
    # Ex: "tous les produits Nutriscore A triés par qualité"
    __table_args__ = (
        Index('idx_nutriscore_quality', 'nutriscore_grade', 'quality_score'),
    )


# =============================================================================
# FONCTIONS DE CONNEXION À LA BASE DE DONNÉES
# =============================================================================

def get_engine():
    """
    Crée et retourne un "engine" SQLAlchemy = connexion à la base de données.
    
    L'engine est le point d'entrée vers la base de données.
    Il gère le pool de connexions et traduit les requêtes Python en SQL.
    
    Returns:
        Engine: Connexion SQLAlchemy vers SQLite ou PostgreSQL
    """
    if USE_SQLITE:
        # Mode SQLite : base de données dans un fichier local
        # Pratique pour le développement, pas besoin d'installer un serveur
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)  # Crée le dossier data/ si besoin
        return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)
    # Mode PostgreSQL : serveur de base de données externe
    # Plus performant pour la production
    return create_engine(POSTGRES_URI, echo=False)


def get_session():
    """
    Crée et retourne une session SQLAlchemy.
    
    Une session est une "conversation" avec la base de données.
    Elle permet de :
    - Faire des requêtes (SELECT)
    - Ajouter des données (INSERT)
    - Modifier des données (UPDATE)
    - Supprimer des données (DELETE)
    - Valider les changements (COMMIT)
    
    Returns:
        Session: Session SQLAlchemy prête à l'emploi
    """
    engine = get_engine()
    # sessionmaker crée une "fabrique" de sessions liées à notre engine
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables():
    """
    Crée toutes les tables dans la base de données.
    
    Cette fonction lit les définitions de classes (Brand, Category, Product)
    et génère automatiquement le SQL CREATE TABLE correspondant.
    
    Si les tables existent déjà, elles ne sont pas modifiées
    (comportement par défaut de create_all).
    
    Returns:
        Engine: L'engine utilisé pour créer les tables
    """
    engine = get_engine()
    # create_all parcourt tous les modèles héritant de Base
    # et crée les tables correspondantes dans la BDD
    Base.metadata.create_all(engine)
    return engine
