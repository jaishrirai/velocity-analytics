from pathlib import Path

import pandas as pd
import pytest

from velocity_analytics import load_history, write_output
from velocity_analytics.cli import main
from velocity_analytics.io import validate_history


def test_missing_columns_are_reported():
    with pytest.raises(ValueError, match="missing columns"):
        validate_history(pd.DataFrame({"Key": ["A-1"]}))


def test_optional_columns_are_added():
    frame = pd.DataFrame({"Key": ["A-1"], "Summary": ["x"], "ActivityDate": ["2026-03-02"], "To": ["Done"], "Team": ["T"], "Assignee": ["m"]})
    out = validate_history(frame)
    assert "Epic Key" in out.columns and out["ActivityDate"].dtype.kind == "M"


def test_output_workbook_has_three_sheets(result, tmp_path):
    path = write_output(result, tmp_path / "out.xlsx")
    assert list(pd.read_excel(path, sheet_name=None)) == ["average_velocity", "worksheet_refined", "worksheet"]


def test_cli_runs(tmp_path, capsys):
    data = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    args = ["--history", str(data / "issue_history.csv"), "--lookups", str(data / "lookup_tables.xlsx"), "--out", str(tmp_path / "o.xlsx")]
    assert main(args) == 0
    assert "ticket rows" in capsys.readouterr().out
