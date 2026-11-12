"""Page 3 — Rating & Quality: scores, formats, genres, and the two score systems."""
from __future__ import annotations

import streamlit as st

from src.analysis import genre_quality, official_vs_community
from src.tables import rank_table
from src.ui import empty_state, page_header, section
from src.visualizations import (box_score_by_type, hbar_genre_scores,
                                histogram_score, hbar_gap,
                                scatter_official_community)

TOP_MEMBERS_STOPS = [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000]


def render(ctx) -> None:
    page_header(
        "Rating & Quality",
        "The official weighted score vs the raw voice of the community — "
        "distributions, leaders and systematic gaps.",
    )

    if ctx.anime.empty:
        empty_state("No titles match the current filters.",
                    "Loosen the filters in the sidebar or press “Reset filters”.")
        return

    section("Score landscape", "Where quality concentrates in this view")
    st.plotly_chart(histogram_score(ctx.anime, ctx.theme), use_container_width=True)

    section("Scores by format and genre")
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.plotly_chart(box_score_by_type(ctx.anime, ctx.theme),
                        use_container_width=True)
    with col_b:
        st.select_slider("Minimum titles per genre tag",
                         options=[10, 25, 50, 75, 100, 150, 200],
                         value=50, key="rq_min_titles",
                         help="Genre averages over very few titles are noisy — "
                              "raise this to focus on well-attested tags.")
        gq = genre_quality(ctx.anime, ctx.genres,
                           min_titles=int(st.session_state.get("rq_min_titles", 50)))
        if gq.empty:
            empty_state("No genre tag meets the minimum title count in this view.",
                        "Lower the minimum above.")
        else:
            st.plotly_chart(hbar_genre_scores(gq, ctx.theme), use_container_width=True)

    section("Top rated", "Highest official scores among broadly-known titles")
    min_members = st.select_slider(
        "Minimum members for the ranking", options=TOP_MEMBERS_STOPS, value=1000,
        key="rq_min_members",
        help="Tiny-sample titles can carry extreme scores (a 10.00 with 13 members); "
             "this threshold keeps the ranking meaningful.")
    scored = ctx.anime[ctx.anime["rating"].notna()]
    d = scored[scored["members"] >= min_members]
    top = d.nlargest(12, "rating")[["name", "type", "episodes", "rating", "members"]]
    st.markdown(rank_table(top, [
        ("#", "", "rank"),
        ("Title", "name", "name"),
        ("Type", "type", "type"),
        ("Eps", "episodes", "int"),
        ("Score", "rating", "score"),
        ("Members", "members", "compact"),
    ]), unsafe_allow_html=True)

    section("Official vs community",
            "The community systematically rates higher than the official weighted score")
    min_explicit = st.slider(
        "Minimum explicit ratings per title", 25, 500, 100, step=25,
        key="rq_min_explicit",
        help="Titles with few explicit ratings have unstable community means.")
    pair = official_vs_community(ctx.anime, min_explicit=min_explicit)
    if pair.empty:
        empty_state("No titles meet the explicit-ratings threshold in this view.")
    else:
        col_c, col_d = st.columns([7, 5], gap="large")
        with col_c:
            st.plotly_chart(scatter_official_community(pair, ctx.theme),
                            use_container_width=True)
        with col_d:
            st.plotly_chart(hbar_gap(pair, ctx.theme, n=8), use_container_width=True)
        n_pos = int((pair["gap"] > 0).sum())
        st.markdown(
            f'<div class="section-note">In this view: {n_pos:,} of {len(pair):,} titles '
            f'({n_pos / max(len(pair), 1) * 100:.0f}%) are rated higher by the community '
            f'than by the official weighted score.</div>',
            unsafe_allow_html=True)
