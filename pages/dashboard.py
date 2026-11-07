import streamlit as st
import pandas as pd
import models


def render():
    st.header(" Dashboard")

    products, today = models.dashboard_kpis()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Products", products["total"])
    c2.metric("Stock Value (cost)", models.money0(products["stock_value_cost"]))
    c3.metric("Stock Value (retail)", models.money0(products["stock_value_retail"]))
    c4.metric("Low Stock Items", products["low_stock"] or 0)

    c5, c6, c7 = st.columns(3)
    c5.metric("Sales Today", today["sales_today"])
    c6.metric("Revenue Today", models.money(today["revenue_today"]))
    c7.metric("Profit Today", models.money(today["profit_today"]))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(" Revenue & Profit (30 days)")
        series = models.sales_by_day(30)
        if series:
            df = pd.DataFrame([dict(r) for r in series])
            df["day"] = pd.to_datetime(df["day"])
            st.line_chart(df.set_index("day")[["revenue", "profit"]], height=300)
        else:
            st.info("No sales in the last 30 days.")

    with col_b:
        st.subheader(" Top Products (30 days)")
        top = models.top_products(limit=8, days=30)
        if top:
            df = pd.DataFrame([dict(r) for r in top])[["name", "revenue"]]
            st.bar_chart(df.set_index("name")["revenue"], height=300)
        else:
            st.info("No sales yet.")

    st.divider()

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader(" Low Stock")
        low = models.low_stock_list()
        if low:
            st.dataframe(pd.DataFrame([dict(r) for r in low]),
                         use_container_width=True, hide_index=True)
        else:
            st.success("All products above reorder level.")

    with col_d:
        st.subheader(" Recent Stock Movements")
        mv = models.recent_movements(15)
        if mv:
            df = pd.DataFrame([dict(m) for m in mv])[
                ["product", "movement_type", "quantity", "reason", "created_at"]
            ]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No movements yet.")
