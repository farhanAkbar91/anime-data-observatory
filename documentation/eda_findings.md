# Exploratory Data Analysis — Findings

**Project:** Anime Data Observatory — Hi-Fi Dashboard Prototype
**Data:** cleaned tables (12,294 titles; 7,813,720 community interaction rows; 73,515 users)
**Script:** `scripts/eda.py` (all numbers below are computed, not estimated)

---

## 1. Overview of the collection

- **12,294 titles**; 98.1% carry an official weighted score (230 missing).
- Official score: **mean 6.47, median 6.57**, IQR 5.88–7.18, range 1.67–10.00 → moderately left-tight distribution centered just above midpoint.
- **222.2M cumulative members** across the collection; median title has only 1,550 members (extreme right skew).
- **7,813,720 interaction events** from **73,515 users**: 81.1% explicit ratings, 18.9% watched-not-scored.

## 2. Format (type) analysis

| Type | Titles | Avg score | Median score | Median members | Median episodes |
|---|---|---|---|---|---|
| TV | 3,787 | **6.90** | 6.94 | 5,947 | 24 |
| Special | 1,676 | 6.52 | 6.63 | 2,247 | 1 |
| OVA | 3,311 | 6.38 | 6.38 | 1,663 | 2 |
| Movie | 2,348 | 6.32 | 6.47 | 500 | 1 |
| ONA | 659 | 5.64 | 5.76 | 312 | 2 |
| Music | 488 | 5.59 | 5.62 | 228 | 1 |

**Insights:** TV titles both dominate the library and score highest; ONA and Music formats score ~1.3 points lower. Movies are half as popular as TV by median membership. The gap is consistent enough to be a headline finding.

## 3. Genre analysis

- **Frequency leaders:** Comedy (4,645 titles — 37.8% of the library), Action (2,845), Adventure (2,348), Fantasy (2,309), Sci-Fi (2,070).
- **Quality leaders** (genres with ≥50 titles): **Josei 7.44**, Thriller 7.38, Mystery 7.23, Police 7.12, Shounen 7.06, Psychological 7.01.
- **Quality laggards:** Dementia 5.01, Unknown 5.36, Music 5.92, Kids 6.11, Hentai 6.18, Horror 6.43.
- **Frequency ≠ quality:** Comedy is the most common genre but sits mid-table (6.62). Drama (2,016 titles, 6.98) outperforms its size.
- **Top co-occurring pairs:** Action+Sci-Fi (1,034 titles), Adventure+Fantasy (951), Comedy+Shounen (939), Adventure+Comedy (916), Action+Adventure (891) — the "shounen action-adventure formula" dominates production.

## 4. Popularity & engagement

- **Most-membered titles:** Death Note (1,013,917), Shingeki no Kyojin (896,229), Sword Art Online (893,100), FMA: Brotherhood (793,665), Angel Beats! (717,796).
- **Most-rated titles (community rows):** Death Note (39,340), SAO (30,582), SnK (29,583), Code Geass (27,717), Elfen Lied (27,506) — the popularity ranking is nearly identical across both measures (rank correlation is visibly near-perfect from the top-15 lists).
- **Popularity ↔ quality:** r = 0.388 linear, **r = 0.648 log10(members)**. Top popularity quartile averages **7.39** vs **5.67** for the bottom quartile (+1.72 points). Popular anime score substantially higher (or become popular because they are good — the data cannot disambiguate causality, which is stated in the dashboard).
- **Engagement depth:** the watched-not-scored share falls monotonically with popularity: **61.8%** (Q1) → 32.0% → 26.4% → **20.7%** (Q4). For niche titles the community mostly logs "watched" without scoring.

## 5. Rating & quality

