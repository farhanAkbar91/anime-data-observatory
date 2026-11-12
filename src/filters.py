"""Global sidebar filters + shared filtering logic.

One `apply_filters` path for every page so KPIs and charts always agree
(mirrors a Tableau global dashboard filter).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

# Stepped stops for the members threshold slider: linear sliders are useless on
# a distribution with median 1,550 and max 1,013,917, so we use quantile-ish stops.
MEMBER_STOPS = [0, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000,
                100000, 250000, 500000, 1000000]

DEFAULT_SCORE_RANGE = (1.67, 10.0)


@dataclass
class FilterState:
    types: list[str] = field(default_factory=list)      # empty list == all
    genres: list[str] = field(default_factory=list)     # empty list == all
    score_range: tuple[float, float] = DEFAULT_SCORE_RANGE
    min_members: int = 0

    def is_active(self) -> bool:
        return bool(self.types) or bool(self.genres) or \
            tuple(self.score_range) != DEFAULT_SCORE_RANGE or self.min_members > 0


def _reset_filters() -> None:
    """on_click callback: runs before widgets are re-instantiated, so setting
    widget keys here is the supported reset pattern."""
    st.session_state["_f_types"] = []
    st.session_state["_f_genres"] = []
    st.session_state["_f_score"] = DEFAULT_SCORE_RANGE
    st.session_state["_f_members"] = 0


def type_options(anime: pd.DataFrame) -> list[str]:
    counts = anime["type"].value_counts()
    ordered = list(counts.index)
    if "Unknown" in ordered:  # keep Unknown last
        ordered.remove("Unknown")
        ordered.append("Unknown")
    return ordered


def genre_options(genres: pd.DataFrame) -> list[str]:
    counts = genres["genre"].value_counts()
    ordered = list(counts.index)
    if "Unknown" in ordered:
        ordered.remove("Unknown")
        ordered.append("Unknown")
    return ordered


def read_filter_state() -> FilterState:
    """Build the FilterState from the current widget keys."""
    return FilterState(
        types=list(st.session_state.get("_f_types", []) or []),
        genres=list(st.session_state.get("_f_genres", []) or []),
        score_range=tuple(st.session_state.get("_f_score", DEFAULT_SCORE_RANGE)),
        min_members=int(st.session_state.get("_f_members", 0) or 0),
    )


def render_sidebar_filters(anime: pd.DataFrame, genres: pd.DataFrame) -> FilterState:
    """Draw the global filter controls; returns the current FilterState."""
    st.sidebar.markdown('<div class="sidebar-heading">Global filters</div>',
                        unsafe_allow_html=True)

    t_opts = type_options(anime)
    st.multiselect(
        "Format (type)", t_opts, default=[], key="_f_types",
        placeholder="All formats",
        help="Keep titles of the selected formats. Empty = all.",
    )

    g_opts = genre_options(genres)
    st.multiselect(
        "Genre", g_opts, default=[], key="_f_genres",
        placeholder="All genres",
        help="Keep titles carrying ANY selected genre tag (OR match). Empty = all.",
    )

    r_min, r_max = float(anime["rating"].min()), float(anime["rating"].max())
    st.slider(
        "Official score range", min_value=r_min, max_value=r_max,
        value=DEFAULT_SCORE_RANGE, step=0.05, key="_f_score", format="%.2f",
        help="Filters on the official weighted score. Titles without a score "
             "(1.9% of the data) are excluded once this filter leaves the full range.",
    )

    st.select_slider(
        "Minimum members", options=MEMBER_STOPS,
        value=0, key="_f_members",
        format_func=lambda v: f"{v:,}" if v else "Any",
        help="Keep titles with at least this many community members. "
             "Stepped scale because the members distribution is extremely skewed.",
    )

    st.button("↺ Reset filters", on_click=_reset_filters,
              use_container_width=True, type="secondary")

    return read_filter_state()


def apply_filters(anime: pd.DataFrame, genres: pd.DataFrame, state: FilterState) -> pd.DataFrame:
    """Apply the FilterState to the metadata table (vectorized, shared by all pages)."""
    df = anime

    if state.types:
        df = df[df["type"].isin(state.types)]

    if state.genres:
        ids = genres.loc[genres["genre"].isin(state.genres), "anime_id"].unique()
        df = df[df["anime_id"].isin(set(ids))]

    lo, hi = state.score_range
    if tuple(state.score_range) != DEFAULT_SCORE_RANGE:
        df = df[df["rating"].between(lo, hi)]  # drops unscored titles (NaN) transparently

    if state.min_members > 0:
        df = df[df["members"] >= state.min_members]

    return df.copy()


def render_filter_chips(state: FilterState) -> None:
    """Show the active filter state as chips above the page content."""
    chips: list[str] = []
    if state.types:
        chips.append("Format: " + ", ".join(state.types))
    if state.genres:
        more = f" +{len(state.genres) - 4} more" if len(state.genres) > 4 else ""
        chips.append("Genre: " + ", ".join(state.genres[:4]) + more)
    if tuple(state.score_range) != DEFAULT_SCORE_RANGE:
        chips.append(f"Score {state.score_range[0]:.2f}–{state.score_range[1]:.2f}")
    if state.min_members > 0:
        chips.append(f"Members ≥ {state.min_members:,}")

    if not chips:
        st.markdown('<div class="chip-row"><span class="chip chip-muted">'
                    'Showing the full collection — adjust filters in the sidebar'
                    '</span></div>', unsafe_allow_html=True)
    else:
        html_chips = "".join(f'<span class="chip">{c}</span>' for c in chips)
        st.markdown(f'<div class="chip-row"><span class="chip chip-label">Filtered view</span>'
                    f'{html_chips}</div>', unsafe_allow_html=True)
