"""Anime Data Observatory — Hi-Fi dashboard prototype (Streamlit).

Run:  streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Anime Data Observatory",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- imports
from src.context import PageContext                      # noqa: E402
from src.data_loader import (build_anime_community,       # noqa: E402
                             count_users_for, load_anime,
                             load_genres, load_ratings)
from src.filters import apply_filters, render_filter_chips, render_sidebar_filters
from src.pages_shim import PAGES                          # noqa: E402
from src.theme import THEME_TOKENS, css_vars

ASSETS_CSS = Path(__file__).parent / "assets" / "custom_styles.css"

NAV = [
    "Overview",
    "Popularity & Engagement",
    "Rating & Quality",
    "Genre Analysis",
    "Episodes & Format",
    "Community Insights",
]

# ---------------------------------------------------------------- theme
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"


def _on_theme_change() -> None:
    val = st.session_state.get("theme_toggle")
    if isinstance(val, list):
        val = val[0] if val else None
    if val:
        st.session_state["theme"] = str(val).lower()


T = THEME_TOKENS.get(st.session_state["theme"], THEME_TOKENS["light"])
_css = css_vars(T) + ASSETS_CSS.read_text(encoding="utf-8")
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------- header
h_left, h_right = st.columns([9, 3], gap="large")
with h_left:
    st.markdown(
        '<div class="ado-header"><div class="ado-brand">'
        '<div class="brand-name"><span class="brand-dot"></span>'
        'Anime Data Observatory</div>'
        '<div class="brand-tag">Exploring 12,294 titles and 7.8M community '
        'interactions — Hi-Fi prototype for the Tableau build</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with h_right:
    st.markdown('<div class="theme-caption">Theme</div>', unsafe_allow_html=True)
    current = st.session_state["theme"].capitalize()
    st.pills(
        "Theme", ["Light", "Dark"], selection_mode="single",
        default=current, key="theme_toggle", on_change=_on_theme_change,
        label_visibility="collapsed",
    )

# ---------------------------------------------------------------- data
try:
    anime = load_anime()
    genres = load_genres()
    ratings = load_ratings()
    enriched = build_anime_community(anime)
except FileNotFoundError as exc:
    st.error(f"Dataset not found: {exc}")
    st.stop()

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sb-name"><span class="brand-dot"></span>Anime Data Observatory</div>'
        '<div class="sb-sub">Hi-Fi prototype · Tableau reference build</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-heading">Sections</div>',
                unsafe_allow_html=True)
    page = st.radio("Navigation", NAV, label_visibility="collapsed", key="nav")
    st.markdown("<hr>", unsafe_allow_html=True)
    state = render_sidebar_filters(enriched, genres)
    st.markdown(
        '<div class="sidebar-note"><b>About the data</b><br>'
        'Kaggle Anime Recommendations database (MyAnimeList snapshot). '
        'The dataset contains no release dates, studios or favorites — '
        'those analyses are out of scope by design. '
        'Score = official weighted average; community stats come from the raw '
        'user log (−1 = watched, not scored).</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- content
filtered = apply_filters(enriched, genres, state)
render_filter_chips(state)

ctx = PageContext(
    anime=filtered,
    genres=genres,
    ratings=ratings,
    user_stats=None,  # set below (kept out of the dataclass default path)
    users=0,
    theme=T,
    state=state,
    unfiltered_count=len(anime),
)

from src.data_loader import build_user_stats  # noqa: E402

user_stats = build_user_stats()
ctx.user_stats = user_stats
ctx.users = count_users_for(tuple(filtered["anime_id"].tolist())) if len(filtered) else 0

PAGES[page](ctx)

st.markdown(
    '<div class="ado-footer"><span>Anime Data Observatory — academic '
    'dashboard prototype · Streamlit → Tableau</span>'
    '<span>Filters apply to every page · scores are official weighted '
    'averages · community stats from the raw user log</span></div>',
    unsafe_allow_html=True,
)
