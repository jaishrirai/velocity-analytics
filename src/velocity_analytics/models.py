"""Plain containers passed between the steps."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Lookups:
    """The seven lookup tables that turn a ticket summary into a delivery stage."""

    roles: pd.DataFrame            # Assignee, Role
    keywords: pd.DataFrame         # Keyword, Sub Stage
    stages: pd.DataFrame           # Keyword, Main Stage
    keywords2: pd.DataFrame        # Keyword, Role, Sub Stage 2
    mainstage_role: pd.DataFrame   # Main Stage, Role, Sub Stage 3
    mapping: pd.DataFrame          # Main Stage, Sub Stage, Data Enablement Stage
    summary_sequence: pd.DataFrame  # Main Stage, Data Enablement Stage (output order)


@dataclass
class VelocityResult:
    worksheet: pd.DataFrame          # one row per ticket and role, every intermediate column
    refined: pd.DataFrame            # rows that count towards the averages
    average_velocity: pd.DataFrame   # average working days per stage, overall and per team
    teams: list
