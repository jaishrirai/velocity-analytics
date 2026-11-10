"""Bar chart of average working days per stage (overall and per team). Needs: pip install -e ".[charts]"

    python demo/make_chart.py          # writes output/average_days_by_stage.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless, nothing opens on screen
import matplotlib.pyplot as plt

from velocity_analytics import Config, load_history, load_lookups, run_velocity

ROOT = Path(__file__).resolve().parents[1]


def main(out: Path | None = None) -> Path:
    data = ROOT / "data" / "synthetic"
    result = run_velocity(load_history(data / "issue_history.csv"), load_lookups(data / "lookup_tables.xlsx"), Config())
    table = result.average_velocity.iloc[:-1]
    labels = [s.replace("BI/Business/Modeling Requirements/Documentation", "Requirements and docs") for s in table["Data Enablement Stage"]]

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.barh(labels, table["Overall"], color="#4C78A8")
    ax.invert_yaxis()
    ax.set_xlabel("Average working days per ticket")
    ax.set_title("Average working days by delivery stage (synthetic data)")
    for y, value in enumerate(table["Overall"]):
        if value == value:
            ax.text(value + 0.1, y, f"{value:.1f}", va="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    out = out or ROOT / "output" / "average_days_by_stage.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    return out


if __name__ == "__main__":
    print("wrote", main())
