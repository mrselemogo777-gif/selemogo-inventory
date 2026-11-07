import streamlit as st
import pandas as pd
from datetime import date, timedelta
import models


def render():
    st.header(" Reports")

    st.subheader("Profit & Loss")
    c1, c2 = st.columns(2)
    default_start = date.today() - timedelta(days=30)
    start = c1.date_input("Start date", value=default_start)
    end = c2.date_input("End date", value=date.today())

    if start and end:
        pnl = models.pnl_report(start.isoformat(), end.isoformat())
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Orders", pnl["orders"])
        m2.metric("Gross Revenue", models.money(pnl["revenue"]))
        m3.metric("Discounts", models.money(pnl["discounts"]))
        m4.metric("Net Revenue", models.money(pnl["net_revenue"]))
        m5.metric("Gross Profit", models.money(pnl["gross_profit"]))

    st.divider()

    st.subheader("Top Products (30 days)")
    top = models.top_products(limit=15, days=30)
    if top:
        df = pd.DataFrame([dict(r) for r in top])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No sales in the last 30 days.")

    st.divider()

    st.subheader("📥 Export Data")
    c1, c2, c3 = st.columns(3)

    sales = models.list_sales(limit=100000, start_date=start.isoformat(), end_date=end.isoformat())
    if sales:
        df_sales = pd.DataFrame([dict(s) for s in sales])
        c1.download_button(
            "⬇️ Sales CSV",
            df_sales.to_csv(index=False).encode("utf-8"),
            f"sales_{start}_{end}.csv",
            "text/csv",
        )

    products = models.list_products(limit=10000)
    if products:
        df_products = pd.DataFrame([dict(p) for p in products])
        c2.download_button(
            "⬇️ Inventory CSV",
            df_products.to_csv(index=False).encode("utf-8"),
            "inventory.csv",
            "text/csv",
        )

    purchases = models.list_purchases(limit=10000)
    if purchases:
        df_purchases = pd.DataFrame([dict(p) for p in purchases])
        c3.download_button(
            "⬇️ Purchases CSV",
            df_purchases.to_csv(index=False).encode("utf-8"),
            "purchases.csv",
            "text/csv",
        )
