"""Custom HTML ranking tables.

Rendered as plain HTML + CSS-variable styling so tables follow the active
theme in both Light and Dark mode (Streamlit's dataframe widget cannot be
re-themed per session). Tables are pre-sorted by their ranking measure;
interactive re-sorting is a Tableau-native capability in the target build.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from .metrics import fmt_compact, fmt_int, fmt_pct, fmt_score


def _cell(value: Any, kind: str) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)) or \
            (isinstance(value, pd.Timestamp) and pd.isna(value)) or \
            (pd.api.types.is_scalar(value) and pd.isna(value)):
        return '<td class="num muted">—</td>' if kind != "name" else '<td class="muted">—</td>'
    if kind == "rank":
        return f'<td class="rank">{value}</td>'
    if kind == "name":
        return f'<td class="name" title="{value}">{value}</td>'
    if kind == "text":
        return f"<td>{value}</td>"
    if kind == "type":
        return f'<td><span class="badge">{value}</span></td>'
    if kind == "int":
        return f'<td class="num">{fmt_int(value)}</td>'
    if kind == "compact":
        return f'<td class="num">{fmt_compact(value)}</td>'
    if kind == "score":
        return f'<td class="num">{fmt_score(float(value))}</td>'
    if kind == "pct":
        return f'<td class="num">{fmt_pct(value)}</td>'
    return f"<td>{value}</td>"


def rank_table(df: pd.DataFrame, columns: list[tuple[str, str, str]],
               *, rank_col: bool = True) -> str:
    """Build a themed ranking table.

    columns: list of (header, df column, kind) where kind is one of
    rank|name|text|type|int|compact|score|pct.
    """
    head = "".join(f"<th>{h}</th>" for h, _, _ in columns)
    body_rows = []
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        cells = []
        for header, col, kind in columns:
            if kind == "rank":
                cells.append(_cell(i, "rank"))
            else:
                cells.append(_cell(row.get(col), kind))
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    body = "".join(body_rows) or '<tr><td colspan="99" class="muted">No titles match the current filters.</td></tr>'
    return (
        f'<div class="table-wrap"><table class="rank-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )
