import streamlit as st
import pandas as pd
import math
from utils import REGION_MAPPING, fetch_web_data, render_results_cards, render_results_table

st.title("📰 World Wide Web Hub")
st.markdown("Ricerca le notizie dal Web in modo esteso. I risultati sono impaginati (Max 10 per pagina).")

# --- Google-like Search Bar ---
st.write("")
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    with st.form(key="search_form", border=False):
        fcol1, fcol2 = st.columns([5, 2])
        with fcol1:
            search_query = st.text_input("Cerca", value="Hantavirus", label_visibility="collapsed", placeholder="Cerca notizie...")
        with fcol2:
            search_pressed = st.form_submit_button("Ricerca Web", use_container_width=True)

# --- Sidebar ---
st.sidebar.header("Impostazioni")
selected_region = st.sidebar.selectbox("Lingua e Regione News", list(REGION_MAPPING.keys()))
view_mode = st.sidebar.radio("Stile di Visualizzazione", ["A Schede (Moderno)", "Tabellare (Stile Excel)"])

if search_pressed:
    if search_query.strip():
        with st.spinner(f'Ricerca Globale su [{selected_region}] in corso...'):
             df = fetch_web_data(search_query, REGION_MAPPING[selected_region])
             st.session_state['data'] = df
             st.session_state['page'] = 1
    else:
        st.warning("Inserisci una parola chiave valida.")


# --- Visualizzazione ---
if 'data' in st.session_state:
    df = st.session_state['data']
    
    if not df.empty:
        df['Data_Parse'] = pd.to_datetime(df['Data'], format='mixed', errors='coerce')

        with col2:
            with st.popover("📰 Fonti"):
                selected_source = st.multiselect("Filtra per Fonte", df["Fonte"].unique(), label_visibility="collapsed")
            
        df_display = df.copy()
        if selected_source:
             df_display = df_display[df_display["Fonte"].isin(selected_source)]

        show_links = False
        st.write("---") 
        if view_mode == "A Schede (Moderno)":
            show_links = st.toggle("Mostra indirizzi web (Link) nei risultati", value=False)
            if not show_links:
                st.caption("I link sono attualmente nascosti. Attiva l'interruttore per caricarli.")

        RESULTS_PER_PAGE = 10
        total_results = len(df_display)
        total_pages = max(1, math.ceil(total_results / RESULTS_PER_PAGE))
        
        st.subheader(f"Risultati Trovati: {total_results}")
        
        cp1, cp2, cp3 = st.columns([1, 1, 1])
        with cp2:
             page = st.number_input(f"Pagina (1 di {total_pages})", min_value=1, max_value=total_pages, step=1, key="page")
        
        start_idx = (page - 1) * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE
        
        with cp2:
             st.caption(f"😎 Visualizzazione {start_idx + 1}-{min(end_idx, total_results)} di {total_results}")

        st.write("")

        tab1, tab2, tab3 = st.tabs(["Per Rilevanza (Default)", "Dal Più Recente", "Dal Più Vecchio"])
        
        with tab1:
             df_tab1 = df_display.iloc[start_idx:end_idx]
             if view_mode == "A Schede (Moderno)":
                 render_results_cards(df_tab1, show_links, "tab1")
             else:
                 render_results_table(df_tab1)
            
        with tab2:
             df_tab2 = df_display.sort_values(by="Data_Parse", ascending=False).iloc[start_idx:end_idx]
             if view_mode == "A Schede (Moderno)":
                 render_results_cards(df_tab2, show_links, "tab2")
             else:
                 render_results_table(df_tab2)
            
        with tab3:
             df_tab3 = df_display.sort_values(by="Data_Parse", ascending=True).iloc[start_idx:end_idx]
             if view_mode == "A Schede (Moderno)":
                 render_results_cards(df_tab3, show_links, "tab3")
             else:
                 render_results_table(df_tab3)
        
        df_csv = df_display.drop(columns=["Data_Parse", "Snippet"], errors="ignore")
        csv = df_csv.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica Report CSV Completo", csv, "notizie_ricerca.csv", "text/csv")
    else:
        st.warning("Nessun risultato trovato dal motore di ricerca. Prova con una parola chiave diversa.")
else:
    st.info("Effettua una ricerca usando la barra centrale per iniziare.")
