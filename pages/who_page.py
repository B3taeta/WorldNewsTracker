import streamlit as st
import pandas as pd
import urllib.request
import xml.etree.ElementTree as ET
import time
from utils import render_results_cards, format_date
from translations import get_text
from streamlit_autorefresh import st_autorefresh

# --- WHO Official RSS Feeds (multilingual) ---
WHO_RSS_URLS = {
    "en": "https://www.who.int/rss-feeds/news-english.xml",
    "it": "https://www.who.int/rss-feeds/news-italian.xml",
    "fr": "https://www.who.int/rss-feeds/news-french.xml",
    "es": "https://www.who.int/rss-feeds/news-spanish.xml",
}

_WHO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# --- Keyword → Topic mapping ---
# Since WHO RSS doesn't include <category> tags, we classify articles
# by scanning their titles against these curated health topic keywords.
WHO_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "🦠 Disease Outbreaks":      ["outbreak", "hantavirus", "mpox", "monkeypox", "ebola", "cholera",
                                   "polio", "measles", "dengue", "malaria", "flu", "influenza",
                                   "rabies", "plague", "typhoid", "yellow fever", "marburg"],
    "🚨 Health Emergencies":     ["emergency", "humanitarian", "crisis", "disaster", "response",
                                   "preparedness", "alert", "surge", "conflict"],
    "💉 Vaccines & Immunization":["vaccine", "vaccination", "immunization", "immunisation",
                                   "dose", "booster", "inoculation", "jab"],
    "🧬 Infectious Diseases":    ["infectious", "virus", "bacterial", "fungal", "parasite",
                                   "infection", "contagious", "pathogen", "antimicrobial",
                                   "antibiotic", "resistance", "AMR", "HIV", "AIDS",
                                   "tuberculosis", "TB", "hepatitis"],
    "🧠 Mental Health":          ["mental", "depression", "anxiety", "suicide", "wellbeing",
                                   "psychosocial", "psychiatric", "burnout", "stress"],
    "🍎 Nutrition":              ["nutrition", "malnutrition", "food", "obesity", "diet",
                                   "hunger", "stunting", "wasting", "famine"],
    "🌍 Climate & Environment":  ["climate", "heat", "pollution", "air quality", "environmental",
                                   "carbon", "wildfire", "flood", "drought"],
    "👶 Maternal & Child Health":["maternal", "child", "newborn", "pregnancy", "infant",
                                   "neonatal", "breastfeeding", "midwif", "birth"],
    "♋ Cancer":                  ["cancer", "tumor", "tumour", "oncology", "carcinoma",
                                   "lymphoma", "leukaemia", "leukemia"],
    "🚬 Tobacco & Substances":   ["tobacco", "smoking", "cigarette", "alcohol", "drug",
                                   "substance", "addiction"],
    "🏥 Health Systems":         ["health system", "primary care", "universal health", "UHC",
                                   "coverage", "workforce", "hospital", "financing"],
    "🔬 Research & Science":     ["research", "study", "trial", "findings", "data",
                                   "evidence", "report", "survey", "analysis", "lancet"],
    "🤝 Global Cooperation":     ["WHO", "member states", "agreement", "treaty", "resolution",
                                   "assembly", "Director-General", "partnership", "United Nations"],
}


