import streamlit as st
from translations import get_text

st.set_page_config(page_title="World News Tracker", layout="wide")

if "ui_lang" not in st.session_state:
    st.session_state["ui_lang"] = "it"

lang_options = {"it": "🇮🇹 Italiano", "en": "🇬🇧 English"}
st.session_state["ui_lang"] = st.sidebar.radio(
    get_text("lang_selector"),
    options=["it", "en"],
    format_func=lambda x: lang_options[x],
    index=0 if st.session_state["ui_lang"] == "it" else 1,
    horizontal=True
)

# --- Global CSS ---
# Injected once here so it applies across all pages without re-emitting per component.
st.markdown("""
    <style>
    /* Style tertiary st.button to look like a blue hyperlink */
    div[data-testid="stButton"] > button[kind="tertiary"] {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        color: #8ab4f8 !important;
        font-size: 22px !important;
        font-weight: 400 !important;
        line-height: 1.3 !important;
        text-align: left !important;
        cursor: pointer !important;
        white-space: normal !important;
        height: auto !important;
        box-shadow: none !important;
    }
    div[data-testid="stButton"] > button[kind="tertiary"]:hover {
        color: #aecbfa !important;
        text-decoration: underline !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/live_page.py", title=get_text("nav_live"), icon="🔴"),
    st.Page("pages/search_page.py", title=get_text("nav_search"), icon="🌍"),
    st.Page("pages/who_page.py", title=get_text("nav_who"), icon="🏥"),
])

pg.run()