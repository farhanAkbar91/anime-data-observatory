"""Page 2 — Popularity & Engagement: who owns the community's attention."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import members_log_hist, watched_share_by_tier
from src.ui import empty_state, page_header, section
from src.visualizations import (bar_tiers, box_members_by_type,
                                hbar_topn, members_log_hist_chart,
                                scatter_score_members)


def _prep_top(anime: pd.DataFrame, column: str, n: int) -> pd.DataFrame:
    """Top-N with friendly display column names for hover text."""
    keep = ["name", "type", "episodes", "rating", "members", "n_ratings",
            "community_mean"]
    d = anime.nlargest(n, column)[keep].copy()
    d["Episodes"] = d["episodes"].map(lambda v: "—" if pd.isna(v) else str(int(v)))
    d["Format"] = d["type"]
    d["Official score"] = d["rating"].map(lambda v: "—" if pd.isna(v) else f"{v:.2f}")
    d["Community mean"] = d["community_mean"].map(
        lambda v: "—" if pd.isna(v) else f"{v:.2f}")
    d["Members"] = d["members"].fillna(0)
    d["Community ratings"] = d["n_ratings"].fillna(0)
    xcol = "Members" if column == "members" else "Community ratings"
    return d.sort_values(column, ascending=True)[[xcol, "name", "Format",
                                                  "Official score", "Episodes",
                                                  "Community mean"]]


def render(ctx) -> None:
    page_header(
        "Popularity & Engagement",
        "Where the community's attention concentrates, and how attention "
        "relates to critical quality.",
    )

    if ctx.anime.empty:
        empty_state("No titles match the current filters.",
                    "Loosen the filters in the sidebar or press “Reset filters”.")
        return

    section("Attention leaders", "Ranking titles by community footprint")
    col_ctl1, col_ctl2 = st.columns([3, 3], gap="large")
    with col_ctl1:
        metric = st.segmented_control(
            "Rank by", ["Members", "Community ratings"],
            default="Members", key="pop_metric",
            help="Members = community members on the platform · "
                 "Community ratings = user interaction events in the log.",
        )
    with col_ctl2:
        top_n = st.select_slider("Top N", options=[10, 15, 20, 25], value=15,
                                 key="pop_topn")

    metric = metric or "Members"
    column = "members" if metric == "Members" else "n_ratings"
    xlabel = "Members" if metric == "Members" else "Community rating events"
    subtitle = (f"Top {top_n} titles by community members · hover for scores"
                if metric == "Members" else
                f"Top {top_n} titles by user interaction events "
                "(explicit ratings + watched-not-scored)")
    top = _prep_top(ctx.anime, column, top_n)
    xcol = xlabel if metric == "Members" else "Community ratings"
    fig = hbar_topn(
        top, x=xcol, y="name", T=ctx.theme,
        title=f"Top titles by {xlabel.lower()}",
        subtitle=subtitle, xlabel=xlabel,
        hover=["Format", "Official score", "Episodes", "Community mean"],
        height=30 + 28 * len(top),
    )
    st.plotly_chart(fig, use_container_width=True)

    section("Popularity vs quality", "Does reaching more people mean scoring higher?")
    st.plotly_chart(scatter_score_members(ctx.anime, ctx.theme),
                    use_container_width=True)

    col_e, col_f = st.columns(2, gap="large")
    with col_e:
        hist = members_log_hist(ctx.anime)
        st.plotly_chart(members_log_hist_chart(hist, ctx.theme),
                        use_container_width=True)
    with col_f:
        st.plotly_chart(box_members_by_type(ctx.anime, ctx.theme),
                        use_container_width=True)

    section("Engagement depth",
            "The share of 'watched but not rated' events falls as popularity rises")
    tiers = watched_share_by_tier(ctx.anime, n_tiers=4)
    if tiers.empty:
        empty_state("Not enough community data in this view to build popularity tiers.")
    else:
        st.plotly_chart(bar_tiers(tiers, ctx.theme), use_container_width=True)
