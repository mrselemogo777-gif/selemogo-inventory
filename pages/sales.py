import streamlit as st
import pandas as pd
import models


def render():
    st.header(" Sales — Point of Sale")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    products = models.list_products(limit=1000)
    if not products:
        st.info("No products. Add some first.")
        return

    st.subheader("🛒 Add to Cart")
    with st.form("add_to_cart", clear_on_submit=True):
        opts = {f"{p['sku']} — {p['name']} ({models.money(p['sell_price'])}, stock {p['stock']})": p
                for p in products}
        choice = st.selectbox("Product", list(opts.keys()))
        qty = st.number_input("Quantity", min_value=1, step=1, value=1)
        if st.form_submit_button("➕ Add"):
            p = opts[choice]
            if qty > p["stock"]:
                st.error(f"Only {p['stock']} in stock.")
            else:
                st.session_state.cart.append({"product_id": p["id"], "quantity": int(qty),
                                              "name": p["name"], "price": p["sell_price"]})
                st.rerun()

    if st.session_state.cart:
        st.subheader("Cart")
        df = pd.DataFrame(st.session_state.cart)
        df["line_total"] = df["price"] * df["quantity"]
        display = df[["name", "price", "quantity", "line_total"]].copy()
        display["price"] = display["price"].map(lambda x: models.money(x))
        display["line_total"] = display["line_total"].map(lambda x: models.money(x))
        st.dataframe(display, use_container_width=True, hide_index=True)
        subtotal = df["line_total"].sum()
        st.write(f"**Subtotal: {models.money(subtotal)}**")

        c1, c2, c3 = st.columns(3)
        discount = c1.number_input("Discount (BWP)", min_value=0.0, value=0.0, step=10.0)
        customer = c2.text_input("Customer name", "")
        c3.write("")
        c3.write("")
        if c3.button(" Complete Sale", type="primary"):
            items = [{"product_id": i["product_id"], "quantity": i["quantity"]}
                     for i in st.session_state.cart]
            ok, msg, _ = models.create_sale(items, discount=discount, customer_name=customer)
            if ok:
                st.success(msg)
                st.session_state.cart = []
                st.rerun()
            else:
                st.error(msg)

        if st.button("🗑️ Clear cart"):
            st.session_state.cart = []
            st.rerun()

    st.divider()
    st.subheader("Recent Sales")
    sales = models.list_sales(limit=20)
    if sales:
        df = pd.DataFrame([dict(s) for s in sales])[
            ["invoice_no", "sale_date", "subtotal", "discount", "total", "profit", "customer_name"]
        ]
        for col in ["subtotal", "discount", "total", "profit"]:
            df[col] = df[col].map(lambda x: models.money(x))
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No sales yet.")
