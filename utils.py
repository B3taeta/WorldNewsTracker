import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import math
import re
import html
import streamlit as st

REGION_MAPPING = {
    "Globale (Inglese US)": ("en-US", "US", "US:en"),
    "Europa (Inglese UK)": ("en-GB", "GB", "GB:en"),
    "Italia (Italiano)": ("it", "IT", "IT:it"),
    "Spagna (Spagnolo)": ("es", "ES", "ES:es"),
    "Francia (Francese)": ("fr", "FR", "FR:fr"),
    "Germania (Tedesco)": ("de", "DE", "DE:de")
}

def create_pseudo_url(fonte, titolo):
    clean_fonte = re.sub(r'[^a-zA-Z0-9\.]', '', fonte).lower()
    if "." not in clean_fonte:
        clean_fonte += ".com"
    clean_title = re.sub(r'[^a-z0-9]+', '-', titolo.lower()).strip('-')[:40]
    return f"{clean_fonte}/news/{clean_title}"

def clean_snippet(html_text):
    if html_text == "N/D": return "Riassunto non disponibile."
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

@st.dialog("✨ AI Gist - Punti Chiave dell'Articolo")
def show_ai_gist(titolo, snippet):
    st.markdown(f"### {titolo}")
    st.write(clean_snippet(snippet))
    st.info("💡 Questo riassunto è generato elaborando ed estraendo le entità informative dai metadati dell'articolo.")

def fetch_web_data(query, lang_settings=("it", "IT", "IT:it")):
    data_list = []
    try:
        safe_query = urllib.parse.quote(query)
        hl, gl, ceid = lang_settings
        url = f"https://news.google.com/rss/search?q={safe_query}&hl={hl}&gl={gl}&ceid={ceid}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        for item in root.findall('.//item'):
            title = item.find('title')
            title_text = title.text if title is not None else "N/D"
            
            link = item.find('link')
            link_text = link.text if link is not None else "N/D"
            
            pubDate = item.find('pubDate')
            date_text = pubDate.text if pubDate is not None else "N/D"
            
            desc = item.find('description')
            snippet_text = desc.text if desc is not None else "N/D"
            
            source = item.find('source')
            if source is not None and source.text:
                domain = source.text
            else:
                domain = urllib.parse.urlparse(link_text).netloc if link_text != "N/D" else "Web"

            data_list.append({
                "Tipo": "News",
                "Titolo": title_text,
                "Data": date_text,
                "Fonte": domain,
                "Snippet": snippet_text, 
                "Link": link_text
            })
    except Exception as e:
        st.error(f"Errore durante la ricerca web nativa: {e}")
        
    return pd.DataFrame(data_list)

def render_results_cards(df_subset, show_links, tab_id="tab"):
    if df_subset.empty:
        st.info("Nessun risultato in questa pagina.")
        return
        
    for idx, row in df_subset.iterrows():
        raw_link = row['Link']
        
        with st.container():
            c_title, c_btn = st.columns([7, 2])
            with c_title:
                st.markdown(f"#### [{row['Tipo']}] {row['Titolo']}")
            
            with c_btn:
                if st.button("🤖 AI Gist", key=f"gist_{tab_id}_{idx}"):
                    show_ai_gist(row['Titolo'], row['Snippet'])
            
            if show_links:
                display_link = create_pseudo_url(row['Fonte'], row['Titolo'])
                st.markdown(f"**Fonte:** {row['Fonte']} &nbsp;&nbsp;|&nbsp;&nbsp; **Data:** {row['Data']} <br> 🔗 **[{display_link}]({raw_link})**", unsafe_allow_html=True)
            else:
                st.markdown(f"**Fonte:** {row['Fonte']} &nbsp;&nbsp;|&nbsp;&nbsp; **Data:** {row['Data']}", unsafe_allow_html=True)
            st.divider()

def render_results_table(df_subset):
    if df_subset.empty:
        st.info("Nessun risultato in questa pagina.")
        return
    
    df_show = df_subset.drop(columns=["Data_Parse", "Snippet"], errors="ignore").copy()
    column_config = {
        "Link": st.column_config.LinkColumn("Pagina Web")
    }
    st.dataframe(df_show, column_config=column_config, use_container_width=True)
