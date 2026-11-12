"""Phase 1C - EDA on the cleaned tables.

Usage: python -I eda.py <processed_dir>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 100)


def section(t: str) -> None:
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def main(proc: Path) -> None:
    anime = pd.read_parquet(proc / "anime_clean.parquet")
    genres = pd.read_parquet(proc / "anime_genres.parquet")
    ratings = pd.read_parquet(proc / "ratings_clean.parquet")

    # ---------------------------------------------------------------- overview
    section("A. OVERVIEW")
    scored = anime["rating"].notna()
    print(f"Titles: {len(anime)} | scored: {scored.sum()} ({scored.mean()*100:.1f}%)")
    print(f"Score mean/median: {anime['rating'].mean():.2f} / {anime['rating'].median():.2f}")
    print(f"Total members: {anime['members'].sum():,} | median members: {anime['members'].median():,.0f}")
    print(f"Community rating rows: {len(ratings):,} | explicit: {(ratings['rating']>0).sum():,} "
          f"| watched-only (-1): {(ratings['rating']==-1).sum():,} ({(ratings['rating']==-1).mean()*100:.1f}%)")
    print(f"Users: {ratings['user_id'].nunique():,}")

    # ------------------------------------------------------------------- types
    section("B. TYPE ANALYSIS")
    by_type = anime.groupby("type").agg(
        titles=("anime_id", "size"),
        avg_score=("rating", "mean"),
        median_score=("rating", "median"),
        avg_members=("members", "median"),
        total_members=("members", "sum"),
        median_episodes=("episodes", "median"),
    ).round(2).sort_values("titles", ascending=False)
    print(by_type)

    # ------------------------------------------------------------------ genres
    section("C. GENRE ANALYSIS")
    gcount = genres["genre"].value_counts()
    print("Genre frequency (all 44):")
    print(gcount.to_string())
    gstats = genres.merge(anime[["anime_id", "rating", "members", "type"]], on="anime_id")
    gs = gstats.groupby("genre").agg(
        titles=("anime_id", "size"),
        avg_score=("rating", "mean"),
        median_score=("rating", "median"),
        median_members=("members", "median"),
    ).round(3)
    gs = gs[gs["titles"] >= 50].sort_values("avg_score", ascending=False)
    print("\nAvg score by genre (titles >= 50), sorted by avg_score:")
    print(gs.to_string())
    # co-occurrence top pairs
    from itertools import combinations
    from collections import Counter
    tag_sets = genres[genres["genre"] != "Unknown"].groupby("anime_id")["genre"].apply(set)
    pairs = Counter()
    for s in tag_sets:
        for a, b in combinations(sorted(s), 2):
            pairs[(a, b)] += 1
    print("\nTop 20 genre pairs (co-occurrence):")
    for (a, b), c in pairs.most_common(20):
        print(f"  {a} + {b}: {c}")

    # --------------------------------------------------------------- popularity
    section("D. POPULARITY & ENGAGEMENT")
    print("Top 15 by members:")
    print(anime.nlargest(15, "members")[["name", "type", "rating", "members"]].to_string(index=False))
    cnt = ratings.groupby("anime_id").agg(
        n_ratings=("rating", "size"),
        n_explicit=("rating", lambda s: (s > 0).sum()),
        n_watched=("rating", lambda s: (s == -1).sum()),
        community_mean=("rating", lambda s: s[s > 0].mean()),
    )
    cnt["watched_share"] = cnt["n_watched"] / cnt["n_ratings"]
    top_cnt = cnt.join(anime.set_index("anime_id")[["name", "type", "members", "rating"]]).nlargest(15, "n_ratings")
    print("\nTop 15 by community rating count:")
    print(top_cnt[["name", "type", "n_ratings", "community_mean", "rating", "members"]].round(2).to_string())
    c1 = anime[["rating", "members"]].corr().iloc[0, 1]
    log_c = anime.assign(logm=np.log10(anime["members"] + 1))[["rating", "logm"]].corr().iloc[0, 1]
    print(f"\nPearson r(score, members) = {c1:.3f} | r(score, log10 members) = {log_c:.3f}")
    q = anime[anime["members"] >= anime["members"].quantile(0.75)]["rating"].mean()
    q0 = anime[anime["members"] < anime["members"].quantile(0.25)]["rating"].mean()
    print(f"Avg score - top popularity quartile: {q:.2f} vs bottom quartile: {q0:.2f}")

    # ------------------------------------------------------------------ ratings
    section("E. RATING & QUALITY")
    print("Score distribution bands:")
    bands = pd.cut(anime["rating"], bins=[0, 4, 5, 6, 7, 8, 9, 10],
                   labels=["<4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10"])
    print(bands.value_counts().sort_index().to_string())
    print("\nTop 15 scored anime (score, then members):")
    print(anime.nlargest(15, "rating")[["name", "type", "episodes", "rating", "members"]].to_string(index=False))
    print("\nBottom 10 scored anime:")
    print(anime.nsmallest(10, "rating")[["name", "type", "rating", "members"]].to_string(index=False))
    # official vs community
    j = anime.set_index("anime_id")[["name", "type", "rating", "members"]].join(cnt)
    j = j[j["n_explicit"] >= 100].copy()
    j["gap"] = j["community_mean"] - j["rating"]
    print(f"\nAnime with >=100 explicit community ratings: {len(j)}")
    print(f"Community mean overall: {j['community_mean'].mean():.3f} vs official mean: {j['rating'].mean():.3f}")
    print(f"Gap (community - official): mean {j['gap'].mean():.3f}, median {j['gap'].median():.3f}")
    print("\nBiggest positive gaps (community loves it more):")
    print(j.nlargest(8, "gap")[["name", "rating", "community_mean", "gap", "n_explicit"]].round(2).to_string(index=False))
    print("\nBiggest negative gaps (community rates it lower):")
    print(j.nsmallest(8, "gap")[["name", "rating", "community_mean", "gap", "n_explicit"]].round(2).to_string(index=False))

    # ---------------------------------------------------------------- episodes
    section("F. EPISODES ANALYSIS")
    ep = anime[anime["episodes"].notna()]
    print(f"Known episodes: {len(ep)} | median {ep['episodes'].median():.0f} | "
          f"mean {ep['episodes'].mean():.1f} | max {ep['episodes'].max():.0f}")
    print(f"Single-episode titles: {(ep['episodes']==1).sum()} ({(ep['episodes']==1).mean()*100:.1f}%)")
    print("\nLongest titles:")
    print(ep.nlargest(10, "episodes")[["name", "type", "episodes", "rating", "members"]].to_string(index=False))
    bins = [0, 1, 6, 12, 26, 52, 100, 10_000]
    labels = ["1", "2-6", "7-12", "13-26", "27-52", "53-100", ">100"]
    ep2 = ep.assign(bucket=pd.cut(ep["episodes"], bins=bins, labels=labels))
    eb = ep2.groupby("bucket", observed=True).agg(
        titles=("anime_id", "size"),
        avg_score=("rating", "mean"),
        median_members=("members", "median"),
    ).round(2)
    print("\nBy episode bucket:")
    print(eb.to_string())

    # --------------------------------------------------------------- community
    section("G. COMMUNITY (USER-SIDE)")
    per_user = ratings.groupby("user_id").agg(
        n=("rating", "size"), n_exp=("rating", lambda s: (s > 0).sum()),
        mean_score=("rating", lambda s: s[s > 0].mean()))
    print("Ratings per user - percentiles:",
          np.percentile(per_user["n"], [10, 25, 50, 75, 90, 99]).round(0))
    print(f"Users with only -1 (watched, never scored): {(per_user['n_exp']==0).sum()}")
    print(f"User mean explicit score: mean {per_user['mean_score'].mean():.2f}, "
          f"median {per_user['mean_score'].median():.2f}")
    print("\nExplicit rating value distribution (%):")
    print((ratings.loc[ratings["rating"] > 0, "rating"].value_counts(normalize=True)
           .sort_index().mul(100).round(1)).to_string())
    # watched-share by popularity tier
    j2 = cnt.join(anime.set_index("anime_id")["members"])
    j2["tier"] = pd.qcut(j2["members"], 4, labels=["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"])
    print("\nWatched-not-scored share by popularity quartile:")
    print(j2.groupby("tier", observed=True)["watched_share"].mean().round(3).to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
