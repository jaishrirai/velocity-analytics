"""velocity-run: issue history + lookup tables in, output workbook out."""
from __future__ import annotations

import argparse

from .config import Config
from .engine import run_velocity
from .io import load_history, load_lookups, write_output


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Average working days per delivery stage and team.")
    p.add_argument("--history", default="data/synthetic/issue_history.csv")
    p.add_argument("--lookups", default="data/synthetic/lookup_tables.xlsx")
    p.add_argument("--out", default="output/velocity_output.xlsx")
    p.add_argument("--teams", help="comma separated; default is every team in the data")
    p.add_argument("--calendar", default="us_federal", choices=["us_federal", "weekdays"])
    p.add_argument("--max-days", type=int, default=20)
    p.add_argument("--done-from")
    p.add_argument("--done-to")
    a = p.parse_args(argv)

    config = Config(
        teams=[t.strip() for t in a.teams.split(",")] if a.teams else None,
        max_working_days=a.max_days,
        holiday_calendar=a.calendar,
        done_from=a.done_from,
        done_to=a.done_to,
    )
    result = run_velocity(load_history(a.history), load_lookups(a.lookups), config)
    path = write_output(result, a.out)
    print(f"{len(result.worksheet)} ticket rows, {len(result.refined)} used for averages. Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
