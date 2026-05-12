import pandas as pd
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import html
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from translations import get_text

REGION_MAPPING = {
    "region_global": [
        ("en-US", "US", "US:en"),
        ("en-GB", "GB", "GB:en"),
        ("it", "IT", "IT:it"),
        ("es", "ES", "ES:es"),
        ("fr", "FR", "FR:fr"),
        ("de", "DE", "DE:de")
    ],
    "region_en": [("en-US", "US", "US:en"), ("en-GB", "GB", "GB:en")],
    "region_it": [("it", "IT", "IT:it")],
    "region_es": [("es", "ES", "ES:es")],
    "region_fr": [("fr", "FR", "FR:fr")],
    "region_de": [("de", "DE", "DE:de")]
}


def clean_snippet(html_text: str) -> str:
    """Strip HTML tags and unescape entities from a snippet string."""
    if html_text in ("N/D", "N/A"):
        return get_text("gist_na")
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def format_date(date_str: str) -> str:
    """Convert RFC 2822 date string to a human-friendly format."""
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%d %b %Y · %H:%M")
        except Exception:
            continue
    return date_str



# Phrases that indicate we got Google's generic page description — not the article
_GENERIC_DESC_PHRASES = (
    "comprehensive up-to-date news",
    "aggregated from sources all over the world by google",
    "stay up to date on",
    "google news",
)

_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def _is_generic(text: str) -> bool:
    """Return True if the text is boilerplate rather than real article content."""
    t = text.lower()
    return len(text) < 40 or any(phrase in t for phrase in _GENERIC_DESC_PHRASES)


def _is_just_title(text: str, title: str) -> bool:
    """Return True if 'text' is essentially just the article title — not a real summary."""
    if not title:
        return False
    t = text.lower().strip()
    n = title.lower().strip()
    # Direct containment
    if n in t or t in n:
        return True
    # High word-overlap ratio (>80% shared words)
    t_words = set(t.split())
    n_words = set(n.split())
    if t_words and n_words:
        overlap = len(t_words & n_words) / min(len(t_words), len(n_words))
        if overlap > 0.80:
            return True
    return False


def _extract_meta_desc(raw: str, title: str = "") -> str:
    """Pull og:description or meta description from HTML.
    Rejects generic boilerplate and descriptions that are just the article title.
    """
    patterns = [
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']{30,})["\']',
        r'<meta[^>]+content=["\']([^"\']{30,})["\'][^>]+property=["\']og:description["\']',
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{30,})["\']',
        r'<meta[^>]+content=["\']([^"\']{30,})["\'][^>]+name=["\']description["\']',
    ]
    for pattern in patterns:
        m = re.search(pattern, raw, re.IGNORECASE)
        if m:
            text = html.unescape(m.group(1).strip())
            if not _is_generic(text) and not _is_just_title(text, title):
                return text
    return ""


def _extract_paragraphs(raw: str) -> str:
    """Return first 2 meaningful <p> paragraphs from the page body."""
    good = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", raw, re.DOTALL | re.IGNORECASE):
        clean = html.unescape(re.sub(r"<[^>]+>", " ", p))
        clean = re.sub(r"\s+", " ", clean).strip()
        if len(clean) > 80 and not _is_generic(clean):
            good.append(clean)
        if len(good) >= 2:
            break
    return " ".join(good)


def _find_real_article_url(raw: str) -> str:
    """
    When we land on a Google News page, extract the actual article URL.
    Tries JSON-LD 'url' fields first, then any external href.
    """
    # JSON-LD / JSON fields (most reliable — Google embeds these in their pages)
    json_hits = re.findall(
        r'"(?:url|articleUrl|mainEntityOfPage)"\s*:\s*"(https?://(?!(?:[\w\-]+\.)*google\.)[^"]{15,})"',
        raw,
    )
    if json_hits:
        return json_hits[0]

    # Any href that points away from Google (e.g. publisher redirect links)
    href_hits = re.findall(
        r'href=["\']?(https?://(?!(?:[\w\-]+\.)*google\.)[^"\'>\s]{20,})["\']?',
        raw,
    )
    if href_hits:
        return href_hits[0]

    return ""


def _fetch_raw(target_url: str):
    """Fetch a URL and return (final_url, html_text)."""
    req = urllib.request.Request(target_url, headers=_FETCH_HEADERS)
    resp = urllib.request.urlopen(req, timeout=8)
    return resp.geturl(), resp.read().decode("utf-8", errors="ignore")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_article_gist(url: str, title: str = "") -> str:
    """
    Fetch the article page and extract a meaningful summary.
    - title: used to detect and skip descriptions that are just the title repeated.
    """
    try:
        final_url, raw = _fetch_raw(url)

        # If we ended up on a Google page, resolve to the real article
        if "google.com" in final_url:
            real_url = _find_real_article_url(raw)
            if real_url:
                try:
                    _, raw = _fetch_raw(real_url)
                except Exception:
                    pass

        # Strategy 1: og:description / meta description (skip if == title)
        desc = _extract_meta_desc(raw, title)
        if desc:
            return desc

        # Strategy 2: first meaningful <p> paragraphs
        paras = _extract_paragraphs(raw)
        if paras and not _is_just_title(paras, title):
            return paras

    except Exception:
        pass

    return ""



