import streamlit as st

st.set_page_config(page_title="World Wide Web Tracker", layout="wide")

# Costruzione del menu di navigazione ufficiale a pagine laterali
pg = st.navigation([
    st.Page("pages/live_page.py", title="Hantavirus LIVE", icon="🔴"),
    st.Page("pages/search_page.py", title="Ricerca", icon="🌍")
])

pg.run()