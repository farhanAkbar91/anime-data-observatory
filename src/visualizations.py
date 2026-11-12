"""Plotly chart builders (theme-aware, reusable).

Every function returns a plotly Figure styled by src.theme.style_figure.
Charts are transparent-backed so they sit on themed card surfaces.
"""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .theme import style_figure, sequential_scale

# ------------------------------------------------------------------ helpers

def _type_color_map(T: dict) -> dict[str, str]:
    return T["type_colors"]


def fmt_members_axis(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.0f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return f"{v:.0f}"


# ------------------------------------------------------------------- page 1
def donut_type(type_counts: pd.DataFrame, T: dict) -> go.Figure:
    """Part-to-whole of title counts by format. Click-to-filter wired in app."""
    cmap = _type_color_map(T)
    fig = px.pie(type_counts, names="type", values="titles", hole=0.58,
                 color="type", color_discrete_map=cmap,
                 category_orders={"type": type_counts["type"].tolist()})
    fig.update_traces(
        texttemplate="%{percent:.1%}", textposition="inside",
        insidetextorientation="horizontal",
        marker=dict(line=dict(color=T["surface"], width=2)),
        hovertemplate="<b>%{label}</b><br>%{value:,} titles (%{percent})<extra></extra>",
        sort=False,
    )
    fig.update_layout(
        uniformtext_minsize=10, uniformtext_mode="hide",
        showlegend=True,
        legend=dict(
            orientation="v", xanchor="left", x=1.02, yanchor="middle", y=0.5,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11.5, color=T["text_muted"]),
        ),
    )
    style_figure(fig, T, legend_horizontal=False,
                 title="Library composition by format",
                 subtitle="Share of titles per format")
    return fig


def hbar_topn(df: pd.DataFrame, x: str, y: str, T: dict, *, title: str,
              subtitle: str = "", color: str | None = None, xlabel: str = "",
              text_fmt: str = ",.0f", hover: list[str] | None = None,
              height: int | None = None) -> go.Figure:
    """Generic sorted horizontal bar (largest at top)."""
    fig = px.bar(df, x=x, y=y, color_discrete_sequence=[color or T["accent"]],
                 orientation="h")
    custom = hover or []
    if custom:
        ht = ("<b>%{y}</b><br>" + xlabel + ": %{x:,.0f}" +
              "".join(f"<br>{c}: %{{customdata[{i}]}}" for i, c in enumerate(custom)) +
              "<extra></extra>")
        customdata = df[custom].to_numpy()
    else:
        ht = "<b>%{y}</b><br>" + xlabel + ": %{x:,.0f}<extra></extra>"
        customdata = None
    fig.update_traces(
        texttemplate=f"%{{x:{text_fmt}}}", textposition="outside",
        cliponaxis=False, customdata=customdata, hovertemplate=ht,
    )
    fig.update_layout(xaxis_title=xlabel, yaxis_title=None)
    fig.update_yaxes(automargin=True)
    if height:
        fig.update_layout(height=height)
    style_figure(fig, T, title=title, subtitle=subtitle)
    return fig


def histogram_score(anime: pd.DataFrame, T: dict, *, bin_size: float = 0.25,
                    show_markers: bool = True) -> go.Figure:
    d = anime[anime["rating"].notna()]
    fig = px.histogram(d, x="rating", nbins=int((10 - 1.5) / bin_size),
                       color_discrete_sequence=[T["accent"]])
    fig.update_traces(hovertemplate="Score band: %{x}<br>Titles: %{y}<extra></extra>")
    fig.update_layout(xaxis_title="Official weighted score", yaxis_title="Titles")
    mean = med = None
    if show_markers and len(d):
        mean, med = d["rating"].mean(), d["rating"].median()
        for val, dash in ((mean, "dot"), (med, "dash")):
            fig.add_vline(x=val, line_dash=dash, line_color=T["text_muted"],
                          line_width=1.2)
    sub = "Titles per score band (bin = 0.25) · unscored titles excluded"
    if mean is not None:
        sub += f" · solid line mean {mean:.2f} · dashed line median {med:.2f}"
    style_figure(fig, T, title="Official score distribution", subtitle=sub)
    return fig


