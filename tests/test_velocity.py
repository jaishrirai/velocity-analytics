import pandas as pd

from conftest import TEAMS
from velocity_analytics import Config, run_velocity


def test_refined_rows_respect_the_outlier_rule_and_need_a_stage(result):
    assert (result.refined["Working Days"] <= 20).all()
    assert result.refined["Data Enablement Stage"].notna().all()
    assert len(result.refined) < len(result.worksheet)


def test_lower_cap_keeps_fewer_rows(history, lookups):
    strict = run_velocity(history, lookups, Config(teams=TEAMS, max_working_days=5))
    assert 0 < len(strict.refined) < 209


def test_table_shape_and_order(result, lookups):
    table = result.average_velocity
    assert list(table.columns) == ["Main Stage", "Data Enablement Stage", "Overall", *TEAMS]
    assert len(table) == len(lookups.summary_sequence) + 1
    assert list(table["Data Enablement Stage"][:-1]) == list(lookups.summary_sequence["Data Enablement Stage"])
    assert table.iloc[-1]["Main Stage"] == "Average"


def test_stage_average_is_the_plain_mean_of_its_tickets(result):
    stage = "Raw Vault ETL"
    expected = result.refined[result.refined["Data Enablement Stage"] == stage]["Working Days"].mean()
    got = result.average_velocity.set_index("Data Enablement Stage").loc[stage, "Overall"]
    assert abs(got - expected) < 1e-9


def test_average_row_is_the_mean_of_the_stage_averages(result):
    table = result.average_velocity
    assert abs(table.iloc[-1]["Overall"] - table.iloc[:-1]["Overall"].mean()) < 1e-9


def test_teams_default_to_the_ones_in_the_data(history, lookups):
    assert run_velocity(history, lookups).teams == sorted(TEAMS)


def test_done_window_filters_tickets(history, lookups):
    early = run_velocity(history, lookups, Config(teams=TEAMS, done_to="2026-02-28"))
    assert 0 < len(early.worksheet) < 255
    assert (early.worksheet["Moved to Done Date"] <= pd.Timestamp("2026-03-01")).all()


def test_empty_history_does_not_crash(history, lookups):
    empty = run_velocity(history.iloc[0:0], lookups, Config(teams=TEAMS))
    assert empty.worksheet.empty and len(empty.average_velocity) == len(lookups.summary_sequence) + 1
