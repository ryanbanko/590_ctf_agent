"""Draw the report's two scored-evaluation figures from aggregate.py's JSON.

Usage (matplotlib is only needed here, so it is not a project dependency):
    uv run --no-project --with matplotlib==3.11.2 python plot_figures.py \\
        evidence/scored/final_summary.json evidence/scored
"""

import argparse
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BAR = "#4a78a8"
MEAN = "#c0392b"


def style(ax):
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.spines[["top", "right"]].set_visible(False)


def label_bars(ax, bars, values):
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value - 0.04, f"{value:.1%}",
                ha="center", va="top", fontsize=10, color="white", fontweight="bold")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("summary", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())

    pass_at = summary["pass_at_k"]
    names = list(pass_at)
    values = [pass_at[name] for name in names]
    fig, ax = plt.subplots(figsize=(5.5, 2.7), dpi=150)
    label_bars(ax, ax.bar(names, values, width=0.55, color=BAR), values)
    style(ax)
    ax.set_ylabel("Challenges solved")
    ax.set_title(f"Figure 1. pass@k\n{len(summary['per_challenge'])} held-out challenges × {summary['trials']} trials",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out_dir / "figure1-passk.png")

    rates = summary["per_trial_solve_rates"]
    mean = statistics.fmean(rates)
    sd = statistics.stdev(rates) * 100
    fig, ax = plt.subplots(figsize=(5.5, 2.7), dpi=150)
    runs = [f"Run {i}" for i in range(1, len(rates) + 1)]
    label_bars(ax, ax.bar(runs, rates, width=0.55, color=BAR), rates)
    ax.axhline(mean, color=MEAN, linestyle="--", linewidth=1)
    style(ax)
    ax.set_ylabel("Challenges solved")
    ax.set_title(f"Figure 2. Solve rate per run\nmean {mean:.1%} (dashed), variance {sd**2:.1f} pp², SD {sd:.1f} pp",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out_dir / "figure2-solve-rate.png")


if __name__ == "__main__":
    main()
