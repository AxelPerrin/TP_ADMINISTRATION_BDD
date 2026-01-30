"""
=============================================================================
GESTIONNAIRE MONGODB - COUCHE D'ACCÈS AUX DONNÉES NOSQL
=============================================================================
Ce fichier gère toutes les interactions avec la base de données MongoDB.

MongoDB est une base de données NoSQL orientée documents :
- Stocke des documents JSON (flexibles, pas de schéma fixe)
- Idéale pour les données semi-structurées comme les produits OpenFoodFacts
- Très performante pour l'insertion massive de données

ARCHITECTURE DES COLLECTIONS :
- products_raw : Données brutes de l'API OpenFoodFacts (sans modification)
- products_enriched : Données après calcul du score qualité et catégorisation

PATTERN UTILISÉ : Context Manager
Permet d'utiliser "with MongoDBManager() as mongo:" pour gérer
automatiquement l'ouverture et la fermeture de la connexion.
=============================================================================
"""

import hashlib  # Pour calculer des hash SHA-256 (empreintes uniques)
import json  # Pour convertir des dictionnaires en chaînes JSON
from datetime import datetime  # Pour les timestamps
from typing import Optional, List  # Pour les annotations de type
from pymongo import MongoClient, ASCENDING  # Client MongoDB et constantes d'index
from pymongo.database import Database  # Type pour la base de données
from pymongo.collection import Collection  # Type pour les collections

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

# Import des configurations MongoDB
from config.settings import (
    MONGODB_URI,       # URI de connexion (mongodb://localhost:27017)
    MONGODB_DATABASE,  # Nom de la base (openfoodfacts)
    COLLECTION_RAW,    # Nom de la collection brute (products_raw)
    COLLECTION_ENRICHED  # Nom de la collection enrichie (products_enriched)
)


def compute_raw_hash(payload: dict) -> str:
    """
    Calcule un hash SHA-256 unique pour un payload de produit.
    
    Ce hash sert à détecter les doublons : si deux produits ont
    exactement le même contenu, ils auront le même hash.
    
    Args:
        payload: Dictionnaire contenant les données du produit
        
    Returns:
        str: Hash hexadécimal de 64 caractères (ex: "a1b2c3...")
        
    Exemple:
        >>> compute_raw_hash({"code": "123", "name": "Test"})
        'e5b9e3b3c5a2f1d4...'  # Hash unique du contenu
    """
    # Convertir le dict en JSON trié (pour que l'ordre des clés n'affecte pas le hash)
    payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    # Calculer le hash SHA-256 et le retourner en hexadécimal
    return hashlib.sha256(payload_str.encode()).hexdigest()


