# Data Cleaning Report

**Project:** Anime Data Observatory — Hi-Fi Dashboard Prototype
**Pipeline:** `scripts/clean_dataset.py` → runtime equivalent in `src/data_cleaning.py`
**Input:** `data/raw/*.csv` · **Output:** `data/processed/*.parquet`

---

## 1. Cleaning principles

1. Keep all 12,294 anime rows — nothing is dropped from the metadata table.
2. Fix representation problems (encoding, types, parsing) without altering recorded values.
3. Missing values are made *visible* (`Unknown` labels or NaN), never imputed or invented.
4 -1 in `rating.csv` is a documented sentinel ("watched, not scored"), not a missing value — it is preserved and used for engagement metrics.
5. Original raw files are never modified; outputs live in `data/processed/`.

## 2. Applied rules

### `anime.csv` → `anime_clean.parquet`, `anime_genres.parquet`

| # | Rule | Rows affected | Rationale |
|---|---|---|---|
| 1 | HTML entities in `name` unescaped (`html.unescape`) | 292 | `Gintama&#039;` → `Gintama'`; display correctness only |
| 2 | `episodes` `"Unknown"` → NaN; column cast to nullable integer (`Int64`) | 340 | Enables numeric analysis; missingness stays visible |
| 3 | `type` NaN → `"Unknown"` | 25 | Transparent category instead of silent exclusion from type filters |
| 4 | `genre` NaN → `"Unknown"` | 62 | Same rationale as rule 3 |
| 5 | `genre` split + trimmed into normalized long table `(anime_id, genre)` | 36,347 pairs, 44 tags | Enables per-genre aggregation without string surgery |
| 6 | `rating` NaN left as NaN | 230 (1.87%) | Excluded from score metrics (`pandas`/Tableau ignore nulls in AVG/MEDIAN); never imputed |

No deduplication was applied to `anime.csv` (verified: 0 duplicate IDs; the 2 duplicate names are distinct titles).

### `rating.csv` → `ratings_clean.parquet`

| # | Rule | Rows affected | Rationale |
|---|---|---|---|
| 1 | Drop duplicate `(user_id, anime_id)` pairs (keep first) | 7 | Idempotent fact table |
| 2 | Drop rows whose `anime_id` is absent from `anime.csv` | 10 | Un-joinable facts (3 orphan IDs) |

Total removed: **17 rows (0.0002%)** → 7,813,720 rows kept (1,476,488 watched-only + 6,337,232 explicit).

### Derived tables (computed, not modified data)

- **Per-anime community aggregates** (`src/analysis.py`, cached): `n_ratings`, `n_explicit`, `n_watched`, `community_mean`, `watched_share` per `anime_id` — computed from `ratings_clean.parquet`; joined to the metadata at query time so global filters apply consistently.
- **Per-user aggregates** (cached): `n_ratings`, `n_explicit`, `mean_explicit_score` per `user_id`.

## 3. What was deliberately *not* done

- No removal of low-member or extreme-score titles (outliers are real; handled analytically via minimum-members thresholds and log scales instead).
- No datetime parsing — **no date columns exist** (documented limitation, not an oversight).
- No merging of near-duplicate franchises (e.g., `Fullmetal Alchemist` vs `Brotherhood` remain separate titles, as in the source).
- No adult-content filtering — `Hentai` (1,141 titles) is a genuine tag in the data and stays a data-driven category; dashboards treat it like any other genre tag.

## 4. Verification

- `anime_clean.parquet`: 12,294 rows × 7 cols; `anime_id` unique; dtypes `int64, str, str, str, Int64, float64, int64`.
- `anime_genres.parquet`: 36,347 rows; 44 distinct tags; every `anime_id` present in `anime_clean.parquet`.
- `ratings_clean.parquet`: 7,813,720 rows; explicit ratings within [1,10]; -1 sentinel intact; every `anime_id` joinable.
- Row-count reconciliation performed and logged by `clean_dataset.py` at run time.

## 5. Processed file sizes

| File | Size |
|---|---|
| `anime_clean.parquet` | 0.5 MB |
| `anime_genres.parquet` | 0.1 MB |
| `ratings_clean.parquet` | 17.5 MB |
