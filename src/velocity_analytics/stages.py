"""Step 2: turn the ticket summary and the assignee role into a delivery stage.

The chain, for every ticket:
  1. Role            from the assignee (people missing from the roles table become 'Not Known').
  2. Main Stage      first stage keyword found in the summary (else 'Not Found').
  3. Sub Stage       first sub stage keyword found in the summary (else 'Not known'),
                     then the keywords2 table (keyword + role), then the mainstage_role table
                     (main stage + role), each only if the previous one left it empty.
  4. Data Enablement Stage   looked up from (Main Stage, Sub Stage) in the mapping table.
Keyword matching is a lower case substring match and the first keyword in table order wins.
"""
from __future__ import annotations

import pandas as pd

from .models import Lookups


def find_keyword_in_summary(summary, keywords: pd.Series):
    """First keyword (in table order) that appears inside the summary, or None."""
    text = summary.lower() if isinstance(summary, str) else ""
    for keyword in keywords:
        if pd.notna(keyword) and str(keyword).lower() in text:
            return keyword
    return None


def _blank(value) -> bool:
    return pd.isna(value) or value == "" or value == "Not known"


def _clean(value):
    return None if pd.isna(value) else value


def classify(worksheet: pd.DataFrame, lookups: Lookups) -> pd.DataFrame:
    ws = worksheet.merge(lookups.roles[["Assignee", "Role"]], on="Assignee", how="left")
    ws["Role"] = ws["Role"].fillna("Not Known")

    ws["status_keyword"] = ws["Summary"].apply(lambda s: find_keyword_in_summary(s, lookups.stages["Keyword"]))
    ws["role_keyword"] = ws["Summary"].apply(lambda s: find_keyword_in_summary(s, lookups.keywords["Keyword"]))

    stage_of_keyword = dict(zip(lookups.stages["Keyword"], lookups.stages["Main Stage"]))
    ws["Main Stage"] = ws["status_keyword"].apply(lambda k: stage_of_keyword.get(k, "Not Found"))

    sub_stage_of_keyword = dict(zip(lookups.keywords["Keyword"], lookups.keywords["Sub Stage"]))
    ws["Sub Stage"] = ws["role_keyword"].apply(lambda k: sub_stage_of_keyword.get(k, "Not known"))

    def second_pass(row):
        if _blank(row["Sub Stage"]):
            hit = lookups.keywords2[
                (lookups.keywords2["Role"] == row["Role"]) & (lookups.keywords2["Keyword"] == row["role_keyword"])
            ]
            if not hit.empty:
                return hit.iloc[0]["Sub Stage 2"]
        return row["Sub Stage"]

    def third_pass(row):
        if _blank(row["Sub Stage"]):
            hit = lookups.mainstage_role[
                (lookups.mainstage_role["Main Stage"] == row["Main Stage"]) & (lookups.mainstage_role["Role"] == row["Role"])
            ]
            if not hit.empty:
                return hit.iloc[0]["Sub Stage 3"]
        return row["Sub Stage"]

    if len(ws):
        ws["Sub Stage"] = ws.apply(second_pass, axis=1)
        ws["Sub Stage"] = ws.apply(third_pass, axis=1)

    stage_of_pair = {
        (_clean(m), _clean(s)): d
        for m, s, d in zip(
            lookups.mapping["Main Stage"], lookups.mapping["Sub Stage"], lookups.mapping["Data Enablement Stage"]
        )
    }
    ws["Data Enablement Stage"] = [
        stage_of_pair.get((_clean(m), _clean(s)), float("nan")) for m, s in zip(ws["Main Stage"], ws["Sub Stage"])
    ]
    return ws
