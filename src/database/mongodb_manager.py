import hashlib
import json
from datetime import datetime
from typing import Optional, List
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])

from config.settings import (
    MONGODB_URI,
    MONGODB_DATABASE,
    COLLECTION_RAW,
    COLLECTION_ENRICHED
)


def compute_raw_hash(payload: dict) -> str:
    """Hash unique du payload."""
    payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload_str.encode()).hexdigest()


class MongoDBManager:
    def __init__(
        self,
        uri: str = MONGODB_URI,
        database: str = MONGODB_DATABASE
    ):
        self.uri = uri
        self.database_name = database
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
    
    def connect(self) -> Database:
        if self._client is None:
            self._client = MongoClient(self.uri)
            self._db = self._client[self.database_name]
            self._create_indexes()
        return self._db
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _create_indexes(self):
        raw_collection = self.get_raw_collection()
        raw_collection.create_index([("raw_hash", ASCENDING)], unique=True)
        raw_collection.create_index([("fetched_at", ASCENDING)])
        
        enriched_collection = self.get_enriched_collection()
        enriched_collection.create_index([("raw_id", ASCENDING)], unique=True)
        enriched_collection.create_index([("status", ASCENDING)])
    
    @property
    def db(self) -> Database:
        if self._db is None:
            self.connect()
        return self._db
    
    def get_raw_collection(self) -> Collection:
        return self.db[COLLECTION_RAW]
    
    def get_enriched_collection(self) -> Collection:
        return self.db[COLLECTION_ENRICHED]
    
    # RAW
    
    def insert_raw_document(self, payload: dict, source: str = "openfoodfacts") -> Optional[str]:
        """Insère un document RAW. Retourne raw_hash ou None si doublon."""
        raw_hash = compute_raw_hash(payload)
        
        document = {
            "source": source,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "raw_hash": raw_hash,
            "payload": payload
        }
        
        try:
            self.get_raw_collection().insert_one(document)
            return raw_hash
        except Exception:
            return None
    
    def insert_raw_documents_batch(self, payloads: List[dict], source: str = "openfoodfacts") -> int:
        fetched_at = datetime.utcnow().isoformat() + "Z"
        inserted_count = 0
        
        for payload in payloads:
            raw_hash = compute_raw_hash(payload)
            
            document = {
                "source": source,
                "fetched_at": fetched_at,
                "raw_hash": raw_hash,
                "payload": payload
            }
            
            try:
                self.get_raw_collection().insert_one(document)
                inserted_count += 1
            except Exception:
                pass
        
        return inserted_count
    
    def count_raw_documents(self) -> int:
        return self.get_raw_collection().count_documents({})
    
    def get_raw_documents_for_enrichment(self) -> List[dict]:
        return list(self.get_raw_collection().find({}))
    
    # ENRICHED
    
    def insert_enriched_document(self, enriched_doc: dict) -> Optional[str]:
        try:
            self.get_enriched_collection().update_one(
                {"raw_id": enriched_doc["raw_id"]},
                {"$set": enriched_doc},
                upsert=True
            )
            return enriched_doc["raw_id"]
        except Exception:
            return None
    
    def insert_enriched_documents_batch(self, enriched_docs: List[dict]) -> int:
        from pymongo import UpdateOne
        
        operations = [
            UpdateOne(
                {"raw_id": doc["raw_id"]},
                {"$set": doc},
                upsert=True
            )
            for doc in enriched_docs if doc.get("raw_id")
        ]
        
        if operations:
            result = self.get_enriched_collection().bulk_write(operations)
            return result.upserted_count + result.modified_count
        return 0
    
    def count_enriched_documents(self, status: Optional[str] = None) -> int:
        query = {"status": status} if status else {}
        return self.get_enriched_collection().count_documents(query)
    
    def get_enriched_documents(self, status: Optional[str] = None, limit: int = 100) -> List[dict]:
        query = {"status": status} if status else {}
        return list(self.get_enriched_collection().find(query).limit(limit))
