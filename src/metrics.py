"""KPI computations and display formatting.

All KPIs are computed dynamically from the filtered frames — nothing is
hardcoded. Definitions are kept Tableau-compatible (see documentation/
tableau_implementation_reference.md).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st


def compute_kpis(anime: pd.DataFrame, user_count: int | None = None) -> dict:
    """Core KPI block for the Overview page (filtered base table)."""
    k: dict = {}
    k["titles"] = int(len(anime))
    k["avg_score"] = float(anime["rating"].mean()) if anime["rating"].notna().any() else None
    k["median_score"] = float(anime["rating"].median()) if anime["rating"].notna().any() else None
    k["scored_share"] = float(anime["rating"].notna().mean()) if len(anime) else 0.0
    k["members_total"] = int(anime["members"].sum()) if len(anime) else 0
    k["members_median"] = int(anime["members"].median()) if len(anime) else 0

    # Community aggregates ride on the precomputed per-anime table (n_* columns)
    for col, key in [("n_ratings", "community_ratings"),
                     ("n_explicit", "explicit_ratings"),
                     ("n_watched", "watched_only")]:
        k[key] = int(anime[col].sum()) if col in anime.columns else 0
    k["users"] = user_count
    k["watched_share"] = (k["watched_only"] / k["community_ratings"]
                          if k["community_ratings"] else None)
    cm = anime["community_mean"] if "community_mean" in anime.columns else pd.Series(dtype=float)
    k["community_mean"] = float(cm.mean()) if cm.notna().any() else None
    return k


def fmt_int(v: float | int | None) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{int(round(v)):,}"


def fmt_compact(v: float | int | None) -> str:
    """222,169,040 -> 222.2M ; 1,550 -> 1.6K ; 981 -> 981"""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    v = float(v)
    neg = v < 0
    v = abs(v)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if v >= div:
            s = f"{v/div:.1f}".rstrip("0").rstrip(".")
            return ("-" if neg else "") + s + suf
    return ("-" if neg else "") + f"{int(v):,}"


def fmt_score(v: float | None) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{v:.2f}"


def fmt_pct(v: float | None, digits: int = 1) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{v * 100:.{digits}f}%"


def kpi_card(label: str, value: str, context: str = "") -> str:
    """Render one rounded KPI card (custom HTML, theme-aware via CSS vars)."""
    ctx = f'<div class="kpi-context">{context}</div>' if context else ""
    return (
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{ctx}</div>'
    )


def kpi_row(cards: list[str]) -> None:
    """Lay out KPI cards in a responsive grid."""
    import math

    n = len(cards)
    cols = 6 if n >= 6 else 4 if n == 4 else 3 if n == 3 else n
    rows = math.ceil(n / cols)
    cells = list(cards) + [""] * (rows * cols - n)
    out = ""
    for r in range(rows):
        row = cells[r * cols:(r + 1) * cols]
        out += '<div class="kpi-grid">' + "".join(
            f'<div class="kpi-cell">{c}</div>' for c in row) + "</div>"
    st.markdown(out, unsafe_allow_html=True)