# ------------------------------------------------------------------- page 2
def scatter_score_members(anime: pd.DataFrame, T: dict) -> go.Figure:
    d = anime[anime["rating"].notna()].copy()
    d["episodes_label"] = d["episodes"].map(lambda v: "—" if pd.isna(v) else str(int(v)))
    cmap = _type_color_map(T)
    order = d["type"].value_counts().index.tolist()
    fig = px.scatter(d, x="members", y="rating", color="type",
                     color_discrete_map=cmap, category_orders={"type": order},
                     custom_data=["name", "episodes_label", "members", "n_ratings"],
                     opacity=0.62)
    fig.update_traces(
        marker=dict(size=6.5, line=dict(width=0.5, color=T["surface"])),
        hovertemplate=("<b>%{customdata[0]}</b><br>Type: %{fullData.name}<br>"
                       "Score: %{y:.2f}<br>Members: %{customdata[2]:,}<br>"
                       "Episodes: %{customdata[1]}<br>Community ratings: "
                       "%{customdata[3]:,.0f}<extra></extra>"),
    )
    fig.update_xaxes(type="log", title="Community members (log scale)",
                     tickvals=[100, 1000, 10000, 100000, 1000000],
                     ticktext=["100", "1K", "10K", "100K", "1M"])
    fig.update_yaxes(title="Official weighted score")
    style_figure(fig, T, title="Does popularity buy quality?",
                 subtitle="Official score vs members, per title (log x) · r = 0.39 linear, 0.65 log")
    return fig


