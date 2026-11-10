import pandas as pd

from conftest import make_history
from velocity_analytics.workdays import make_calendar
from velocity_analytics.worksheet import build_worksheet

CAL = make_calendar("weekdays")


def test_reopened_ticket_is_measured_from_last_restart():
    h = make_history([
        ("A-1", "In Progress", "2026-03-02 09:00", "T", "m1", "x"),
        ("A-1", "To Do", "2026-03-03 09:00", "T", "m1", "x"),
        ("A-1", "In Progress", "2026-03-09 09:00", "T", "m1", "x"),
        ("A-1", "Done", "2026-03-11 15:00", "T", "m1", "x"),
    ])
    ws = build_worksheet(h, CAL)
    assert len(ws) == 1
    assert ws.loc[0, "Moved in Progress Date"] == pd.Timestamp("2026-03-09 09:00")
    assert ws.loc[0, "Working Days"] == 3


def test_ticket_never_in_progress_is_dropped():
    h = make_history([("A-2", "Done", "2026-03-02 09:00", "T", "m1", "x")])
    assert build_worksheet(h, CAL).empty


def test_open_ticket_has_no_done_date_and_no_days():
    h = make_history([("A-3", "In Progress", "2026-03-02 09:00", "T", "m1", "x")])
    ws = build_worksheet(h, CAL)
    assert pd.isna(ws.loc[0, "Moved to Done Date"]) and pd.isna(ws.loc[0, "Working Days"])
