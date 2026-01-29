import streamlit as st
import requests

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

API_URL = "http://localhost:8000"


def api_get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Erreur API: {e}")
        return None


st.title("📊 Dashboard Produits")

stats = api_get("/stats")
if stats:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produits", stats["total_products"])
    col2.metric("Marques", stats["total_brands"])
    col3.metric("Catégories", stats["total_categories"])
    col4.metric("Score moyen", stats["avg_quality_score"])
    
    st.subheader("Distribution Nutriscore")
    dist = stats.get("nutriscore_distribution", {})
    cols = st.columns(5)
    colors = {"a": "🟢", "b": "🟡", "c": "🟠", "d": "🔴", "e": "⚫"}
    for i, grade in enumerate(["a", "b", "c", "d", "e"]):
        cols[i].metric(f"{colors[grade]} {grade.upper()}", dist.get(grade, 0))

st.divider()

st.subheader("🔍 Liste des produits")

with st.sidebar:
    st.header("Filtres")
    filter_category = st.text_input("Catégorie")
    filter_brand = st.text_input("Marque")
    filter_nutriscore = st.selectbox("Nutriscore", ["", "a", "b", "c", "d", "e"])
    filter_min_quality = st.slider("Score qualité min", 0, 100, 0)

col1, col2 = st.columns([1, 4])
page = col1.number_input("Page", min_value=1, value=1)
page_size = 20

params = {"page": page, "page_size": page_size}
if filter_category:
    params["category"] = filter_category
if filter_brand:
    params["brand"] = filter_brand
if filter_nutriscore:
    params["nutriscore"] = filter_nutriscore
if filter_min_quality > 0:
    params["min_quality"] = filter_min_quality

data = api_get("/items", params)

if data:
    st.caption(f"Total: {data['total']} produits | Page {data['page']}/{data['total_pages']}")
    
    for item in data["items"]:
        with st.expander(f"**{item['product_name']}** - {item.get('brand') or 'N/A'}"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Code:** {item['code']}")
            col2.write(f"**Catégorie:** {item.get('category') or 'N/A'}")
            col3.write(f"**Nutriscore:** {(item.get('nutriscore_grade') or 'N/A').upper()}")
            st.write(f"**Score qualité:** {item.get('quality_score') or 'N/A'}")
            
            if st.button(f"Voir détail", key=f"btn_{item['id']}"):
                detail = api_get(f"/items/{item['id']}")
                if detail:
                    st.json(detail)
else:
    st.info("Aucun produit trouvé. Vérifiez que l'API est lancée.")