def members_log_hist_chart(hist: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.bar(hist, x="bin_center", y="titles",
                 color_discrete_sequence=[T["accent"]])
    fig.update_traces(hovertemplate="≈ %{x:,.0f} members<br>Titles: %{y:,}<extra></extra>",
                      marker=dict(line=dict(color=T["surface"], width=0.5)))
    fig.update_xaxes(type="log", title="Members (log scale, binned)",
                     tickvals=[1, 10, 100, 1000, 10000, 100000, 1000000],
                     ticktext=["1", "10", "100", "1K", "10K", "100K", "1M"])
    fig.update_yaxes(title="Titles")
    style_figure(fig, T, title="How concentrated is attention?",
                 subtitle="Titles per members bin (log binned) · median title: 1.5K members")
    return fig


def box_members_by_type(anime: pd.DataFrame, T: dict) -> go.Figure:
    cmap = _type_color_map(T)
    order = anime["type"].value_counts().index.tolist()
    fig = px.box(anime, x="type", y="members", color="type",
                 color_discrete_map=cmap, category_orders={"type": order},
                 points="outliers", custom_data=["type"])
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Members (per title): %{y:,}<extra></extra>")
    fig.update_xaxes(title=None)
    fig.update_yaxes(type="log", title="Members per title (log scale)",
                     tickvals=[10, 100, 1000, 10000, 100000, 1000000],
                     ticktext=["10", "100", "1K", "10K", "100K", "1M"])
    fig.update_layout(showlegend=False)
    style_figure(fig, T, title="Members per title, by format",
                 subtitle="Box = quartiles · dots = outliers · log scale")
    return fig


def bar_tiers(tiers: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.bar(tiers, x="tier", y="watched_share",
                 color_discrete_sequence=[T["accent"]], custom_data=["titles", "tier_hint"])
    fig.update_traces(
        texttemplate="%{y:.0%}", textposition="outside", cliponaxis=False,
        hovertemplate=("<b>%{x}</b> (%{customdata[1]})<br>Watched-not-scored: %{y:.1%}"
                       "<br>Titles: %{customdata[0]:,}<extra></extra>"),
        marker=dict(line=dict(color=T["surface"], width=0.5)),
    )
    fig.update_layout(xaxis_title="Popularity tier (quartiles of members)",
                      yaxis_title="Watched-not-scored share", yaxis_tickformat=".0%")
    style_figure(fig, T, title="Do niche titles get scored?",
                 subtitle="Share of 'watched but not rated' events by popularity tier (within current view)")
    return fig


# ------------------------------------------------------------------- page 3
def box_score_by_type(anime: pd.DataFrame, T: dict) -> go.Figure:
    d = anime[anime["rating"].notna()]
    cmap = _type_color_map(T)
    order = d["type"].value_counts().index.tolist()
    fig = px.box(d, x="type", y="rating", color="type",
                 color_discrete_map=cmap, category_orders={"type": order},
                 points="outliers")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Official weighted score")
    fig.update_layout(showlegend=False)
    style_figure(fig, T, title="Score distribution by format",
                 subtitle="Box = quartiles · dots = outliers · unscored excluded")
    return fig


def hbar_genre_scores(gq: pd.DataFrame, T: dict) -> go.Figure:
    d = gq.sort_values("avg_score", ascending=True)
    fig = px.bar(d, x="avg_score", y="genre", orientation="h",
                 color_discrete_sequence=[T["accent"]],
                 custom_data=["titles", "median_members"])
    fig.update_traces(
        texttemplate="%{x:.2f}", textposition="outside", cliponaxis=False,
        hovertemplate=("<b>%{y}</b><br>Avg score: %{x:.2f}<br>Titles: %{customdata[0]:,}"
                       "<br>Median members: %{customdata[1]:,.0f}<extra></extra>"),
    )
    fig.update_xaxes(title="Average official score", range=[max(1, d["avg_score"].min() - 0.4)
                                                            if len(d) else 1, None])
    fig.update_yaxes(title=None, automargin=True)
    style_figure(fig, T, title="Which genres deliver quality?",
                 subtitle="Average official score per genre tag · filtered by minimum title count")
    return fig


def scatter_official_community(d: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.scatter(d, x="rating", y="community_mean", color="gap",
                     color_continuous_scale=T["diverging"],
                     color_continuous_midpoint=0,
                     custom_data=["name", "type", "n_explicit", "gap"],
                     opacity=0.7)
    lims = [min(d["rating"].min(), d["community_mean"].min()) - 0.3,
            max(d["rating"].max(), d["community_mean"].max()) + 0.3]
    fig.add_trace(go.Scatter(x=lims, y=lims, mode="lines", showlegend=False,
                             line=dict(color=T["text_muted"], width=1.2, dash="dash"),
                             hoverinfo="skip", name="y = x"))
    fig.update_traces(selector=0,
                      marker=dict(size=7, line=dict(width=0.5, color=T["surface"])),
                      hovertemplate=("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                                     "Official: %{x:.2f}<br>Community: %{y:.2f}"
                                     "<br>Gap: %{customdata[3]:+.2f}<br>"
                                     "Explicit ratings: %{customdata[2]:,}<extra></extra>"))
    fig.update_coloraxes(colorbar=dict(title="Gap", thickness=12, len=0.85,
                                       tickfont=dict(size=10.5, color=T["text_muted"])))
    fig.update_xaxes(title="Official weighted score")
    fig.update_yaxes(title="Community mean (explicit ratings)")
    style_figure(fig, T, title="Official score vs raw community sentiment",
                 subtitle="Above the diagonal = community rates higher than official · below = stricter")
    return fig


def hbar_gap(d: pd.DataFrame, T: dict, n: int = 10) -> go.Figure:
    dd = pd.concat([d.nlargest(n, "gap").assign(kind="Community rates higher"),
                    d.nsmallest(n, "gap").assign(kind="Community rates lower")])
    dd = dd.sort_values("gap")
    colors = dd["gap"].map(lambda v: T["diverging"][2] if v >= 0 else T["diverging"][0])
    fig = go.Figure(go.Bar(
        x=dd["gap"], y=dd["name"], orientation="h",
        marker_color=colors.tolist(),
        customdata=dd[["rating", "community_mean", "kind"]].to_numpy(),
        hovertemplate=("<b>%{y}</b><br>Gap: %{x:+.2f}<br>Official: %{customdata[0]:.2f}"
                       "<br>Community: %{customdata[1]:.2f}<br>%{customdata[2]}<extra></extra>"),
    ))
    fig.update_xaxes(title="Community mean − official score")
    fig.update_yaxes(title=None, automargin=True, visible=False)
    fig.update_layout(showlegend=False)
    style_figure(fig, T, title="Largest score gaps, both directions",
                 subtitle="Titles whose community sentiment diverges most from the official score")
    return fig


# ------------------------------------------------------------------- page 4
def bubble_genres(gq: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.scatter(gq, x="titles", y="avg_score", size="median_members",
                     color_discrete_sequence=[T["accent"]], opacity=0.75,
                     custom_data=["genre", "median_members", "median_score"])
    sizeref = (2.0 * gq["median_members"].max() / (34 ** 2)) if len(gq) else 1.0
    fig.update_traces(
        marker=dict(line=dict(width=1, color=T["surface"]),
                    sizeref=sizeref, sizemode="area"),
        hovertemplate=("<b>%{customdata[0]}</b><br>Titles: %{x:,}<br>"
                       "Avg score: %{y:.2f}<br>Median score: %{customdata[2]:.2f}"
                       "<br>Median members: %{customdata[1]:,.0f}<extra></extra>"),
        mode="markers+text",
        text=gq["genre"] if len(gq) else [],
        textposition="top center",
        textfont=dict(size=10, color=T["text_muted"]),
    )
    if len(gq):
        fig.add_hline(y=float(gq["avg_score"].mean()), line_dash="dot",
                      line_color=T["text_muted"], line_width=1.2,
                      annotation_text=f"all-genre avg {gq['avg_score'].mean():.2f}",
                      annotation_font=dict(size=10.5, color=T["text_muted"]))
    fig.update_xaxes(title="Titles tagged (volume)", type="log", dtick="D1")
    fig.update_yaxes(title="Average official score")
    style_figure(fig, T, title="Volume vs quality per genre",
                 subtitle="Bubble size = median members · x log scale · tags with min title count")
    return fig


def heatmap_genre_type(mat: pd.DataFrame, T: dict) -> go.Figure:
    z = mat.values
    fig = go.Figure(go.Heatmap(
        z=z, x=mat.columns.tolist(), y=mat.index.tolist(),
        colorscale=sequential_scale(T), showscale=True,
        colorbar=dict(title="Titles", thickness=12, len=0.9,
                      tickfont=dict(size=10.5, color=T["text_muted"])),
        xgap=1, ygap=1,
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>%{z:,} titles<extra></extra>",
    ))
    fig.update_xaxes(title=None, side="top")
    fig.update_yaxes(title=None, automargin=True, autorange="reversed")
    style_figure(fig, T, title="Where does each genre live?",
                 subtitle=f"Titles per genre × format · top {len(mat.index)} genres by volume")
    return fig


def hbar_pairs(pairs: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.bar(pairs, x="titles", y="pair", orientation="h",
                 color_discrete_sequence=[T["accent"]])
    fig.update_traces(texttemplate="%{x:,}", textposition="outside", cliponaxis=False,
                      hovertemplate="<b>%{y}</b><br>%{x:,} titles share both tags<extra></extra>")
    fig.update_xaxes(title="Titles carrying both tags")
    fig.update_yaxes(title=None, automargin=True)
    style_figure(fig, T, title="Most common genre combinations",
                 subtitle="Co-occurrence counts of tag pairs (a title counts in every pair it carries)")
    return fig


# ------------------------------------------------------------------- page 5
def histogram_episodes(hist: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.bar(hist, x="ep_value", y="titles", color_discrete_sequence=[T["accent"]])
    fig.update_traces(hovertemplate="≈ %{x:,.0f} episodes<br>Titles: %{y:,}<extra></extra>",
                      marker=dict(line=dict(color=T["surface"], width=0.5)))
    fig.update_xaxes(type="log", title="Episodes per title (log scale, binned)",
                     tickvals=[1, 2, 5, 10, 25, 50, 100, 200],
                     ticktext=["1", "2", "5", "10", "25", "50", "100", "200"])
    fig.update_yaxes(title="Titles")
    style_figure(fig, T, title="How long are titles, really?",
                 subtitle="Log-binned episode counts · 47.5% of titles are single-episode")
    return fig


def box_episodes_by_type(anime: pd.DataFrame, T: dict) -> go.Figure:
    d = anime[anime["episodes"].notna()].copy()
    d["episodes"] = d["episodes"].astype(int)
    cmap = _type_color_map(T)
    order = anime["type"].value_counts().index.tolist()
    fig = px.box(d, x="type", y="episodes", color="type",
                 color_discrete_map=cmap, category_orders={"type": order},
                 points="outliers")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Episodes: %{y:,}<extra></extra>")
    fig.update_xaxes(title=None)
    fig.update_yaxes(type="log", title="Episodes per title (log scale)",
                     tickvals=[1, 2, 6, 12, 26, 52, 100, 500, 2000],
                     ticktext=["1", "2", "6", "12", "26", "52", "100", "500", "2K"])
    fig.update_layout(showlegend=False)
    style_figure(fig, T, title="Length by format",
                 subtitle="Box = quartiles · dots = outliers · log scale")
    return fig


def bar_episode_buckets(buckets: pd.DataFrame, T: dict, metric: str = "avg_score") -> go.Figure:
    if metric == "avg_score":
        y, ytitle, fmt = "avg_score", "Average official score", ".2f"
        hover_t = ("Score: %{y:.2f}<br>Titles: %{customdata[0]:,}"
                   "<br>Median members: %{customdata[1]:,.0f}")
        color = T["accent"]
    else:
        y, ytitle, fmt = "median_members", "Median members per title", ",.0f"
        hover_t = ("Median members: %{y:,.0f}<br>Titles: %{customdata[0]:,}"
                   "<br>Avg score: %{customdata[2]:.2f}")
        color = T["type_colors"]["Movie"]
    fig = px.bar(buckets, x="bucket", y=y, color_discrete_sequence=[color],
                 custom_data=["titles", "median_members", "avg_score"])
    fig.update_traces(
        texttemplate=f"%{{y:{fmt}}}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x} episodes</b><br>" + hover_t + "<extra></extra>",
        marker=dict(line=dict(color=T["surface"], width=0.5)),
    )
    fig.update_xaxes(title="Episode-count bucket")
    fig.update_yaxes(title=ytitle)
    style_figure(fig, T, title="Does length buy quality or reach?",
                 subtitle="Episode buckets in current view · metric selectable")
    return fig


# ------------------------------------------------------------------- page 6
def bar_rating_values(dist: pd.DataFrame, T: dict) -> go.Figure:
    dist = dist.copy()
    dist["share"] = dist["count"] / dist["count"].sum() if dist["count"].sum() else 0
    fig = px.bar(dist, x="score", y="share", color_discrete_sequence=[T["accent"]],
                 custom_data=["count"])
    fig.update_traces(
        texttemplate="%{y:.1%}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}-star</b><br>%{customdata[0]:,} ratings (%{y:.1%})<extra></extra>",
        marker=dict(line=dict(color=T["surface"], width=0.5)),
    )
    fig.update_xaxes(title="Explicit rating (1–10)", tickmode="linear", tick0=1, dtick=1)
    fig.update_yaxes(title="Share of explicit ratings", tickformat=".0%")
    style_figure(fig, T, title="How the community actually rates",
                 subtitle="Distribution of explicit user ratings in the current view")
    return fig


def hist_user_activity(hist: pd.DataFrame, T: dict) -> go.Figure:
    fig = px.bar(hist, x="n_center", y="users", color_discrete_sequence=[T["accent"]])
    fig.update_traces(hovertemplate="≈ %{x:,.0f} interactions<br>Users: %{y:,}<extra></extra>",
                      marker=dict(line=dict(color=T["surface"], width=0.5)))
    fig.update_xaxes(type="log", title="Interactions per user (log scale, binned)",
                     tickvals=[1, 10, 100, 1000, 10000],
                     ticktext=["1", "10", "100", "1K", "10K"])
    fig.update_yaxes(title="Users")
    style_figure(fig, T, title="Who powers the community?",
                 subtitle="Users per interaction-count bin (log binned) · median user: 57")
    return fig
