-- =============================================
-- SCHÉMA SQL - TP Administration BDD
-- Produits alimentaires & qualité nutritionnelle
-- =============================================

-- Table des marques
CREATE TABLE IF NOT EXISTS brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(name);

-- Table des catégories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- Table des produits
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(500) NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    category_id INTEGER REFERENCES categories(id),
    nutriscore_grade VARCHAR(1),
    nova_group INTEGER,
    quality_score INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les colonnes filtrées
CREATE INDEX IF NOT EXISTS idx_products_code ON products(code);
CREATE INDEX IF NOT EXISTS idx_products_brand_id ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_nutriscore ON products(nutriscore_grade);
CREATE INDEX IF NOT EXISTS idx_products_quality ON products(quality_score);

-- Index composé pour requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_nutriscore_quality ON products(nutriscore_grade, quality_score);
