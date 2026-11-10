from pathlib import Path

import pandas as pd
import pytest

from velocity_analytics import Config, load_history, load_lookups, run_velocity

ROOT = Path(__file__).resolve().parents[1]
TEAMS = ["Supply Chain Pod", "Finance Pod", "Commerce Pod", "Sales Pod"]


@pytest.fixture(scope="session")
def history():
    return load_history(ROOT / "data" / "synthetic" / "issue_history.csv")


@pytest.fixture(scope="session")
def lookups():
    return load_lookups(ROOT / "data" / "synthetic" / "lookup_tables.xlsx")


@pytest.fixture(scope="session")
def result(history, lookups):
    return run_velocity(history, lookups, Config(teams=TEAMS))


def make_history(rows):
    """rows: (key, to, when, team, assignee, summary)."""
    frame = pd.DataFrame(rows, columns=["Key", "To", "ActivityDate", "Team", "Assignee", "Summary"])
    frame["ActivityDate"] = pd.to_datetime(frame["ActivityDate"])
    frame["Epic Key"] = "E-1"
    frame["Story Points"] = 3.0
    return frame
