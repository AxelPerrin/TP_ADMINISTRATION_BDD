"""
=============================================================================
MODULE D'ENRICHISSEMENT DES DONNÉES
=============================================================================
Ce fichier contient la logique d'enrichissement des données brutes.

L'enrichissement transforme les données brutes de l'API en données
exploitables en ajoutant :
- Un score de qualité calculé (0-100)
- Une catégorie normalisée et lisible
- Un statut de traitement (success/failed)

FLUX DE DONNÉES :
Document RAW (MongoDB) → enrich_product() → Document ENRICHED (MongoDB)

L'enrichissement est "retry-able" : en cas d'erreur, on réessaie
plusieurs fois avant de marquer le document comme "failed".
=============================================================================
"""

from datetime import datetime
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit("src", 1)[0])


# =============================================================================
# CONSTANTES POUR LE CALCUL DU SCORE QUALITÉ
# =============================================================================

# Mapping Nutriscore → Score numérique
# Le Nutriscore A donne 100 points, E donne 20 points
# Ces valeurs sont utilisées pour calculer le score qualité global
NUTRISCORE_SCORES = {"a": 100, "b": 80, "c": 60, "d": 40, "e": 20}


# =============================================================================
# FONCTION PRINCIPALE D'ENRICHISSEMENT
# =============================================================================

def enrich_product(raw_doc: dict, max_retries: int = 2) -> dict:
    """
    Enrichit un document brut et retourne le document enrichi.
    
    Cette fonction prend les données brutes d'un produit et les transforme
    en ajoutant des informations calculées (score qualité, catégorie normalisée).
    
    Elle gère les erreurs avec un système de retry : si l'enrichissement
    échoue, on réessaie jusqu'à max_retries fois avant d'abandonner.
    
    Args:
        raw_doc: Document brut de MongoDB (avec _id et payload)
        max_retries: Nombre de tentatives en cas d'erreur (défaut: 2)
        
    Returns:
        dict: Document enrichi avec la structure suivante :
            {
                "raw_id": "ObjectId du document RAW",
                "status": "success" | "failed" | "pending",
                "enriched_at": "2024-01-15T10:30:00Z",
                "data": {
                    "code": "code-barres",
                    "product_name": "Nom du produit",
                    "brands": "Marque",
                    "quality_score": 75,  # Score calculé 0-100
                    "category": "Catégorie normalisée",
                    "nutriscore_grade": "b",
                    "nova_group": 3
                },
                "error": {...}  # Seulement si status == "failed"
            }
    """
    # Extraire l'identifiant unique du document RAW
    # C'est un ObjectId MongoDB converti en string
    raw_id = str(raw_doc.get("_id", ""))
    
    # Extraire le payload (les données brutes du produit)
    payload = raw_doc.get("payload", {})
    
    # Boucle de retry : on essaie plusieurs fois en cas d'erreur
    for attempt in range(max_retries + 1):
        try:
            # === CALCULS D'ENRICHISSEMENT ===
            
            # Calculer le score de qualité (combinaison Nutriscore + complétude)
            quality_score = _calculate_quality_score(payload)
            
            # Déterminer la catégorie principale et la normaliser
            category = _categorize_product(payload)
            
            # === CONSTRUCTION DU DOCUMENT ENRICHI ===
            return {
                "raw_id": raw_id,  # Lien vers le document RAW original
                "status": "success",  # L'enrichissement a réussi
                "enriched_at": datetime.utcnow().isoformat() + "Z",  # Timestamp ISO 8601
                "data": {
                    # Données extraites du payload original
                    "code": payload.get("code", ""),
                    "product_name": payload.get("product_name", ""),
                    "brands": payload.get("brands", ""),
                    # Données calculées par l'enrichissement
                    "quality_score": quality_score,
                    "category": category,
                    # Données nutritionnelles existantes
                    "nutriscore_grade": payload.get("nutriscore_grade", ""),
                    "nova_group": payload.get("nova_group"),
                }
            }
            
        except Exception as e:
            # L'enrichissement a échoué
            if attempt == max_retries:
                # C'était la dernière tentative → marquer comme failed
                return {
                    "raw_id": raw_id,
                    "status": "failed",  # Échec définitif
                    "enriched_at": datetime.utcnow().isoformat() + "Z",
                    "data": {},  # Pas de données enrichies
                    "error": {
                        "code": type(e).__name__,  # Type d'erreur (ex: "ValueError")
                        "message": str(e)  # Message d'erreur détaillé
                    }
                }
            # Sinon, on réessaie (la boucle continue)
    
    # Fallback de sécurité (ne devrait jamais être atteint)
    return {"raw_id": raw_id, "status": "pending", "enriched_at": None, "data": {}}


# =============================================================================
# FONCTIONS UTILITAIRES DE CALCUL
# =============================================================================

def _calculate_quality_score(payload: dict) -> int:
    """
    Calcule un score de qualité global (0-100) pour un produit.
    
    Le score combine deux critères :
    - Nutriscore (50% du score) : A=100, B=80, C=60, D=40, E=20
    - Complétude des données (50% du score) : Pourcentage de champs remplis
    
    Formule : score = (nutriscore_score × 0.5) + (completeness × 50)
    
    Args:
        payload: Données brutes du produit
        
    Returns:
        int: Score qualité entre 0 et 100
        
    Exemples:
        - Produit Nutriscore A avec 100% de complétude → 100
        - Produit Nutriscore C avec 50% de complétude → 55
        - Produit sans Nutriscore ni données → 0
    """
    score = 0
    
    # === COMPOSANTE 1 : NUTRISCORE (50% du score final) ===
    # Récupérer le nutriscore et le convertir en minuscule
    nutriscore = payload.get("nutriscore_grade", "").lower()
    # Chercher le score correspondant dans le mapping, défaut 0 si inconnu
    # Puis multiplier par 0.5 car ça compte pour 50%
    score += NUTRISCORE_SCORES.get(nutriscore, 0) * 0.5
    
    # === COMPOSANTE 2 : COMPLÉTUDE DES DONNÉES (50% du score final) ===
    # La complétude est un nombre entre 0 et 1 fourni par OpenFoodFacts
    # Elle indique quel pourcentage des champs du produit sont remplis
    completeness = payload.get("completeness", 0) or 0  # Gérer None
    # Multiplier par 50 pour avoir une contribution de 0 à 50 points
    score += completeness * 50
    
    # S'assurer que le score ne dépasse pas 100 et le convertir en entier
    return int(min(score, 100))


def _categorize_product(payload: dict) -> str:
    """
    Détermine et formate la catégorie principale du produit.
    
    Ordre de priorité :
    1. Catégorie principale (main_category) si elle existe
    2. Première catégorie de la liste categories_tags
    3. "Non catégorisé" si aucune catégorie trouvée
    
    Le formatage transforme les tags techniques en texte lisible :
    "en:breakfast-cereals" → "Breakfast Cereals"
    
    Args:
        payload: Données brutes du produit
        
    Returns:
        str: Nom de catégorie formaté et lisible
    """
    # Essayer d'abord la catégorie principale
    main_cat = payload.get("main_category", "")
    if main_cat:
        # Nettoyer le format : enlever "en:", remplacer "-" par espace, capitaliser
        return main_cat.replace("en:", "").replace("-", " ").title()
    
    # Sinon, utiliser la première catégorie de la liste
    categories = payload.get("categories_tags", [])
    if categories:
        # Prendre la première et la formater
        return categories[0].replace("en:", "").replace("-", " ").title()
    
    # Aucune catégorie trouvée
    return "Non catégorisé"
