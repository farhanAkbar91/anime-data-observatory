# Tableau Implementation Reference

**Purpose:** blueprint for rebuilding the Anime Data Observatory prototype (Streamlit) as the final Tableau dashboard. Everything below is chosen to be directly recreatable in Tableau Desktop/Public.

**Primary design reference:** **Light Mode** (see §7). The Streamlit Dark Mode is a prototype convenience — Tableau has no native dynamic theme toggle; build one theme (Light) in Tableau.

---

## 1. Data model

Connect Tableau to the **processed tables** (Parquet via a small CSV export, or re-run `scripts/clean_dataset.py` with a CSV writer):

| Table | Grain | Key fields |
|---|---|---|
| `anime` | 1 row = 1 title | `anime_id`, `name`, `type`, `episodes`, `rating`, `members` |
| `anime_genres` | 1 row = (title, genre tag) | `anime_id`, `genre` |
| `ratings` | 1 row = (user, title) interaction | `user_id`, `anime_id`, `rating` (-1 sentinel) |
| `anime_community` (derived) | 1 row = 1 title | `n_ratings`, `n_explicit`, `n_watched`, `community_mean`, `watched_share` |

Relationships (logical layer):
- `anime` ↔ `anime_genres` on `anime_id` (1:N) — **genre worksheets only**, to avoid row multiplication of `members`/`rating` measures.
- `anime` ↔ `anime_community` on `anime_id` (1:1) — or compute `anime_community` in Tableau with FIXED LODs instead of pre-joining:
  - `n_ratings = { FIXED [anime_id] : COUNT([ratings rows]) }` … on a secondary source or extract containing `ratings`.
- Recommended: publish a single flattened extract `anime_flat` = `anime` + `anime_community` columns for all non-genre sheets; keep `anime_genres` as a second table for genre sheets. This mirrors the Streamlit implementation exactly.

Data types: `episodes` = integer with nulls (from "Unknown"); `rating` = decimal; keep -1 sentinel in `ratings` (do not alias to null — engagement metrics need it).

## 2. Calculated fields (KPIs)

| KPI | Tableau calculation | Notes |
|---|---|---|
| Titles | `COUNTD([anime_id])` | |
| Avg Official Score | `AVG([rating])` | nulls auto-ignored |
| Median Official Score | `MEDIAN([rating])` | |
| Scored Share | `SUM(IIF(ISNULL([rating]),0,1)) / COUNT([anime_id])` | |
| Total Members | `SUM([members])` | |
| Community Ratings | `SUM([n_ratings])` | from `anime_flat` |
| Explicit Ratings | `SUM([n_explicit])` | |
| Watched-not-Scored % | `SUM([n_watched]) / SUM([n_ratings])` | |
| Community Mean | `AVG([community_mean])` | per-title mean, then averaged across titles (same as prototype) |
| Sentiment Bias | `AVG([community_mean]) - AVG([rating])` | on titles where both exist |
| Users Engaged | `COUNTD(IF [n_ratings] > 0 THEN user-context …)` — compute as `COUNTD([user_id])` against `ratings` filtered to the current title set | see §6 filter architecture |
| Genre: Titles per tag | `COUNTD([anime_id])` on `anime_genres` sheet | multi-counting is intentional; label as "titles per tag" |

## 3. Dashboard layout (per page)

Tab layout mirrors the prototype's six pages — one Tableau dashboard per section, or one dashboard with a sheet-swap parameter. Recommended: six dashboards in one workbook, same floating filter bar.

| Page | Sheets (in order) |
|---|---|
| **Overview** | KPI band (6 BANs) → donut (type) → bar (top 12 genres) → histogram (score) → table (top 10 members) |
| **Popularity & Engagement** | bar (top N by members / rating events, parameter swap) → scatter (score vs members, log-x) → histogram (log-binned members) + box (members by type) → bar (watched-not-scored by tier) |
| **Rating & Quality** | histogram + reference lines → box (score by type) → bar (avg score by genre, min-titles filter) → table (top rated, min-members parameter) → scatter (official vs community + 45° line) |
| **Genre Analysis** | bar (frequency) → bubble (frequency vs avg score, size = median members) → highlight table (genre × type) → bar (genre pairs) |
| **Episodes & Format** | KPI BANs → histogram (log-binned episodes) + box (episodes by type, log-y) → bar (avg score by episode bucket / median members, parameter) → table (longest titles) |
| **Community Insights** | KPI BANs → bar (explicit rating 1–10) → histogram (ratings per user, log-binned) → table (most-rated titles) |

