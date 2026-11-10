"""Read the inputs and write the output workbook."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import Lookups, VelocityResult

REQUIRED_HISTORY_COLUMNS = ["Key", "Summary", "ActivityDate", "To", "Team", "Assignee"]
OPTIONAL_HISTORY_COLUMNS = ["Epic Key", "Story Points", "From", "Current Status", "Issue Created Time"]
LOOKUP_SHEETS = ["roles", "keywords", "stages", "keywords2", "mainstage_role", "mapping", "summary_sequence"]


def validate_history(history: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_HISTORY_COLUMNS if c not in history.columns]
    if missing:
        raise ValueError(f"issue history is missing columns: {missing}")
    history = history.copy()
    for column in OPTIONAL_HISTORY_COLUMNS:
        if column not in history.columns:
            history[column] = pd.NA if column != "Story Points" else float("nan")
    for column in ("ActivityDate", "Issue Created Time"):
        if column in history.columns:
            values = pd.to_datetime(history[column], errors="coerce")
            if getattr(values.dt, "tz", None) is not None:
                values = values.dt.tz_localize(None)
            history[column] = values
    return history


def load_history(path) -> pd.DataFrame:
    """Status change history: one row per status change of a ticket (csv or xlsx)."""
    path = Path(path)
    frame = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    return validate_history(frame)


def load_lookups(path) -> Lookups:
    sheets = pd.read_excel(path, sheet_name=None)
    missing = [s for s in LOOKUP_SHEETS if s not in sheets]
    if missing:
        raise ValueError(f"lookup workbook is missing sheets: {missing}")
    return Lookups(**{name: sheets[name] for name in LOOKUP_SHEETS})


def write_output(result: VelocityResult, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        result.average_velocity.to_excel(writer, sheet_name="average_velocity", index=False)
        result.refined.to_excel(writer, sheet_name="worksheet_refined", index=False)
        result.worksheet.to_excel(writer, sheet_name="worksheet", index=False)
    return path
