"""Data cleaning pipeline (runtime-safe reproduction of scripts/clean_dataset.py).

Rebuilds the processed parquet tables from the raw CSVs when they are missing,
so the app is runnable end-to-end from the raw data alone.
"""
from __future__ import annotations

import html
from pathlib import Path

import pandas as pd


def clean_anime(anime: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (anime_clean, genres_long). Rules documented in documentation/data_cleaning_report.md."""
    anime = anime.copy()

    # 1. HTML entities in names (display correctness only)
    anime["name"] = anime["name"].map(lambda s: html.unescape(s) if isinstance(s, str) else s)

    # 2. episodes 'Unknown' -> NaN, nullable integer
    anime["episodes"] = pd.to_numeric(anime["episodes"], errors="coerce").astype("Int64")

    # 3./4. transparent 'Unknown' categories instead of silent nulls
    anime["type"] = anime["type"].fillna("Unknown")
    anime["genre"] = anime["genre"].fillna("Unknown")

    # 5. normalized (anime_id, genre) long table
    genres = (
        anime.assign(genre=anime["genre"].str.split(","))
        .explode("genre")
        .assign(genre=lambda d: d["genre"].str.strip())
        .loc[:, ["anime_id", "genre"]]
        .reset_index(drop=True)
    )

    # 6. rating NaN kept as NaN - excluded from score metrics, never imputed
    return anime.reset_index(drop=True), genres


def clean_ratings(ratings: pd.DataFrame, anime: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate and drop un-joinable facts; keep the -1 sentinel intact."""
    ratings = ratings.drop_duplicates(subset=["user_id", "anime_id"], keep="first")
    return ratings[ratings["anime_id"].isin(set(anime["anime_id"]))].reset_index(drop=True)


def build_processed(raw_dir: Path, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Full pipeline: raw CSVs -> processed parquet files. Returns the three tables."""
    out_dir.mkdir(parents=True, exist_ok=True)
    anime = pd.read_csv(raw_dir / "anime.csv")
    ratings = pd.read_csv(raw_dir / "rating.csv")

    anime_clean, genres = clean_anime(anime)
    ratings_clean = clean_ratings(ratings, anime_clean)

    anime_clean.to_parquet(out_dir / "anime_clean.parquet", index=False)
    genres.to_parquet(out_dir / "anime_genres.parquet", index=False)
    ratings_clean.to_parquet(out_dir / "ratings_clean.parquet", index=False)
    return anime_clean, genres, ratings_clean
