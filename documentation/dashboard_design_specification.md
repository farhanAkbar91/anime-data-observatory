# Dashboard Design Specification

**Project:** Anime Data Observatory — Hi-Fi Dashboard Prototype (Streamlit)
**Target platform for production:** Tableau (see `tableau_implementation_reference.md`)
**Design direction:** clean editorial analytics aesthetic with a restrained anime-inspired identity — professional BI tool, not a fan site.

---

## 1. Information architecture

Six navigation sections, driven entirely by what the data supports (the brief's suggested "Temporal Trends" and "studio production" pages are impossible without fabrication — no dates/studios exist; see `dataset_profile.md` §12):

| # | Page | Analytical question |
|---|---|---|
| 1 | **Overview** | What does the collection look like at a glance? |
| 2 | **Popularity & Engagement** | Which titles own the community's attention, and how does attention relate to quality? |
| 3 | **Rating & Quality** | What is good, according to whom — official weighted score or raw community sentiment? |
| 4 | **Genre Analysis** | Which genres dominate, and which perform? |
| 5 | **Episodes & Format** | How do length and format shape reach and reception? |
| 6 | **Community Insights** | How does the user base actually rate and behave? |

### Page content map

**1. Overview**
- KPI row (6 cards): Titles, Avg Official Score, Median Official Score, Total Members, Community Ratings, Community Users.
- Donut: title count by type. Bar: top 12 genres by titles. Histogram: official score distribution. Table: Top 10 by members.
- Chart-driven cross-filtering (e.g., clicking a donut slice to filter) is **delegated to the Tableau build** (dashboard filter actions). It was prototyped and deliberately removed from the Streamlit build: Plotly's pie-trace selection events proved unreliable inside Streamlit, and the brief forbids relying on Streamlit-specific interactions as essential functionality.

**2. Popularity & Engagement**
- Horizontal bars: Top 15 by members; Top 15 by community rating count (toggle between them via segmented control).
- Scatter: official score vs members (log x-axis; size/tooltip carry episodes & type).
- Histogram: members distribution (log bins) + box view by type (segmented control).
- Bar: watched-not-scored share by popularity quartile.

**3. Rating & Quality**
- Histogram: official score distribution with mean/median markers.
- Box: score by type. Bar: avg score by genre (min-titles threshold slider, default 50).
- Table: Top rated with **min-members slider** (default 1,000 — anti small-sample bias).
- Scatter: official vs community mean (≥100 explicit ratings), 45° reference line, colored by gap.

**4. Genre Analysis**
- Bar: genre frequency (top-N slider). Scatter: frequency vs avg score (bubble = median members, quadrant shading).
- Heatmap: genre × type title counts. Bar: top 15 genre pairs by co-occurrence.

**5. Episodes & Format**
- KPI strip: % single-episode, median episodes, best-scoring episode bucket.
- Histogram: episode counts (log bins). Box: episodes by type (log y).
- Bar: avg score by episode bucket (+ median members overlay table). Table: longest titles.

**6. Community Insights**
- KPI strip: users, explicit ratings, watched-not-scored %, community mean vs official mean.
- Bar: explicit rating distribution (1–10). Histogram: ratings per user (log bins).
- Bar: watched-not-scored share by popularity tier. Table: most-rated titles with community mean.

## 2. Global filters (sidebar)

Only filters the data supports. Year/season/status/studio filters are impossible (no such columns) and are deliberately absent.

| Filter | Control | Semantics | Applies to |
|---|---|---|---|
| Type | Multiselect (default: all 7) | Keep selected types | All pages, all charts/KPIs |
| Genre | Multiselect (default: none = all) | Keep titles carrying **any** selected tag (OR semantics, stated in UI) | All pages |
| Score range | Dual-handle slider 1.67–10.00 | Keep titles with official score in range; unscored titles (NaN, 1.9%) are **excluded once the filter is touched from default** and the UI says so | All pages |
| Min members | Stepped slider (quantile stops 0→1,000,000) | Keep titles with `members ≥ threshold` | All pages |
| Reset | Button | Restores defaults | — |

- Active filter state renders as chips above the content ("Filtered view: Type: TV, Movie · Genre: Action… · Members ≥ 1,000").
- Filters recompute KPIs and charts through one shared `apply_filters()` function — identical behavior on every page (Tableau: same effect as global dashboard filters).

## 3. Page-local controls (kept minimal)

| Page | Control | Purpose |
|---|---|---|
| Popularity | Top-N selector (10/15/20/25) | Bar length |
| Popularity | Segmented control: rank by members vs community-rating events | Two complementary popularity measures without chart junk |
| Rating & Quality | Min titles per genre slider (10–200) | Avoids thin-genre noise |
| Rating & Quality | Min explicit community ratings slider (25–500) for the bias scatter | Statistical reliability |
| Rating & Quality | Min-members stepped slider for the Top-rated ranking | Solves the small-sample score artifact |
| Genre | Top-N genres slider (10–30), heatmap width slider (10–30), min-titles slider (10–200) | Focus |
| Episodes | Segmented control: bucket metric (avg score / median members) | Same axis, two measures |

## 4. Visual design system

### Theme support
- **Light mode = default** (and the primary Tableau design reference); **Dark mode** = full alternate theme via header toggle (segmented control in the app header).
- Theme state lives in `st.session_state`; CSS is driven by `data-theme` attribute + CSS variables; every Plotly figure is rebuilt with the matching template — no stale chart colors after toggle.
- Contrast checked for text (≥ 7:1 body, ≥ 4.5:1 secondary) and chart series in both themes.

### Color palette (restrained, consistent across themes)

| Token | Light | Dark | Use |
|---|---|---|---|
| `bg` | `#F6F7FB` | `#0F1420` | App background |
| `surface` | `#FFFFFF` | `#171E2E` | Cards, sidebar, tables |
| `text` | `#1B2437` | `#E8ECF4` | Primary text |
| `text-muted` | `#5B6779` | `#9AA6BC` | Secondary text |
| `border` | `#E3E7EF` | `#26304A` | Card borders |
| `accent` | `#5457D6` (indigo) | `#7C7FF0` | Primary series, links, KPI accent |
| Categorical (10) | `#5457D6` `#E8930C` `#2FA36B` `#D8578B` `#3E7BC4` `#8C63D9` `#C74A44` `#2E9BA6` `#D97B2E` `#6B7BB6` | same hues, +6% lightness | Type/genre series — **identical assignment order in both themes** |
| Diverging (gap charts) | `#C74A44 → #E3E7EF → #2FA36B` | `#E06A64 → #26304A → #4FBF8B` | official-vs-community gap |

Chart surfaces are transparent (`paper/plot bg = transparent`) so figures sit on card backgrounds in both themes. Grids: `#E3E7EF` (light) / `#26304A` (dark).

### Typography & layout
- Streamlit font stack with system UI fallbacks; sizes: KPI value 1.7rem semibold, KPI label 0.78rem uppercase letter-spaced muted, section headers via styled `st.subheader`.
- Cards: 12px radius, 1px border, very soft shadow (`0 1px 3px rgba(16,24,40,.06)` light / stronger ring in dark).
- KPI cards: rounded, icon-free, value + label + small delta/context line where meaningful.
- Max content width ~1,400px; consistent 1rem gutters; charts in equal-height rows; decorative elements limited to a thin accent rule under the header.

## 5. Interaction & chart behavior

- Every figure: descriptive title + subtitle question (e.g., "Does popularity buy quality?"), labeled axes with units, formatted hover tooltips (thousands separators, 2-dec scores), legend only when it adds information.
- Bar charts sorted by value (horizontal bars descending); heatmaps sorted by frequency; tables pre-sorted by the ranking measure (ranking tables are HTML for full theme control; interactive re-sorting is Tableau-native).
- Log scales where skew demands (members, episodes) — labeled explicitly on the axis.
- Plotly-native zoom, pan, hover and fullscreen are available on every chart.
- Empty filter results render a styled empty-state card with a "reset filters" hint (no blank screens, no exceptions).

## 6. Performance

- Parquet + `st.cache_data` for loads (once per session), cleaned table < 0.6 MB; community aggregates precomputed per anime (11,200 rows) and per user (73,515 rows); only thin boolean-mask filtering per rerun.
- All aggregations vectorized pandas; no per-row Python in render paths.
