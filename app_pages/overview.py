"""Page 1 — Overview: headline KPIs, composition and quality landscape."""
from __future__ import annotations

import streamlit as st

from src.analysis import top_genres, type_distribution
from src.metrics import fmt_compact, fmt_pct, fmt_score, kpi_card, kpi_row
from src.tables import rank_table
from src.ui import empty_state, page_header, section
from src.visualizations import donut_type, histogram_score, hbar_topn


def render(ctx) -> None:
    page_header(
        "Overview",
        "The anime collection at a glance — all numbers recomputed live from the "
        "filters on the left.",
    )

    if ctx.anime.empty:
        empty_state("No titles match the current filters.",
                    "Loosen the filters in the sidebar or press “Reset filters”.")
        return

    k = ctx.anime
    users_txt = fmt_compact(ctx.users)
    kpi_row([
        kpi_card("Titles", f"{len(k):,}",
                 f"of {ctx.unfiltered_count:,} in the dataset"),
        kpi_card("Avg official score", fmt_score(k["rating"].mean()),
                 f"median {fmt_score(k['rating'].median())} · {fmt_pct(k['rating'].notna().mean())} scored"),
        kpi_card("Total members", fmt_compact(k["members"].sum()),
                 f"median title {fmt_compact(k['members'].median())}"),
        kpi_card("Community ratings", fmt_compact(k["n_ratings"].sum()),
                 f"{fmt_compact(k['n_explicit'].sum())} explicit scores"),
        kpi_card("Users engaged", users_txt,
                 "interacted with this selection"),
        kpi_card("Watched-not-scored", fmt_pct(
                    k["n_watched"].sum() / k["n_ratings"].sum()) if k["n_ratings"].sum() else "—",
                 "share of -1 “logged, no score” events"),
    ])

    # ---------------------------------------------------------- composition
    section("Composition", "What the collection is made of")
    col_a, col_b = st.columns([5, 7], gap="large")
    with col_a:
        tc = type_distribution(ctx.anime)
        st.plotly_chart(donut_type(tc, ctx.theme), use_container_width=True)
    with col_b:
        tg = top_genres(ctx.anime, ctx.genres, top_n=12)
        fig = hbar_topn(tg, x="titles", y="genre", T=ctx.theme,
                        title="Most common genre tags", xlabel="Titles",
                        subtitle="Top 12 tags in the current view · a title counts once per tag")
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------- quality
    section("Quality landscape", "How scores are distributed, and which titles lead on reach")
    col_c, col_d = st.columns([7, 5], gap="large")
    with col_c:
        st.plotly_chart(histogram_score(ctx.anime, ctx.theme), use_container_width=True)
    with col_d:
        section("Top titles by community members")
        top10 = ctx.anime.nlargest(10, "members")[
            ["name", "type", "episodes", "rating", "members"]]
        st.markdown(rank_table(top10, [
            ("#", "", "rank"),
            ("Title", "name", "name"),
            ("Type", "type", "type"),
            ("Eps", "episodes", "int"),
            ("Score", "rating", "score"),
            ("Members", "members", "compact"),
        ]), unsafe_allow_html=True)
