import streamlit as st


def apply():
    st.markdown("""
    <style>
    /* Main background: subtle gradient  */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4ecf7 100%);
    }

    /*  Sidebar: dark, crisp  */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2a44 0%, #2b3a5f 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e8ecf4 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        padding: 6px 10px;
        border-radius: 8px;
        transition: background 0.15s ease;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.08);
    }

    /*  Headers  */
    h1, h2, h3 {
        color: #1f2a44 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /*  KPI metric cards  */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e3e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 6px rgba(31,42,68,0.06);
    }
    div[data-testid="stMetricLabel"] {
        color: #6b7896 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1f2a44 !important;
        font-weight: 700 !important;
    }

    /*  Buttons  */
    .stButton > button {
        background: #3b6fd8;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 18px;
        transition: background 0.15s ease;
    }
    .stButton > button:hover {
        background: #2c5cc4;
        color: #ffffff;
    }
    .stButton > button[kind="primary"] {
        background: #1f8a4c;
    }
    .stButton > button[kind="primary"]:hover {
        background: #17703d;
    }

    /* Dataframes / tables  */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e3e8f0;
    }

    /*  Forms & inputs  */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* Expander  */
    details[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e3e8f0;
        border-radius: 10px;
        padding: 4px 8px;
    }

    /*  Divider  */
    hr {
        border: none;
        border-top: 1px solid #d8dee9;
        margin: 1rem 0;
    }

    /*  Success / warning / error  */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
