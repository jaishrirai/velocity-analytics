"""The whole pipeline."""
from __future__ import annotations

import pandas as pd

from .config import Config
from .io import validate_history
from .models import Lookups, VelocityResult
from .stages import classify
from .velocity import average_velocity, refine
from .workdays import make_calendar
from .worksheet import build_worksheet


def _within_done_window(history: pd.DataFrame, done_from, done_to) -> pd.DataFrame:
    if not done_from and not done_to:
        return history
    last_done = history[history["To"] == "Done"].groupby("Key")["ActivityDate"].max()
    if done_from:
        last_done = last_done[last_done >= pd.Timestamp(done_from)]
    if done_to:
        last_done = last_done[last_done.dt.normalize() <= pd.Timestamp(done_to)]
    return history[history["Key"].isin(last_done.index)]


def run_velocity(history: pd.DataFrame, lookups: Lookups, config: Config | None = None) -> VelocityResult:
    config = config or Config()
    history = _within_done_window(validate_history(history), config.done_from, config.done_to)

    teams = config.teams
    if teams is None:
        teams = sorted(t for t in history["Team"].dropna().unique() if t != "Unknown")

    worksheet = build_worksheet(history, make_calendar(config.holiday_calendar))
    worksheet = classify(worksheet, lookups)
    refined = refine(worksheet, config.max_working_days)
    table = average_velocity(refined, lookups.summary_sequence, list(teams))
    return VelocityResult(worksheet=worksheet, refined=refined, average_velocity=table, teams=list(teams))
