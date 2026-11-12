# Anime Data Observatory

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.44%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Apache Arrow](https://img.shields.io/badge/Parquet-Columnar%20Storage-E05A47)](https://arrow.apache.org/)

An enterprise-grade interactive Business Intelligence dashboard exploring **12,294 titles** and **7,813,720 user interaction events** from MyAnimeList. Built with **Streamlit + Plotly**, featuring token-driven CSS styling, dynamic Light/Dark themes, synchronized global state filtering, and sub-second analytical aggregations.

---

## Key Analytical Insights

1. **Popularity vs. Acclaim ($r = 0.65$ log-scale):** Audience attention is heavily right-skewed (median title has only 1,550 members; top title reaches 1.01M). Analyzing members on a logarithmic scale reveals that popularity strongly correlates with critical acclaim ($+1.72$ points higher average in the top quartile).
2. **Voluntary Rating Positivity Bias (+0.14 gap):** Comparing official Bayesian weighted scores against raw voluntary community averages across 4,143 qualifying titles reveals that **83% of titles are rated higher by community members** than their official score. Over 82.6% of explicit user scores fall strictly between 7 and 10 stars, peaking at 8 stars (26.0%).
3. **Engagement Depth Disparity:** The proportion of *"watched but not rated"* interaction records (sentinel `-1`) drops monotonically from **61.8%** for niche titles down to **20.7%** for mainstream hits, proving casual users catalog niche entries without scoring.
4. **Format & Duration Sweet Spot:** While 47.5% of the catalog consists of single-episode entries (movies, OVAs, specials), critical acclaim peaks in the **13–26 episode "two-cour" bracket** (average score 6.97), while audience reach peaks at **7–12 episodes** (median 21.6K members).

---

## Dashboard Pages & Architecture

The application is structured into six dedicated analytical domains:

| # | Page | Core Analytical Objective |
|---|---|---|
| 1 | **Overview** | Macro executive summary: catalog volume, format breakdown (donut), score distribution histogram, top-12 genre frequencies, and reach leaders table. |
| 2 | **Popularity & Engagement** | Dissecting audience attention: metric toggles (Members vs. Community ratings), log-scale correlation scatter plot, and engagement depth tiers. |
| 3 | **Rating & Quality** | Quality benchmarks: format box plots, genre quality ranking with sample-size threshold sliders, anti-sample-bias top-rated table, and official vs. community sentiment gap analysis. |
| 4 | **Genre Analysis** | Structural content taxonomy: tag frequency ranking, volume vs. quality log-scale bubble chart, $20 \times 6$ genre-by-format matrix heatmap, and co-occurring tag pairings. |
| 5 | **Episodes & Format** | Runtime economics: log-binned episode histogram, format duration box plots, episode bucket performance bars, and marathon series table. |
| 6 | **Community Insights** | User-side dynamics: 73.5K user interaction behaviors, 10-point explicit rating distribution, power-user tail histogram, and side-by-side score comparison. |

---

## Technical Highlights

- **Synchronized Global Filter Pipeline:** A unified, vectorized filter pipeline (`src/filters.py`) drives all six pages simultaneously (Format, Genre OR-matching, Official Score Range, and Quantile-stepped Minimum Members).
- **Columnar Parquet Storage:** High-volume user interaction tables (7.8M records) are serialized in compressed Apache Parquet format (<18 MB), loaded once per session with `@st.cache_data` for instant sub-second filtering without memory bottlenecks.
- **Token-Driven Editorial Design System:** Fully custom CSS variable system (`assets/custom_styles.css`) enforcing 12px card enclosures, consistent typography hierarchy, tabular numerals, and complete Light/Dark mode parity.
- **Statistical Integrity:** Heavy-tailed metrics (members, episodes, user activity) employ mathematically sound log-axes and log-binning to preserve distributional shape.
- **Missing Data Transparency:** Unscored titles (1.9%) and missing format/genre tags are surfaced explicitly as `Unknown` categories rather than silently dropped.

---

## Project Structure

```
anime-data-observatory/
├── app.py                      # Main application entry point & page dispatcher
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Streamlit runtime theme configuration
├── assets/
│   └── custom_styles.css       # Token-driven editorial stylesheet (Light + Dark)
├── app_pages/                  # Modular dashboard pages
│   ├── overview.py
│   ├── popularity.py
│   ├── ratings.py
│   ├── genres.py
│   ├── episodes.py
│   └── community.py
├── src/                        # Core backend modules
│   ├── analysis.py             # Vectorized analytical aggregations
│   ├── context.py              # PageContext dataclass
│   ├── data_cleaning.py        # Data cleaning & validation logic
│   ├── data_loader.py          # Cached data loading & aggregate builders
│   ├── filters.py              # Filter state & vectorized filter application
│   ├── metrics.py              # KPI calculation & formatting functions
│   ├── tables.py               # Themed HTML ranking tables
│   ├── theme.py                # Visual design tokens & Plotly styling engine
│   └── visualizations.py       # Theme-aware Plotly chart builders
├── data/
│   └── processed/              # Cleaned Parquet tables (<18MB, tracked in git)
├── scripts/                    # Standalone CLI analysis scripts
│   ├── profile_dataset.py      # Automated dataset profiling
│   ├── clean_dataset.py        # ETL data cleaning pipeline
│   └── eda.py                  # Exploratory data analysis calculation engine
└── documentation/              # Data engineering & analytics reports
    ├── dataset_profile.md      # Data dictionary, coverage, and missingness audit
    ├── data_cleaning_report.md # Step-by-step cleaning rules & verification
    ├── eda_findings.md         # Ground-truth statistical findings
    ├── dashboard_design_specification.md
    └── visualization_rationale.md
```

---

## Quick Start (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/anime-data-observatory.git
cd anime-data-observatory
```

### 2. Set up virtual environment
```bash
# macOS/Linux:
python -m venv .venv && source .venv/bin/activate

# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```
The application will launch in your browser at `http://localhost:8501`.

---

## Data Pipeline Reproduction (Optional)

The repository includes the cleaned Parquet tables under `data/processed/` so the dashboard runs immediately out-of-the-box. To reproduce the data cleaning and EDA from raw files:

```bash
# 1. Profile the raw dataset
python scripts/profile_dataset.py data/raw

# 2. Run the cleaning ETL pipeline
python scripts/clean_dataset.py data/raw data/processed

# 3. Compute ground-truth EDA statistics
python scripts/eda.py data/processed
```

---

## License

This project is licensed under the [MIT License](LICENSE).
