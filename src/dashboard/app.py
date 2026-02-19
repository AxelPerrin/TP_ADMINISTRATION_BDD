"""
=============================================================================
DASHBOARD STREAMLIT - INTERFACE DE VISUALISATION PROFESSIONNELLE
=============================================================================
Dashboard sobre et professionnel pour visualiser les données OpenFoodFacts.

UTILISATION :
    streamlit run src/dashboard/app.py

Accessible via : http://localhost:8501
=============================================================================
"""

import streamlit as st
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Food Analytics",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# =============================================================================
# STYLES CSS - DESIGN SOBRE ET PROFESSIONNEL
# =============================================================================

st.markdown("""
<style>
    /* === THEME SOMBRE PROFESSIONNEL === */
    
    .stApp {
        background-color: #1e1e1e;
    }
    
    /* Header principal */
    .hero-section {
        background: linear-gradient(135deg, #2d2d2d 0%, #1e1e1e 100%);
        border: 1px solid #3d3d3d;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .hero-mission {
        color: #4CAF50;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.8rem;
    }
    
    .subtitle {
        color: #aaa;
        font-size: 0.95rem;
        margin-bottom: 0;
        line-height: 1.5;
    }
    
    /* Cartes métriques */
    .stat-card {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #3d3d3d;
        text-align: center;
        transition: transform 0.2s;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: #4d4d4d;
    }
    
    .stat-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #888;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-desc {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    /* Nutriscore badges */
    .nutri-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
        color: white;
    }
    
    .nutri-a { background: #038141; }
    .nutri-b { background: #85BB2F; }
    .nutri-c { background: #FECB02; color: #333; }
    .nutri-d { background: #EE8100; }
    .nutri-e { background: #E63E11; }
    .nutri-unknown { background: #555; color: #aaa; }
    
    /* Distribution Nutriscore */
    .nutri-dist-item {
        background: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .nutri-dist-count {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Pagination */
    .pagination-bar {
        background: #2d2d2d;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        border: 1px solid #3d3d3d;
        text-align: center;
        color: #ccc;
        font-size: 0.9rem;
        margin: 0.8rem 0;
    }
    
    /* Carte produit améliorée */
    .product-card {
        background: linear-gradient(145deg, #2d2d2d 0%, #252525 100%);
        border: 1px solid #3d3d3d;
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        border-color: #4CAF50;
        box-shadow: 0 12px 24px rgba(76, 175, 80, 0.2);
    }
    
    .product-name {
        color: #fff;
        font-weight: 600;
        font-size: 0.95rem;
        line-height: 1.3;
        min-height: 2.6em;
    }
    
    .product-brand {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .product-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #3d3d3d;
    }
    
    .quality-score {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 0.9rem;
    }
    
    /* Image placeholder */
    .img-placeholder {
        background: linear-gradient(145deg, #3d3d3d 0%, #2d2d2d 100%);
        height: 160px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        font-size: 2rem;
        margin-bottom: 0.8rem;
    }
    
    /* Image produit avec taille fixe */
    .product-img-container {
        width: 100%;
        height: 160px;
        background: linear-gradient(145deg, #3d3d3d 0%, #2d2d2d 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 0.8rem;
        position: relative;
    }
    
    .product-img-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.4) 100%);
        border-radius: 12px;
        pointer-events: none;
        z-index: 1;
    }
    
    .product-img-container img {
        transition: transform 0.3s ease;
    }
    
    .product-card:hover .product-img-container img {
        transform: scale(1.05);
    }
    
    /* Filtre barre */
    .filter-bar {
        background: linear-gradient(145deg, #2d2d2d 0%, #252525 100%);
        border: 1px solid #3d3d3d;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .filter-chip {
        display: inline-flex;
        align-items: center;
        background: #3d3d3d;
        border: 1px solid #4d4d4d;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #ccc;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .filter-chip:hover {
        background: #4d4d4d;
        border-color: #4CAF50;
    }
    
    .filter-chip.active {
        background: #4CAF50;
        border-color: #4CAF50;
        color: #fff;
    }
    
    /* Bouton stylé */
    .btn-detail {
        background: linear-gradient(145deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
        text-align: center;
    }
    
    .btn-detail:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
    }
    
    /* Recherche intégrée */
    .search-container {
        background: linear-gradient(145deg, #2d2d2d 0%, #252525 100%);
        border: 1px solid #3d3d3d;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    
    .search-input {
        background: #1e1e1e !important;
        border: 2px solid #3d3d3d !important;
        border-radius: 25px !important;
        padding: 0.8rem 1.2rem !important;
        color: #fff !important;
        font-size: 1rem !important;
        width: 100%;
        transition: border-color 0.2s ease;
    }
    
    .search-input:focus {
        border-color: #4CAF50 !important;
        outline: none;
    }
    
    /* Style pour st.image */
    .stImage {
        border: 2px solid #fff;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stImage img {
        border-radius: 6px;
        max-height: 150px;
        object-fit: contain;
    }
    
    .product-img-container img {
        max-width: 100%;
        max-height: 150px;
        object-fit: contain;
    }
    
    /* Sidebar sombre */
    section[data-testid="stSidebar"] {
        background: #252525 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #fff;
    }
    
    /* Inputs sombres */
    .stTextInput input {
        background-color: #3d3d3d !important;
        color: #fff !important;
        border-color: #4d4d4d !important;
    }
    
    .stSelectbox > div > div {
        background-color: #3d3d3d !important;
        color: #fff !important;
    }
            
    /* Header Streamlit */
    header[data-testid="stHeader"] {
        background: #1e1e1e;
    }
    
    /* Supprimer le gap entre les colonnes (cartes collées) */
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
    
    /* Texte général blanc */
    .stMarkdown, .stText, p, span, label {
        color: #e0e0e0 !important;
    }
    
    /* Expanders sombres */
    .streamlit-expanderHeader {
        background: #2d2d2d !important;
        color: #fff !important;
    }
    
    .streamlit-expanderContent {
        background: #252525 !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: #3d3d3d;
        color: #fff;
        border: 1px solid #4d4d4d;
    }
    
    .stButton > button:hover {
        background: #4d4d4d;
        border-color: #5d5d5d;
    }
    
    /* Dividers */
    hr {
        border-color: #3d3d3d !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def api_get(endpoint: str, params: dict = None):
    """Requête GET vers l'API."""
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def get_image_url(code: str) -> str:
    """
    Génère l'URL directe de l'image du produit.
    Pas d'appel API - URL construite directement depuis le code-barres.
    """
    if not code or len(code) < 8:
        return None
    
    # Nettoyer le code (enlever espaces, tirets)
    code = code.replace(" ", "").replace("-", "")
    
    # Formater le code pour l'URL (structure de dossiers OpenFoodFacts)
    if len(code) <= 8:
        path = code
    else:
        # Pour les codes longs, utiliser la structure XXX/XXX/XXX/XXXX
        code = code.zfill(13)
        path = f"{code[0:3]}/{code[3:6]}/{code[6:9]}/{code[9:]}"
    
    # URL directe vers l'image
    return f"https://images.openfoodfacts.org/images/products/{path}/front_fr.400.jpg"


def get_nutriscore_class(grade: str) -> str:
    """Retourne la classe CSS pour le nutriscore."""
    if not grade:
        return "nutri-unknown"
    return f"nutri-{grade.lower()}"


@st.cache_data(ttl=86400)
def fetch_product_image(code: str) -> str:
    """
    Récupère l'URL de l'image depuis l'API OpenFoodFacts.
    Mise en cache 24h pour éviter les appels répétés.
    """
    if not code:
        return None
    try:
        r = requests.get(
            f"https://world.openfoodfacts.org/api/v0/product/{code}.json",
            timeout=5
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == 1:
                product = data.get("product", {})
                # Essayer plusieurs champs d'image
                img = product.get("image_front_small_url") or \
                      product.get("image_front_url") or \
                      product.get("image_url") or \
                      product.get("image_small_url")
                return img
    except:
        pass
    return None


def render_product_image(code: str):
    """
    Affiche une image produit avec taille fixe et bordure blanche.
    """
    img_url = fetch_product_image(code)
    if img_url:
        st.markdown(f'''
        <div style="width:100%; height:150px; border:2px solid #fff; border-radius:8px; 
                    background:#3d3d3d; display:flex; align-items:center; justify-content:center; 
                    overflow:hidden; margin-bottom:0.5rem;">
            <img src="{img_url}" style="max-width:100%; max-height:146px; object-fit:contain;" />
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width:100%; height:150px; border:2px solid #fff; border-radius:8px; background:#3d3d3d; display:flex; align-items:center; justify-content:center; color:#888;">Pas d\'image</div>', unsafe_allow_html=True)


# =============================================================================
# VÉRIFICATION API
# =============================================================================

stats = api_get("/stats")

if not stats:
    st.markdown("## Food Analytics")
    st.error("Impossible de se connecter à l'API.")
    st.code("python -m uvicorn src.api.main:app --reload", language="bash")
    st.stop()


# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None
# Initialisation des filtres
if 'product_search' not in st.session_state:
    st.session_state.product_search = ""
if 'nutri_a' not in st.session_state:
    st.session_state.nutri_a = True
if 'nutri_b' not in st.session_state:
    st.session_state.nutri_b = True
if 'nutri_c' not in st.session_state:
    st.session_state.nutri_c = True
if 'nutri_d' not in st.session_state:
    st.session_state.nutri_d = True
if 'nutri_e' not in st.session_state:
    st.session_state.nutri_e = True
if 'category_filter' not in st.session_state:
    st.session_state.category_filter = "Toutes"


# =============================================================================
# SIDEBAR - NAVIGATION ET FILTRES
# =============================================================================

with st.sidebar:
    st.markdown("### 🥗 Food Analytics")
    st.caption("Base de données alimentaires")
    
    st.divider()
    
    # Navigation avec icônes
    st.markdown("**🧭 Navigation**")
    page_mode = st.radio(
        "Navigation",
        ["Tableau de bord", "Produits"],
        label_visibility="collapsed",
        captions=["Vue d'ensemble et statistiques", "Explorer et rechercher"]
    )
    
    st.divider()
    
    st.caption("Données issues de Open Food Facts")


# =============================================================================
# PAGE : TABLEAU DE BORD (Statistiques)
# =============================================================================

if page_mode == "Tableau de bord":
    
    # Section explicative
    st.markdown('''
    <div style="background:#252525; border-radius:8px; padding:1rem; margin-bottom:1.5rem; border-left:4px solid #4CAF50;">
        <strong style="color:#4CAF50;">📊 Tableau de bord</strong><br>
        <span style="color:#aaa;">Vue d'ensemble des données collectées depuis Open Food Facts. Ces statistiques représentent l'ensemble des produits dans notre base de données.</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Métriques principales avec explications
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-value">{stats["total_products"]:,}</div>
            <div class="stat-label">Produits</div>
            <div class="stat-desc">Nombre total de produits alimentaires référencés</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">🏭</div>
            <div class="stat-value">{stats["total_brands"]:,}</div>
            <div class="stat-label">Marques</div>
            <div class="stat-desc">Marques différentes dans la base</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">🗂️</div>
            <div class="stat-value">{stats["total_categories"]:,}</div>
            <div class="stat-label">Catégories</div>
            <div class="stat-desc">Types de produits (boissons, snacks...)</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        avg = stats["avg_quality_score"] or 0
        st.markdown(f'''
        <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">{avg:.0f}<span style="font-size:0.9rem;color:#888;">/100</span></div>
            <div class="stat-label">Score moyen</div>
            <div class="stat-desc">Qualité moyenne des produits</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Distribution Nutriscore avec explication
    st.markdown('''
    <div style="background:#252525; border-radius:8px; padding:1rem; margin-bottom:1rem; border-left:4px solid #85BB2F;">
        <strong style="color:#85BB2F;">🏷️ Répartition Nutriscore</strong><br>
        <span style="color:#aaa;">Le Nutriscore classe les produits de A (excellent) à E (à limiter) selon leur qualité nutritionnelle.</span>
    </div>
    ''', unsafe_allow_html=True)
    
    dist = stats.get("nutriscore_distribution", {})
    cols = st.columns(5)
    
    grades_info = [("A", "#038141"), ("B", "#85BB2F"), ("C", "#FECB02"), ("D", "#EE8100"), ("E", "#E63E11")]
    
    for i, (grade, color) in enumerate(grades_info):
        count = dist.get(grade.lower(), 0)
        with cols[i]:
            st.markdown(f'''
            <div class="nutri-dist-item">
                <div class="nutri-badge nutri-{grade.lower()}" style="margin: 0 auto 0.5rem auto;">{grade}</div>
                <div class="nutri-dist-count">{count}</div>
            </div>
            ''', unsafe_allow_html=True)


# =============================================================================
# PAGE : PRODUITS (Liste avec images)
# =============================================================================

elif page_mode == "Produits":
    
    # Vérifier si on affiche un détail
    if st.session_state.selected_product_id:
        
        # Bouton retour
        if st.button("← Retour à la liste"):
            st.session_state.selected_product_id = None
            st.rerun()
        
        st.divider()
        
        # Charger le détail
        detail = api_get(f"/items/{st.session_state.selected_product_id}")
        
        if detail:
            # === HEADER PRODUIT ===
            nutriscore = detail.get('nutriscore_grade', '')
            quality = detail.get('quality_score') or 0
            nova = detail.get('nova_group')
            brand = detail.get('brand') or 'Marque inconnue'
            category = detail.get('category') or 'Non catégorisé'
            
            # Couleurs Nutriscore
            nutri_colors = {'a': '#038141', 'b': '#85BB2F', 'c': '#FECB02', 'd': '#EE8100', 'e': '#E63E11'}
            nutri_color = nutri_colors.get(nutriscore.lower(), '#555') if nutriscore else '#555'
            
            # Layout principal - 3 colonnes pour espacer
            img_col, spacer_col, info_col = st.columns([1.2, 0.15, 1.8])
            
            with img_col:
                # Image avec cadre stylé
                img_url = fetch_product_image(detail['code'])
                if img_url:
                    st.markdown(f'''
                    <div style="background: linear-gradient(145deg, #2d2d2d, #252525); 
                                border-radius: 16px; padding: 1.5rem; 
                                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                                display: flex; align-items: center; justify-content: center;
                                min-height: 280px;">
                        <img src="{img_url}" style="max-width: 100%; max-height: 250px; 
                                                     object-fit: contain; border-radius: 8px;" />
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown('''
                    <div style="background: linear-gradient(145deg, #2d2d2d, #252525); 
                                border-radius: 16px; padding: 1.5rem; 
                                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                                display: flex; align-items: center; justify-content: center;
                                min-height: 280px; color: #666; font-size: 4rem;">
                        📦
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Catégorie sous l'image
                st.markdown(f'''
                <div style="background: #2d2d2d; border-left: 4px solid #4CAF50; padding: 0.8rem 1rem; 
                            border-radius: 0 8px 8px 0; margin-top: 1rem;">
                    <span style="color: #888; font-size: 0.75rem; text-transform: uppercase;">Catégorie</span><br>
                    <span style="color: #fff; font-size: 0.95rem;">{category}</span>
                </div>
                ''', unsafe_allow_html=True)
            
            with spacer_col:
                st.write("")  # Colonne vide pour l'espacement
            
            with info_col:
                # Titre et marque
                st.markdown(f'''
                <div style="margin-bottom: 1.5rem;">
                    <h1 style="color: #fff; font-size: 1.8rem; margin: 0; line-height: 1.3;">
                        {detail['product_name']}
                    </h1>
                    <p style="color: #888; font-size: 1rem; margin-top: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">
                        {brand}
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Badges Nutriscore et Score
                st.markdown(f'''
                <div style="display: flex; gap: 1rem; margin: 1.5rem 0;">
                    <div style="background: {nutri_color}; color: white; padding: 0.8rem 1.5rem; 
                                border-radius: 12px; text-align: center; min-width: 100px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                        <div style="font-size: 2rem; font-weight: 700;">{nutriscore.upper() if nutriscore else '?'}</div>
                        <div style="font-size: 0.75rem; opacity: 0.9;">NUTRISCORE</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; 
                                padding: 0.8rem 1.5rem; border-radius: 12px; text-align: center; min-width: 100px;
                                box-shadow: 0 4px 12px rgba(76,175,80,0.3);">
                        <div style="font-size: 2rem; font-weight: 700;">{quality}</div>
                        <div style="font-size: 0.75rem; opacity: 0.9;">SCORE /100</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # === INFORMATIONS DÉTAILLÉES ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            detail_cols = st.columns(3)
            
            with detail_cols[0]:
                st.markdown(f'''
                <div style="background: linear-gradient(145deg, #2d2d2d, #252525); border-radius: 12px; 
                            padding: 1.2rem; text-align: center; height: 120px;
                            display: flex; flex-direction: column; justify-content: center;">
                    <div style="color: #888; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Code-barres</div>
                    <div style="color: #4CAF50; font-size: 1.1rem; font-family: monospace; font-weight: 600;">{detail['code']}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with detail_cols[1]:
                nova_labels = {1: "Non transformé", 2: "Culinaire", 3: "Transformé", 4: "Ultra-transformé"}
                nova_colors = {1: "#038141", 2: "#85BB2F", 3: "#EE8100", 4: "#E63E11"}
                nova_label = nova_labels.get(nova, "Non disponible") if nova else "Non disponible"
                nova_color = nova_colors.get(nova, "#555") if nova else "#555"
                
                st.markdown(f'''
                <div style="background: linear-gradient(145deg, #2d2d2d, #252525); border-radius: 12px; 
                            padding: 1.2rem; text-align: center; height: 120px;
                            display: flex; flex-direction: column; justify-content: center;">
                    <div style="color: #888; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Groupe NOVA</div>
                    <div style="color: {nova_color}; font-size: 1.8rem; font-weight: 700;">{nova if nova else '?'}</div>
                    <div style="color: #aaa; font-size: 0.8rem;">{nova_label}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with detail_cols[2]:
                # Barre de progression visuelle
                progress_color = "#4CAF50" if quality >= 70 else "#FECB02" if quality >= 40 else "#E63E11"
                st.markdown(f'''
                <div style="background: linear-gradient(145deg, #2d2d2d, #252525); border-radius: 12px; 
                            padding: 1.2rem; text-align: center; height: 120px;
                            display: flex; flex-direction: column; justify-content: center;">
                    <div style="color: #888; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem;">Qualité globale</div>
                    <div style="background: #1e1e1e; border-radius: 10px; height: 12px; overflow: hidden; margin: 0.5rem 0;">
                        <div style="background: linear-gradient(90deg, {progress_color}, {progress_color}aa); 
                                    width: {quality}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                    <div style="color: #fff; font-size: 0.9rem;">{quality}/100</div>
                </div>
                ''', unsafe_allow_html=True)
            
        else:
            st.error("Produit non trouvé")
    
    else:
        # Liste des produits
        
        # Fonction de reset des filtres
        def reset_filters():
            st.session_state.current_page = 1
            st.session_state["product_search"] = ""
            st.session_state["nutri_a"] = True
            st.session_state["nutri_b"] = True
            st.session_state["nutri_c"] = True
            st.session_state["nutri_d"] = True
            st.session_state["nutri_e"] = True
            st.session_state["category_filter"] = "Toutes"
        
        # === BARRE DE RECHERCHE ===
        search_col1, search_col2 = st.columns([4, 1])
        with search_col2:
            st.button("🔄 Reset", use_container_width=True, on_click=reset_filters)
        with search_col1:
            search_query = st.text_input(
                "🔍 Rechercher un produit",
                placeholder="Nom, marque, code-barres...",
                label_visibility="collapsed",
                key="product_search"
            )
        
        # === FILTRES ===
        with st.expander("🎛️ Filtres avancés", expanded=False):
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                # Filtre Nutriscore
                st.markdown("**🏷️ Nutriscore**")
                nutri_cols = st.columns(5)
                with nutri_cols[0]:
                    nutri_a = st.checkbox("A", key="nutri_a")
                with nutri_cols[1]:
                    nutri_b = st.checkbox("B", key="nutri_b")
                with nutri_cols[2]:
                    nutri_c = st.checkbox("C", key="nutri_c")
                with nutri_cols[3]:
                    nutri_d = st.checkbox("D", key="nutri_d")
                with nutri_cols[4]:
                    nutri_e = st.checkbox("E", key="nutri_e")
            
            with filter_col2:
                # Filtre Catégories
                st.markdown("**🗂️ Catégorie**")
                categories_list = api_get("/categories") or []
                selected_category = st.selectbox(
                    "Catégorie",
                    options=["Toutes"] + categories_list,
                    label_visibility="collapsed",
                    key="category_filter"
                )
        
        # Construire la liste des nutriscores sélectionnés
        selected_nutri = []
        if nutri_a: selected_nutri.append("a")
        if nutri_b: selected_nutri.append("b")
        if nutri_c: selected_nutri.append("c")
        if nutri_d: selected_nutri.append("d")
        if nutri_e: selected_nutri.append("e")
        
        # Catégorie sélectionnée
        selected_categories = [selected_category] if selected_category != "Toutes" else []
        filter_brand = None
        page_size = 48
        
        # Filtres actifs
        active_filters = []
        if search_query:
            active_filters.append(f"🔎 \"{search_query}\"")
        if selected_categories:
            active_filters.append(f"🗂️ {selected_categories[0]}")
        if len(selected_nutri) < 5:
            active_filters.append(f"🏷️ {', '.join([n.upper() for n in selected_nutri])}")
        
        if active_filters:
            st.markdown(f'''
            <div style="background:#1e1e1e; border:1px solid #4CAF50; border-radius:8px; padding:0.5rem 1rem; margin:0.5rem 0 1rem 0;">
                <span style="color:#4CAF50; font-size:0.85rem;">Filtres:</span> 
                <span style="color:#ccc; font-size:0.85rem;">{" • ".join(active_filters)}</span>
            </div>
            ''', unsafe_allow_html=True)
        
        # Construire les paramètres
        params = {"page": st.session_state.current_page, "page_size": page_size}
        
        if search_query:
            params["search"] = search_query
        # Catégorie : prendre la première sélectionnée s'il y en a
        if selected_categories:
            params["category"] = selected_categories[0]
        if filter_brand:
            params["brand"] = filter_brand
        # Nutriscore : on filtre côté client pour permettre plusieurs sélections
        
        data = api_get("/items", params)
        
        if data and data["total"] > 0:
            
            # Navigation pages
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("← Précédent", disabled=data["page"] <= 1, use_container_width=True):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col3:
                if st.button("Suivant →", disabled=data["page"] >= data["total_pages"], use_container_width=True):
                    st.session_state.current_page += 1
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Grille de produits (4 colonnes)
            cols = st.columns(4, gap="small")
            
            # Filtrer par nutriscore sélectionné
            filtered_items = [
                item for item in data["items"]
                if not item.get('nutriscore_grade') or item.get('nutriscore_grade', '').lower() in selected_nutri
            ]
            
            for idx, item in enumerate(filtered_items):
                with cols[idx % 4]:
                    
                    # Récupérer les données
                    name = item['product_name']
                    display_name = name[:32] + '...' if len(name) > 32 else name
                    brand = item.get('brand') or 'Marque inconnue'
                    nutriscore = item.get('nutriscore_grade', '')
                    quality = item.get('quality_score')
                    nutri_class = f"nutri-{nutriscore.lower()}" if nutriscore else "nutri-unknown"
                    nutri_display = nutriscore.upper() if nutriscore else "?"
                    
                    # Image avec fallback
                    img_url = fetch_product_image(item['code'])
                    img_html = f'<img src="{img_url}" style="max-width:100%; max-height:140px; object-fit:contain; border-radius:8px;" />' if img_url else '<div style="font-size:3rem; color:#555;">📦</div>'
                    
                    # Carte produit HTML complète
                    st.markdown(f'''
                    <div class="product-card">
                        <div style="width:100%; height:150px; background:linear-gradient(145deg, #3d3d3d 0%, #2d2d2d 100%); 
                                    border-radius:12px; display:flex; align-items:center; justify-content:center; 
                                    overflow:hidden; margin-bottom:0.8rem;">
                            {img_html}
                        </div>
                        <div class="product-name">{display_name}</div>
                        <div class="product-brand">{brand}</div>
                        <div class="product-meta">
                            <span class="nutri-badge {nutri_class}">{nutri_display}</span>
                            <span class="quality-score">Score: {quality or '-'}/100</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Bouton voir détail
                    if st.button("👁️ Détails", key=f"btn_{item['id']}", use_container_width=True):
                        st.session_state.selected_product_id = item['id']
                        st.rerun()
            
            # === PAGINATION EN BAS ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Boutons navigation (en bas)
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("← Précédent", disabled=data["page"] <= 1, use_container_width=True, key="prev_bottom"):
                    st.session_state.current_page -= 1
                    st.rerun()
            with col3:
                if st.button("Suivant →", disabled=data["page"] >= data["total_pages"], use_container_width=True, key="next_bottom"):
                    st.session_state.current_page += 1
                    st.rerun()
        
        else:
            st.info("Aucun produit trouvé. Modifiez les filtres.")


# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown('''
<div style="text-align:center; padding:1rem;">
    <p style="color:#666; font-size:0.85rem; margin:0;">🥗 <strong>Food Analytics</strong> — Données issues de <a href="https://world.openfoodfacts.org" target="_blank" style="color:#4CAF50;">Open Food Facts</a></p>
    <p style="color:#555; font-size:0.75rem; margin-top:0.5rem;">TP Administration BDD • Les données sont mises à jour régulièrement</p>
</div>
''', unsafe_allow_html=True)
