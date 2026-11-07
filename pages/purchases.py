import streamlit as st
import pandas as pd
import models


def render():
    st.header(" Purchases — Restock from Suppliers")

    if "po_cart" not in st.session_state:
        st.session_state.po_cart = []

    products = models.list_products(limit=1000)
    sups = models.list_suppliers()
    if not products:
        st.info("No products. Add some first.")
        return

    st.subheader("🛒 Add items to purchase order")
    with st.form("add_po", clear_on_submit=True):
        opts = {f"{p['sku']} — {p['name']} (stock {p['stock']}, cost {models.money(p['cost_price'])})": p
                for p in products}
        choice = st.selectbox("Product", list(opts.keys()))
        c1, c2 = st.columns(2)
        qty = c1.number_input("Quantity", min_value=1, step=1, value=1)
        unit_cost = c2.number_input("Unit Cost (BWP)", min_value=0.0, value=0.0, step=10.0)
        if st.form_submit_button("➕ Add"):
            p = opts[choice]
            cost = unit_cost if unit_cost > 0 else p["cost_price"]
            st.session_state.po_cart.append({
                "product_id": p["id"], "name": p["name"],
                "quantity": int(qty), "unit_cost": float(cost),
            })
            st.rerun()

    if st.session_state.po_cart:
        st.subheader("Purchase Order Draft")
        df = pd.DataFrame(st.session_state.po_cart)
        df["line_total"] = df["quantity"] * df["unit_cost"]
        display = df[["name", "quantity", "unit_cost", "line_total"]].copy()
        display["unit_cost"] = display["unit_cost"].map(lambda x: models.money(x))
        display["line_total"] = display["line_total"].map(lambda x: models.money(x))
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.write(f"**Total cost: {models.money(df['line_total'].sum())}**")

        c1, c2 = st.columns(2)
        sup_choice = c1.selectbox(
            "Supplier",
            options=[(0, "—")] + [(s["id"], s["name"]) for s in sups],
            format_func=lambda x: x[1])
        notes = c2.text_input("Notes", "Restock")
        b1, b2 = st.columns(2)
        if b1.button(" Record Purchase", type="primary"):
            items = [{"product_id": i["product_id"], "quantity": i["quantity"],
                      "unit_cost": i["unit_cost"]} for i in st.session_state.po_cart]
            ok, msg, _ = models.create_purchase(items, sup_choice[0] or None, notes)
            if ok:
                st.success(msg)
                st.session_state.po_cart = []
                st.rerun()
            else:
                st.error(msg)
        if b2.button("🗑️ Clear"):
            st.session_state.po_cart = []
            st.rerun()

    st.divider()
    st.subheader("Recent Purchases")
    purchases = models.list_purchases(limit=20)
    if purchases:
        df = pd.DataFrame([dict(p) for p in purchases])[
            ["po_number", "purchase_date", "supplier", "total_cost", "notes"]]
        df["total_cost"] = df["total_cost"].map(lambda x: models.money(x))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No purchases yet.")
