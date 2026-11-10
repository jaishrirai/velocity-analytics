"""Seeded synthetic data for the fictional company 'Larkspur Synthetic Group'.

Writes, into data/synthetic/:
  issue_history.csv     one row per status change of a ticket
  lookup_tables.xlsx    roles, keywords, stages, keywords2, mainstage_role, mapping, summary_sequence

    python scripts/generate_synthetic_data.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

SEED = 7
OUT = Path(__file__).resolve().parents[1] / "data" / "synthetic"
BDAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())

TEAMS = ["Supply Chain Pod", "Finance Pod", "Commerce Pod", "Sales Pod"]
TEAM_SPEED = {"Supply Chain Pod": 1.0, "Finance Pod": 0.85, "Commerce Pod": 1.2, "Sales Pod": 0.95}
TOPICS = {
    "Supply Chain Pod": ["Purchase Orders", "Shipments", "Supplier Master", "Warehouse Stock", "Carrier Lanes"],
    "Finance Pod": ["Ledger Entries", "Invoices Payable", "Budget Lines", "Cost Centers", "Receivables Ageing"],
    "Commerce Pod": ["Web Orders", "Product Catalog", "Returns", "Basket Events", "Promotions"],
    "Sales Pod": ["Pipeline", "Quotes", "Customer Accounts", "Targets", "Territories"],
}

# (summary suffix, typical business days, roles that usually do it)
TEMPLATES = [
    ("Discovery", 4, ["BI Engineer"]),
    ("Staging ETL", 6, ["Data Engineer"]),
    ("Staging Model", 5, ["Data Modeler"]),
    ("Staging QA", 3, ["QA / MDM Analyst"]),
    ("Business Requirements", 5, ["BI Engineer", "PO/SM"]),
    ("Raw Vault Model", 6, ["Data Modeler"]),
    ("Raw Vault ETL", 8, ["Data Engineer"]),
    ("Raw Vault QA", 4, ["QA / MDM Analyst"]),
    ("Business Vault Model", 7, ["Data Modeler"]),
    ("Business Vault ETL", 9, ["Data Engineer"]),
    ("Business Vault QA", 4, ["QA / MDM Analyst"]),
    ("Info Mart Model", 6, ["Data Modeler"]),
    ("Info Mart ETL", 8, ["Data Engineer"]),
    ("Info Mart QA", 4, ["QA / MDM Analyst"]),
    ("Dashboard Build", 7, ["BI Engineer"]),
    ("Visual Report", 5, ["BI Engineer"]),
    ("Prod Release Deployment", 3, ["Data Engineer"]),
    ("Data Validation", 3, ["QA / MDM Analyst"]),
]

# Members per team: Data Engineer x2, Data Modeler, QA / MDM Analyst, BI Engineer, PO/SM.
MEMBER_ROLES = ["Data Engineer", "Data Engineer", "Data Modeler", "QA / MDM Analyst", "BI Engineer", "PO/SM"]
EXTRA_ROLES = {"Member 22": "Data Modeler", "Member 45": "QA / MDM Analyst"}  # two roles for one person


def members():
    out = {}
    for t, team in enumerate(TEAMS, start=1):
        out[team] = [(f"Member {t}{i}", role) for i, role in enumerate(MEMBER_ROLES, start=1)]
    return out


def lookup_tables() -> dict:
    keywords = [
        ("etl", "ETL"), ("model", "Model"), ("dashboard", "Build Visualization"), ("qa", "QA"), ("prod", None),
        ("deploy", None), ("requirement", "Business Requirements"), ("discover", "Discovery"),
        ("visual", "Build Visualization"), ("tableau", None), ("data", None), ("BV", "Business Vault"),
        ("elt", "ETL"), ("Business Vault Model", "Business Vault Modeling"), ("Raw Vault QA", "Raw Vault QA"),
        ("Data Validation", "QA"), ("Raw Vault Model", "Raw Vault Model"), ("Business Vault QA", "Business Vault QA"),
    ]
    stages = [
        ("info", "Info Mart"), ("business require", "Business Requirements"), ("business", "Business Vault"),
        ("raw", "Raw Vault"), ("stag", "Staging"), ("bi", "BI"), ("dashboard", "BI"), ("visual", "BI"),
        ("requirement", "Business Requirements"), ("discover", "Staging"), ("bronze", "Staging"),
        ("BV", "Business Vault"), ("RV", "Raw Vault"), ("Business Vault", "Business Vault"), ("Raw Vault", "Raw Vault"),
    ]
    keywords2 = [
        ("etl", "Data Engineer", "ETL"), ("model", "Data Modeler", "Model"), ("dashboard", "BI Engineer", "Build Visualization"),
        ("qa", "QA / MDM Analyst", "QA"), ("prod", "Data Engineer", "ETL"), ("deploy", "Data Engineer", "ETL"),
        ("requirement", "BI Engineer", "Business Requirements"), ("visual", "BI Engineer", "Build Visualization"),
        ("prod", "Data Modeler", "Model"), ("deploy", "Data Modeler", "Model"), ("data", "Data Engineer", "ETL"),
        ("tableau", "BI Engineer", "Build Visualization"), ("tableau", "QA / MDM Analyst", "QA"), ("elt", "Data Engineer", "ETL"),
    ]
    mainstage_role = [
        ("BI", "BI Engineer", "Build Visualization"), ("BI", "Data Engineer", None), ("BI", "Data Modeler", None),
        ("BI", "PO/SM", None), ("BI", "QA / MDM Analyst", None),
        ("Business Requirements", "BI Engineer", "Business Requirements"),
        ("Business Requirements", "Data Engineer", "Business Requirements"),
        ("Business Requirements", "Data Modeler", "Business Requirements"),
        ("Business Vault", "BI Engineer", "Build Visualization"), ("Business Vault", "Data Engineer", "ETL"),
        ("Business Vault", "Data Modeler", "Model"), ("Business Vault", "QA / MDM Analyst", "QA"),
        ("Info Mart", "BI Engineer", "Build Visualization"), ("Info Mart", "Data Engineer", "ETL"),
        ("Info Mart", "Data Modeler", "Model"), ("Info Mart", "QA / MDM Analyst", "QA"),
        ("Raw Vault", "BI Engineer", "Build Visualization"), ("Raw Vault", "Data Engineer", "ETL"),
        ("Raw Vault", "Data Modeler", "Model"), ("Raw Vault", "QA / MDM Analyst", "QA"),
        ("Staging", "BI Engineer", "Discovery"), ("Staging", "Data Engineer", "Staging Area (Bronze)"),
        ("Staging", "Data Modeler", "Model"),
    ]
    br = "BI/Business/Modeling Requirements/Documentation"
    mapping = [
        ("Staging", "Discovery", "Discovery"), ("Staging", "ETL", "Staging Area (Bronze)"),
        ("Staging", "Model", "Modeling"), ("Staging", "QA", "Staging QA"),
        ("Business Requirements", None, br), ("Raw Vault", "Model", "Raw Vault Model"),
        ("Raw Vault", "ETL", "Raw Vault ETL"), ("Raw Vault", "QA", "Raw Vault QA"),
        ("Business Vault", "Model", "Business Vault Model"), ("Business Vault", "ETL", "Business Vault ETL"),
        ("Business Vault", "QA", "Business Vault QA"), ("Info Mart", "Model", "Info Mart Model"),
        ("Info Mart", "ETL", "Info Mart ETL"), ("Info Mart", "QA", "Info Mart QA"),
        ("BI", "Build Visualization", "Build Visualization"),
        ("Business Requirements", "Business Requirements", br),
    ]
    sequence = [
        ("Staging", "Discovery"), ("Staging", "Staging Area (Bronze)"), ("Staging", "Staging QA"), ("Staging", "Modeling"),
        ("Business Requirements", br), ("Raw Vault", "Raw Vault Model"), ("Raw Vault", "Raw Vault ETL"),
        ("Raw Vault", "Raw Vault QA"), ("Business Vault", "Business Vault Model"), ("Business Vault", "Business Vault ETL"),
        ("Business Vault", "Business Vault QA"), ("Info Mart", "Info Mart Model"), ("Info Mart", "Info Mart ETL"),
        ("Info Mart", "Info Mart QA"), ("BI", "Build Visualization"),
    ]
    roles = [(name, role) for team in members().values() for name, role in team]
    roles += [(name, role) for name, role in EXTRA_ROLES.items()]
    return {
        "roles": pd.DataFrame(roles, columns=["Assignee", "Role"]),
        "keywords": pd.DataFrame(keywords, columns=["Keyword", "Sub Stage"]),
        "stages": pd.DataFrame(stages, columns=["Keyword", "Main Stage"]),
        "keywords2": pd.DataFrame(keywords2, columns=["Keyword", "Role", "Sub Stage 2"]),
        "mainstage_role": pd.DataFrame(mainstage_role, columns=["Main Stage", "Role", "Sub Stage 3"]),
        "mapping": pd.DataFrame(mapping, columns=["Main Stage", "Sub Stage", "Data Enablement Stage"]),
        "summary_sequence": pd.DataFrame(sequence, columns=["Main Stage", "Data Enablement Stage"]),
    }


def at_time(day, rng, lo, hi):
    return pd.Timestamp(day).normalize() + pd.Timedelta(hours=int(rng.integers(lo, hi)), minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))


def to_business_day(ts):
    """Move a weekend or holiday timestamp to the next business day, keeping the time of day."""
    day = ts.normalize()
    if BDAY.is_on_offset(day):
        return ts
    return day + BDAY * 1 + (ts - day)


def build_history(rng) -> pd.DataFrame:
    team_members = members()
    rows = []
    issue_no = 1000
    epic_no = 100
    first_day = pd.Timestamp("2026-01-05")

    def row(key, summary, when, frm, to, current, created, points, epic, team, who):
        rows.append({"Key": key, "Summary": summary, "ActivityDate": when, "From": frm, "To": to,
                     "Current Status": current, "Issue Created Time": created, "Story Points": points,
                     "Epic Key": epic, "Team": team, "Assignee": who})

    for team in TEAMS:
        for topic in TOPICS[team]:
            epic_no += 1
            epic = f"LRK-{epic_no}"
            chosen = rng.choice(len(TEMPLATES), size=12, replace=False)
            for idx in sorted(chosen):
                suffix, base, roles = TEMPLATES[idx]
                issue_no += 1
                key = f"LRK-{issue_no}"
                summary = f"{topic} - {suffix}"
                pool = [m for m in team_members[team] if m[1] in roles] or team_members[team]
                who = pool[int(rng.integers(len(pool)))][0]
                points = int(rng.choice([1, 2, 3, 5, 8], p=[0.1, 0.3, 0.3, 0.2, 0.1]))
                start_day = first_day + BDAY * int(rng.integers(0, 105))
                created = at_time(start_day - pd.Timedelta(days=int(rng.integers(5, 60))), rng, 8, 17)

                kind = rng.random()
                if kind < 0.03:  # closed without any work
                    row(key, summary, at_time(start_day, rng, 9, 17), "To Do", "Done", "Done", created, points, epic, team, who)
                    continue

                start = at_time(start_day, rng, 8, 11)
                row(key, summary, start, "To Do", "In Progress", None, created, points, epic, team, who)
                if rng.random() < 0.10:  # reopened: measured from the last restart
                    back = start + pd.Timedelta(days=1, hours=5)
                    row(key, summary, back, "In Progress", "To Do", None, created, points, epic, team, who)
                    start = at_time(back.normalize() + BDAY * int(rng.integers(1, 4)), rng, 8, 11)
                    row(key, summary, start, "To Do", "In Progress", None, created, points, epic, team, who)

                days = base * TEAM_SPEED[team] * float(np.exp(rng.normal(0, 0.35)))
                if rng.random() < 0.05:
                    days *= 4  # outlier, dropped by the 20 day rule
                days = max(1, int(round(days)))
                done_day = start.normalize() + BDAY * (days - 1)
                done = at_time(done_day, rng, 13, 18)
                if days == 1:
                    done = max(done, start + pd.Timedelta(hours=3))
                qa = min(to_business_day(start + (done - start) * 0.6), done)
                accept = min(to_business_day(start + (done - start) * 0.85), done)
                accept = max(accept, qa)

                if kind < 0.08:  # still open
                    row(key, summary, qa, "In Progress", "Ready for QA", "Ready for QA", created, points, epic, team, who)
                    continue
                row(key, summary, qa, "In Progress", "Ready for QA", "Done", created, points, epic, team, who)
                row(key, summary, accept, "Ready for QA", "Ready for Acceptance", "Done", created, points, epic, team, who)
                row(key, summary, done, "Ready for Acceptance", "Done", "Done", created, points, epic, team, who)

    frame = pd.DataFrame(rows)
    # rows of an open ticket get its real current status
    frame["Current Status"] = frame.groupby("Key")["To"].transform("last").where(frame["Current Status"].isna(), frame["Current Status"])
    frame = frame.sort_values(["Key", "ActivityDate"], ascending=[True, False]).reset_index(drop=True)
    frame["Story Points"] = frame["Story Points"].astype(float)
    return frame


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    history = build_history(rng)
    history.to_csv(OUT / "issue_history.csv", index=False)
    with pd.ExcelWriter(OUT / "lookup_tables.xlsx", engine="openpyxl") as writer:
        for name, table in lookup_tables().items():
            table.to_excel(writer, sheet_name=name, index=False)
    print(f"{history['Key'].nunique()} tickets, {len(history)} status changes -> {OUT}")


if __name__ == "__main__":
    main()
