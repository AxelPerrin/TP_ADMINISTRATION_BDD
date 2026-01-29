from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

from src.etl.models import get_session, Product, Brand, Category


class ItemSummary(BaseModel):
    id: int
    code: str
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    nutriscore_grade: Optional[str]
    quality_score: Optional[int]

class ItemDetail(ItemSummary):
    nova_group: Optional[int]

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


app = FastAPI(title="API Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    nutriscore: Optional[str] = Query(None),
    min_quality: Optional[int] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """Liste paginée avec filtres."""
    query = db.query(Product)
    
    if category:
        query = query.join(Category).filter(Category.name.ilike(f"%{category}%"))
    
    if brand:
        query = query.join(Brand).filter(Brand.name.ilike(f"%{brand}%"))
    
    if nutriscore:
        query = query.filter(Product.nutriscore_grade == nutriscore.lower())
    
    if min_quality is not None:
        query = query.filter(Product.quality_score >= min_quality)
    
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    
    offset = (page - 1) * page_size
    products = query.order_by(Product.quality_score.desc()).offset(offset).limit(page_size).all()
    
    items = [
        ItemSummary(
            id=p.id,
            code=p.code,
            product_name=p.product_name,
            brand=p.brand.name if p.brand else None,
            category=p.category.name if p.category else None,
            nutriscore_grade=p.nutriscore_grade,
            quality_score=p.quality_score
        )
        for p in products
    ]
    
    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@app.get("/items/{item_id}", response_model=ItemDetail)
def get_item(item_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return ItemDetail(
        id=product.id,
        code=product.code,
        product_name=product.product_name,
        brand=product.brand.name if product.brand else None,
        category=product.category.name if product.category else None,
        nutriscore_grade=product.nutriscore_grade,
        quality_score=product.quality_score,
        nova_group=product.nova_group
    )


@app.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total_products = db.query(Product).count()
    total_brands = db.query(Brand).count()
    total_categories = db.query(Category).count()
    
    avg_quality = db.query(func.avg(Product.quality_score)).scalar()
    
    nutriscore_dist = {}
    for grade in ["a", "b", "c", "d", "e"]:
        count = db.query(Product).filter(Product.nutriscore_grade == grade).count()
        nutriscore_dist[grade] = count
    
    return StatsResponse(
        total_products=total_products,
        total_brands=total_brands,
        total_categories=total_categories,
        avg_quality_score=round(avg_quality, 1) if avg_quality else None,
        nutriscore_distribution=nutriscore_dist
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
