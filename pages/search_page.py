import streamlit as st
import pandas as pd
import math
from utils import REGION_MAPPING, fetch_web_data, render_results_cards, render_results_table
from translations import get_text

has_data = "data" in st.session_state

# --- Title / Description (hidden once results exist) ---
if not has_data:
    st.markdown(f"<h1 style='text-align: center;'>{get_text('search_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{get_text('search_desc')}</p>", unsafe_allow_html=True)
    st.write("")

# --- Search Bar ---
# Wide layout after search; centered layout before first search.
if has_data:
    col_main, col_side = st.columns([8, 2])
    with col_main:
        with st.form(key="search_form", border=False):
            fcol1, fcol2 = st.columns([5, 1])
            with fcol1:
                search_query = st.text_input(
                    get_text("search_label"),
                    value=st.session_state.get("last_query", "Hantavirus"),
                    label_visibility="collapsed",
                    placeholder=get_text("search_placeholder"),
                )
            with fcol2:
                search_pressed = st.form_submit_button(get_text("search_btn"), use_container_width=True)
        results_count_placeholder = st.empty()
else:
    col1, col2, col3 = st.columns([1, 4, 1])
    col_main = col2  # alias so the visualization block can always reference col_main
    results_count_placeholder = st.empty()
    with col2:
        with st.form(key="search_form", border=False):
            fcol1, fcol2 = st.columns([5, 2])
            with fcol1:
                search_query = st.text_input(
                    get_text("search_label"),
                    value=st.session_state.get("last_query", "Hantavirus"),
                    label_visibility="collapsed",
                    placeholder=get_text("search_placeholder"),
                )
            with fcol2:
                search_pressed = st.form_submit_button(get_text("search_btn"), use_container_width=True)

# --- Sidebar ---
st.sidebar.header(get_text("sidebar_settings"))
selected_region_key = st.sidebar.selectbox(
    get_text("sidebar_region"),
    list(REGION_MAPPING.keys()),
    format_func=lambda x: get_text(x),
)
view_mode = st.sidebar.radio(get_text("sidebar_view"), [get_text("view_cards"), get_text("view_table")])

# Track region changes for auto-refresh
if "last_region" not in st.session_state:
    st.session_state["last_region"] = list(REGION_MAPPING.keys())[0]

region_changed = st.session_state["last_region"] != selected_region_key
st.session_state["last_region"] = selected_region_key

should_search = search_pressed or (region_changed and has_data)

if should_search:
    query_to_search = search_query if search_pressed else st.session_state.get("last_query", search_query)
    if query_to_search.strip():
        with st.spinner(get_text("search_in_progress", region=get_text(selected_region_key))):
            df = fetch_web_data(query_to_search, REGION_MAPPING[selected_region_key])
            st.session_state["data"] = df
            st.session_state["page_bottom"] = 1
            st.session_state["last_query"] = query_to_search
            st.session_state.pop("last_source_filter", None)  # reset filter on new search
        st.rerun()
    else:
        st.warning(get_text("search_invalid"))

# --- Visualizzazione ---
if "data" in st.session_state:
    df = st.session_state["data"]

    if not df.empty:
        # Ensure date column is parsed (survives across reruns via session state)
        if "Data_Parse" not in df.columns:
            df["Data_Parse"] = pd.to_datetime(df["Data"], format="mixed", errors="coerce")
            st.session_state["data"] = df

        # Source filter popover
        with col_main:
            selected_source = []
            with st.popover(get_text("sources_popover")):
                selected_source = st.multiselect(
                    get_text("sources_filter"),
                    df["Fonte"].unique(),
                    label_visibility="collapsed",
                )

        # Reset page when filter changes
        prev_filter = st.session_state.get("last_source_filter", [])
        if set(selected_source) != set(prev_filter):
            st.session_state["page_bottom"] = 1
            st.session_state["last_source_filter"] = selected_source

        df_display = df.copy()
        if selected_source:
            df_display = df_display[df_display["Fonte"].isin(selected_source)]

        RESULTS_PER_PAGE = 10
        total_results = len(df_display)
        total_pages = max(1, math.ceil(total_results / RESULTS_PER_PAGE))

        # Results count below search bar
        results_count_placeholder.markdown(
            f'<p style="font-size: 14px; color: #9aa0a6; margin-left: 5px;">'
            f'{get_text("results_found", total=total_results)}</p>',
            unsafe_allow_html=True,
        )

        page = st.session_state.get("page_bottom", 1)
        start_idx = (page - 1) * RESULTS_PER_PAGE
        end_idx = start_idx + RESULTS_PER_PAGE

        # Tabs + results
        with col_main:
            st.write("")
            tab1, tab2, tab3 = st.tabs(
                [get_text("tab_relevance"), get_text("tab_recent"), get_text("tab_oldest")]
            )

        with tab1:
            df_tab1 = df_display.iloc[start_idx:end_idx]
            if view_mode == get_text("view_cards"):
                render_results_cards(df_tab1, "tab1")
            else:
                render_results_table(df_tab1)

        with tab2:
            df_tab2 = df_display.sort_values(by="Data_Parse", ascending=False).iloc[start_idx:end_idx]
            if view_mode == get_text("view_cards"):
                render_results_cards(df_tab2, "tab2")
            else:
                render_results_table(df_tab2)

        with tab3:
            df_tab3 = df_display.sort_values(by="Data_Parse", ascending=True).iloc[start_idx:end_idx]
            if view_mode == get_text("view_cards"):
                render_results_cards(df_tab3, "tab3")
            else:
                render_results_table(df_tab3)

        # Page selector at bottom
        with col_main:
            st.write("---")
            cp1, cp2, cp3 = st.columns([1, 1, 1])
            with cp2:
                st.number_input(
                    get_text("page_selector", total=total_pages),
                    min_value=1,
                    max_value=total_pages,
                    step=1,
                    key="page_bottom",
                )
                st.caption(
                    get_text(
                        "viewing_range",
                        start=start_idx + 1,
                        end=min(end_idx, total_results),
                        total=total_results,
                    )
                )

        # CSV export
        df_csv = df_display.drop(columns=["Data_Parse", "Data_Formatted", "Snippet"], errors="ignore")
        csv = df_csv.to_csv(index=False).encode("utf-8")
        st.download_button(get_text("download_csv"), csv, "notizie_ricerca.csv", "text/csv")

    else:
        st.warning(get_text("no_results_search"))
else:
    st.info(get_text("awaiting_search"))
