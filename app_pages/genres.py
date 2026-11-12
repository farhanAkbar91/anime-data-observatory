"""Page 4 — Genre Analysis: volume, quality, formats and combinations."""
from __future__ import annotations

import streamlit as st

from src.analysis import genre_pairs, genre_quality, genre_type_matrix, top_genres
from src.ui import empty_state, page_header, section
from src.visualizations import (bubble_genres, hbar_pairs, hbar_topn,
                                heatmap_genre_type)


def render(ctx) -> None:
    page_header(
        "Genre Analysis",
        "Which tags dominate the library, which deliver quality, and which "
        "combinations recur most often.",
    )

    if ctx.anime.empty:
        empty_state("No titles match the current filters.",
                    "Loosen the filters in the sidebar or press “Reset filters”.")
        return

    col_ctl, col_spacer = st.columns([3, 9], gap="large")
    with col_ctl:
        top_n = st.select_slider("Genres to show (frequency)", options=[10, 15, 20, 25, 30],
                                 value=15, key="gn_topn")

    top_n = int(top_n)
    tg = top_genres(ctx.anime, ctx.genres, top_n=top_n)
    if tg.empty:
        empty_state("No genre tags in this view.")
        return
    st.plotly_chart(
        hbar_topn(tg, x="titles", y="genre", T=ctx.theme,
                  title=f"Top {len(tg)} genre tags by title count",
                  subtitle="A title counts once per tag it carries, so totals exceed the "
                           "number of titles",
                  xlabel="Titles"),
        use_container_width=True)

    section("Volume vs quality", "Are the biggest genres also the best-rated?")
    min_titles = st.select_slider("Minimum titles per genre tag",
                                  options=[10, 25, 50, 100, 200],
                                  value=50, key="gn_min_titles")
    gq = genre_quality(ctx.anime, ctx.genres, min_titles=int(min_titles))
    if gq.empty:
        empty_state("No genre tag meets the minimum title count in this view.",
                    "Lower the minimum above.")
    else:
        st.plotly_chart(bubble_genres(gq, ctx.theme), use_container_width=True)

    section("Genre × format", "Where each tag lives across TV, movies and the rest")
    width = st.select_slider("Genres in heatmap", options=[10, 15, 20, 25, 30],
                             value=20, key="gn_heat_n")
    mat = genre_type_matrix(ctx.anime, ctx.genres, top_n=int(width))
    if mat.empty:
        empty_state("Not enough tagged titles in this view for a matrix.")
    else:
        st.plotly_chart(heatmap_genre_type(mat, ctx.theme), use_container_width=True)

    section("Combinations", "Which pairs of tags co-occur most often")
    pairs = genre_pairs(ctx.genres, ctx.anime["anime_id"], top_n=15)
    if pairs.empty:
        empty_state("No co-occurring genre pairs in this view.")
    else:
        st.plotly_chart(hbar_pairs(pairs, ctx.theme), use_container_width=True)
