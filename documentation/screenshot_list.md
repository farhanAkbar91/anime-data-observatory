# Pitch-Deck Screenshot Capture Plan

The validation runs in `gui-test-screenshots/` already produced usable captures (listed at the end).
For the academic pitch deck, capture the following set — each at 1600×1000 or larger, Light Mode
unless stated, with a **consistent filter story** so slides feel coherent (suggest: one slide with
unfiltered view, one with a "TV only" view to demonstrate live filtering).

## Must-capture (deck core)

| # | Shot | State | Notes |
|---|---|---|---|
| 1 | App hero — Overview top | Light, no filters | KPI band + donut + genre bars; title slide visual |
| 2 | Overview quality landscape | Light, scrolled to histogram + top-10 table | Shows score distribution + table styling |
| 3 | Popularity — attention leaders | Light, Top-15 by members | Death Note 1.01M headline |
| 4 | Popularity — "Does popularity buy quality?" scatter | Light, no filters | The log-scale r=0.65 story |
| 5 | Popularity — engagement depth tiers | Light, scrolled | 65%→18% watched-not-scored bars |
| 6 | Rating & Quality — histogram | Light | Score bands + mean/median lines |
| 7 | Rating & Quality — Top rated table | Light, min-members = 1,000 | FMA: Brotherhood 9.26 headline |
| 8 | Rating & Quality — official vs community scatter | Light, min explicit = 100 | The +0.14 bias story, 45° line |
| 9 | Genre Analysis — volume vs quality bubble | Light | Josei/Thriller high, Dementia low |
| 10 | Genre Analysis — genre × format heatmap | Light, top 20 | Dense-matrix visual |
| 11 | Genre Analysis — top pairs | Light | Action+Sci-Fi 1,034 headline |
| 12 | Episodes & Format — buckets | Light, "Avg score" metric | 13–26 eps sweet spot |
| 13 | Community Insights — KPI band + rating distribution | Light | 8★ peak, user mean 8.23 vs official 6.47 |
| 14 | Filter interaction | Light, Format = TV | Chip row + updated KPIs (3,787 / 6.90 / 161.6M) |
| 15 | Dark Mode — Overview | **Dark**, no filters | Full-page top view |
| 16 | Dark Mode — Rating & Quality | **Dark**, scrolled | Charts + tables in dark |

## Nice-to-have

| # | Shot | State |
|---|---|---|
| 17 | Empty state | Light, Music + members ≥ 1M ("No titles match…" card) |
| 18 | Sidebar close-up | Light, filter panel + About-the-data note |
| 19 | Popularity — Community ratings toggle | Light, rank-by = rating events |
| 20 | Episodes — median members metric toggle | Light |

## Already captured during validation (reusable)

- `t04_overview_light_top.png` — ≈ shot 1
- `t05_overview_light_bottom.png` — ≈ shot 2 (pre mean/median-subtitle fix)
- `t11_overview_light_filtered_tv.png` — ≈ shot 14
- `t12/t13_popularity…png` — ≈ shots 3, 5 (TV-filtered state)
- `t14_ratings_top.png` — ≈ shots 6–7 (TV-filtered state)
- `t15_genres_top.png`, `t16_episodes_top.png`, `t17_community_top.png` — pages 4–6 (TV-filtered)
- `t10_overview_dark_final.png`, `t07_overview_dark_fixed.png` — ≈ shot 15
- `t19_empty_state.png` — ≈ shot 17

For deck-quality versions, re-capture after resetting to the unfiltered state (the validation
captures intentionally carry the TV filter).
