"""
=============================================================================
DASHBOARD STREAMLIT - INTERFACE DE VISUALISATION
=============================================================================
Ce fichier définit le dashboard interactif pour visualiser les données.

Streamlit est un framework Python pour créer rapidement des applications
web de data science. Il transforme du code Python en interface web.

FONCTIONNALITÉS :
- Affichage des statistiques globales (métriques clés)
- Distribution des Nutriscore (graphique)
- Liste paginée des produits avec filtres
- Détail des produits individuels

PRÉREQUIS :
L'API FastAPI doit être lancée sur http://localhost:8000

UTILISATION :
    streamlit run src/dashboard/app.py

Accessible via : http://localhost:8501
=============================================================================
"""

import streamlit as st  # Framework de dashboard
import requests  # Pour appeler notre API REST

# Configuration de la page Streamlit
# - page_title : Titre dans l'onglet du navigateur
# - page_icon : Emoji affiché dans l'onglet
# - layout : "wide" utilise toute la largeur de l'écran
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# URL de notre API FastAPI
# Le dashboard consomme les données via l'API REST
API_URL = "http://localhost:8000"


def api_get(endpoint: str, params: dict = None):
    """
    Effectue une requête GET vers notre API.
    
    Cette fonction centralise les appels API et gère les erreurs
    de manière uniforme.
    
    Args:
        endpoint: Chemin de l'endpoint (ex: "/items", "/stats")
        params: Paramètres de requête optionnels
        
    Returns:
        dict: Réponse JSON de l'API, ou None en cas d'erreur
    """
    try:
        # Construire l'URL complète et faire la requête
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()  # Lever une exception si erreur HTTP
        return r.json()  # Retourner les données JSON
    except Exception as e:
        # Afficher l'erreur dans l'interface Streamlit
        st.error(f"Erreur API: {e}")
        return None


# =============================================================================
# EN-TÊTE DU DASHBOARD
# =============================================================================

# Titre principal de la page
st.title("📊 Dashboard Produits")

# =============================================================================
# SECTION STATISTIQUES GLOBALES
# =============================================================================

# Récupérer les statistiques depuis l'API
stats = api_get("/stats")

if stats:
    # Afficher les métriques clés dans 4 colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    # Chaque métrique affiche une valeur avec son label
    col1.metric("Produits", stats["total_products"])       # Nombre total de produits
    col2.metric("Marques", stats["total_brands"])          # Nombre de marques
    col3.metric("Catégories", stats["total_categories"])   # Nombre de catégories
    col4.metric("Score moyen", stats["avg_quality_score"]) # Score qualité moyen
    
    # === DISTRIBUTION DES NUTRISCORE ===
    st.subheader("Distribution Nutriscore")
    
    # Récupérer la distribution depuis les stats
    dist = stats.get("nutriscore_distribution", {})
    
    # Afficher chaque grade dans une colonne avec son emoji de couleur
    cols = st.columns(5)
    # Mapping des grades vers des emojis colorés
    colors = {"a": "🟢", "b": "🟡", "c": "🟠", "d": "🔴", "e": "⚫"}
    
    # Afficher chaque grade Nutriscore
    for i, grade in enumerate(["a", "b", "c", "d", "e"]):
        cols[i].metric(f"{colors[grade]} {grade.upper()}", dist.get(grade, 0))

# Ligne de séparation visuelle
st.divider()

# =============================================================================
# SECTION LISTE DES PRODUITS
# =============================================================================

st.subheader("🔍 Liste des produits")

# === BARRE LATÉRALE AVEC FILTRES ===
# La sidebar permet de filtrer les produits sans encombrer la vue principale
with st.sidebar:
    st.header("Filtres")
    
    # Champ texte pour filtrer par catégorie
    filter_category = st.text_input("Catégorie")
    # Champ texte pour filtrer par marque
    filter_brand = st.text_input("Marque")
    # Menu déroulant pour le Nutriscore
    filter_nutriscore = st.selectbox("Nutriscore", ["", "a", "b", "c", "d", "e"])
    # Slider pour le score qualité minimum
    filter_min_quality = st.slider("Score qualité min", 0, 100, 0)

# === PAGINATION ===
col1, col2 = st.columns([1, 4])
page = col1.number_input("Page", min_value=1, value=1)  # Sélecteur de page
page_size = 20  # Nombre de produits par page

# Construire les paramètres de requête
params = {"page": page, "page_size": page_size}

# Ajouter les filtres s'ils sont définis
if filter_category:
    params["category"] = filter_category
if filter_brand:
    params["brand"] = filter_brand
if filter_nutriscore:
    params["nutriscore"] = filter_nutriscore
if filter_min_quality > 0:
    params["min_quality"] = filter_min_quality

# Récupérer les produits depuis l'API
data = api_get("/items", params)

if data:
    # Afficher les infos de pagination
    st.caption(f"Total: {data['total']} produits | Page {data['page']}/{data['total_pages']}")
    
    # === LISTE DES PRODUITS ===
    for item in data["items"]:
        # Chaque produit est dans un "expander" (accordéon cliquable)
        with st.expander(f"**{item['product_name']}** - {item.get('brand') or 'N/A'}"):
            # Afficher les détails sur 3 colonnes
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Code:** {item['code']}")
            col2.write(f"**Catégorie:** {item.get('category') or 'N/A'}")
            col3.write(f"**Nutriscore:** {(item.get('nutriscore_grade') or 'N/A').upper()}")
            st.write(f"**Score qualité:** {item.get('quality_score') or 'N/A'}")
            
            # Bouton pour voir plus de détails (appel API item individuel)
            if st.button(f"Voir détail", key=f"btn_{item['id']}"):
                detail = api_get(f"/items/{item['id']}")
                if detail:
                    # Afficher le JSON complet du produit
                    st.json(detail)
else:
    # Message si aucun produit trouvé ou API non disponible
    st.info("Aucun produit trouvé. Vérifiez que l'API est lancée.")