**Log-binned histograms:** Tableau histograms are linear. Recreate the prototype's log-binned histograms with a calculated bin field:
- members: `LOG10([members] + 1)` binned into 35 bins (bin size = (log10(max+1))/35), axis ticks labeled 1/10/1K/10K/100K/1M.
- Same pattern for episodes (cap at 200) and interactions-per-user.

## 4. Dimensions & measures per chart (aggregation spec)

| Chart | Dimension(s) | Measure(s) | Aggregation | Sort |
|---|---|---|---|---|
| Donut type | `type` | Titles | COUNTD | Descending |
| Top genres bar | `genre` | Titles per tag | COUNTD on genre sheet | Descending (top N parameter) |
| Score histogram | bin(rating, 0.25) | Titles | COUNT | Ascending band |
| Box score by type | `type` | rating | Distribution (quartiles) | By median desc |
| Avg score by genre | `genre` | AVG(rating) | AVG | Descending; filter titles ≥ param |
| Scatter score↔members | detail = `anime_id` | X: members (log), Y: AVG(rating) | per-title (ATTR) | — |
| Official vs community | detail = `anime_id` | X: rating, Y: community_mean, Color: gap (diverging) | per-title | — |
| Genre × type | `genre` rows, `type` cols | Titles | COUNTD | Rows by total desc |
| Bubble genres | `genre` | X: titles (COUNTD), Y: AVG(rating), Size: MEDIAN(members) | | |
| Episode buckets | `bucket` (calculated: 1 / 2–6 / 7–12 / 13–26 / 27–52 / 53–100 / >100) | AVG(rating) or MEDIAN(members) | | By bucket order |
| Tier bars | `tier` (calculated quartile of members — use FIXED LOD rank or Table Set) | AVG(watched_share) | | Tier order |
| Rating values bar | `ratings.rating` (1–10, explicit only) | share of explicit | COUNT / total | 1→10 |
| User activity | bin(LOG10(ratings per user)) | Users | COUNTD | |

## 5. Filters (global, applied to all sheets)

| Filter | Type | Behavior | Tableau implementation |
|---|---|---|---|
| Format (type) | Multi-select dropdown | Empty = all | `type` dimension filter, applied to all sheets |
| Genre | Multi-select dropdown, **OR semantics** | Keep titles carrying ANY selected tag | On genre sheets: direct `genre` filter. On non-genre sheets: `anime_id` Set from genre selection (Set with "All" default), or a FIXED LOD boolean: `{FIXED [anime_id]: MAX(IIF([genre] IN (param list),1,0))} = 1` driven by a genre multi-select parameter |
| Score range | Range slider 1.67–10.00, step 0.05 | Excludes unscored titles once moved from full range | `rating` measure filter (range) — Tableau automatically excludes nulls in a range filter; document the null behavior |
| Min members | Single-value "at least" list (0, 100, 250, 500, 1K, 2.5K, 5K, 10K, 25K, 50K, 100K, 250K, 500K, 1M) | Keeps titles ≥ threshold | `members` filter with "At least" / parameter + boolean |
| Reset | — | — | Tableau: use the built-in filter reset or a "Reset" bookmark |

Apply all four as **global filters** (Apply to Worksheets → All Using This Data Source). Page-local controls are worksheet-level filters or parameters (top N, min-titles, min-explicit, metric swap).

## 6. Interactions

