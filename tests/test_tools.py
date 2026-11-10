import json

import pytest

from velocity_analytics import tools


def test_stage_velocity_is_json_friendly(result):
    out = tools.stage_velocity(result, "raw vault etl")
    json.dumps(out)
    assert out["stage"] == "Raw Vault ETL" and out["team"] == "Overall" and out["tickets"] > 0
    assert 0 < out["avg_working_days"] <= 20


def test_stage_velocity_for_one_team(result):
    out = tools.stage_velocity(result, "Raw Vault ETL", team="Finance Pod")
    assert out["team"] == "Finance Pod" and out["tickets"] > 0


def test_unknown_stage_or_team_raises_with_choices(result):
    with pytest.raises(ValueError, match="choose from"):
        tools.stage_velocity(result, "nope")
    with pytest.raises(ValueError, match="choose from"):
        tools.stage_velocity(result, "Raw Vault ETL", team="Nobody")


def test_slowest_stages_are_sorted(result):
    out = tools.slowest_stages(result, n=3)
    json.dumps(out)
    values = [r["avg_working_days"] for r in out]
    assert len(out) == 3 and values == sorted(values, reverse=True)
    assert out[0]["stage"] == "Business Vault ETL"
