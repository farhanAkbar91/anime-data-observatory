# Dataset Profile Report

**Project:** Anime Data Observatory — Hi-Fi Dashboard Prototype
**Source files:** `data/raw/anime.csv` (936 KB), `data/raw/rating.csv` (111 MB)
**Origin:** Kaggle *Anime Recommendations Database* (MyAnimeList scrape, 2016/2019 snapshot)

---

## 1. File inventory

| File | Rows | Columns | Description |
|---|---|---|---|
| `anime.csv` | 12,294 | 7 | One row per anime title (metadata + aggregated popularity/score) |
| `rating.csv` | 7,813,737 | 3 | One row per (user, anime) interaction event |

## 2. Column dictionary — `anime.csv`

| Column | Type | Semantics | Missing | Notes |
|---|---|---|---|---|
| `anime_id` | int64 | Unique MyAnimeList identifier | 0 | No duplicates (0/12,294) |
| `name` | string | Title | 0 | 292 rows contain HTML entities (`&#039;`, `&amp;`, `&quot;`) |
| `genre` | string | Comma-separated genre tags | 62 (0.50%) | 1–13 tags per title; **43 distinct tags** (+1 `Unknown` after cleaning) |
| `type` | string | Format: TV / OVA / Movie / Special / ONA / Music | 25 (0.20%) | 6 valid categories |
| `episodes` | string→numeric | Episode count | 340 stored as `"Unknown"` | Otherwise numeric; median 2, max 1,818 |
| `rating` | float | **Weighted community average score** (1–10 scale, MyAnimeList-style Bayesian weighting) | 230 (1.87%) | Mean 6.47, median 6.57, range 1.67–10.00 |
| `members` | int | Number of community members who added the title | 0 | Heavily right-skewed: median 1,550, max 1,013,917 |

## 3. Column dictionary — `rating.csv`

| Column | Type | Semantics | Notes |
|---|---|---|---|
| `user_id` | int64 | Anonymized user | 73,515 distinct users |
| `anime_id` | int64 | References `anime.csv` | 11,200 distinct titles referenced; 3 IDs not present in `anime.csv` |
| `rating` | int | **-1 = watched but not scored**; 1–10 = explicit score | -1 share: 18.9% (1,476,496 rows) |

## 4. Data types & structure

- No date/time fields exist in either file (no airing dates, seasons, or years).
- No studio, source-material, theme, demographic, favorites, or ranking columns exist.
- `rating.csv` is an interaction log, not pre-aggregated: 6,337,232 explicit ratings + 1,476,488 watched-only events.

## 5. Categorical distributions

**`type`** (counts): TV 3,787 · OVA 3,311 · Movie 2,348 · Special 1,676 · ONA 659 · Music 488 · (missing 25)

**Top genre tags** (out of 43): Comedy 4,645 · Action 2,845 · Adventure 2,348 · Fantasy 2,309 · Sci-Fi 2,070 · Drama 2,016 · Shounen 1,712 · Kids 1,609 · Romance 1,464 · School 1,220 · Slice of Life 1,220 · Hentai 1,141 · Supernatural 1,037 · Mecha 944 · Music 860 … rarest: Yaoi 39, Yuri 42, Josei 54, Shoujo Ai 55, Shounen Ai 65, Cars 72.

**Tags per title**: 1 tag × 2,804 · 2 × 2,677 · 3 × 2,599 · 4 × 1,940 · 5 × 1,261 · 6 × 595 · 7 × 228 · 8 × 73 · 9 × 40 · 10 × 12 · 11 × 2 · 13 × 1.

## 6. Missing values (anime.csv)

| Column | Missing | % |
|---|---|---|
| `rating` | 230 | 1.87% |
| `genre` | 62 | 0.50% |
| `type` | 25 | 0.20% |
| `episodes` (as `"Unknown"`) | 340 | 2.77% |

`rating.csv` contains no NaNs.

## 7. Duplicates

- `anime.csv`: 0 duplicate `anime_id`; 2 duplicate *names* (`Saru Kani Gassen`, `Shi Wan Ge Leng Xiaohua`) — verified as **genuinely different titles** (different IDs, types, data). Kept.
- `rating.csv`: 7 duplicate `(user_id, anime_id)` pairs.

## 8. Inconsistent formatting / invalid values

- HTML entities embedded in 292 title strings (`Gintama&#039;` → `Gintama'`).
- `episodes` mixes numeric strings with the literal `"Unknown"` (340 rows).
- 25 rows with null `type`; 62 with null `genre`.
- 3 `anime_id` values in `rating.csv` have no metadata row in `anime.csv` (10 rating rows total).
- One user-anime pair logic check: no negative ratings other than the sentinel -1; explicit range strictly 1–10.

## 9. Outliers (verified plausible, retained)

- `members`: max 1,013,917 (Death Note) — genuine top of a heavy-tail distribution.
- `episodes`: max 1,818 (Oyako Club) — long-running TV series; plausible.
- `rating` 10.00 appears on titles with as few as 13 members — small-sample artifact, retained but flagged as the reason "Top rated" views require a minimum-members threshold.
- `rating.csv`: one user with 10,227 interactions (legitimate power user).

## 10. Relationships between variables (measured)

| Relationship | Statistic |
|---|---|
| Official score ↔ members (linear) | Pearson r = **0.388** |
| Official score ↔ log10(members) | Pearson r = **0.648** → popularity–score relation is multiplicative/log-shaped |
| Official score ↔ mean explicit user score (per anime, ≥100 ratings, n=4,143) | Pearson r = **0.845**; community mean 7.37 vs official 7.23 (+0.137 bias) |
| Explicit user ratings distribution | Strongly left-clustered: 82.6% of explicit ratings are 7–10; user mean 7.81 (per rating), 8.23 (per-user mean) |
| Watched-not-scored share by popularity quartile | Q1 61.8% → Q2 32.0% → Q3 26.4% → Q4 20.7% |

## 11. Cross-file coverage

| Metric | Value |
|---|---|
| Titles in `anime.csv` | 12,294 |
| Titles receiving ≥1 interaction | 11,197 (91.1%) |
| Titles with ≥1 explicit rating | 9,927 (80.7%) |
| Titles with no community data | 1,097 (8.9%) |

## 12. Limitations discovered (drives dashboard scoping)

1. **No temporal data** — release-year/season/temporal-trend pages are impossible without fabrication. Excluded from scope.
2. **No studio / source / demographics / favorites** — "production" and "studio performance" analyses are impossible. Excluded from scope.
3. `members` and community counts are cumulative at scrape time (2016/2019), so "engagement" reflects that snapshot, not present-day values.
4. `rating` is already a *weighted* average; it is not an average of `rating.csv` rows — the two are consistent (r=0.845) but not identical.
5. Small-sample score artifacts exist at the top of the rating range.