def ai_gist_dialog(titolo: str, snippet: str, link: str):
    """Open a Streamlit dialog showing the article title, a real gist, and a link."""
    header = "📰 " + titolo[:60] + ("..." if len(titolo) > 60 else "")

    @st.dialog(header)
    def _show():
        st.markdown(f"### {titolo}")
        st.divider()
        st.markdown("**✨ Gist:**")

        with st.spinner(get_text("gist_loading")):
            gist_text = fetch_article_gist(link, titolo)

        if gist_text:
            st.write(gist_text)
        else:
            # Fallback: cleaned RSS snippet
            fallback = clean_snippet(snippet)
            if fallback and fallback != get_text("gist_na"):
                st.write(fallback)
            else:
                st.info(get_text("gist_na"))

        st.caption(get_text("gist_info"))
        st.markdown(f"🔗 **[{get_text('open_article')}]({link})**")

    _show()


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_single_region(query: str, hl: str, gl: str, ceid: str) -> list:
    """
    Pure cached HTTP fetch for a single Google News RSS region.
    Returns a list of article dicts. Raises on network/parse errors.
    """
    data_list = []
    safe_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={safe_query}&hl={hl}&gl={gl}&ceid={ceid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req, timeout=10)
    root = ET.fromstring(response.read())

    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        date_el = item.find("pubDate")
        desc_el = item.find("description")
        source_el = item.find("source")

        title_text = title_el.text if title_el is not None else "N/A"
        link_text = link_el.text if link_el is not None else "N/A"
        date_text = date_el.text if date_el is not None else "N/A"
        snippet_text = desc_el.text if desc_el is not None else "N/A"

        if source_el is not None and source_el.text:
            domain = source_el.text
        else:
            domain = urllib.parse.urlparse(link_text).netloc or "Web"

        data_list.append({
            "Titolo": title_text,
            "Data": date_text,
            "Fonte": domain,
            "Snippet": snippet_text,
            "Link": link_text,
        })
    return data_list


def fetch_web_data(query: str, lang_settings=("it", "IT", "IT:it")) -> pd.DataFrame:
    """
    Fetch news articles for the given query from one or more regions.
    Multi-region fetches run in parallel. Results are deduplicated by Link.
    """
    settings_list = [lang_settings] if isinstance(lang_settings, tuple) else list(lang_settings)

    all_data: list = []
    errors: list = []

    with ThreadPoolExecutor(max_workers=max(1, len(settings_list))) as executor:
        futures = {
            executor.submit(_fetch_single_region, query, hl, gl, ceid): (hl, gl, ceid)
            for hl, gl, ceid in settings_list
        }
        for future in as_completed(futures):
            try:
                all_data.extend(future.result())
            except Exception as e:
                errors.append(str(e))

    for err in errors:
        st.error(get_text("search_error", e=err))

    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.drop_duplicates(subset=["Link"])
        df["Data_Formatted"] = df["Data"].apply(format_date)
    return df


def render_results_cards(df_subset: pd.DataFrame, tab_id: str = "tab"):
    """Render a list of news articles in a Google-style card layout."""
    if df_subset.empty:
        st.info(get_text("no_results_page"))
        return

    # Show dialog if this tab triggered one
    if (
        st.session_state.get("gist_tab") == tab_id
        and "gist_titolo" in st.session_state
    ):
        ai_gist_dialog(
            st.session_state.pop("gist_titolo"),
            st.session_state.pop("gist_snippet"),
            st.session_state.pop("gist_link"),
        )
        st.session_state.pop("gist_tab", None)

    # CSS: card overlay + tighten the gap between button and date
    st.markdown("""
        <style>
        /* Light grey card background for each news item */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 10px !important;
            padding: 2px 10px 6px 10px !important;
            margin-bottom: 6px !important;
        }
        /* Collapse the default bottom margin Streamlit adds under buttons inside cards */
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] {
            margin-bottom: -10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    for idx, row in df_subset.iterrows():
        raw_link = row["Link"]
        fonte = row["Fonte"]
        titolo = row["Titolo"]
        data = row.get("Data_Formatted", row["Data"])

        # Derive domain for favicon lookup
        parsed = urllib.parse.urlparse(raw_link)
        domain = parsed.netloc or (fonte.lower().replace(" ", "") + ".com")
        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"

        with st.container(border=True):
            # Source breadcrumb with real favicon
            st.markdown(f"""
                <div style="margin-bottom: 2px; display: flex; align-items: center; gap: 8px;">
                    <img src="{favicon_url}"
                         style="width:20px;height:20px;border-radius:4px;object-fit:cover;"
                         onerror="this.style.display='none'">
                    <div style="font-size: 14px; color: #bdc1c6;">
                        <span style="color: #e8eaed; font-weight: 500;">{fonte}</span>
                        <span style="margin: 0 4px;">›</span>
                        <span style="font-size: 12px;">news</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Title button — opens dialog on click
            if st.button(titolo, key=f"title_{tab_id}_{idx}", type="tertiary", use_container_width=False):
                st.session_state["gist_tab"] = tab_id
                st.session_state["gist_titolo"] = titolo
                st.session_state["gist_snippet"] = row["Snippet"]
                st.session_state["gist_link"] = raw_link
                st.rerun()

            # Date — tight below title
            st.markdown(f"""
                <div style="font-size: 14px; color: #9aa0a6; margin-top: -4px; padding-bottom: 2px;">
                    {data}
                </div>
            """, unsafe_allow_html=True)



def render_results_table(df_subset: pd.DataFrame):
    """Render news articles in a dataframe/table view."""
    if df_subset.empty:
        st.info(get_text("no_results_page"))
        return

    df_show = df_subset.drop(
        columns=["Data", "Data_Formatted", "Snippet"], errors="ignore"
    ).copy()
    column_config = {
        "Link": st.column_config.LinkColumn(get_text("web_page"))
    }
    st.dataframe(df_show, column_config=column_config, use_container_width=True)