def classify_topics(title: str, snippet: str = "") -> list[str]:
    """Return a list of WHO topic labels that match the article title/snippet."""
    text = (title + " " + snippet).lower()
    matched = []
    for topic, keywords in WHO_TOPIC_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            matched.append(topic)
    return matched if matched else ["📋 General"]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_who_news(lang: str = "en") -> pd.DataFrame:
    """
    Fetch WHO official RSS news feed.
    Articles are auto-classified into health topics via keyword matching.
    Cached for 5 minutes.
    """
    data_list = []
    urls_to_try = list({WHO_RSS_URLS.get(lang, WHO_RSS_URLS["en"]), WHO_RSS_URLS["en"]})

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers=_WHO_HEADERS)
            response = urllib.request.urlopen(req, timeout=10)
            root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title_el  = item.find("title")
                link_el   = item.find("link")
                date_el   = item.find("pubDate")
                desc_el   = item.find("description")

                title_text   = title_el.text.strip()  if title_el  is not None and title_el.text  else "N/A"
                link_text    = link_el.text.strip()   if link_el   is not None and link_el.text   else "N/A"
                date_text    = date_el.text.strip()   if date_el   is not None and date_el.text   else "N/A"
                snippet_text = desc_el.text           if desc_el   is not None and desc_el.text   else "N/A"

                data_list.append({
                    "Titolo":  title_text,
                    "Data":    date_text,
                    "Fonte":   "WHO",
                    "Snippet": snippet_text,
                    "Link":    link_text,
                    "Topics":  classify_topics(title_text, snippet_text),
                })

            if data_list:
                break  # success — skip fallback

        except Exception:
            continue

    df = pd.DataFrame(data_list)
    if not df.empty:
        df = df.drop_duplicates(subset=["Link"])
        df["Data_Formatted"] = df["Data"].apply(format_date)
        df["Data_Parse"] = pd.to_datetime(df["Data"], format="mixed", errors="coerce")
        df = df.sort_values(by="Data_Parse", ascending=False).reset_index(drop=True)

    return df


# ─────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────

st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
        <img src="https://www.google.com/s2/favicons?domain=who.int&sz=48"
             style="width:40px;height:40px;border-radius:8px;">
        <div>
            <h1 style="margin:0; font-size:28px;">{get_text("who_title")}</h1>
            <p style="margin:0; color:#9aa0a6; font-size:14px;">{get_text("who_desc")}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Auto-refresh every 5 minutes
count = st_autorefresh(interval=300_000, limit=500, key="who_autorefresh")
st.caption(get_text("who_update", time=time.strftime("%X"), count=count))

# ─────────────────────────────────────────────
# FETCH
# ─────────────────────────────────────────────
lang = st.session_state.get("ui_lang", "en")

with st.spinner(get_text("who_loading")):
    df_who = fetch_who_news(lang)

# ─────────────────────────────────────────────
# SIDEBAR — topic filter
# ─────────────────────────────────────────────
if not df_who.empty:
    # All topic labels that appear in the fetched articles (preserving WHO_TOPIC_KEYWORDS order)
    present_topics = [
        t for t in WHO_TOPIC_KEYWORDS.keys()
        if df_who["Topics"].apply(lambda lst: t in lst).any()
    ]
    # Also include "General" if any unmatched articles exist
    if df_who["Topics"].apply(lambda lst: "📋 General" in lst).any():
        present_topics.append("📋 General")

    st.sidebar.header(get_text("who_sidebar_header"))

    selected_topics = st.sidebar.multiselect(
        get_text("who_topic_filter"),
        options=present_topics,
        default=[],
        placeholder=get_text("who_all_topics"),
    )

    st.sidebar.markdown("---")
    st.sidebar.info(get_text("who_sidebar_info"))

    # ─────────────────────────────────────────────
    # FILTER & DISPLAY
    # ─────────────────────────────────────────────
    df_display = df_who.copy()

    if selected_topics:
        df_display = df_display[
            df_display["Topics"].apply(
                lambda t: any(topic in t for topic in selected_topics)
            )
        ]

    total = len(df_display)
    tag_str = "  ·  " + "  ".join(f"`{t}`" for t in selected_topics) if selected_topics else ""
    st.markdown(
        f'<p style="font-size:14px;color:#9aa0a6;">'
        f'{get_text("who_articles_count", n=total)}{tag_str}</p>',
        unsafe_allow_html=True,
    )

    if df_display.empty:
        st.info(get_text("who_no_results"))
    else:
        render_results_cards(df_display, tab_id="who")

else:
    st.warning(get_text("who_empty"))
    st.sidebar.header(get_text("who_sidebar_header"))
    st.sidebar.info(get_text("who_sidebar_info"))
