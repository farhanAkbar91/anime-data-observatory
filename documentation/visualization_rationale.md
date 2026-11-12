# Visualization Rationale

Every chart in the prototype exists to answer one specific question with a Tableau-recreable chart type. No 3D, no dual-axis tricks, no decoration-only visuals.

---

## Page 1 — Overview

| Chart | Type | Question it answers | Why this type | Tableau match |
|---|---|---|---|---|
| Titles by type | Donut | What share of the library is each format? | 6-part part-to-whole with clear legend labels; slices > 3% so labels stay readable | Donut/pie |
| Top genres | Horizontal bar | Which tags dominate the library? | Ranking of 12 categories with count labels; bars beat pie for 12 items | Bar (sorted) |
| Score distribution | Histogram | Where does quality concentrate? | Continuous distribution; bin width 0.25 keeps shape honest | Histogram |
| Top 10 by members | Ranked table | Which titles hold the community's footprint? | Exact values + type/score context columns | Table |

## Page 2 — Popularity & Engagement

| Chart | Type | Question | Why | Tableau match |
|---|---|---|---|---|
| Top by members / rating count | Horizontal bar (segmented toggle) | Who owns attention? | Long names need horizontal space; toggle keeps the page focused | Bar |
| Score vs members | Scatter (log-x) | Does popularity buy quality? | r=0.388 linear vs 0.648 log — log axis reveals the true monotone relation | Scatter (log axis) |
| Members distribution | Histogram (log bins) + box-by-type | How concentrated is attention? | Heavy right tail; two views answer "overall shape" and "per format" | Histogram / Box |
| Watched-not-scored by tier | Bar | Do niche titles get real ratings? | Quartile comparison of a share metric | Bar |

## Page 3 — Rating & Quality

| Chart | Type | Question | Why | Tableau match |
|---|---|---|---|---|
| Score distribution + markers | Histogram | What is "normal" quality? | Shows left tail and the 6–7 mass; mean/median lines quantify skew | Histogram + reference lines |
| Score by type | Box | Which formats score better? | Distribution comparison, not just means | Box plot |
| Avg score by genre | Horizontal bar + threshold slider | Which genres deliver quality? | Sorted bars; min-titles slider prevents thin-genre noise | Bar with filter |
| Top rated | Ranked table + min-members slider | What is actually "best"? | Solves the 10.00-with-13-members artifact with a visible, adjustable control | Table + parameter |
| Official vs community | Scatter + 45° line, diverging color on gap | Who rates stricter? | Direct pairwise comparison; diagonal makes bias readable at a glance | Scatter + reference line |

## Page 4 — Genre Analysis

| Chart | Type | Question | Why | Tableau match |
|---|---|---|---|---|
| Genre frequency | Horizontal bar (top-N) | Which genres exist in volume? | Baseline composition | Bar |
| Frequency vs avg score | Bubble scatter | Which genres are both common and good? | Two measures at once; bubble size = median members adds context without a third axis | Scatter w/ size |
| Genre × type | Heatmap | Where does each genre live (format-wise)? | 44×7 matrix is unreadable as bars; heatmap handles density | Highlight table |
| Genre pairs | Horizontal bar | Which combinations recur? | Pairwise co-occurrence counts; pairs read naturally as bar labels | Bar |

## Page 5 — Episodes & Format

| Chart | Type | Question | Why | Tableau match |
|---|---|---|---|---|
| Episode count distribution | Histogram (log bins) | How long are titles, really? | 1→1,818 range needs log binning to stay legible | Histogram |
| Episodes by type | Box (log-y) | Does length differ by format? | TV vs Movie vs OVA length spread | Box |
| Avg score by episode bucket | Bar (+ optional median-members companion) | Does length buy quality/attention? | Ordered categorical buckets; toggle avoids dual-axis confusion | Bar |
| Longest titles | Table | What are the marathon shows? | Extreme values with context | Table |

## Page 6 — Community Insights

| Chart | Type | Question | Why | Tableau match |
|---|---|---|---|---|
| Explicit rating distribution | Bar (1–10) | How do users rate? | Discrete 10-point scale; bars show the top-heavy skew plainly | Bar |
| Ratings per user | Histogram (log bins) | Who powers the community? | Power-user tail; log bins expose it | Histogram |
| Watched-not-scored by tier | Bar | Where do users log without scoring? | Monotone 62%→21% pattern is a clean bar story | Bar |
| Most-rated titles | Table with community mean + official score | What gets rated most? | Side-by-side score columns make bias scannable | Table |

## Cross-cutting rules

1. **Sorted by measure, always** (bars descending), unless the axis itself is ordinal (score bands, episode buckets).
2. **Log scales only where skew demands**, and always labeled ("log scale" on axis title).
3. **Color encodes category consistently** — same type → same color on every page, both themes.
4. **Tooltips carry full context** (title, type, episodes, score, members, community stats) so users never need cross-referencing.
5. **Reference lines** (mean/median/45°) only where they support the stated question.
6. **Missing values**: excluded from score metrics, shown as their own `Unknown` category where categorical (type/genre), and reported in KPI context lines — never silently dropped.
7. **Empty states** render guidance instead of blank canvases.
