"""Maps sidebar navigation names to page render functions.

The package is named `app_pages` (not `pages/`) because Streamlit auto-detects
a literal `pages/` directory as a multipage app, which would conflict with the
custom single-app navigation in app.py.
"""
from __future__ import annotations

from app_pages import community, episodes, genres, overview, popularity, ratings

PAGES = {
    "Overview": overview.render,
    "Popularity & Engagement": popularity.render,
    "Rating & Quality": ratings.render,
    "Genre Analysis": genres.render,
    "Episodes & Format": episodes.render,
    "Community Insights": community.render,
}
