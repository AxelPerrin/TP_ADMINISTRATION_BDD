"""Modèles SQLAlchemy pour la base de données SQL."""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])
from config.settings import SQLITE_PATH, POSTGRES_URI, USE_SQLITE

Base = declarative_base()


class Brand(Base):
    """Table des marques."""
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    products = relationship("Product", back_populates="brand")


class Category(Base):
    """Table des catégories."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    products = relationship("Product", back_populates="category")


class Product(Base):
    """Table principale des produits."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    nutriscore_grade = Column(String(1), index=True)
    nova_group = Column(Integer)
    quality_score = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    nutrition = relationship("NutritionFacts", back_populates="product", uselist=False)
    
    __table_args__ = (Index('idx_nutriscore_quality', 'nutriscore_grade', 'quality_score'),)


class NutritionFacts(Base):
    """Table des données nutritionnelles (relation 1:1 avec Product)."""
    __tablename__ = 'nutrition_facts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), unique=True, nullable=False)
    energy_kcal = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    saturated_fat = Column(Float, nullable=True)
    carbohydrates = Column(Float, nullable=True)
    sugars = Column(Float, nullable=True)
    fiber = Column(Float, nullable=True)
    proteins = Column(Float, nullable=True)
    salt = Column(Float, nullable=True)
    
    product = relationship("Product", back_populates="nutrition")


def get_engine():
    """Crée la connexion à la base de données."""
    if USE_SQLITE:
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)
    return create_engine(POSTGRES_URI, echo=False)


def get_session():
    """Crée une session SQLAlchemy."""
    return sessionmaker(bind=get_engine())()


def create_tables():
    """Crée les tables dans la base de données."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
