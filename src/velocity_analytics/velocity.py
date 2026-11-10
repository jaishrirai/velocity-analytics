"""Step 3: keep the usable rows and average the working days by stage and team."""
from __future__ import annotations

import pandas as pd

REFINED_COLUMNS = [
    "Key", "Epic Key", "Summary", "Team", "Role", "Story Points",
    "Moved to Done Date", "Main Stage", "Working Days", "Data Enablement Stage",
]


def refine(worksheet: pd.DataFrame, max_working_days: int = 20) -> pd.DataFrame:
    """Keep rows with a known stage and at most `max_working_days` working days (no outliers, no open tickets)."""
    days = pd.to_numeric(worksheet["Working Days"], errors="coerce")
    keep = (days <= max_working_days) & worksheet["Data Enablement Stage"].notna()
    return worksheet.loc[keep, REFINED_COLUMNS]


def average_velocity(refined: pd.DataFrame, sequence: pd.DataFrame, teams: list) -> pd.DataFrame:
    """Average working days per (Main Stage, Data Enablement Stage), overall and per team.

    Rows follow `sequence`. The last row, 'Average', is the mean of the column above it (stages with
    no data are skipped), not a ticket weighted average.
    """
    nan = float("nan")
    columns = {"Main Stage": [], "Data Enablement Stage": [], "Overall": []}
    for team in teams:
        columns[team] = []

    for _, row in sequence.iterrows():
        subset = refined[
            (refined["Main Stage"] == row["Main Stage"]) & (refined["Data Enablement Stage"] == row["Data Enablement Stage"])
        ]
        columns["Main Stage"].append(row["Main Stage"])
        columns["Data Enablement Stage"].append(row["Data Enablement Stage"])
        columns["Overall"].append(subset["Working Days"].mean() if not subset.empty else nan)
        for team in teams:
            team_rows = subset[subset["Team"] == team]
            columns[team].append(team_rows["Working Days"].mean() if not team_rows.empty else nan)

    table = pd.DataFrame(columns)
    averages = {"Main Stage": "Average", "Data Enablement Stage": "Average"}
    for name in ["Overall", *teams]:
        averages[name] = table[name].mean()
    table.loc[len(table)] = averages
    return table
