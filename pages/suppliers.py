import streamlit as st
import pandas as pd
import models


def render():
    st.header(" Suppliers")
    with st.form("add_supplier", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Supplier name *")
        contact = c2.text_input("Contact person")
        email = c3.text_input("Email")
        c4, c5 = st.columns([1, 2])
        phone = c4.text_input("Phone")
        address = c5.text_input("Address")
        if st.form_submit_button("Add Supplier"):
            if not name.strip():
                st.error("Name is required.")
            else:
                ok, msg = models.add_supplier(name.strip(), contact, email, phone, address)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()

    st.divider()
    sups = models.list_suppliers()
    if sups:
        st.dataframe(pd.DataFrame([dict(s) for s in sups]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No suppliers yet.")
