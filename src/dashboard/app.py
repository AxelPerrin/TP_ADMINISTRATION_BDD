"""Dashboard Streamlit - Food Analytics"""

import streamlit as st
import requests

# Configuration
st.set_page_config(page_title="Food Analytics", page_icon="🥗", layout="wide", initial_sidebar_state="expanded")
API_URL = "http://localhost:8000"

# CSS - Thème professionnel sombre
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #111827;
        --bg-secondary: #1f2937;
        --bg-card: #1f2937;
        --accent: #3b82f6;
        --accent-light: #60a5fa;
        --text-primary: #f9fafb;
        --text-secondary: #9ca3af;
        --text-muted: #6b7280;
        --border: #374151;
        --border-light: #4b5563;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    header[data-testid="stHeader"] {
        background: var(--bg-secondary) !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div { gap: 0.4rem; }
    section[data-testid="stSidebar"] .stRadio label {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: var(--border) !important;
        border-color: var(--accent) !important;
    }
    
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .stat-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.3); transform: translateY(-2px); }
    .stat-icon { font-size: 1.8rem; margin-bottom: 0.6rem; }
    .stat-value { font-size: 2rem; font-weight: 700; color: var(--text-primary); }
    .stat-label { font-size: 0.75rem; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; margin-top: 0.3rem; }
    .stat-desc { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.3rem; }
    
    .nutri-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        color: white;
    }
    .nutri-a { background: #059669; }
    .nutri-b { background: #84cc16; }
    .nutri-c { background: #eab308; color: #1f2937; }
    .nutri-d { background: #f97316; }
    .nutri-e { background: #dc2626; }
    .nutri-unknown { background: #6b7280; }
    
    .nutri-dist-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    .nutri-dist-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
    .nutri-dist-count { font-size: 1.3rem; font-weight: 600; color: var(--text-primary); margin-top: 0.4rem; }
    
    .section-header {
        background: var(--bg-card);
        padding: 0.9rem 1.2rem;
        border-radius: 10px;
        border-left: 3px solid var(--accent);
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    }
    .section-header strong { color: var(--text-primary) !important; font-size: 0.95rem; font-weight: 600; }
    
    .stTextInput input {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 0.7rem 1rem !important;
    }
    .stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important; }
    
    .stSelectbox > div > div {
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: var(--accent-light) !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
    }
            
    .stMarkdown, p {color:#ffffff !important;}
    
    .stMarkdown, span, label { color: var(--text-secondary) !important; }
    h1, h2, h3 { color: var(--text-primary) !important; }
    
    [data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }
    
    .stExpander {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    
    .stCheckbox label span { color: var(--text-primary) !important; }
    
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
    
    hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


def api_get(endpoint: str, params: dict = None):
    """Requête GET vers l'API."""
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return None


# Vérification API
stats = api_get("/stats")
if not stats:
    st.error("API non disponible. Lancez: python -m uvicorn src.api.main:app --reload")
    st.stop()

# Session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None
for key in ['product_search', 'category_filter']:
    if key not in st.session_state:
        st.session_state[key] = "" if key == 'product_search' else "Toutes"
for grade in ['a', 'b', 'c', 'd', 'e']:
    if f'nutri_{grade}' not in st.session_state:
        st.session_state[f'nutri_{grade}'] = True

# Sidebar
with st.sidebar:
    st.markdown("### 🥗 Food Analytics")
    st.caption("Base de données alimentaires")
    st.divider()
    page_mode = st.radio("Navigation", ["Tableau de bord", "Produits"], label_visibility="collapsed")
    st.divider()
    st.caption("Données: Open Food Facts")


# Page: Tableau de bord
if page_mode == "Tableau de bord":
    st.markdown('<div class="section-header"><strong>📊 Tableau de bord</strong></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    for col, icon, value, label, desc in [
        (col1, "📦", stats["total_products"], "Produits", "Produits référencés"),
        (col2, "🏭", stats["total_brands"], "Marques", "Marques différentes"),
        (col3, "🗂️", stats["total_categories"], "Catégories", "Types de produits"),
        (col4, "⭐", f'{(stats["avg_quality_score"] or 0):.0f}', "Score moyen", "Qualité moyenne"),
    ]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-icon">{icon}</div><div class="stat-value">{value}</div><div class="stat-label">{label}</div><div class="stat-desc">{desc}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header"><strong>🏷️ Répartition Nutriscore</strong></div>', unsafe_allow_html=True)
    
    dist = stats.get("nutriscore_distribution", {})
    cols = st.columns(5)
    for i, (grade, color) in enumerate([("A", "#059669"), ("B", "#84cc16"), ("C", "#eab308"), ("D", "#f97316"), ("E", "#dc2626")]):
        with cols[i]:
            st.markdown(f'<div class="nutri-dist-item"><div class="nutri-badge nutri-{grade.lower()}" style="margin:0 auto 0.5rem auto;">{grade}</div><div class="nutri-dist-count">{dist.get(grade.lower(), 0)}</div></div>', unsafe_allow_html=True)


# Page: Produits
elif page_mode == "Produits":
    
    # DÉTAIL PRODUIT
    if st.session_state.selected_product_id:
        if st.button("← Retour aux produits", use_container_width=False):
            st.session_state.selected_product_id = None
            st.rerun()
        
        detail = api_get(f"/items/{st.session_state.selected_product_id}")
        if not detail:
            st.error("Produit non trouvé")
            st.stop()
        
        nutriscore = detail.get('nutriscore_grade', '')
        quality = detail.get('quality_score') or 0
        nova = detail.get('nova_group')
        brand = detail.get('brand') or 'Marque inconnue'
        category = detail.get('category') or 'Non catégorisé'
        nutri_colors = {'a': '#059669', 'b': '#84cc16', 'c': '#eab308', 'd': '#f97316', 'e': '#dc2626'}
        nutri_bg = nutri_colors.get(nutriscore.lower(), '#9ca3af') if nutriscore else '#9ca3af'
        
        # Hero Section
        st.markdown(f'''
        <div style="background: #1f2937; border: 1px solid #374151; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
            <div style="display: flex; gap: 2rem; align-items: flex-start; flex-wrap: wrap;">
                <div style="flex: 0 0 260px; display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 240px; height: 240px; background: #111827; border-radius: 12px; display: flex; align-items: center; justify-content: center; border: 1px solid #374151;">
                        {f'<img src="{detail.get("image_url")}" style="max-width: 90%; max-height: 90%; object-fit: contain;" />' if detail.get('image_url') else '<span style="font-size: 4rem; color: #4b5563;">📦</span>'}
                    </div>
                    <div style="margin-top: 1rem; background: #374151; border-radius: 8px; padding: 0.5rem 1rem; text-align: center;">
                        <span style="color: #9ca3af; font-size: 0.75rem;">🏷️ {category}</span>
                    </div>
                </div>
                <div style="flex: 1; min-width: 280px;">
                    <h1 style="color: #f9fafb; font-size: 1.6rem; margin: 0 0 0.5rem 0; font-weight: 600;">{detail["product_name"]}</h1>
                    <p style="color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem; margin-bottom: 1.5rem;">{brand}</p>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <div style="background: {nutri_bg}; color: {'#1f2937' if nutriscore == 'c' else 'white'}; padding: 1rem 1.5rem; border-radius: 12px; text-align: center; min-width: 100px;">
                            <div style="font-size: 2rem; font-weight: 700;">{nutriscore.upper() if nutriscore else '?'}</div>
                            <div style="font-size: 0.65rem; letter-spacing: 1px; opacity: 0.9;">NUTRISCORE</div>
                        </div>
                        <div style="background: #3b82f6; color: white; padding: 1rem 1.5rem; border-radius: 12px; text-align: center; min-width: 100px;">
                            <div style="font-size: 2rem; font-weight: 700;">{quality}</div>
                            <div style="font-size: 0.65rem; letter-spacing: 1px;">SCORE /100</div>
                        </div>
                    </div>
                    <div style="margin-top: 1.5rem; padding: 1rem; background: #111827; border-radius: 8px; border-left: 3px solid #3b82f6;">
                        <span style="color: #6b7280; font-size: 0.7rem; text-transform: uppercase;">Code-barres</span><br>
                        <span style="color: #f9fafb; font-family: monospace; font-size: 1rem;">{detail["code"]}</span>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Info Cards
        nova_labels = {1: "Non transformé", 2: "Ingrédients culinaires", 3: "Aliments transformés", 4: "Ultra-transformés"}
        nova_colors = {1: "#059669", 2: "#84cc16", 3: "#f97316", 4: "#dc2626"}
        progress_color = "#10b981" if quality >= 70 else "#f59e0b" if quality >= 40 else "#ef4444"
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
            <div style="background: #1f2937; border: 1px solid #374151; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
                <div style="color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Groupe NOVA</div>
                <div style="color: {nova_colors.get(nova, '#6b7280')}; font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;">{nova if nova else '?'}</div>
                <div style="color: #f9fafb; font-size: 0.85rem;">{nova_labels.get(nova, 'Non disponible')}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
            <div style="background: #1f2937; border: 1px solid #374151; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
                <div style="color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Score Qualité</div>
                <div style="background: #374151; border-radius: 6px; height: 8px; overflow: hidden; margin: 1rem 0;">
                    <div style="background: {progress_color}; width: {quality}%; height: 100%; border-radius: 6px;"></div>
                </div>
                <div style="color: #f9fafb; font-size: 1.5rem; font-weight: 600;">{quality}<span style="color: #6b7280; font-size: 0.9rem;">/100</span></div>
            </div>
            ''', unsafe_allow_html=True)
    
    # LISTE PRODUITS
    else:
        def reset_filters():
            st.session_state.current_page = 1
            st.session_state.product_search = ""
            st.session_state.category_filter = "Toutes"
            for g in ['a', 'b', 'c', 'd', 'e']:
                st.session_state[f'nutri_{g}'] = True
        
        # Header de recherche stylisé
        st.markdown('<div class="section-header"><strong>🔍 Catalogue produits</strong></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        with col1:
            search = st.text_input("Recherche", placeholder="🔎 Rechercher par nom, marque ou code-barres...", label_visibility="collapsed", key="product_search")
        with col2:
            st.button("↻ Reset", use_container_width=True, on_click=reset_filters)
        
        with st.expander("⚙️ Filtres avancés", expanded=False):
            f1, f2 = st.columns(2)
            with f1:
                st.markdown("<p style='color:#f9fafb; font-weight:500; margin-bottom:0.5rem;'>Nutriscore</p>", unsafe_allow_html=True)
                nc = st.columns(5)
                nutri_checks = {}
                for i, g in enumerate(['a', 'b', 'c', 'd', 'e']):
                    with nc[i]:
                        nutri_checks[g] = st.checkbox(g.upper(), key=f"nutri_{g}")
            with f2:
                st.markdown("<p style='color:#f9fafb; font-weight:500; margin-bottom:0.5rem;'>Catégorie</p>", unsafe_allow_html=True)
                categories = api_get("/categories") or []
                st.selectbox("Cat", ["Toutes"] + categories, label_visibility="collapsed", key="category_filter")
        
        selected_nutri = [g for g in ['a', 'b', 'c', 'd', 'e'] if nutri_checks.get(g)]
        
        params = {"page": st.session_state.current_page, "page_size": 48}
        if search:
            params["search"] = search
        if st.session_state.category_filter != "Toutes":
            params["category"] = st.session_state.category_filter
        
        data = api_get("/items", params)
        
        if data and data["total"] > 0:
            # Pagination stylisée
            st.markdown(f'''
            <div style="display:flex; justify-content:space-between; align-items:center; background:#1f2937; border:1px solid #374151; border-radius:10px; padding:0.8rem 1.2rem; margin-bottom:1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.15);">
                <span style="color:#9ca3af; font-size:0.85rem;">📦 <strong style="color:#f9fafb;">{data["total"]}</strong> produits trouvés</span>
                <span style="color:#3b82f6; font-size:0.85rem;">Page <strong>{data["page"]}</strong> / {data["total_pages"]}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1:
                if st.button("◀ Précédent", disabled=data["page"] <= 1, use_container_width=True):
                    st.session_state.current_page -= 1
                    st.rerun()
            with c3:
                if st.button("Suivant ▶", disabled=data["page"] >= data["total_pages"], use_container_width=True):
                    st.session_state.current_page += 1
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            cols = st.columns(4)
            items = data["items"] if not selected_nutri else [i for i in data["items"] if not i.get('nutriscore_grade') or i.get('nutriscore_grade', '').lower() in selected_nutri]
            
            for idx, item in enumerate(items):
                with cols[idx % 4]:
                    name = item['product_name'][:30] + '...' if len(item['product_name']) > 30 else item['product_name']
                    nutri = item.get('nutriscore_grade', '')
                    img_url = item.get('image_url')
                    quality = item.get('quality_score') or 0
                    nutri_colors = {'a': '#059669', 'b': '#84cc16', 'c': '#eab308', 'd': '#f97316', 'e': '#dc2626'}
                    nutri_color = nutri_colors.get(nutri.lower(), '#9ca3af') if nutri else '#9ca3af'
                    quality_color = '#10b981' if quality >= 70 else '#f59e0b' if quality >= 40 else '#ef4444'
                    
                    img_html = f'<img src="{img_url}" style="max-width:90%; max-height:120px; object-fit:contain;" />' if img_url else '<div style="font-size:3rem; color:#4b5563;">📦</div>'
                    
                    st.markdown(f'''
                    <div style="background:#1f2937; border:1px solid #374151; border-radius:12px; padding:1rem; margin-bottom:1rem; transition:all 0.2s ease; box-shadow:0 1px 3px rgba(0,0,0,0.2);" onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.3)'; this.style.transform='translateY(-2px)';" onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.2)'; this.style.transform='translateY(0)';">
                        <div style="width:100%; height:140px; background:#111827; border-radius:8px; display:flex; align-items:center; justify-content:center; overflow:hidden; margin-bottom:0.8rem;">
                            {img_html}
                        </div>
                        <div style="color:#f9fafb; font-weight:500; font-size:0.9rem; min-height:2.4em; line-height:1.2; margin-bottom:0.3rem;">{name}</div>
                        <div style="color:#6b7280; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.3px; margin-bottom:0.8rem;">{item.get('brand') or 'Marque inconnue'}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; padding-top:0.8rem; border-top:1px solid #374151;">
                            <div style="background:{nutri_color}; width:28px; height:28px; border-radius:6px; display:flex; align-items:center; justify-content:center; font-weight:600; font-size:0.8rem; color:{'#1f2937' if nutri == 'c' else '#fff'};">{nutri.upper() if nutri else '?'}</div>
                            <div style="text-align:right;">
                                <div style="color:{quality_color}; font-weight:600; font-size:0.95rem;">{quality}</div>
                                <div style="color:#6b7280; font-size:0.6rem;">/100</div>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button("Voir détails", key=f"btn_{item['id']}", use_container_width=True):
                        st.session_state.selected_product_id = item['id']
                        st.rerun()
        else:
            st.markdown('''
            <div style="text-align:center; padding:4rem 2rem; background:#1f2937; border-radius:12px; border:1px solid #374151;">
                <div style="font-size:3rem; margin-bottom:1rem; color:#4b5563;">🔍</div>
                <h3 style="color:#f9fafb; margin-bottom:0.5rem;">Aucun produit trouvé</h3>
                <p style="color:#9ca3af;">Essayez de modifier vos critères de recherche</p>
            </div>
            ''', unsafe_allow_html=True)


# Footer
st.divider()
st.markdown('<div style="text-align:center; padding:1rem;"><p style="color:#6b7280; font-size:0.8rem;">Food Analytics — <a href="https://world.openfoodfacts.org" style="color:#3b82f6; text-decoration:none;">Open Food Facts</a></p></div>', unsafe_allow_html=True)
