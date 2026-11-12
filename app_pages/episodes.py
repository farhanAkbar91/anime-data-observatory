"""Page 5 — Episodes & Format: how length shapes reach and reception."""
from __future__ import annotations

import streamlit as st

from src.analysis import episode_buckets, episodes_hist, longest_titles
from src.metrics import fmt_compact, fmt_pct, fmt_score, kpi_card, kpi_row
from src.tables import rank_table
from src.ui import empty_state, page_header, section
from src.visualizations import (bar_episode_buckets, box_episodes_by_type,
                                histogram_episodes)


def render(ctx) -> None:
    page_header(
        "Episodes & Format",
        "Episode counts as a production choice — and what it does to reach "
        "and reception.",
    )

    ep = ctx.anime[ctx.anime["episodes"].notna()]
    if ep.empty:
        empty_state("No titles with known episode counts match the current filters.")
        return

    buckets = episode_buckets(ep)
    single = (ep["episodes"].astype(int) == 1).mean()
    med_eps = int(ep["episodes"].astype(int).median())
    best = buckets[buckets["avg_score"].notna()]
    best_bucket = best.nlargest(1, "avg_score") if len(best) else None

    kpi_row([
        kpi_card("Titles with known length", f"{len(ep):,}",
                 f"{fmt_pct(len(ep) / max(len(ctx.anime), 1))} of the current view"),
        kpi_card("Single-episode titles", fmt_pct(single),
                 "movies, specials and one-shot OVAs"),
        kpi_card("Median episode count", f"{med_eps}",
                 "half of all titles run 1–12 episodes"),
        kpi_card("Best-scoring length", best_bucket["bucket"].iloc[0] if best_bucket is not None and len(best_bucket) else "—",
                 f"avg score {fmt_score(best_bucket['avg_score'].iloc[0])}" if best_bucket is not None and len(best_bucket) else ""),
        kpi_card("Widest-reaching length",
                 best.nlargest(1, "median_members")["bucket"].iloc[0] if len(best) else "—",
                 f"median members {fmt_compact(best.nlargest(1, 'median_members')['median_members'].iloc[0])}" if len(best) else ""),
    ])

    section("Length distribution", "From one-shots to 1,800-episode marathons")
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.plotly_chart(histogram_episodes(episodes_hist(ep), ctx.theme),
                        use_container_width=True)
    with col_b:
        st.plotly_chart(box_episodes_by_type(ctx.anime, ctx.theme),
                        use_container_width=True)

    section("Length vs outcomes", "Score and reach per episode bucket")
    metric = st.segmented_control("Metric", ["Avg score", "Median members"],
                                  default="Avg score", key="ep_metric",
                                  help="Same buckets, two complementary measures.")
    metric = metric or "Avg score"
    fig = bar_episode_buckets(buckets, ctx.theme,
                              metric="avg_score" if metric == "Avg score" else "median_members")
    st.plotly_chart(fig, use_container_width=True)

    section("Marathon titles", "The longest runs in the current view")
    st.markdown(rank_table(longest_titles(ep, 10), [
        ("#", "", "rank"),
        ("Title", "name", "name"),
        ("Type", "type", "type"),
        ("Episodes", "episodes", "int"),
        ("Score", "rating", "score"),
        ("Members", "members", "compact"),
    ]), unsafe_allow_html=True)
