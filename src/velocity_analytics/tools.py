"""Functions for an agent. They return plain, JSON friendly values so a model never does the arithmetic."""
from __future__ import annotations

import math

from .models import VelocityResult


def _num(value):
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else round(float(value), 2)


def _stage_rows(result: VelocityResult):
    table = result.average_velocity
    return table[table["Main Stage"] != "Average"]


def stage_velocity(result: VelocityResult, stage: str, team: str | None = None) -> dict:
    """Average working days for one Data Enablement Stage, overall or for one team."""
    rows = _stage_rows(result)
    match = rows[rows["Data Enablement Stage"].str.lower() == stage.strip().lower()]
    if match.empty:
        raise ValueError(f"unknown stage {stage!r}; choose from {rows['Data Enablement Stage'].tolist()}")
    column = team or "Overall"
    if column not in match.columns:
        raise ValueError(f"unknown team {team!r}; choose from {result.teams}")
    stage_name = match.iloc[0]["Data Enablement Stage"]
    refined = result.refined[result.refined["Data Enablement Stage"] == stage_name]
    if team:
        refined = refined[refined["Team"] == team]
    return {
        "stage": stage_name,
        "team": team or "Overall",
        "avg_working_days": _num(match.iloc[0][column]),
        "tickets": int(len(refined)),
    }


def slowest_stages(result: VelocityResult, n: int = 3, team: str | None = None) -> list:
    """The n stages with the highest average working days (stages with no data are skipped)."""
    column = team or "Overall"
    rows = _stage_rows(result)
    if column not in rows.columns:
        raise ValueError(f"unknown team {team!r}; choose from {result.teams}")
    ranked = rows.dropna(subset=[column]).sort_values(column, ascending=False).head(n)
    return [
        {"stage": r["Data Enablement Stage"], "main_stage": r["Main Stage"], "avg_working_days": _num(r[column])}
        for _, r in ranked.iterrows()
    ]
