from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

from config.settings import SQLITE_PATH, POSTGRES_URI, USE_SQLITE

Base = declarative_base()


class Brand(Base):
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    products = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(500), nullable=False)
    
    brand_id = Column(Integer, ForeignKey('brands.id'), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    
    nutriscore_grade = Column(String(1), index=True)
    nova_group = Column(Integer)
    quality_score = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    
    __table_args__ = (
        Index('idx_nutriscore_quality', 'nutriscore_grade', 'quality_score'),
    )


def get_engine():
    if USE_SQLITE:
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)
    return create_engine(POSTGRES_URI, echo=False)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
