"""Shared page context passed to every dashboard page."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .filters import FilterState


@dataclass
class PageContext:
    anime: pd.DataFrame        # filtered metadata (with community aggregate columns)
    genres: pd.DataFrame       # full normalized (anime_id, genre) table
    ratings: pd.DataFrame      # full cleaned rating log
    user_stats: pd.DataFrame   # global per-user aggregates
    users: int                 # distinct users within the filtered set
    theme: dict                # active theme tokens
    state: FilterState         # active global filter state
    unfiltered_count: int      # total titles before filtering
