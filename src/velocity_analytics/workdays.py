"""Business day counting."""
from __future__ import annotations

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar


def make_calendar(name: str):
    if name == "us_federal":
        return pd.offsets.CustomBusinessDay(calendar=USFederalHolidayCalendar())
    if name == "weekdays":
        return pd.offsets.BDay()
    raise ValueError(f"unknown holiday_calendar {name!r}; use 'us_federal' or 'weekdays'")


def business_days_between(start, end, calendar):
    """Number of business days from start to end, counted the way the original script did.

    It lists one date per business day starting at the start timestamp (same time of day) and counts
    the ones that are not after the end timestamp. So 'Monday 09:00' to 'next Monday 00:30' is 5,
    and 'Monday 09:00' to 'next Monday 17:00' is 6. Returns None when either date is missing.
    """
    if pd.isna(start) or pd.isna(end):
        return None
    return len(pd.date_range(start=start, end=end, freq=calendar))
