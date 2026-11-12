"""Page 6 — Community Insights: how the 73.5K users actually rate and behave."""
from __future__ import annotations

import streamlit as st

from src.analysis import explicit_rating_distribution, ratings_per_user_hist
from src.data_loader import user_stats_for
from src.metrics import fmt_compact, fmt_pct, fmt_score, kpi_card, kpi_row
from src.tables import rank_table
from src.ui import empty_state, page_header, section
from src.visualizations import bar_rating_values, hist_user_activity


def render(ctx) -> None:
    page_header(
        "Community Insights",
        "User-side behavior from the raw interaction log — rating habits, "
        "positivity bias and where engagement concentrates.",
    )

    if ctx.anime.empty:
        empty_state("No titles match the current filters.",
                    "Loosen the filters in the sidebar or press “Reset filters”.")
        return

    ids = tuple(ctx.anime["anime_id"].tolist())
    filtered_active = ctx.state.is_active()

    if filtered_active:
        us = user_stats_for(ids, ctx.user_stats)
        scope_note = ("Stats restricted to users who interacted with the "
                      "filtered selection of titles.")
    else:
        us = ctx.user_stats
        scope_note = "Full user base (73,515 users) — no filters active."

    n_exp = int(ctx.anime["n_explicit"].sum()) if "n_explicit" in ctx.anime else 0
    n_all = int(ctx.anime["n_ratings"].sum()) if "n_ratings" in ctx.anime else 0
    n_watch = n_all - n_exp
    cm = ctx.anime["community_mean"]
    official = ctx.anime["rating"]

    kpi_row([
        kpi_card("Users in scope", f"{ctx.users:,}", scope_note.split(" (")[0].lower()),
        kpi_card("Interaction events", fmt_compact(n_all),
                 f"{fmt_compact(n_exp)} explicit · {fmt_compact(n_watch)} logged-only"),
        kpi_card("Watched-not-scored", fmt_pct(n_watch / n_all) if n_all else "—",
                 "users log without scoring — mostly niche titles"),
        kpi_card("User mean score", fmt_score(us["mean_explicit"].mean()) if us["mean_explicit"].notna().any() else "—",
                 "average of per-user explicit means"),
        kpi_card("Community mean per title", fmt_score(cm.mean()) if cm.notna().any() else "—",
                 f"vs official {fmt_score(official.mean())} in this view"),
        kpi_card("Sentiment bias", f"{cm.mean() - official.mean():+.2f}" if cm.notna().any() and official.notna().any() else "—",
                 "community mean − official mean, per title"),
    ])

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        dist = explicit_rating_distribution(ctx.ratings, ids)
        st.plotly_chart(bar_rating_values(dist, ctx.theme), use_container_width=True)
    with col_b:
        st.plotly_chart(hist_user_activity(ratings_per_user_hist(us), ctx.theme),
                        use_container_width=True)

    section("Most-rated titles",
            "Where the community's rating activity concentrates — both score "
            "systems side by side")
    top = (ctx.anime.dropna(subset=["n_ratings"]).nlargest(15, "n_ratings")[
        ["name", "type", "n_ratings", "community_mean", "rating", "members"]]
        .rename(columns={"n_ratings": "n_rate"}))
    top["gap"] = top["community_mean"] - top["rating"]
    st.markdown(rank_table(top, [
        ("#", "", "rank"),
        ("Title", "name", "name"),
        ("Type", "type", "type"),
        ("Rating events", "n_rate", "compact"),
        ("Community mean", "community_mean", "score"),
        ("Official score", "rating", "score"),
        ("Members", "members", "compact"),
    ]), unsafe_allow_html=True)
