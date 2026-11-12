"""Cached data access for the dashboard.

Loads the processed parquet tables once per session and builds the derived
aggregate tables (per-anime community stats, per-user stats) once per session.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROC_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data(show_spinner="Loading anime metadata…")
def load_anime() -> pd.DataFrame:
    _ensure_processed()
    return pd.read_parquet(PROC_DIR / "anime_clean.parquet")


@st.cache_data(show_spinner=False)
def load_genres() -> pd.DataFrame:
    _ensure_processed()
    return pd.read_parquet(PROC_DIR / "anime_genres.parquet")


@st.cache_data(show_spinner="Loading community rating log…")
def load_ratings() -> pd.DataFrame:
    _ensure_processed()
    return pd.read_parquet(PROC_DIR / "ratings_clean.parquet")


def _ensure_processed() -> None:
    """Rebuild processed tables from raw CSVs if they are missing."""
    needed = ["anime_clean.parquet", "anime_genres.parquet", "ratings_clean.parquet"]
    if all((PROC_DIR / f).exists() for f in needed):
        return
    if not (RAW_DIR / "anime.csv").exists() or not (RAW_DIR / "rating.csv").exists():
        raise FileNotFoundError(
            "Neither processed tables (data/processed/) nor raw files "
            "(data/raw/anime.csv, data/raw/rating.csv) were found."
        )
    from .data_cleaning import build_processed

    build_processed(RAW_DIR, PROC_DIR)


@st.cache_data(show_spinner="Aggregating community statistics per title…")
def build_anime_community(anime: pd.DataFrame) -> pd.DataFrame:
    """Per-anime community aggregates joined onto the metadata.

    Columns added: n_ratings, n_explicit, n_watched, community_mean, watched_share.
    Titles without any community data get NaN aggregates.
    """
    ratings = load_ratings()
    pos = ratings["rating"] > 0
    neg = ratings["rating"] == -1

    n_ratings = ratings.groupby("anime_id").size().rename("n_ratings").astype("int64")
    n_explicit = ratings.loc[pos].groupby("anime_id").size().rename("n_explicit").astype("int64")
    n_watched = ratings.loc[neg].groupby("anime_id").size().rename("n_watched").astype("int64")
    community_mean = (ratings.loc[pos].groupby("anime_id")["rating"].mean()
                      .rename("community_mean"))

    agg = pd.concat([n_ratings, n_explicit, n_watched, community_mean], axis=1)
    agg["watched_share"] = agg["n_watched"] / agg["n_ratings"]

    out = anime.merge(agg.reset_index(), on="anime_id", how="left")
    return out


@st.cache_data(show_spinner="Aggregating user behavior…")
def build_user_stats() -> pd.DataFrame:
    """Per-user aggregates: activity size and explicit-score behavior."""
    ratings = load_ratings()
    pos = ratings["rating"] > 0

    n_ratings = ratings.groupby("user_id").size().rename("n_ratings").astype("int64")
    n_explicit = ratings.loc[pos].groupby("user_id").size().rename("n_explicit").astype("int64")
    mean_explicit = (ratings.loc[pos].groupby("user_id")["rating"].mean()
                     .rename("mean_explicit"))

    per_user = pd.concat([n_ratings, n_explicit, mean_explicit], axis=1)
    return per_user.reset_index()


@st.cache_data(show_spinner=False, max_entries=16)
def count_users_for(anime_ids: tuple[int, ...]) -> int:
    """Distinct users who interacted with the given set of titles (filtered KPI)."""
    if len(anime_ids) == 0:
        return 0
    ratings = load_ratings()
    return int(ratings.loc[ratings["anime_id"].isin(anime_ids), "user_id"].nunique())


@st.cache_data(show_spinner=False, max_entries=8)
def user_stats_for(anime_ids: tuple[int, ...], _user_stats: pd.DataFrame) -> pd.DataFrame:
    """Per-user stats restricted to a filtered subset of titles.

    Recomputes activity/behavior from the raw log for the given anime ids so the
    Community page responds to global filters. Falls back to the cached global
    table when all titles are selected.
    """
    if len(anime_ids) == 0:
        return _user_stats.iloc[0:0]
    ratings = load_ratings()
    sub = ratings[ratings["anime_id"].isin(set(anime_ids))]
    pos = sub["rating"] > 0
    per_user = pd.concat([
        sub.groupby("user_id").size().rename("n_ratings").astype("int64"),
        sub.loc[pos].groupby("user_id").size().rename("n_explicit").astype("int64"),
        sub.loc[pos].groupby("user_id")["rating"].mean().rename("mean_explicit"),
    ], axis=1)
    return per_user.reset_index()
