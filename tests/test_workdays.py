import pandas as pd

from velocity_analytics.workdays import business_days_between, make_calendar


def days(a, b, cal="us_federal"):
    return business_days_between(pd.Timestamp(a), pd.Timestamp(b), make_calendar(cal))


def test_same_day_counts_one():
    assert days("2026-03-02 09:00", "2026-03-02 17:00") == 1


def test_time_of_day_rule():
    # Monday 09:00 to next Monday: the last Monday only counts if its 09:00 is not after the end
    assert days("2026-03-02 09:00", "2026-03-09 00:30") == 5
    assert days("2026-03-02 09:00", "2026-03-09 17:00") == 6


def test_weekend_is_skipped():
    assert days("2026-03-06 10:00", "2026-03-09 12:00") == 2  # Friday and Monday


def test_us_federal_holiday_is_skipped_but_weekdays_calendar_counts_it():
    # Monday 2026-01-19 is Martin Luther King Jr. Day
    assert days("2026-01-16 09:00", "2026-01-20 17:00") == 2
    assert days("2026-01-16 09:00", "2026-01-20 17:00", "weekdays") == 3


def test_missing_date_gives_none():
    assert business_days_between(pd.Timestamp("2026-03-02"), pd.NaT, make_calendar("weekdays")) is None
