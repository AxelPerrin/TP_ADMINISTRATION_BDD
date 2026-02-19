"""API FastAPI pour exposer les données produits."""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

from src.etl.models import get_session, Product, Brand, Category


# Modèles Pydantic
class NutritionResponse(BaseModel):
    energy_kcal: Optional[float] = None
    fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    sugars: Optional[float] = None
    fiber: Optional[float] = None
    proteins: Optional[float] = None
    salt: Optional[float] = None


class ItemSummary(BaseModel):
    id: int
    code: str
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    nutriscore_grade: Optional[str]
    quality_score: Optional[int]
    image_url: Optional[str] = None


class ItemDetail(ItemSummary):
    nova_group: Optional[int]
    nutrition: Optional[NutritionResponse] = None


class ItemListResponse(BaseModel):
    items: List[ItemSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total_products: int
    total_brands: int
    total_categories: int
    avg_quality_score: Optional[float]
    nutriscore_distribution: dict


# App FastAPI
app = FastAPI(title="Food Analytics API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/items", response_model=ItemListResponse)
def get_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    nutriscore: Optional[str] = None,
    min_quality: Optional[int] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """Liste paginée des produits avec filtres."""
    query = db.query(Product)
    
    if search:
        term = f"%{search}%"
        query = query.outerjoin(Brand).outerjoin(Category).filter(
            (Product.product_name.ilike(term)) | (Brand.name.ilike(term)) | (Category.name.ilike(term))
        )
    
    if category:
        if not search:
            query = query.join(Category)
        query = query.filter(Category.name.ilike(f"%{category}%"))
    
    if brand:
        if not search and not category:
            query = query.join(Brand)
        query = query.filter(Brand.name.ilike(f"%{brand}%"))
    
    if nutriscore:
        query = query.filter(Product.nutriscore_grade.ilike(nutriscore))
    
    if min_quality is not None:
        query = query.filter(Product.quality_score >= min_quality)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    products = query.order_by(Product.quality_score.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ItemListResponse(
        items=[ItemSummary(
            id=p.id, code=p.code, product_name=p.product_name,
            brand=p.brand.name if p.brand else None,
            category=p.category.name if p.category else None,
            nutriscore_grade=p.nutriscore_grade, quality_score=p.quality_score, image_url=p.image_url
        ) for p in products],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@app.get("/items/{item_id}", response_model=ItemDetail)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Détail d'un produit."""
    product = db.query(Product).filter(Product.id == item_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    nutrition = None
    if product.nutrition:
        nutrition = NutritionResponse(
            energy_kcal=product.nutrition.energy_kcal, fat=product.nutrition.fat,
            saturated_fat=product.nutrition.saturated_fat, carbohydrates=product.nutrition.carbohydrates,
            sugars=product.nutrition.sugars, fiber=product.nutrition.fiber,
            proteins=product.nutrition.proteins, salt=product.nutrition.salt
        )
    
    return ItemDetail(
        id=product.id, code=product.code, product_name=product.product_name,
        brand=product.brand.name if product.brand else None,
        category=product.category.name if product.category else None,
        nutriscore_grade=product.nutriscore_grade, quality_score=product.quality_score,
        nova_group=product.nova_group, image_url=product.image_url, nutrition=nutrition
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Statistiques globales."""
    nutri_dist = {grade: db.query(Product).filter(Product.nutriscore_grade == grade).count() for grade in ['a', 'b', 'c', 'd', 'e']}
    
    return StatsResponse(
        total_products=db.query(Product).count(),
        total_brands=db.query(Brand).count(),
        total_categories=db.query(Category).count(),
        avg_quality_score=db.query(func.avg(Product.quality_score)).scalar(),
        nutriscore_distribution=nutri_dist
    )


@app.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """Liste des catégories."""
    return [c.name for c in db.query(Category).order_by(Category.name).all()]


@app.get("/brands", response_model=List[str])
def get_brands(db: Session = Depends(get_db)):
    """Liste des marques."""
    return [b.name for b in db.query(Brand).order_by(Brand.name).all()]


@app.get("/health")
def health():
    return {"status": "ok"}
