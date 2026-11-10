"""Settings for one run."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    """teams: columns of the result table, in this order. None means every team found in the data.
    max_working_days: tickets that took longer are treated as outliers and left out of the averages.
    holiday_calendar: 'us_federal' (weekends and US federal holidays) or 'weekdays' (weekends only).
    done_from, done_to: optional 'YYYY-MM-DD' window; only tickets last moved to Done inside it are kept.
    """

    teams: Optional[List[str]] = None
    max_working_days: int = 20
    holiday_calendar: str = "us_federal"
    done_from: Optional[str] = None
    done_to: Optional[str] = None
