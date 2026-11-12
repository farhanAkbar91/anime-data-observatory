"""Theme tokens, palettes and the Plotly layout contract for both themes.

Light mode is the default and the primary Tableau design reference.
Both themes share the same categorical color assignment order so chart
colors stay consistent when toggling.
"""
from __future__ import annotations

from typing import Any

FONT_STACK = (
    '"Segoe UI", "Helvetica Neue", Arial, system-ui, -apple-system, sans-serif'
)

# ---------------------------------------------------------------- palettes
# 10-step categorical palette: hue order is fixed and shared by both themes.
CAT_PALETTE = [
    "#5457D6",  # indigo   (primary accent)
    "#E8930C",  # amber
    "#2FA36B",  # emerald
    "#D8578B",  # rose
    "#3E7BC4",  # blue
    "#8C63D9",  # violet
    "#C74A44",  # red
    "#2E9BA6",  # teal
    "#D97B2E",  # orange
    "#6B7BB6",  # slate blue
]

# Fixed color assignment for the six anime formats (+ Unknown).
# The same hue means the same format on every chart in both themes.
TYPE_COLORS = {
    "light": {
        "TV": "#5457D6",
        "Movie": "#E8930C",
        "OVA": "#2FA36B",
        "Special": "#D8578B",
        "ONA": "#3E7BC4",
        "Music": "#8C63D9",
        "Unknown": "#8892A6",
    },
    "dark": {
        "TV": "#7C7FF0",
        "Movie": "#F5A623",
        "OVA": "#4CC58C",
        "Special": "#E8789F",
        "ONA": "#6B9EE0",
        "Music": "#A98BE8",
        "Unknown": "#7E89A0",
    },
}

# Diverging scale used for official-vs-community score gaps.
DIVERGING = {
    "light": ["#C74A44", "#B9BECB", "#2FA36B"],
    "dark": ["#E06A64", "#5A6480", "#4FBF8B"],
}

THEME_TOKENS: dict[str, dict[str, Any]] = {
    "light": {
        "name": "light",
        "bg": "#F6F7FB",
        "surface": "#FFFFFF",
        "surface_alt": "#FAFBFD",
        "text": "#1B2437",
        "text_muted": "#5B6779",
        "border": "#E3E7EF",
        "grid": "#EAEDF4",
        "accent": "#5457D6",
        "accent_soft": "#EEEEFC",
        "shadow": "0 1px 3px rgba(16, 24, 40, 0.07), 0 1px 2px rgba(16, 24, 40, 0.04)",
        "hover_bg": "#F1F2F8",
        "type_colors": TYPE_COLORS["light"],
        "diverging": DIVERGING["light"],
        "cat_palette": CAT_PALETTE,
    },
    "dark": {
        "name": "dark",
        "bg": "#0F1420",
        "surface": "#171E2E",
        "surface_alt": "#1B2334",
        "text": "#E8ECF4",
        "text_muted": "#9AA6BC",
        "border": "#26304A",
        "grid": "#222C42",
        "accent": "#7C7FF0",
        "accent_soft": "#23294A",
        "shadow": "0 1px 3px rgba(0, 0, 0, 0.45), 0 1px 2px rgba(0, 0, 0, 0.35)",
        "hover_bg": "#1E2740",
        "type_colors": TYPE_COLORS["dark"],
        "diverging": DIVERGING["dark"],
        "cat_palette": CAT_PALETTE,
    },
}


def get_theme() -> dict[str, Any]:
    """Return the token dict for the active theme (session-state driven)."""
    import streamlit as st

    name = st.session_state.get("theme", "light")
    return THEME_TOKENS.get(name, THEME_TOKENS["light"])


# ------------------------------------------------------------- plotly base
def style_figure(fig, T: dict[str, Any], *, title: str | None = None,
                 subtitle: str | None = None, legend_title: str | None = None,
                 legend_horizontal: bool = True) -> None:
    """Apply the shared editorial layout contract to any figure."""
    import plotly.graph_objects as go  # noqa: F401  (kept for callers' typing ease)

    if title:
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", font=dict(size=14.5, color=T["text"]),
                       x=0.005, xanchor="left", pad_t=6),
        )
        if subtitle:
            fig.add_annotation(
                text=f'<span style="color:{T["text_muted"]}">{subtitle}</span>',
                xref="paper", yref="paper", x=0, y=1.045, xanchor="left",
                showarrow=False, font=dict(size=11.5),
            )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, size=12.5, color=T["text_muted"]),
        hoverlabel=dict(
            bgcolor=T["surface"], bordercolor=T["border"],
            font=dict(color=T["text"], family=FONT_STACK, size=12.5),
        ),
        margin=dict(l=8, r=18, t=52 if title else 14, b=8),
        showlegend=True,
    )
    if legend_title:
        fig.update_layout(legend_title=dict(text=legend_title,
                                           font=dict(size=11.5, color=T["text"])))
    if legend_horizontal:
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1.0,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11.5, color=T["text_muted"]),
            )
        )
    else:
        fig.update_layout(
            legend=dict(bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11.5, color=T["text_muted"]))
        )

    fig.update_xaxes(
        gridcolor=T["grid"], gridwidth=1, zeroline=False, showline=False,
        ticks="outside", ticklen=4, tickcolor=T["border"],
        tickfont=dict(color=T["text_muted"]),
    )
    fig.update_yaxes(
        gridcolor=T["grid"], gridwidth=1, zeroline=False, showline=False,
        ticks="outside", ticklen=4, tickcolor=T["border"],
        tickfont=dict(color=T["text_muted"]),
    )


def sequential_scale(T: dict[str, Any]) -> list[tuple[float, str]]:
    """Surface -> accent sequential scale for heatmaps (theme-aware)."""
    return [(0.0, T["surface"] if T["name"] == "light" else T["surface_alt"]),
            (1.0, T["accent"])]


def css_vars(T: dict[str, Any]) -> str:
    """CSS custom properties matching the active theme tokens."""
    return (
        ":root{"
        f"--bg:{T['bg']};"
        f"--surface:{T['surface']};"
        f"--surface-alt:{T['surface_alt']};"
        f"--text:{T['text']};"
        f"--text-muted:{T['text_muted']};"
        f"--border:{T['border']};"
        f"--grid:{T['grid']};"
        f"--accent:{T['accent']};"
        f"--accent-soft:{T['accent_soft']};"
        f"--shadow:{T['shadow']};"
        f"--hover-bg:{T['hover_bg']};"
        "}"
    )
