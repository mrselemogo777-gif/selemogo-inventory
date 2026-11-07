import streamlit as st
import pandas as pd
import models


def _margin_badge(cost, sell):
    """Return a Streamlit-rendered margin preview."""
    if cost <= 0 or sell <= 0:
        st.caption("Margin: —")
        return
    profit = sell - cost
    margin_pct = (profit / sell) * 100
    if profit <= 0:
        st.markdown(
            f"<div style='background:#fde8e8;color:#b42318;padding:8px 12px;"
            f"border-radius:8px;font-weight:600;'>"
            f"Margin: {margin_pct:.1f}% (P {profit:,.2f} profit/unit) — LOSS"
            f"</div>",
            unsafe_allow_html=True,
        )
    elif margin_pct < 20:
        st.markdown(
            f"<div style='background:#fef3c7;color:#92400e;padding:8px 12px;"
            f"border-radius:8px;font-weight:600;'>"
            f"Margin: {margin_pct:.1f}% (P {profit:,.2f} profit/unit) — THIN"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:#d1fae5;color:#065f46;padding:8px 12px;"
            f"border-radius:8px;font-weight:600;'>"
            f"Margin: {margin_pct:.1f}% (P {profit:,.2f} profit/unit)"
            f"</div>",
            unsafe_allow_html=True,
        )


def render():
    st.header("🛒 Products")
    cats = models.list_categories()
    sups = models.list_suppliers()

    # Add product 
    with st.expander("➕ Add new product", expanded=False):
        with st.form("add_product", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            sku = c1.text_input("SKU *")
            name = c2.text_input("Product Name *")
            cat = c3.selectbox("Category", options=[(0, "—")] + [(c["id"], c["name"]) for c in cats],
                               format_func=lambda x: x[1])
            c4, c5 = st.columns(2)
            sup = c4.selectbox("Supplier", options=[(0, "—")] + [(s["id"], s["name"]) for s in sups],
                               format_func=lambda x: x[1])
            c6, c7, c8, c9 = st.columns(4)
            cost = c6.number_input("Cost Price (BWP)", min_value=0.0, step=10.0)
            sell = c7.number_input("Sell Price (BWP)", min_value=0.0, step=10.0)
            stock = c8.number_input("Opening Stock", min_value=0, step=1)
            reorder = c9.number_input("Reorder Level", min_value=0, step=1, value=5)
            if st.form_submit_button("Add Product"):
                if not sku.strip() or not name.strip():
                    st.error("SKU and Name are required.")
                elif sell < cost:
                    st.error("Sell price should be >= cost price.")
                else:
                    ok, msg = models.add_product(
                        sku.strip(), name.strip(), cat[0] or None, sup[0] or None,
                        cost, sell, int(stock), int(reorder))
                    (st.success if ok else st.error)(msg)
                    if ok: st.rerun()

    st.divider()

    # Search / filter 
    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input(" Search by name or SKU", "")
    cat_filter = c2.selectbox("Category", options=[(None, "All")] + [(c["id"], c["name"]) for c in cats],
                              format_func=lambda x: x[1])
    low_only = c3.checkbox("Low stock only")

    per_page = st.selectbox("Rows per page", [10, 25, 50], index=1)
    page = st.number_input("Page", min_value=1, step=1, value=1)
    offset = (int(page) - 1) * per_page

    total = models.count_products(search, cat_filter[0], low_only)
    products = models.list_products(search, cat_filter[0], low_only, per_page, offset)
    st.caption(f"Showing {len(products)} of {total} products")

    if products:
        df = pd.DataFrame([dict(p) for p in products])
        df["margin"] = ((df["sell_price"] - df["cost_price"]) / df["sell_price"] * 100).round(1)
        display = df[["sku", "name", "category", "supplier", "cost_price", "sell_price",
                      "margin", "stock", "reorder_level"]].copy()
        display["cost_price"] = display["cost_price"].map(lambda x: models.money(x))
        display["sell_price"] = display["sell_price"].map(lambda x: models.money(x))
        display["margin"] = display["margin"].map(lambda x: f"{x}%")
        st.dataframe(display, use_container_width=True, hide_index=True)

        # Edit product with live margin preview 
        st.subheader("Edit Product")
        edit_opts = {f"{p['sku']} — {p['name']}": p for p in products}
        chosen = st.selectbox("Select product to edit", list(edit_opts.keys()))
        p = edit_opts[chosen]

        st.markdown("**Pricing**")
        pc1, pc2 = st.columns(2)
        new_cost = pc1.number_input(
            "Cost Price (BWP)", value=float(p["cost_price"]), min_value=0.0,
            step=10.0, key=f"cost_{p['id']}")
        new_sell = pc2.number_input(
            "Sell Price (BWP)", value=float(p["sell_price"]), min_value=0.0,
            step=10.0, key=f"sell_{p['id']}")

        # Live margin badge — recalculates on every keystroke
        _margin_badge(new_cost, new_sell)

        st.markdown("**Details**")
        with st.form(f"edit_form_{p['id']}"):
            e1, e2, e3 = st.columns(3)
            new_name = e1.text_input("Name", p["name"])
            new_cat = e2.selectbox("Category",
                                   options=[(0, "—")] + [(c["id"], c["name"]) for c in cats],
                                   index=next((i + 1 for i, c in enumerate(cats) if c["id"] == p["category_id"]), 0),
                                   format_func=lambda x: x[1])
            new_sup = e3.selectbox("Supplier",
                                   options=[(0, "—")] + [(s["id"], s["name"]) for s in sups],
                                   index=next((i + 1 for i, s in enumerate(sups) if s["id"] == p["supplier_id"]), 0),
                                   format_func=lambda x: x[1])
            new_reorder = st.number_input("Reorder Level", value=int(p["reorder_level"]), min_value=0)

            if st.form_submit_button("💾 Save all changes"):
                ok, msg = models.update_product(
                    p["id"], new_name, new_cat[0] or None, new_sup[0] or None,
                    new_cost, new_sell, int(new_reorder))
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()
