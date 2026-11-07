import streamlit as st
from database import init_db
st.set_page_config(page_title="Selemogo Inventory", page_icon="📦", layout="wide")
st.set_option("client.showSidebarNavigation", False)

init_db()

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
