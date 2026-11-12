"""Phase 1B - Data cleaning pipeline.

Usage: python -I clean_dataset.py <raw_data_dir> <processed_out_dir>
Reads raw anime.csv / rating.csv, applies documented cleaning rules and
writes processed parquet tables + a cleaning summary to stdout.
"""
import html
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main(raw_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    anime = pd.read_csv(raw_dir / "anime.csv")
    rating = pd.read_csv(raw_dir / "rating.csv")

    print("=== CLEANING SUMMARY: anime.csv ===")
    n0 = len(anime)

    # 1. HTML entities in names (e.g. Gintama&#039; -> Gintama')
    mask_ent = anime["name"].str.contains("&", na=False)
    anime["name"] = anime["name"].map(lambda s: html.unescape(s) if isinstance(s, str) else s)
    print(f"1. Names cleaned of HTML entities: {mask_ent.sum()} rows")

    # 2. episodes: 'Unknown' -> NaN, cast to nullable Int64
    unknown_eps = (anime["episodes"] == "Unknown").sum()
    anime["episodes"] = pd.to_numeric(anime["episodes"], errors="coerce").astype("Int64")
    print(f"2. episodes 'Unknown' -> NaN: {unknown_eps} rows; dtype -> Int64")

    # 3. type: NaN -> 'Unknown' (kept transparent, not dropped)
    n_type = anime["type"].isna().sum()
    anime["type"] = anime["type"].fillna("Unknown")
    print(f"3. type NaN -> 'Unknown': {n_type} rows")

    # 4. genre: NaN -> 'Unknown'; split into normalized long table
    n_genre = anime["genre"].isna().sum()
    anime["genre"] = anime["genre"].fillna("Unknown")
    print(f"4. genre NaN -> 'Unknown': {n_genre} rows")
    genres = (
        anime.assign(genre=anime["genre"].str.split(","))
        .explode("genre")
        .assign(genre=lambda d: d["genre"].str.strip())
        .loc[:, ["anime_id", "genre"]]
        .reset_index(drop=True)
    )
    print(f"   Normalized genre table: {len(genres)} (anime_id, genre) rows, "
          f"{genres['genre'].nunique()} distinct tags")

    # 5. rating: keep NaN (230) - excluded from score metrics, not imputed
    print(f"5. rating NaN kept as NaN: {anime['rating'].isna().sum()} rows "
          f"({anime['rating'].isna().mean()*100:.2f}%) - excluded from score metrics, never imputed")

    # sanity: no duplicate ids, no rows dropped
    assert anime["anime_id"].duplicated().sum() == 0
    assert len(anime) == n0
    print(f"6. Rows dropped from anime.csv: 0 (all {n0} kept)")

    anime = anime.reset_index(drop=True)
    anime.to_parquet(out_dir / "anime_clean.parquet", index=False)
    genres.to_parquet(out_dir / "anime_genres.parquet", index=False)

    print("\n=== CLEANING SUMMARY: rating.csv ===")
    n0 = len(rating)
    dup = rating.duplicated(subset=["user_id", "anime_id"]).sum()
    rating = rating.drop_duplicates(subset=["user_id", "anime_id"], keep="first")
    print(f"1. Duplicate (user_id, anime_id) pairs dropped: {dup}")

    known_ids = set(anime["anime_id"])
    orphan = (~rating["anime_id"].isin(known_ids)).sum()
    rating = rating[rating["anime_id"].isin(known_ids)]
    print(f"2. Ratings for anime_ids absent from anime.csv dropped: {orphan}")

    print(f"3. Total rows dropped from rating.csv: {n0 - len(rating)} of {n0} "
          f"({(n0 - len(rating))/n0*100:.4f}%)")
    print(f"   Kept: {len(rating)} rows | -1 (watched-not-scored): "
          f"{(rating['rating'] == -1).sum()} | explicit: {(rating['rating'] > 0).sum()}")

    rating.to_parquet(out_dir / "ratings_clean.parquet", index=False)

    print("\n=== OUTPUT FILES ===")
    for f in sorted(out_dir.glob("*.parquet")):
        print(f"  {f.name}: {f.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
