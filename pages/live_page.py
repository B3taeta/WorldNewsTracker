import streamlit as st
import pandas as pd
from utils import fetch_web_data, render_results_cards
from streamlit_autorefresh import st_autorefresh
import time

st.title("🔴 Hantavirus LIVE Feed")
st.markdown("Questa pagina si aggiorna automaticamente in tempo reale catturando le ultimissime notizie a livello globale sul termine 'Hantavirus'.")

# --- Autorefresher Setup ---
# Aggiorna la pagina ogni 60 secondi (60000 millisecondi) per fornire una stream "live"
count = st_autorefresh(interval=60000, limit=1000, key="hantavirus_live_refresh")

st.caption(f"Ultimo aggiornamento automatico: {time.strftime('%X')} (Ciclo #{count})")

st.divider()

# --- Fetch Data Dinamico ---
with st.spinner("Sincronizzazione Live Data..."):
    # Impostiamo su Globale/US per prendere i feeds mondiali più estesi
    df_live = fetch_web_data("Hantavirus", lang_settings=("en-US", "US", "US:en"))
    
    if not df_live.empty:
        # Pulisce le date 
        df_live['Data_Parse'] = pd.to_datetime(df_live['Data'], format='mixed', errors='coerce')
        
        # Ordina categoricamente dal più recente all'assoluto. Mostriamo solo i top 15
        df_live_sorted = df_live.sort_values(by="Data_Parse", ascending=False).head(15)
        
        # Rendirizza le news verticalmente in formato moderno showing Links by default for live feeds
        render_results_cards(df_live_sorted, show_links=True, tab_id="live")
        
    else:
        st.warning("📡 In attesa di segnale dai server globali... riprova a breve.")

st.sidebar.info("Il Live Tracker è limitato alle 15 notizie più scottanti in tutto il mondo al minuto e si ricarica in background per garantirti il dato in tempo reale.")
