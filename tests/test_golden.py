"""The package must reproduce the original single script logic, value for value.

tests/golden/golden_output.xlsx was produced by running the original prototype script (with its ticket
fetching replaced by this synthetic issue history) and saving its three result tables.
"""
from pathlib import Path

import pandas as pd
import pytest

GOLDEN = Path(__file__).parent / "golden" / "golden_output.xlsx"


@pytest.mark.parametrize(
    "attribute, sheet",
    [("average_velocity", "average_velocity"), ("refined", "worksheet_refined"), ("worksheet", "worksheet")],
)
def test_matches_golden(result, attribute, sheet):
    expected = pd.read_excel(GOLDEN, sheet_name=sheet)
    got = getattr(result, attribute).reset_index(drop=True)
    got = got.astype(object).where(got.notna(), float("nan"))  # Excel stores a missing value as blank, which reads back as NaN
    expected = expected.astype(object).where(expected.notna(), float("nan"))
    pd.testing.assert_frame_equal(got, expected, check_dtype=False)