class MongoDBManager:
    """
    Gestionnaire de connexion et d'opérations MongoDB.
    
    Cette classe encapsule toutes les opérations sur MongoDB :
    - Connexion/déconnexion
    - Insertion de documents bruts (RAW)
    - Insertion de documents enrichis (ENRICHED)
    - Requêtes de lecture
    
    Peut être utilisée comme context manager :
        with MongoDBManager() as mongo:
            mongo.insert_raw_document(...)
    
    Attributs:
        uri: URI de connexion MongoDB
        database_name: Nom de la base de données
        _client: Client MongoDB (connexion)
        _db: Base de données MongoDB
    """
    
    def __init__(
        self,
        uri: str = MONGODB_URI,
        database: str = MONGODB_DATABASE
    ):
        """
        Initialise le gestionnaire MongoDB.
        
        Args:
            uri: URI de connexion (par défaut depuis settings.py)
            database: Nom de la base de données à utiliser
        """
        self.uri = uri
        self.database_name = database
        # Connexion lazy : on ne se connecte pas tout de suite,
        # mais seulement quand on en a besoin
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
    
    def connect(self) -> Database:
        """
        Établit la connexion à MongoDB.
        
        Crée le client MongoDB, sélectionne la base de données,
        et crée les index nécessaires pour les performances.
        
        Returns:
            Database: L'objet base de données MongoDB connecté
        """
        if self._client is None:
            # Créer le client MongoDB (établit la connexion TCP)
            self._client = MongoClient(self.uri)
            # Sélectionner la base de données (créée automatiquement si inexistante)
            self._db = self._client[self.database_name]
            # Créer les index pour optimiser les requêtes
            self._create_indexes()
        return self._db
    
    def close(self):
        """
        Ferme la connexion à MongoDB.
        
        Important pour libérer les ressources réseau et éviter les fuites.
        """
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    # === CONTEXT MANAGER ===
    # Permet d'utiliser "with MongoDBManager() as mongo:"
    
    def __enter__(self):
        """Appelé au début du 'with'. Retourne self pour l'utiliser."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Appelé à la fin du 'with'. Ferme la connexion automatiquement."""
        self.close()
    
    def _create_indexes(self):
        """
        Crée les index sur les collections pour optimiser les performances.
        
        Les index sont comme un index de livre : ils permettent de trouver
        rapidement des documents sans parcourir toute la collection.
        
        Index créés :
        - raw_hash (unique) : Empêche les doublons dans products_raw
        - fetched_at : Pour trier/filtrer par date de collecte
        - raw_id (unique) : Lie products_enriched à products_raw
        - status : Pour filtrer par statut (success/failed)
        """
        # Index sur la collection RAW
        raw_collection = self.get_raw_collection()
        # Index unique sur raw_hash : empêche d'insérer deux fois le même produit
        raw_collection.create_index([("raw_hash", ASCENDING)], unique=True)
        # Index sur la date de collecte (pour le tri chronologique)
        raw_collection.create_index([("fetched_at", ASCENDING)])
        
        # Index sur la collection ENRICHED
        enriched_collection = self.get_enriched_collection()
        # Index unique sur raw_id : un seul enrichissement par document RAW
        enriched_collection.create_index([("raw_id", ASCENDING)], unique=True)
        # Index sur le statut (pour filtrer success/failed/pending)
        enriched_collection.create_index([("status", ASCENDING)])
    
    @property
    def db(self) -> Database:
        """
        Propriété pour accéder à la base de données.
        
        Se connecte automatiquement si pas encore fait (lazy loading).
        
        Returns:
            Database: La base de données MongoDB
        """
        if self._db is None:
            self.connect()
        return self._db
    
    def get_raw_collection(self) -> Collection:
        """
        Retourne la collection des documents bruts (RAW).
        
        Returns:
            Collection: Collection MongoDB 'products_raw'
        """
        return self.db[COLLECTION_RAW]
    
    def get_enriched_collection(self) -> Collection:
        """
        Retourne la collection des documents enrichis.
        
        Returns:
            Collection: Collection MongoDB 'products_enriched'
        """
        return self.db[COLLECTION_ENRICHED]
    
    # =========================================================================
    # OPÉRATIONS SUR LES DOCUMENTS BRUTS (RAW)
    # =========================================================================
    
    def insert_raw_document(self, payload: dict, source: str = "openfoodfacts") -> Optional[str]:
        """
        Insère un document brut dans la collection RAW.
        
        Le document est enrichi avec des métadonnées :
        - source : origine des données (ex: "openfoodfacts")
        - fetched_at : date/heure de collecte
        - raw_hash : empreinte unique pour détecter les doublons
        
        Args:
            payload: Données du produit telles que reçues de l'API
            source: Origine des données (par défaut: openfoodfacts)
            
        Returns:
            str: Le raw_hash si insertion réussie, None si doublon
        """
        # Calculer le hash unique du payload
        raw_hash = compute_raw_hash(payload)
        
        # Construire le document à insérer
        document = {
            "source": source,  # D'où viennent les données
            "fetched_at": datetime.utcnow().isoformat() + "Z",  # Quand on les a récupérées
            "raw_hash": raw_hash,  # Hash unique pour détecter les doublons
            "payload": payload  # Les données brutes du produit
        }
        
        try:
            # Tenter l'insertion
            self.get_raw_collection().insert_one(document)
            return raw_hash  # Succès!
        except Exception:
            # L'insertion a échoué (probablement un doublon à cause de l'index unique)
            return None
    
    def insert_raw_documents_batch(self, payloads: List[dict], source: str = "openfoodfacts") -> int:
        """
        Insère plusieurs documents bruts en une seule opération.
        
        Plus efficace que d'appeler insert_raw_document en boucle car
        on réduit les allers-retours réseau avec MongoDB.
        
        Les doublons sont ignorés silencieusement grâce à l'index unique.
        
        Args:
            payloads: Liste des données produits à insérer
            source: Origine des données
            
        Returns:
            int: Nombre de documents effectivement insérés (hors doublons)
        """
        # Timestamp commun pour tous les documents du batch
        fetched_at = datetime.utcnow().isoformat() + "Z"
        inserted_count = 0
        
        for payload in payloads:
            # Calculer le hash de chaque payload
            raw_hash = compute_raw_hash(payload)
            
            document = {
                "source": source,
                "fetched_at": fetched_at,
                "raw_hash": raw_hash,
                "payload": payload
            }
            
            try:
                self.get_raw_collection().insert_one(document)
                inserted_count += 1  # Compter les insertions réussies
            except Exception:
                # Ignorer les doublons (l'exception vient de l'index unique)
                pass
        
        return inserted_count
    
    def count_raw_documents(self) -> int:
        """
        Compte le nombre total de documents bruts.
        
        Returns:
            int: Nombre de documents dans products_raw
        """
        return self.get_raw_collection().count_documents({})
    
    def get_raw_documents_for_enrichment(self) -> List[dict]:
        """
        Récupère tous les documents bruts pour les enrichir.
        
        Returns:
            List[dict]: Liste de tous les documents RAW
        """
        return list(self.get_raw_collection().find({}))
    
    # =========================================================================
    # OPÉRATIONS SUR LES DOCUMENTS ENRICHIS (ENRICHED)
    # =========================================================================
    
    def insert_enriched_document(self, enriched_doc: dict) -> Optional[str]:
        """
        Insère ou met à jour un document enrichi.
        
        Utilise "upsert" : si le document existe (même raw_id),
        il est mis à jour ; sinon il est créé.
        
        Args:
            enriched_doc: Document enrichi à insérer
            
        Returns:
            str: Le raw_id si succès, None sinon
        """
        try:
            # update_one avec upsert=True : crée ou met à jour
            self.get_enriched_collection().update_one(
                {"raw_id": enriched_doc["raw_id"]},  # Critère de recherche
                {"$set": enriched_doc},  # Données à insérer/mettre à jour
                upsert=True  # Créer si inexistant
            )
            return enriched_doc["raw_id"]
        except Exception:
            return None
    
    def insert_enriched_documents_batch(self, enriched_docs: List[dict]) -> int:
        """
        Insère plusieurs documents enrichis en une opération bulk.
        
        Utilise bulk_write pour optimiser les performances :
        toutes les opérations sont envoyées en une seule requête.
        
        Args:
            enriched_docs: Liste des documents enrichis
            
        Returns:
            int: Nombre de documents insérés/modifiés
        """
        from pymongo import UpdateOne
        
        # Construire la liste des opérations bulk
        operations = [
            UpdateOne(
                {"raw_id": doc["raw_id"]},  # Critère de recherche
                {"$set": doc},  # Données à insérer/mettre à jour
                upsert=True  # Créer si inexistant
            )
            for doc in enriched_docs if doc.get("raw_id")  # Ignorer les docs sans raw_id
        ]
        
        if operations:
            # Exécuter toutes les opérations en une seule requête (très efficace!)
            result = self.get_enriched_collection().bulk_write(operations)
            # Retourner le total des docs créés + modifiés
            return result.upserted_count + result.modified_count
        return 0
    
    def count_enriched_documents(self, status: Optional[str] = None) -> int:
        """
        Compte les documents enrichis, optionnellement filtrés par statut.
        
        Args:
            status: Filtre optionnel ("success", "failed", "pending")
            
        Returns:
            int: Nombre de documents correspondants
        """
        # Si un statut est spécifié, filtrer ; sinon compter tout
        query = {"status": status} if status else {}
        return self.get_enriched_collection().count_documents(query)
    
    def get_enriched_documents(self, status: Optional[str] = None, limit: int = 100) -> List[dict]:
        """
        Récupère les documents enrichis avec filtrage et limitation.
        
        Args:
            status: Filtre optionnel par statut
            limit: Nombre maximum de documents à retourner
            
        Returns:
            List[dict]: Liste des documents enrichis
        """
        query = {"status": status} if status else {}
        return list(self.get_enriched_collection().find(query).limit(limit))
