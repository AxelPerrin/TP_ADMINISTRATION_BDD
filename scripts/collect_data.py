"""
=============================================================================
SCRIPT DE COLLECTE DE DONNÉES - OPENFOODFACTS
=============================================================================
Ce script récupère des données de produits alimentaires depuis l'API
OpenFoodFacts et les stocke dans MongoDB.

OpenFoodFacts est une base de données ouverte et collaborative sur
les produits alimentaires du monde entier.

UTILISATION :
    python scripts/collect_data.py                    # Collecte 300 produits
    python scripts/collect_data.py --count 500        # Collecte 500 produits
    python scripts/collect_data.py -c beverages       # Collecte seulement les boissons
    python scripts/collect_data.py --output data.json # Sauvegarde en JSON

FONCTIONNEMENT :
1. Parcourt les catégories de produits définies dans settings.py
2. Récupère des produits via l'API OpenFoodFacts
3. Vérifie la validité des données (champs obligatoires présents)
4. Élimine les doublons (basé sur le code-barres)
5. Stocke les données brutes dans MongoDB (collection products_raw)
=============================================================================
"""

import argparse  # Pour parser les arguments en ligne de commande
import json      # Pour lire/écrire des fichiers JSON
import sys
import time      # Pour les délais entre requêtes
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import requests  # Librairie pour faire des requêtes HTTP
from loguru import logger  # Librairie de logging avancée

# Ajouter le chemin racine au path Python pour pouvoir importer nos modules
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configuration des logs : format coloré avec timestamp
# logger.remove() enlève le handler par défaut
# logger.add() ajoute notre propre format
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")