- Score bands: <4: 266 · 4–5: 797 · 5–6: 2,437 · 6–7: 4,742 · 7–8: 3,239 · 8–9: 565 · 9–10: 18. Only 0.15% of titles reach 9+.
- **Small-sample trap:** the raw top-score list is headed by titles with 10.00 from as few as 13 members (e.g., *Taka no Tsume 8*). Any "Top rated" view requires a **minimum-members threshold** (default 1,000 in the dashboard) to be meaningful. With that threshold, the top of the list is FMA: Brotherhood (9.26), Gintama° (9.25), Steins;Gate (9.17) — i.e., critically acclaimed *and* widely watched titles.
- **Community bias:** for titles with ≥100 explicit ratings (n=4,143), the community mean (7.37) exceeds the official weighted score (7.23) by **+0.137 on average**. User-level mean is 8.23 — 82.6% of explicit ratings are 7–10, confirming strong positivity bias in voluntary ratings.
- **Systematic score gaps:** largest *negative* gaps (community < official) are concentrated in adult-tagged titles (e.g., the *Oni Chichi* series, −0.32…−0.34), suggesting the official weighted score penalizes that segment beyond what its actual raters give.

## 6. Episodes & format depth

- 47.5% of titles with known counts are **single-episode** (movies/specials/OVAs); median across all is 2.
- **Score by episode bucket:** 1 ep 6.22 → 2–6 6.41 → 7–12 6.81 → **13–26 6.97** → 27–52 6.87 → 53–100 6.84 → >100 6.99. The "one-cour sweet spot" (13–26 episodes) and long-runners score highest; single-episode titles score lowest (they also include specials of varying quality).
- **Median members peak at 7–12 episodes (21,584)** — the modern seasonal-cour length attracts the widest audience.
- Longest titles are long-running kids/family TV (Oyako Club 1,818 eps, Doraemon (1979) 1,787).

## 7. Community (user-side) behavior

- Ratings per user: median **57**, 75th pct 136, 99th pct 708, max 10,227 — a classic power-user tail.
- **3,915 users (5.3%) never scored anything** — only -1 events.
- Explicit rating distribution: 1★ 0.3% · 5★ 4.5% · 6★ 10.1% · 7★ 21.7% · 8★ 26.0% · 9★ 19.8% · 10★ 15.1% → strong top-heavy skew.

## 8. Statistical observations & caveats

1. `members` and event counts are cumulative snapshot values (2016/2019 scrape) — treat as "community footprint", not live numbers.
2. The official `rating` is a weighted (Bayesian-style) average and is *not* recomputable exactly from `rating.csv`; consistency is high (r = 0.845) but not identity — comparisons are legitimate at the title level.
3. Voluntary-rating positivity bias inflates community means vs official scores; the dashboard reports both and never mixes them in one KPI.
4. Genre-tag aggregation multi-counts titles (a title tags into every genre it carries) — genre charts state "titles per tag", never summing to 12,294.
5. No temporal, studio, or source data → those analyses are out of scope (see dataset_profile.md §12).

## 9. Recommended KPIs (all computed dynamically)

| KPI | Definition (Tableau-compatible) |
|---|---|
| Titles | `COUNTD([anime_id])` on filtered base |
| Avg / Median Official Score | `AVG([rating])` / `MEDIAN([rating])`, nulls ignored |
| Total Members | `SUM([members])` |
| Community Ratings | `COUNT([rating rows])` (incl. -1) |
| Explicit Ratings | `COUNT([rating rows]) WHERE rating > 0` |
| Watched-not-Scored % | share of -1 rows |
| Community Mean Score | `AVG(rating) WHERE rating > 0` (per-title aggregate join) |

## 10. What the dashboard should show (and why)

Supported by the findings above, the six information pages are: **Overview**, **Popularity & Engagement**, **Rating & Quality**, **Genre Analysis**, **Episodes & Format**, **Community Insights**. Charts excluded as low-signal during EDA: name-length trivia, ID-based analyses, redundant per-type genre breakdowns (kept as one heatmap), and any temporal chart (no data).
