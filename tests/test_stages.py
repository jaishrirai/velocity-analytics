import pandas as pd

from conftest import make_history
from velocity_analytics.models import Lookups
from velocity_analytics.stages import classify, find_keyword_in_summary
from velocity_analytics.workdays import make_calendar
from velocity_analytics.worksheet import build_worksheet


def stage_of(summary, assignee, lookups):
    h = make_history([
        ("S-1", "In Progress", "2026-03-02 09:00", "T", assignee, summary),
        ("S-1", "Done", "2026-03-04 15:00", "T", assignee, summary),
    ])
    out = classify(build_worksheet(h, make_calendar("weekdays")), lookups)
    return out.iloc[0]


def test_first_keyword_in_table_order_wins():
    kw = pd.Series(["etl", "model", "qa"])
    assert find_keyword_in_summary("Orders - Model and ETL", kw) == "etl"
    assert find_keyword_in_summary("nothing here", kw) is None
    assert find_keyword_in_summary(float("nan"), kw) is None


def test_plain_mapping(lookups):
    row = stage_of("Orders - Raw Vault ETL", "Member 11", lookups)
    assert (row["Main Stage"], row["Sub Stage"], row["Data Enablement Stage"]) == ("Raw Vault", "ETL", "Raw Vault ETL")


def test_second_pass_uses_keyword_and_role(lookups):
    # 'prod' has no sub stage of its own; a Data Engineer doing it means ETL
    row = stage_of("Orders - Raw Vault Prod Release", "Member 11", lookups)
    assert row["Sub Stage"] == "ETL"


def test_third_pass_uses_main_stage_and_role(lookups):
    row = stage_of("Orders - Info Mart Build", "Member 13", lookups)  # no keyword; Data Modeler in Info Mart
    assert row["Sub Stage"] == "Model" and row["Data Enablement Stage"] == "Info Mart Model"


def test_unknown_stage_and_unknown_person(lookups):
    row = stage_of("Orders - Data Validation", "Somebody Else", lookups)
    assert row["Role"] == "Not Known" and row["Main Stage"] == "Not Found" and pd.isna(row["Data Enablement Stage"])


def test_blank_sub_stage_matches_a_mapping_row_with_blank_sub_stage(lookups):
    # Business Requirements has a mapping row with no sub stage. A PO/SM has no role rule, so the sub
    # stage stays blank and the blank row is the match.
    row = stage_of("Orders - Prod Business Requirements", "Member 16", lookups)
    assert row["Main Stage"] == "Business Requirements" and pd.isna(row["Sub Stage"])
    assert row["Data Enablement Stage"] == "BI/Business/Modeling Requirements/Documentation"


def test_person_with_two_roles_gives_one_row_per_role(lookups):
    h = make_history([
        ("D-1", "In Progress", "2026-03-02 09:00", "T", "Member 22", "Orders - Raw Vault ETL"),
        ("D-1", "Done", "2026-03-04 15:00", "T", "Member 22", "Orders - Raw Vault ETL"),
    ])
    out = classify(build_worksheet(h, make_calendar("weekdays")), lookups)
    assert sorted(out["Role"]) == ["Data Engineer", "Data Modeler"]