class Collector:
    """
    Classe responsable de la collecte de données depuis OpenFoodFacts.
    
    Elle gère :
    - Les requêtes HTTP vers l'API avec retry en cas d'erreur
    - La validation des données reçues
    - La déduplication des produits
    - Les statistiques de collecte
    
    Attributs:
        page_size: Nombre de produits par page de résultats
        delay: Délai entre chaque requête (en secondes)
        timeout: Timeout des requêtes HTTP (en secondes)
        max_retries: Nombre de tentatives en cas d'erreur
        stats: Dictionnaire de statistiques de collecte
        session: Session HTTP requests (réutilise les connexions)
    """
    
    # Champs obligatoires : un produit DOIT avoir ces champs
    # pour être considéré comme valide
    REQUIRED_FIELDS = ["code", "product_name"]
    
    def __init__(self, page_size: int = 100, delay: float = 1.0, timeout: int = 30, max_retries: int = 3):
        """
        Initialise le collecteur avec ses paramètres.
        
        Args:
            page_size: Nombre de produits par requête (max 100 pour OpenFoodFacts)
            delay: Pause entre les requêtes pour ne pas surcharger l'API
            timeout: Temps maximum d'attente pour une réponse
            max_retries: Nombre de tentatives en cas d'échec
        """
        self.page_size = page_size
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Statistiques de collecte (pour le rapport final)
        self.stats = {
            "collected": 0,       # Produits collectés avec succès
            "errors": 0,          # Erreurs totales
            "timeouts": 0,        # Timeouts (serveur trop lent)
            "invalid_format": 0,  # Réponses JSON invalides
            "missing_data": 0     # Produits avec données manquantes
        }
        
        # Session HTTP persistante (optimisation des performances)
        # Réutilise les connexions TCP au lieu d'en créer une par requête
        self.session = requests.Session()
        # User-Agent : identifie notre script auprès de l'API
        self.session.headers.update({"User-Agent": "TP_BDD_Collector/1.0"})
    
    def _request(self, url: str, params: dict) -> Optional[dict]:
        """
        Effectue une requête HTTP GET avec retry en cas d'erreur.
        
        Cette méthode est robuste : elle réessaie plusieurs fois
        en cas de timeout ou d'erreur réseau, avec un délai croissant.
        
        Args:
            url: URL de l'API à appeler
            params: Paramètres de la requête (passés en query string)
            
        Returns:
            dict: Réponse JSON parsée, ou None en cas d'erreur définitive
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Effectuer la requête GET
                response = self.session.get(url, params=params, timeout=self.timeout)
                # Lever une exception si le code HTTP indique une erreur (4xx, 5xx)
                response.raise_for_status()
                # Parser et retourner le JSON
                return response.json()
                
            except requests.exceptions.Timeout:
                # Le serveur n'a pas répondu à temps
                self.stats["timeouts"] += 1
                self.stats["errors"] += 1
                logger.warning(f"Timeout (tentative {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    # Attendre de plus en plus longtemps entre les tentatives
                    # (backoff exponentiel : 2s, 4s, 6s, ...)
                    time.sleep(attempt * 2)
                    
            except json.JSONDecodeError:
                # La réponse n'est pas du JSON valide
                self.stats["invalid_format"] += 1
                self.stats["errors"] += 1
                logger.warning("Format JSON invalide")
                return None  # Pas de retry, c'est une erreur de données
                
            except requests.exceptions.RequestException as e:
                # Autres erreurs HTTP (connexion refusée, DNS, etc.)
                self.stats["errors"] += 1
                logger.error(f"Erreur requête: {e}")
                if attempt < self.max_retries:
                    time.sleep(attempt * 2)
                    
        # Toutes les tentatives ont échoué
        return None
    
    def _is_valid(self, product: dict) -> bool:
        """
        Vérifie si un produit a les champs obligatoires.
        
        Un produit sans code-barres ou sans nom n'est pas exploitable.
        
        Args:
            product: Données du produit à valider
            
        Returns:
            bool: True si le produit est valide, False sinon
        """
        for field in self.REQUIRED_FIELDS:
            # Vérifier que le champ existe et n'est pas vide
            if not product.get(field):
                return False
        return True
    
    def collect(self, target_count: int = 300, categories: Optional[List[str]] = None, country: str = "france") -> List[dict]:
        """
        Collecte des produits depuis OpenFoodFacts.
        
        Parcourt les catégories une par une et récupère des produits
        jusqu'à atteindre l'objectif (target_count).
        
        Args:
            target_count: Nombre de produits à collecter (objectif minimum)
            categories: Liste des catégories à parcourir (défaut: MAIN_CATEGORIES)
            country: Pays des produits à récupérer (défaut: France)
            
        Returns:
            List[dict]: Liste des produits collectés (données brutes)
        """
        # Import des constantes depuis la config
        from config.settings import MAIN_CATEGORIES, OPENFOODFACTS_SEARCH_URL
        
        # Utiliser les catégories par défaut si non spécifiées
        if categories is None:
            categories = MAIN_CATEGORIES
        
        collected = []  # Liste des produits collectés
        seen_codes = set()  # Ensemble des codes-barres déjà vus (pour déduplication)
        
        # Calculer combien de produits récupérer par catégorie
        # On prend un peu plus que nécessaire pour compenser les doublons
        products_per_category = max(target_count // len(categories) + 10, 50)
        
        logger.info(f"🎯 Objectif: {target_count} produits")
        
        # === BOUCLE SUR LES CATÉGORIES ===
        for category in categories:
            # Arrêter si on a atteint l'objectif
            if len(collected) >= target_count:
                break
            
            logger.info(f"📂 Catégorie: {category}")
            page = 1  # Numéro de page (pagination de l'API)
            category_count = 0  # Compteur pour cette catégorie
            
            # === BOUCLE DE PAGINATION ===
            while category_count < products_per_category and len(collected) < target_count:
                # Construire les paramètres de la requête de recherche
                params = {
                    "action": "process",      # Action de recherche
                    "json": 1,                # Réponse en JSON
                    "page_size": self.page_size,  # Produits par page
                    "page": page,             # Numéro de page
                    # Filtre par catégorie
                    "tagtype_0": "categories",
                    "tag_contains_0": "contains",
                    "tag_0": category,
                    # Filtre par pays
                    "tagtype_1": "countries",
                    "tag_contains_1": "contains",
                    "tag_1": country
                }
                
                # Effectuer la requête
                data = self._request(OPENFOODFACTS_SEARCH_URL, params)
                if not data or not isinstance(data, dict):
                    break  # Erreur ou réponse invalide
                
                products = data.get("products", [])
                if not products:
                    break  # Plus de produits dans cette catégorie
                
                # === TRAITEMENT DE CHAQUE PRODUIT ===
                for raw_product in products:
                    # Vérifier qu'on n'a pas atteint l'objectif
                    if len(collected) >= target_count:
                        break
                    
                    # Vérifier que c'est bien un dictionnaire
                    if not isinstance(raw_product, dict):
                        self.stats["invalid_format"] += 1
                        continue
                    
                    # Récupérer le code-barres pour la déduplication
                    code = raw_product.get("code", "")
                    if code in seen_codes:
                        continue  # Produit déjà collecté, on saute
                    
                    # Valider les champs obligatoires
                    if not self._is_valid(raw_product):
                        self.stats["missing_data"] += 1
                        continue
                    
                    # Produit valide ! On l'ajoute à la collection
                    collected.append(raw_product)
                    seen_codes.add(code)  # Marquer comme vu
                    category_count += 1
                    self.stats["collected"] += 1
                
                # Passer à la page suivante
                page += 1
                # Attendre un peu pour être poli avec l'API
                time.sleep(self.delay)
        
        # Afficher le résumé de la collecte
        logger.info(f"✅ Collectés: {self.stats['collected']} | Erreurs: {self.stats['errors']} | Timeouts: {self.stats['timeouts']} | Format invalide: {self.stats['invalid_format']} | Données manquantes: {self.stats['missing_data']}")
        return collected
    
    def save_to_mongodb(self, raw_products: List[dict]) -> int:
        """
        Sauvegarde les produits collectés dans MongoDB.
        
        Utilise le MongoDBManager pour insérer les produits dans
        la collection products_raw. Les doublons sont ignorés.
        
        Args:
            raw_products: Liste des produits à sauvegarder
            
        Returns:
            int: Nombre de produits effectivement insérés
        """
        from src.database.mongodb_manager import MongoDBManager
        
        # Utiliser le context manager pour gérer la connexion
        with MongoDBManager() as mongo:
            count = mongo.insert_raw_documents_batch(raw_products, source="openfoodfacts")
            logger.info(f"💾 {count} documents insérés dans MongoDB (RAW)")
            return count


# =============================================================================
# POINT D'ENTRÉE DU SCRIPT
# =============================================================================

def main():
    """
    Fonction principale du script de collecte.
    
    Parse les arguments en ligne de commande et lance la collecte.
    """
    # Définir les arguments acceptés par le script
    parser = argparse.ArgumentParser(description="Collecte OpenFoodFacts")
    parser.add_argument("--count", "-n", type=int, default=300, 
                        help="Nombre minimum de produits (défaut: 300)")
    parser.add_argument("--categories", "-c", nargs="+", default=None, 
                        help="Catégories à collecter")
    parser.add_argument("--country", default="france", 
                        help="Pays cible (défaut: france)")
    parser.add_argument("--no-mongodb", action="store_true", 
                        help="Ne pas sauvegarder dans MongoDB")
    parser.add_argument("--output", "-o", type=str, default=None, 
                        help="Fichier JSON de sortie")
    
    # Parser les arguments
    args = parser.parse_args()
    
    # Créer le collecteur avec les paramètres par défaut
    collector = Collector()
    
    try:
        # Lancer la collecte
        products = collector.collect(
            target_count=args.count, 
            categories=args.categories, 
            country=args.country
        )
        
        # Vérifier qu'on a bien des produits
        if not products:
            logger.error("Aucun produit collecté!")
            sys.exit(1)
        
        # Si un fichier de sortie est spécifié, sauvegarder en JSON
        if args.output:
            # Gérer les chemins relatifs et absolus
            output_path = Path(args.output) if Path(args.output).is_absolute() else ROOT_DIR / args.output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Écrire le fichier JSON avec indentation pour lisibilité
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Sauvegardé dans: {output_path}")
        
        # Sauvegarder dans MongoDB (sauf si --no-mongodb)
        if not args.no_mongodb:
            try:
                collector.save_to_mongodb(products)
            except Exception as e:
                logger.warning(f"MongoDB non disponible: {e}")
        
        logger.success(f"✅ Collecte terminée: {len(products)} produits")
        
    except KeyboardInterrupt:
        # L'utilisateur a appuyé sur Ctrl+C
        logger.warning("Collecte interrompue")
        sys.exit(1)


if __name__ == "__main__":
    main()
