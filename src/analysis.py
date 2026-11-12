"""Analytical aggregations used by the dashboard pages.

Every function is vectorized pandas over the (filtered) frames and returns
chart-ready DataFrames. Nothing is hardcoded: numbers always come from the
current filtered data.
"""
from __future__ import annotations

from itertools import combinations
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st

EPISODE_BINS = [0, 1, 6, 12, 26, 52, 100, 10_000]
EPISODE_LABELS = ["1 ep", "2–6", "7–12", "13–26", "27–52", "53–100", ">100"]

SCORE_BANDS = [0, 4, 5, 6, 7, 8, 9, 10]
SCORE_BAND_LABELS = ["<4", "4–5", "5–6", "6–7", "7–8", "8–9", "9–10"]


# ------------------------------------------------------------------ overview
def type_distribution(anime: pd.DataFrame) -> pd.DataFrame:
    t = anime["type"].value_counts().reset_index()
    t.columns = ["type", "titles"]
    return t


def top_genres(anime: pd.DataFrame, genres: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """Genres ranked by title count within the filtered set (titles carry every
    tag they have, so a title can appear under several genres)."""
    sub = genres[genres["anime_id"].isin(set(anime["anime_id"]))]
    g = sub.groupby("genre").agg(titles=("anime_id", "size")).reset_index()
    g["titles"] = g["titles"].astype(int)
    return g.nlargest(top_n, "titles").sort_values("titles", ascending=True)


def score_bands(anime: pd.DataFrame) -> pd.DataFrame:
    scored = anime[anime["rating"].notna()]
    b = pd.cut(scored["rating"], bins=SCORE_BANDS, labels=SCORE_BAND_LABELS)
    out = b.value_counts().reindex(SCORE_BAND_LABELS).fillna(0).astype(int)
    return out.rename_axis("band").reset_index(name="titles")


# ------------------------------------------------------------- popularity
def top_by_column(anime: pd.DataFrame, column: str, n: int = 15) -> pd.DataFrame:
    cols = ["name", "type", "episodes", "rating", "members"]
    extra = [c for c in ["n_ratings", "community_mean"] if c in anime.columns]
    cols += extra
    top = anime.nlargest(n, column)[cols]
    return top.sort_values(column, ascending=True)


def members_log_hist(anime: pd.DataFrame) -> pd.DataFrame:
    """Pre-binned log10(members) histogram so bins stay honest on a log axis."""
    m = anime["members"].clip(lower=1)
    bins = np.logspace(0, np.log10(m.max() + 1), 36)
    labels = np.arange(len(bins) - 1)
    idx = np.digitize(m.to_numpy(), bins) - 1
    idx = np.clip(idx, 0, len(labels) - 1)
    out = (pd.DataFrame({"bin": idx})
           .groupby("bin").size().reindex(labels, fill_value=0)
           .rename_axis("bin").reset_index(name="titles"))
    out["bin_center"] = np.sqrt(bins[:-1] * bins[1:])[out["bin"]]
    return out


def watched_share_by_tier(anime: pd.DataFrame, n_tiers: int = 4) -> pd.DataFrame:
    """Watched-not-scored share across popularity tiers computed *within the
    filtered set* (quartiles of members)."""
    df = anime[anime["n_ratings"].notna()].copy()
    if len(df) < n_tiers * 3:
        return pd.DataFrame(columns=["tier", "watched_share", "titles"])
    try:
        df["tier"] = pd.qcut(df["members"], q=n_tiers, duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["tier", "watched_share", "titles"])
    tiers = df["tier"].unique()
    tier_labels = {t: f"Tier {i + 1}" for i, t in
                   enumerate(sorted(tiers, key=lambda t: t.left))}
    g = df.groupby("tier").agg(
        watched_share=("watched_share", "mean"),
        titles=("anime_id", "size"),
        members=("members", "min"),
    ).reset_index()
    g["tier"] = g["tier"].map(tier_labels)
    g["tier_hint"] = g["members"].map(lambda m: f"members ≥ {int(m):,}")
    return g.sort_values("tier")


# ------------------------------------------------------------------ ratings
def score_by_type_long(anime: pd.DataFrame) -> pd.DataFrame:
    """Long-form (type, rating) for box plots; unscored titles excluded."""
    d = anime[anime["rating"].notna()][["type", "rating"]]
    return d.rename(columns={"rating": "score"})


def genre_quality(anime: pd.DataFrame, genres: pd.DataFrame, min_titles: int = 50) -> pd.DataFrame:
    """Avg/median official score and median members per genre tag."""
    sub = genres[genres["anime_id"].isin(set(anime["anime_id"]))]
    m = sub.merge(anime[["anime_id", "rating", "members"]], on="anime_id")
    g = m.groupby("genre").agg(
        titles=("anime_id", "size"),
        avg_score=("rating", "mean"),
        median_score=("rating", "median"),
        median_members=("members", "median"),
    ).reset_index()
    g = g[g["titles"] >= min_titles]
    return g.sort_values("avg_score", ascending=False)


def official_vs_community(anime: pd.DataFrame, min_explicit: int = 100) -> pd.DataFrame:
    d = anime[anime["n_explicit"].notna() & (anime["n_explicit"] >= min_explicit) &
              anime["rating"].notna() & anime["community_mean"].notna()].copy()
    d["gap"] = d["community_mean"] - d["rating"]
    return d


# ------------------------------------------------------------------- genres
def genre_type_matrix(anime: pd.DataFrame, genres: pd.DataFrame,
                      top_n: int = 20) -> pd.DataFrame:
    """(genre × type) title-count matrix for the heatmap."""
    sub = genres[genres["anime_id"].isin(set(anime["anime_id"]))]
    m = sub.merge(anime[["anime_id", "type"]], on="anime_id")
    top = sub.groupby("genre").size().nlargest(top_n).index
    m = m[m["genre"].isin(top)]
    mat = m.pivot_table(index="genre", columns="type", values="anime_id",
                        aggfunc="size", fill_value=0)
    type_order = (m["type"].value_counts().index.tolist())
    mat = mat.reindex(columns=type_order)
    genre_order = mat.sum(axis=1).sort_values(ascending=False).index
    return mat.reindex(genre_order)


def genre_pairs(genres: pd.DataFrame, anime_ids, top_n: int = 15) -> pd.DataFrame:
    """Top co-occurring genre pairs within the current (filtered) view.
    Recomputed per rerun via sort + np.split (no groupby.apply) — fast and
    filter-correct."""
    sub = genres[genres["anime_id"].isin(set(anime_ids)) & (genres["genre"] != "Unknown")]
    sub = sub.sort_values("anime_id", kind="mergesort")
    names = sub["genre"].to_numpy()
    ids_arr = sub["anime_id"].to_numpy()
    boundaries = np.flatnonzero(np.diff(ids_arr)) + 1
    groups = np.split(names, boundaries) if len(names) else []

    pairs: Counter = Counter()
    for tags in groups:
        uniq = sorted(set(tags))
        for a, b in combinations(uniq, 2):
            pairs[(a, b)] += 1

    if not pairs:
        return pd.DataFrame(columns=["pair", "titles"])
    rows = [{"pair": f"{a}  +  {b}", "titles": c} for (a, b), c in pairs.most_common(top_n)]
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- episodes
def episodes_hist(anime: pd.DataFrame) -> pd.DataFrame:
    ep = anime[anime["episodes"].notna()]
    eps = ep["episodes"].astype(int).clip(upper=200)
    bins = np.logspace(0, np.log10(200 + 1), 30)
    idx = np.digitize(eps.to_numpy(), bins) - 1
    labels = np.arange(len(bins) - 1)
    out = (pd.DataFrame({"bin": idx}).groupby("bin").size()
           .reindex(labels, fill_value=0).rename_axis("bin").reset_index(name="titles"))
    out["ep_value"] = np.sqrt(bins[:-1] * bins[1:])[out["bin"]]
    return out


def episode_buckets(anime: pd.DataFrame) -> pd.DataFrame:
    ep = anime[anime["episodes"].notna()].copy()
    ep["bucket"] = pd.cut(ep["episodes"].astype(int), bins=EPISODE_BINS,
                          labels=EPISODE_LABELS)
    g = ep.groupby("bucket", observed=True).agg(
        titles=("anime_id", "size"),
        avg_score=("rating", "mean"),
        median_members=("members", "median"),
        scored=("rating", "count"),
    ).reset_index()
    return g


def longest_titles(anime: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    ep = anime[anime["episodes"].notna()]
    return ep.nlargest(n, "episodes")[["name", "type", "episodes", "rating", "members"]]


# ---------------------------------------------------------------- community
def explicit_rating_distribution(ratings: pd.DataFrame,
                                 anime_ids: tuple[int, ...]) -> pd.DataFrame:
    """Distribution of explicit 1-10 ratings for the given (filtered) titles."""
    sub = ratings[ratings["anime_id"].isin(set(anime_ids))]
    vc = sub.loc[sub["rating"] > 0, "rating"].value_counts()
    out = pd.DataFrame({
        "score": list(range(1, 11)),
        "count": [int(vc.get(v, 0)) for v in range(1, 11)],
    })
    return out


def ratings_per_user_hist(user_stats: pd.DataFrame) -> pd.DataFrame:
    n = user_stats["n_ratings"].clip(lower=1)
    bins = np.logspace(0, np.log10(n.max() + 1), 30)
    idx = np.digitize(n.to_numpy(), bins) - 1
    labels = np.arange(len(bins) - 1)
    out = (pd.DataFrame({"bin": idx}).groupby("bin").size()
           .reindex(labels, fill_value=0).rename_axis("bin").reset_index(name="users"))
    out["n_center"] = np.sqrt(bins[:-1] * bins[1:])[out["bin"]]
    return out
