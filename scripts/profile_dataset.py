"""Phase 1A - Dataset profiling for the anime dataset.

Usage: python -I profile_dataset.py <path_to_data_dir>
Prints a structured profile of anime.csv and rating.csv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 50)


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main(data_dir: Path) -> None:
    # ------------------------------------------------------------------ anime
    section("1. anime.csv - STRUCTURE")
    anime = pd.read_csv(data_dir / "anime.csv")
    print(f"Shape: {anime.shape[0]} rows x {anime.shape[1]} cols")
    print("\nColumns & dtypes:")
    print(anime.dtypes)
    print("\nHead:")
    print(anime.head(8))

    section("2. anime.csv - MISSING VALUES")
    miss = anime.isna().sum()
    pct = (anime.isna().mean() * 100).round(2)
    print(pd.DataFrame({"missing": miss, "pct": pct}))

    section("3. anime.csv - DUPLICATES")
    print(f"Duplicate anime_id rows: {anime['anime_id'].duplicated().sum()}")
    print(f"Duplicate name rows:     {anime['name'].duplicated().sum()}")
    dup_names = anime[anime["name"].duplicated(keep=False)].sort_values("name")
    if len(dup_names):
        print("\nDuplicate name examples (up to 15):")
        print(dup_names.head(15).to_string())

    section("4. anime.csv - CATEGORICAL: type")
    print(anime["type"].value_counts(dropna=False))

    section("5. anime.csv - episodes FIELD")
    print("Non-numeric 'episodes' value counts:")
    ep_num = pd.to_numeric(anime["episodes"], errors="coerce")
    nonnum = anime.loc[ep_num.isna() & anime["episodes"].notna(), "episodes"]
    print(nonnum.value_counts())
    print(f"\nEpisodes NaN after coercion (incl. original NaN): {ep_num.isna().sum()}")
    print("\nEpisodes describe (numeric only):")
    print(ep_num.describe().round(2))
    print("\nTop episode counts:")
    print(ep_num.value_counts().head(10))

    section("6. anime.csv - rating (weighted score) FIELD")
    print(anime["rating"].describe().round(3))
    print(f"NaN: {anime['rating'].isna().sum()}  ({anime['rating'].isna().mean()*100:.2f}%)")
    print("\nPercentiles:", np.percentile(anime["rating"].dropna(), [1, 5, 25, 50, 75, 95, 99]).round(2))

    section("7. anime.csv - members FIELD")
    print(anime["members"].describe().round(1))
    print("Percentiles:", np.percentile(anime["members"], [1, 5, 25, 50, 75, 95, 99]).astype(np.int64))

    section("8. anime.csv - genre FIELD")
    print(f"NaN genres: {anime['genre'].isna().sum()}")
    n_genres = anime["genre"].dropna().str.split(",").apply(len)
    print("Genres-per-anime distribution:")
    print(n_genres.value_counts().sort_index())
    exploded = anime["genre"].dropna().str.split(",").explode().str.strip()
    print(f"\nDistinct genre tags: {exploded.nunique()}")
    print("\nTop 25 genre tags:")
    print(exploded.value_counts().head(25))
    print("\nRare genre tags (count <= 20):")
    vc = exploded.value_counts()
    print(vc[vc <= 20])

    section("9. anime.csv - name FIELD quirks")
    weird = anime[anime["name"].str.contains("&quot;|&amp;|&#039;", na=False)]
    print(f"Rows with HTML entities in name: {len(weird)}")
    print(weird[["anime_id", "name"]].head(10).to_string())

    # ----------------------------------------------------------------- rating
    section("10. rating.csv - STRUCTURE")
    rating = pd.read_csv(data_dir / "rating.csv")
    print(f"Shape: {rating.shape[0]} rows x {rating.shape[1]} cols")
    print("\nColumns & dtypes:")
    print(rating.dtypes)
    print(rating.head(5))

    section("11. rating.csv - MISSING / DUPLICATES")
    print(f"NaNs: {rating.isna().sum().sum()}")
    dup = rating.duplicated(subset=["user_id", "anime_id"]).sum()
    print(f"Duplicate (user_id, anime_id) pairs: {dup}")

    section("12. rating.csv - VALUES")
    print(f"Distinct users: {rating['user_id'].nunique()}")
    print(f"Distinct anime rated: {rating['anime_id'].nunique()}")
    print("\nRating value counts (-1 = watched, not scored):")
    print(rating["rating"].value_counts().sort_index())
    n_neg = (rating["rating"] == -1).sum()
    print(f"\n-1 share: {n_neg} ({n_neg/len(rating)*100:.1f}%)")
    expl = rating.loc[rating["rating"] > 0, "rating"]
    print("\nExplicit ratings describe:")
    print(expl.describe().round(3))
    print("\nRatings per user describe:")
    per_user = rating.groupby("user_id").size()
    print(per_user.describe().round(1))
    print("\nRatings per anime describe:")
    per_anime = rating.groupby("anime_id").size()
    print(per_anime.describe().round(1))

    section("13. CROSS-FILE COVERAGE")
    anime_ids = set(anime["anime_id"])
    rated_ids = set(rating["anime_id"])
    print(f"Anime in anime.csv:        {len(anime_ids)}")
    print(f"Anime present in ratings:  {len(rated_ids & anime_ids)}")
    print(f"Rated but not in anime.csv:{len(rated_ids - anime_ids)}")
    print(f"In anime.csv, no ratings:  {len(anime_ids - rated_ids)}")
    mean_user_rating = rating[rating["rating"] > 0].groupby("anime_id")["rating"].mean()
    print("\nMean explicit user rating per anime - describe:")
    print(mean_user_rating.describe().round(3))
    joined = anime.set_index("anime_id").join(mean_user_rating.rename("user_mean"))
    print("\nCorrelation between anime.csv 'rating' and mean explicit user rating:")
    print(joined[["rating", "user_mean"]].corr().round(3))
    print("\nCorrelation between 'rating' and 'members':")
    print(anime[["rating", "members"]].corr().round(3))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
