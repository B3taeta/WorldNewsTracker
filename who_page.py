import streamlit as st
import time
from utils import (
    render_results_cards,
    fetch_who_news,
    WHO_TOPIC_KEYWORDS,
)
from translations import get_text
from streamlit_autorefresh import st_autorefresh

# ─────────────────────────────────────────────
# PAGE HEADER
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
    # Keep topic order from WHO_TOPIC_KEYWORDS; only show topics present in the feed
    present_topics = [
        t for t in WHO_TOPIC_KEYWORDS
        if df_who["Topics"].apply(lambda lst: t in lst).any()
    ]
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
            df_display["Topics"].apply(lambda t: any(topic in t for topic in selected_topics))
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
