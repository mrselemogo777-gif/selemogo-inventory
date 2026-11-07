import streamlit as st
from database import init_db
st.set_page_config(page_title="Selemogo Inventory", page_icon="📦", layout="wide")
st.set_option("client.showSidebarNavigation", False)

init_db()

# Auto-seed on first run (e.g. Streamlit Cloud with empty DB)
from database import get_connection
with get_connection() as _conn:
    _has_products = _conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
if _has_products == 0:
    from seed import seed
    seed()

import styles
styles.apply()

from pages import dashboard, products, suppliers, sales, purchases, reports

st.sidebar.title("📦 Selemogo Inventory")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Products", "Suppliers", "Sales (POS)", "Purchases", "Reports"],
    label_visibility="collapsed",
)

if page == "Dashboard":
    dashboard.render()
elif page == "Products":
    products.render()
elif page == "Suppliers":
    suppliers.render()
elif page == "Sales (POS)":
    sales.render()
elif page == "Purchases":
    purchases.render()
elif page == "Reports":
    reports.render()
