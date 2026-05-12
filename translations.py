import streamlit as st

TRANSLATIONS = {
    "it": {
        # App
        "app_title": "World News Tracker",
        "nav_live": "Hantavirus LIVE",
        "nav_search": "Ricerca",
        "nav_who": "WHO News",
        "lang_selector": "Lingua / Language",

        # Live Page
        "live_title": "🔴 Hantavirus LIVE Feed",
        "live_desc": "Questa pagina si aggiorna automaticamente in tempo reale catturando le ultimissime notizie a livello globale sul termine 'Hantavirus'.",
        "live_update": "Ultimo aggiornamento automatico: {time} (Ciclo #{count})",
        "live_sync": "Sincronizzazione Live Data...",
        "live_waiting": "📡 In attesa di segnale dai server globali... riprova a breve.",
        "live_info": "Il Live Tracker è limitato alle 15 notizie più scottanti in tutto il mondo al minuto e si ricarica in background per garantirti il dato in tempo reale.",

        # WHO Page
        "who_title": "WHO Newsroom",
        "who_desc": "Notizie ufficiali dall'Organizzazione Mondiale della Sanità, aggiornate in tempo reale.",
        "who_update": "Aggiornato alle {time} (Ciclo #{count})",
        "who_loading": "Caricamento notizie WHO...",
        "who_empty": "📡 Nessuna notizia WHO disponibile al momento. Riprova tra poco.",
        "who_sidebar_header": "🔍 Filtra per Argomento",
        "who_topic_filter": "Seleziona argomenti",
        "who_all_topics": "Tutti gli argomenti...",
        "who_articles_count": "{n} articoli trovati",
        "who_no_results": "Nessun articolo corrisponde agli argomenti selezionati.",
        "who_sidebar_info": "Le notizie provengono dal feed RSS ufficiale dell'OMS e vengono aggiornate automaticamente ogni 5 minuti.",

        # Search Page
        "search_title": "📰 World News Tracker",
        "search_desc": "Ricerca le notizie dal Web in modo esteso. I risultati sono impaginati (Max 10 per pagina).",
        "search_label": "Cerca",
        "search_placeholder": "Cerca notizie...",
        "search_btn": "Ricerca Web",
        "sidebar_settings": "Impostazioni",
        "sidebar_region": "Lingua e Regione News",
        "sidebar_view": "Stile di Visualizzazione",
        "view_cards": "A Schede (Moderno)",
        "view_table": "Tabellare (Stile Excel)",
        "search_in_progress": "Ricerca Globale su [{region}] in corso...",
        "search_invalid": "Inserisci una parola chiave valida.",
        "sources_popover": "📰 Fonti",
        "sources_filter": "Filtra per Fonte",
        "toggle_links": "Mostra indirizzi web (Link) nei risultati",
        "results_found": "Risultati Trovati: {total}",
        "page_selector": "Pagina (1 di {total})",
        "viewing_range": "😎 Visualizzazione {start}-{end} di {total}",
        "tab_relevance": "Per Rilevanza (Default)",
        "tab_recent": "Dal Più Recente",
        "tab_oldest": "Dal Più Vecchio",
        "download_csv": "Scarica Report CSV Completo",
        "no_results_search": "Nessun risultato trovato dal motore di ricerca. Prova con una parola chiave diversa.",
        "awaiting_search": "Effettua una ricerca usando la barra centrale per iniziare.",

        # Regions
        "region_global": "Globale",
        "region_en": "Inglese",
        "region_it": "Italia (Italiano)",
        "region_es": "Spagna (Spagnolo)",
        "region_fr": "Francia (Francese)",
        "region_de": "Germania (Tedesco)",

        # Utils / Shared
        "gist_title": "✨ AI Gist - Punti Chiave dell'Articolo",
        "gist_info": "Estratto dalla pagina dell'articolo (meta description o primo paragrafo).",
        "gist_loading": "Caricamento gist dall'articolo...",
        "gist_na": "Riassunto non disponibile.",
        "na": "N/D",
        "search_error": "Errore durante la ricerca web nativa: {e}",
        "no_results_page": "Nessun risultato in questa pagina.",
        "source": "Fonte",
        "date": "Data",
        "web_page": "Pagina Web",
        "default_web": "Web",
        "open_article": "Apri Articolo Completo",
    },
    "en": {
        # App
        "app_title": "World News Tracker",
        "nav_live": "Hantavirus LIVE",
        "nav_search": "Search",
        "nav_who": "WHO News",
        "lang_selector": "Lingua / Language",

        # Live Page
        "live_title": "🔴 Hantavirus LIVE Feed",
        "live_desc": "This page updates automatically in real-time, capturing the latest global news on the term 'Hantavirus'.",
        "live_update": "Last automatic update: {time} (Cycle #{count})",
        "live_sync": "Syncing Live Data...",
        "live_waiting": "📡 Waiting for signal from global servers... please try again shortly.",
        "live_info": "The Live Tracker is limited to the top 15 hottest news worldwide per minute and reloads in the background to guarantee real-time data.",

        # WHO Page
        "who_title": "WHO Newsroom",
        "who_desc": "Official news from the World Health Organization, updated in real-time.",
        "who_update": "Updated at {time} (Cycle #{count})",
        "who_loading": "Loading WHO news...",
        "who_empty": "📡 No WHO news available at this time. Please try again shortly.",
        "who_sidebar_header": "🔍 Filter by Topic",
        "who_topic_filter": "Select topics",
        "who_all_topics": "All topics...",
        "who_articles_count": "{n} articles found",
        "who_no_results": "No articles match the selected topics.",
        "who_sidebar_info": "News is sourced from the official WHO RSS feed and refreshes automatically every 5 minutes.",

        # Search Page
        "search_title": "📰 World News Tracker",
        "search_desc": "Extensively search news from the Web. Results are paginated (Max 10 per page).",
        "search_label": "Search",
        "search_placeholder": "Search news...",
        "search_btn": "Web Search",
        "sidebar_settings": "Settings",
        "sidebar_region": "News Language and Region",
        "sidebar_view": "View Style",
        "view_cards": "Cards (Modern)",
        "view_table": "Tabular (Excel Style)",
        "search_in_progress": "Global Search on [{region}] in progress...",
        "search_invalid": "Please enter a valid keyword.",
        "sources_popover": "📰 Sources",
        "sources_filter": "Filter by Source",
        "toggle_links": "Show web addresses (Links) in results",
        "results_found": "Results Found: {total}",
        "page_selector": "Page (1 of {total})",
        "viewing_range": "😎 Viewing {start}-{end} of {total}",
        "tab_relevance": "By Relevance (Default)",
        "tab_recent": "Newest First",
        "tab_oldest": "Oldest First",
        "download_csv": "Download Full CSV Report",
        "no_results_search": "No results found from the search engine. Try a different keyword.",
        "awaiting_search": "Perform a search using the center bar to begin.",

        # Regions
        "region_global": "Global",
        "region_en": "English",
        "region_it": "Italy (Italian)",
        "region_es": "Spain (Spanish)",
        "region_fr": "France (French)",
        "region_de": "Germany (German)",

        # Utils / Shared
        "gist_title": "✨ AI Gist - Article Key Points",
        "gist_info": "Extracted from the article page (meta description or first paragraph).",
        "gist_loading": "Loading gist from article...",
        "gist_na": "Summary not available.",
        "na": "N/A",
        "search_error": "Error during native web search: {e}",
        "no_results_page": "No results on this page.",
        "source": "Source",
        "date": "Date",
        "web_page": "Web Page",
        "default_web": "Web",
        "open_article": "Open Full Article",
    },
}


def get_text(key: str, **kwargs) -> str:
    """Look up a translation key in the current UI language, with optional format args."""
    lang = st.session_state.get("ui_lang", "it")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["it"]).get(key, key)
    return text.format(**kwargs) if kwargs else text
