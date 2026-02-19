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
    
    /* Carte produit */
    .product-card {
        background: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .product-name {
        color: #fff;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .product-brand {
        color: #aaa;
        font-size: 0.85rem;
    }
    
    /* Image placeholder */
    .img-placeholder {
        background: #3d3d3d;
        height: 150px;
        border: 2px solid #fff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        font-size: 0.8rem;
    }
    
    /* Image produit avec taille fixe */
    .product-img-container {
        width: 100%;
        height: 150px;
        background: #3d3d3d;
        border: 2px solid #fff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 0.5rem;
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
        ["Tableau de bord", "Produits", "Recherche"],
        label_visibility="collapsed",
        captions=["Vue d'ensemble", "Parcourir le catalogue", "Recherche avancée"]
    )
    
    st.divider()
    
    # === BARRE DE RECHERCHE ===
    st.markdown("**🔍 Recherche rapide**")
    search_query = st.text_input(
        "Rechercher",
        placeholder="Nom, marque, catégorie...",
        label_visibility="collapsed",
        help="Tapez un mot-clé pour filtrer les produits"
    )
    
    st.divider()
    
    # === FILTRES NUTRISCORE (Checkboxes) ===
    st.markdown("**🏷️ Nutriscore**")
    st.caption("A = Excellent → E = À limiter")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        nutri_a = st.checkbox("A", value=True, key="nutri_a")
    with col2:
        nutri_b = st.checkbox("B", value=True, key="nutri_b")
    with col3:
        nutri_c = st.checkbox("C", value=True, key="nutri_c")
    with col4:
        nutri_d = st.checkbox("D", value=True, key="nutri_d")
    with col5:
        nutri_e = st.checkbox("E", value=True, key="nutri_e")
    
    # Construire la liste des nutriscores sélectionnés
    selected_nutri = []
    if nutri_a: selected_nutri.append("a")
    if nutri_b: selected_nutri.append("b")
    if nutri_c: selected_nutri.append("c")
    if nutri_d: selected_nutri.append("d")
    if nutri_e: selected_nutri.append("e")
    
    st.divider()
    
    # === FILTRES CATÉGORIES (Checkboxes) ===
    st.markdown("**🗂️ Catégories**")
    st.caption("Filtrer par type de produit")
    
    # Récupérer les catégories depuis l'API
    categories_list = api_get("/categories") or []
    
    # Afficher les catégories en checkboxes (max 10 affichées)
    selected_categories = []
    filter_brand = None  # Filtre marque (non implémenté pour l'instant)
    if categories_list:
        # Limiter à 10 catégories pour ne pas surcharger
        display_cats = categories_list[:10]
        for cat in display_cats:
            if st.checkbox(cat, value=False, key=f"cat_{cat}"):
                selected_categories.append(cat)
        
        if len(categories_list) > 10:
            st.caption(f"+ {len(categories_list) - 10} autres catégories")
    else:
        st.caption("Aucune catégorie")
    
    # Nombre fixe de produits par page
    page_size = 48
    
    st.divider()
    
    if st.button("Réinitialiser", use_container_width=True):
        st.session_state.current_page = 1
        st.session_state.selected_product_id = None
        st.rerun()


# =============================================================================
# HEADER
# =============================================================================

# Header principal avec mission
st.markdown('''
<div class="hero-section">
    <p class="main-title">🥗 Food Analytics</p>
    <p class="hero-mission">Explorez et analysez les données nutritionnelles</p>
    <p class="subtitle">
        Découvrez la qualité nutritionnelle de milliers de produits alimentaires.<br>
        Filtrez par Nutriscore, catégorie ou marque pour trouver les meilleurs choix pour votre santé.
    </p>
</div>
''', unsafe_allow_html=True)


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
    
    # Section explicative
    st.markdown('''
    <div style="background:#252525; border-radius:8px; padding:1rem; margin-bottom:1rem; border-left:4px solid #2196F3;">
        <strong style="color:#2196F3;">📦 Catalogue Produits</strong><br>
        <span style="color:#aaa;">Parcourez tous les produits. Cliquez sur "Voir détail" pour consulter les informations nutritionnelles complètes.</span>
    </div>
    ''', unsafe_allow_html=True)
    
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
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Image du produit
                render_product_image(detail['code'])
            
            with col2:
                st.markdown(f"### {detail['product_name']}")
                st.caption(detail.get('brand') or 'Marque inconnue')
                
                st.divider()
                
                # Infos en grille
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown("**Code-barres**")
                    st.code(detail['code'])
                    
                    st.markdown("**Catégorie**")
                    st.write(detail.get('category') or 'Non catégorisé')
                
                with info_col2:
                    nutriscore = detail.get('nutriscore_grade', '')
                    st.markdown("**Nutriscore**")
                    if nutriscore:
                        st.markdown(f'<span class="nutri-badge nutri-{nutriscore.lower()}">{nutriscore.upper()}</span>', unsafe_allow_html=True)
                    else:
                        st.write("Non disponible")
                    
                    st.markdown("**Score qualité**")
                    quality = detail.get('quality_score')
                    if quality:
                        st.progress(quality / 100)
                        st.write(f"{quality}/100")
                    else:
                        st.write("Non disponible")
                
                st.divider()
                
                nova = detail.get('nova_group')
                if nova:
                    nova_labels = {1: "Aliments non transformés", 2: "Ingrédients culinaires", 3: "Aliments transformés", 4: "Produits ultra-transformés"}
                    st.markdown(f"**Groupe NOVA** : {nova} - {nova_labels.get(nova, '')}")
        else:
            st.error("Produit non trouvé")
    
    else:
        # Liste des produits
        
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
            
            # Info pagination
            st.markdown(f'''
            <div class="pagination-bar">
                {data["total"]} produits • Page {data["page"]} sur {data["total_pages"]}
            </div>
            ''', unsafe_allow_html=True)
            
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
            cols = st.columns(4)
            
            # Filtrer par nutriscore sélectionné
            filtered_items = [
                item for item in data["items"]
                if not item.get('nutriscore_grade') or item.get('nutriscore_grade', '').lower() in selected_nutri
            ]
            
            for idx, item in enumerate(filtered_items):
                with cols[idx % 4]:
                    
                    # Container pour chaque produit
                    with st.container():
                        # Image produit
                        render_product_image(item['code'])
                        
                        # Nom produit (tronqué)
                        name = item['product_name']
                        display_name = name[:35] + '...' if len(name) > 35 else name
                        st.markdown(f"**{display_name}**")
                        
                        # Marque
                        st.caption(item.get('brand') or 'Marque inconnue')
                        
                        # Nutriscore et score
                        nutriscore = item.get('nutriscore_grade', '')
                        quality = item.get('quality_score')
                        
                        meta_col1, meta_col2 = st.columns(2)
                        with meta_col1:
                            if nutriscore:
                                st.markdown(f'<span class="nutri-badge nutri-{nutriscore.lower()}">{nutriscore.upper()}</span>', unsafe_allow_html=True)
                            else:
                                st.markdown('<span class="nutri-badge nutri-unknown">?</span>', unsafe_allow_html=True)
                        with meta_col2:
                            st.caption(f"Score: {quality or '-'}")
                        
                        # Bouton voir détail
                        if st.button("Voir détail", key=f"btn_{item['id']}", use_container_width=True):
                            st.session_state.selected_product_id = item['id']
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # === PAGINATION EN BAS ===
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Info pagination
            st.markdown(f'''
            <div class="pagination-bar">
                {data["total"]} produits • Page {data["page"]} sur {data["total_pages"]}
            </div>
            ''', unsafe_allow_html=True)
            
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
# PAGE : RECHERCHE
# =============================================================================

elif page_mode == "Recherche":
    
    # Section explicative
    st.markdown('''
    <div style="background:#252525; border-radius:8px; padding:1rem; margin-bottom:1rem; border-left:4px solid #FF9800;">
        <strong style="color:#FF9800;">🔍 Recherche Avancée</strong><br>
        <span style="color:#aaa;">Utilisez les filtres dans la barre latérale ou entrez un code-barres pour trouver un produit spécifique.</span>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("**📷 Recherche par code-barres**")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        search_code = st.text_input("Code-barres", placeholder="Ex: 3017620422003", label_visibility="collapsed")
    with col2:
        search_btn = st.button("Rechercher", use_container_width=True)
    
    st.divider()
    
    # Afficher résultats si filtres actifs ou recherche
    if any([selected_categories, filter_brand, search_query]):
        
        st.markdown("**Résultats filtrés**")
        
        params = {"page": 1, "page_size": 20}
        if search_query:
            params["search"] = search_query
        if selected_categories:
            params["category"] = selected_categories[0]
        if filter_brand:
            params["brand"] = filter_brand
        
        data = api_get("/items", params)
        
        if data and data["total"] > 0:
            st.success(f"{data['total']} produit(s) trouvé(s)")
            
            for item in data["items"][:10]:
                with st.expander(f"{item['product_name']} - {item.get('brand') or 'N/A'}"):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        render_product_image(item['code'])
                    
                    with col2:
                        st.markdown(f"**Code:** `{item['code']}`")
                        st.markdown(f"**Catégorie:** {item.get('category') or 'N/A'}")
                        
                        nutriscore = item.get('nutriscore_grade', '')
                        quality = item.get('quality_score')
                        st.markdown(f"**Nutriscore:** {nutriscore.upper() if nutriscore else 'N/A'} | **Score:** {quality or 'N/A'}")
        else:
            st.warning("Aucun résultat")
    else:
        st.caption("Utilisez les filtres dans la barre latérale pour rechercher des produits.")


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
