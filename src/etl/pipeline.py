"""
=============================================================================
PIPELINE ETL (Extract - Transform - Load)
=============================================================================
Ce fichier contient le processus ETL qui transfère les données enrichies
depuis MongoDB vers la base de données SQL (SQLite ou PostgreSQL).

ETL signifie :
- Extract (Extraire) : Récupérer les données depuis MongoDB
- Transform (Transformer) : Adapter les données au format SQL
- Load (Charger) : Insérer les données dans les tables SQL

FLUX DE DONNÉES :
MongoDB (products_enriched) → Transformation → SQL (products, brands, categories)

Ce pipeline est "idempotent" : on peut le relancer plusieurs fois,
les produits existants seront mis à jour au lieu d'être dupliqués.
=============================================================================
"""

from typing import Optional
from loguru import logger  # Librairie de logging avancée
from sqlalchemy.orm import Session  # Pour typer les sessions SQLAlchemy

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

# Import du gestionnaire MongoDB pour extraire les données
from src.database.mongodb_manager import MongoDBManager
# Import des modèles SQL et fonctions de connexion
from src.etl.models import get_session, create_tables, Product, Brand, Category


class ETLPipeline:
    """
    Classe principale du pipeline ETL.
    
    Elle orchestre le transfert des données enrichies de MongoDB
    vers la base de données SQL relationnelle.
    
    Attributs:
        session: Session SQLAlchemy pour interagir avec la BDD SQL
        brands_cache: Cache des marques déjà créées (évite les requêtes répétées)
        categories_cache: Cache des catégories déjà créées
    """
    
    def __init__(self):
        """
        Initialise le pipeline ETL.
        
        Les caches permettent d'éviter de chercher en base à chaque produit
        si une marque/catégorie existe déjà. C'est une optimisation importante!
        """
        self.session: Optional[Session] = None  # Session SQL (sera créée dans run())
        self.brands_cache = {}  # Cache: {"Nestlé": <Brand object>, ...}
        self.categories_cache = {}  # Cache: {"Céréales": <Category object>, ...}
    
    def run(self):
        """
        Exécute le pipeline ETL complet.
        
        Étapes :
        1. Crée les tables SQL si elles n'existent pas
        2. Ouvre une session SQL
        3. Extrait les documents enrichis de MongoDB
        4. Charge chaque produit dans SQL
        5. Commit les changements (sauvegarde définitive)
        
        En cas d'erreur, tout est annulé (rollback) pour garder
        la base de données dans un état cohérent.
        """
        logger.info("Démarrage ETL")
        
        # ÉTAPE 1 : Créer les tables SQL (products, brands, categories)
        # Si elles existent déjà, cette fonction ne fait rien
        create_tables()
        
        # ÉTAPE 2 : Ouvrir une session SQL
        # La session garde trace de tous les changements jusqu'au commit
        self.session = get_session()
        
        try:
            # ÉTAPE 3 : EXTRACT - Récupérer les données de MongoDB
            # On utilise un context manager (with) pour fermer proprement la connexion
            with MongoDBManager() as mongo:
                # Récupère uniquement les documents enrichis avec succès
                # limit=10000 évite de surcharger la mémoire
                enriched_docs = mongo.get_enriched_documents(status="success", limit=10000)
            
            logger.info(f"📥 {len(enriched_docs)} documents extraits")
            
            # ÉTAPE 4 : TRANSFORM + LOAD - Charger chaque produit en SQL
            loaded = 0  # Compteur de produits chargés
            for doc in enriched_docs:
                # _load_product transforme et charge un document
                # Retourne True si le produit a été chargé avec succès
                if self._load_product(doc):
                    loaded += 1
            
            # ÉTAPE 5 : COMMIT - Sauvegarder tous les changements
            # Tant qu'on n'a pas fait commit, rien n'est vraiment en base!
            self.session.commit()
            logger.info(f"✅ {loaded} produits chargés en SQL")
            
        except Exception as e:
            # En cas d'erreur, on annule TOUS les changements
            # La base revient à son état d'avant le run()
            self.session.rollback()
            logger.error(f"Erreur ETL: {e}")
            raise  # On propage l'erreur pour que l'appelant soit au courant
        finally:
            # Dans tous les cas (succès ou erreur), on ferme la session
            # C'est important pour libérer les ressources
            self.session.close()
    
    def _get_or_create_brand(self, name: str) -> Optional[Brand]:
        """
        Récupère une marque existante ou en crée une nouvelle.
        
        Cette méthode implémente le pattern "Get or Create" :
        1. Vérifie si la marque est dans le cache (très rapide)
        2. Sinon, cherche dans la base de données
        3. Si elle n'existe pas, on la crée
        4. On l'ajoute au cache pour les prochains appels
        
        Args:
            name: Nom de la marque (ex: "Nestlé")
            
        Returns:
            Brand: L'objet marque, ou None si le nom est vide
        """
        # Si pas de nom, pas de marque
        if not name:
            return None
        
        # Nettoyer le nom : enlever les espaces et limiter à 255 caractères
        name = name.strip()[:255]
        
        # ÉTAPE 1 : Vérifier le cache (O(1), ultra rapide)
        if name in self.brands_cache:
            return self.brands_cache[name]
        
        # ÉTAPE 2 : Chercher dans la base de données
        brand = self.session.query(Brand).filter_by(name=name).first()
        
        # ÉTAPE 3 : Si elle n'existe pas, la créer
        if not brand:
            brand = Brand(name=name)
            self.session.add(brand)  # Ajoute à la session (pas encore en BDD)
            self.session.flush()  # Force l'insertion pour obtenir l'ID
        
        # ÉTAPE 4 : Mettre en cache pour les prochains produits de cette marque
        self.brands_cache[name] = brand
        return brand
    
    def _get_or_create_category(self, name: str) -> Optional[Category]:
        """
        Récupère une catégorie existante ou en crée une nouvelle.
        
        Même logique que _get_or_create_brand, mais pour les catégories.
        
        Args:
            name: Nom de la catégorie (ex: "Céréales")
            
        Returns:
            Category: L'objet catégorie, ou None si le nom est vide
        """
        if not name:
            return None
        
        # Nettoyage du nom
        name = name.strip()[:255]
        
        # Vérifier le cache
        if name in self.categories_cache:
            return self.categories_cache[name]
        
        # Chercher en base
        category = self.session.query(Category).filter_by(name=name).first()
        
        # Créer si inexistante
        if not category:
            category = Category(name=name)
            self.session.add(category)
            self.session.flush()
        
        # Mettre en cache
        self.categories_cache[name] = category
        return category
    
    def _load_product(self, enriched_doc: dict) -> bool:
        """
        Charge un produit enrichi en SQL (création ou mise à jour).
        
        Cette méthode est "idempotente" : on peut la rappeler plusieurs fois
        avec le même produit, il sera mis à jour au lieu d'être dupliqué.
        
        Args:
            enriched_doc: Document enrichi de MongoDB contenant les données produit
            
        Returns:
            bool: True si le produit a été chargé, False si données invalides
        """
        # Extraire les données du document MongoDB
        # Structure: {"raw_id": "...", "status": "success", "data": {...}}
        data = enriched_doc.get("data", {})
        code = data.get("code")  # Code-barres du produit
        
        # Sans code, impossible d'identifier le produit
        if not code:
            return False
        
        # Chercher si le produit existe déjà (par son code-barres)
        existing = self.session.query(Product).filter_by(code=code).first()
        
        if existing:
            # === MODE MISE À JOUR ===
            # Le produit existe, on met à jour ses informations
            existing.product_name = data.get("product_name", "")[:500]
            existing.nutriscore_grade = (data.get("nutriscore_grade") or "")[:1]
            existing.nova_group = data.get("nova_group")
            existing.quality_score = data.get("quality_score")
            
            # Récupérer ou créer la marque et la catégorie
            brand = self._get_or_create_brand(data.get("brands", ""))
            category = self._get_or_create_category(data.get("category", ""))
            existing.brand = brand
            existing.category = category
        else:
            # === MODE CRÉATION ===
            # Le produit n'existe pas, on le crée
            brand = self._get_or_create_brand(data.get("brands", ""))
            category = self._get_or_create_category(data.get("category", ""))
            
            # Créer le nouvel objet Product avec toutes ses données
            product = Product(
                code=code,
                product_name=data.get("product_name", "")[:500],
                brand=brand,  # SQLAlchemy gère automatiquement brand_id
                category=category,  # SQLAlchemy gère automatiquement category_id
                nutriscore_grade=(data.get("nutriscore_grade") or "")[:1],
                nova_group=data.get("nova_group"),
                quality_score=data.get("quality_score")
            )
            # Ajouter le produit à la session (sera inséré au commit)
            self.session.add(product)
        
        return True
