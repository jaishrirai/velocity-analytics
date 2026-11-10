"""Step 1: from status change history to one row per ticket."""
from __future__ import annotations

import pandas as pd

from .workdays import business_days_between

WORKSHEET_COLUMNS = [
    "Key", "Epic Key", "Team", "Summary", "Story Points", "Assignee",
    "Moved in Progress Date", "Moved to Done Date", "Working Days",
]
SORT_COLUMNS = ["Team", "Epic Key", "Key", "ActivityDate"]


def sort_history(history: pd.DataFrame) -> pd.DataFrame:
    return history.sort_values(by=SORT_COLUMNS, ascending=[True, True, True, False]).reset_index(drop=True)


def build_worksheet(history: pd.DataFrame, calendar) -> pd.DataFrame:
    """One row per ticket that was ever moved to 'In Progress'.

    The in progress date is the LAST time it moved to 'In Progress' and the done date is the LAST time it
    moved to 'Done', so a reopened ticket is measured from its final restart.
    """
    ordered = sort_history(history)
    rows = []
    for key, group in ordered.groupby("Key"):
        in_progress = group.loc[group["To"] == "In Progress", "ActivityDate"].max()
        done = group.loc[group["To"] == "Done", "ActivityDate"].max()
        if pd.isna(in_progress):
            continue
        rows.append(
            {
                "Key": key,
                "Epic Key": group["Epic Key"].iloc[0],
                "Team": group["Team"].iloc[0],
                "Summary": group["Summary"].iloc[0],
                "Story Points": group["Story Points"].iloc[0],
                "Assignee": group["Assignee"].iloc[0],
                "Moved in Progress Date": in_progress,
                "Moved to Done Date": done,
            }
        )
    worksheet = pd.DataFrame(rows, columns=WORKSHEET_COLUMNS[:-1])
    days = [
        business_days_between(a, b, calendar)
        for a, b in zip(worksheet["Moved in Progress Date"], worksheet["Moved to Done Date"])
    ]
    worksheet["Working Days"] = pd.Series(days, index=worksheet.index, dtype=None)
    return worksheet
