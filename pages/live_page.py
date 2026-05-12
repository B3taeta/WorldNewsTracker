import streamlit as st
import pandas as pd
from utils import REGION_MAPPING, fetch_web_data, render_results_cards
from streamlit_autorefresh import st_autorefresh
import time
from translations import get_text

st.title(get_text("live_title"))
st.markdown(get_text("live_desc"))

# Auto-refresh every 60 seconds
count = st_autorefresh(interval=60000, limit=1000, key="hantavirus_live_refresh")
st.caption(get_text("live_update", time=time.strftime("%X"), count=count))
st.divider()

# Fetch live data — use the English region (US + UK) for broad global coverage
with st.spinner(get_text("live_sync")):
    df_live = fetch_web_data("Hantavirus", lang_settings=REGION_MAPPING["region_en"])

    if not df_live.empty:
        df_live["Data_Parse"] = pd.to_datetime(df_live["Data"], format="mixed", errors="coerce")
        df_live_sorted = df_live.sort_values(by="Data_Parse", ascending=False).head(15)
        render_results_cards(df_live_sorted, tab_id="live")
    else:
        st.warning(get_text("live_waiting"))

st.sidebar.info(get_text("live_info"))