| Prototype behavior | Tableau equivalent |
|---|---|
| Sidebar global filters | Global filter cards on each dashboard (top or left zone) |
| Filter chips readout | Filter card captions / a "current filters" worksheet title |
| Hover tooltips | Native tooltips, formatted (scores 2-dec, counts with separators, episodes "—" for null) |
| Zoom/pan on charts | Native; keep panes simple for a static deck |
| Top-N / parameter swaps | Parameters + sheet swap |
| Watched-not-scored tier bars | Table Set of members quartiles (dynamic set) |
| Donut click-to-filter | **Dashboard filter action** on the donut (Select → filter all sheets). This was removed from the Streamlit prototype as unreliable; in Tableau it is a first-class feature and SHOULD be implemented. |
| Light/Dark toggle | Not native — build the Light theme only (§7) |
| HTML ranking tables | Standard Tableau tables (text table), pre-sorted by rank measure |

## 7. Color palette & typography (Light theme = design reference)

| Token | Hex | Use |
|---|---|---|
| Background | `#F6F7FB` | Dashboard background |
| Surface (cards) | `#FFFFFF` | Zone backgrounds, BAN cards |
| Text primary | `#1B2437` | Titles, labels |
| Text secondary | `#5B6779` | Subtitles, axis labels |
| Border | `#E3E7EF` | Zone dividers, card borders |
| Accent (primary series) | `#5457D6` | Bars, KPI accents, slider |
| Categorical palette (fixed order) | `#5457D6, #E8930C, #2FA36B, #D8578B, #3E7BC4, #8C63D9, #C74A44, #2E9BA6, #D97B2E, #6B7BB6` | Type/genre series; same hue = same format on every sheet |
| Format colors | TV `#5457D6` · Movie `#E8930C` · OVA `#2FA36B` · Special `#D8578B` · ONA `#3E7BC4` · Music `#8C63D9` · Unknown `#8892A6` | Assign explicitly per format |
| Diverging (score gap) | `#C74A44 → #B9BECB → #2FA36B` | Community − official gap, centered at 0 |
| Sequential (heatmap) | `#FFFFFF → #5457D6` | Genre × type counts |

- Grid lines: `#EAEDF4`; reference lines: `#5B6779`.
- Font: Tableau's default "Tableau Book"/"Segoe UI"; titles semibold 14–15px, axis 11–12px, KPI values 24–28px semibold, KPI labels 10px uppercase letter-spaced.
- Chart backgrounds transparent/white; no gradients beyond the diverging ramp; no animations.

## 8. KPI card (BAN) specifications

Six per page as in the prototype: value (big), label (uppercase), context line (small, muted — e.g., "median 6.57 · 98.1% scored"). Implement as text worksheets or zone-stacked BANs; 6-column grid, 12px corner radius on zones, 1px border + soft shadow.

## 9. Known parity notes & limitations

1. `members`/counts are a 2016/2019 snapshot — state this in the dashboard subtitle, as the prototype does.
2. Genre-tag sheets multi-count titles; label "titles per tag" and never sum to 12,294 in a heading.
3. `rating` is the official weighted score — never blend it with `AVG(ratings.rating)` in one KPI; the prototype keeps two clearly separated score systems (official vs community).
4. Log-binned histograms need the calculated-bin pattern (§3); linear-binned histograms on members/episodes/user-activity would be unreadable.
5. Users-Engaged KPI requires the `ratings` table's `COUNTD([user_id])` — either a secondary source relationship or an LOD against an extract that includes `ratings`.
6. The Streamlit "click-to-filter donut" prototype interaction was removed (unreliable); in Tableau implement it properly with a dashboard filter action.

## 10. Build checklist

1. Clean data (`scripts/clean_dataset.py`) → CSV exports → Tableau extract.
2. Build `anime_flat` (with community aggregates) + `anime_genres` tables; define relationships.
3. Create parameters: Top-N, min titles/genre, min explicit ratings, min members (ranking), metric swap, rank-by swap.
4. Create calculated fields (§2) + bin fields (§3) + quartile tier set.
5. Build sheets in the §3 order, apply §5 global filters, wire donut filter action.
6. Apply §7 colors/typography; validate KPI BAN values against the prototype screenshots (the numbers in this repo's EDA findings are the ground truth).
7. Publish; confirm filters and tooltips in Tableau Public/Desktop.
