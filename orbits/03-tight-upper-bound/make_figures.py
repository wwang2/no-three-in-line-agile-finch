"""
make_figures.py — generate narrative.png and results.png for orbit 03.

narrative.png: a clean 1-panel visualization of the pigeonhole proof —
"21 points in 10 rows forces some row to have 3, and 3 on a horizontal
line is collinear" — rendered on the actual 10x10 grid, with the
forced collision highlighted.

results.png: a canonical 2x2 grid (per research/style.md):
  (a) search-space size comparison (log scale)
  (b) branches-explored comparison (B&B at target=21 vs 20)
  (c) the 20-point witness from solution.py on the grid
  (d) metric panel: committed metric = -20.
"""

from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


HERE = Path(__file__).resolve().parent
FIGDIR = HERE / "figures"
FIGDIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Style block (matches research/style.md).
# ---------------------------------------------------------------------------


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "medium",
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.grid": True,
    "grid.alpha": 0.15,
    "grid.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlepad": 10.0,
    "axes.labelpad": 6.0,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.frameon": False,
    "legend.borderpad": 0.3,
    "legend.handletextpad": 0.5,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "figure.constrained_layout.use": True,
})


COLORS = {
    "baseline": "#888888",
    "method_good": "#4C72B0",   # the 20-point valid set
    "method_bad": "#C44E52",    # the forced-collision row
    "highlight": "#DD8452",
    "accent": "#55A868",
}


N = 10


PARENT_POINTS = [
    (0, 0), (0, 9), (1, 3), (1, 5), (2, 3), (2, 4),
    (3, 7), (3, 8), (4, 1), (4, 7), (5, 2), (5, 8),
    (6, 1), (6, 2), (7, 5), (7, 6), (8, 4), (8, 6),
    (9, 0), (9, 9),
]


# ---------------------------------------------------------------------------
# Helper: draw a single 10x10 board in a given axis.
# ---------------------------------------------------------------------------


def draw_grid(ax, title=None):
    ax.set_xlim(-0.6, N - 0.4)
    ax.set_ylim(-0.6, N - 0.4)
    # Grid lines every 1.
    for k in range(N):
        ax.axhline(k, color="#cccccc", lw=0.6, zorder=1)
        ax.axvline(k, color="#cccccc", lw=0.6, zorder=1)
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_aspect("equal")
    ax.grid(False)
    ax.invert_yaxis()
    ax.set_xlabel("column")
    ax.set_ylabel("row")
    if title is not None:
        ax.set_title(title)
    # Keep only left / bottom spines faintly.
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#888888")
        ax.spines[side].set_linewidth(0.8)


# ---------------------------------------------------------------------------
# narrative.png — the pigeonhole argument.
# ---------------------------------------------------------------------------


def make_narrative(out_path: Path):
    # Construct a "forced-collision" 21-point attempt by spreading 21 points
    # as evenly as possible: two per row for 9 rows, and three in the last
    # row (r = 9). Columns are chosen so the rows below r = 9 are actually
    # collinearity-free — we want the figure to show the one forced
    # violation, not ten of them. For the top 9 rows we reuse columns from
    # the parent's valid 20-point config. The offending row is r = 9 with
    # columns 0, 5, 9 — three points on y = 9.
    points_21 = []
    # For rows 0..8, pick the parent's points restricted to those rows.
    parent_by_row: dict[int, list[int]] = {r: [] for r in range(N)}
    for r, c in PARENT_POINTS:
        parent_by_row[r].append(c)
    for r in range(9):
        for c in sorted(parent_by_row[r])[:2]:
            points_21.append((r, c))
    # Row 9: instead of 2, force 3 (0, 5, 9). This is the pigeonhole-forced
    # overflow row.
    forced_row = 9
    forced_cols = [0, 5, 9]
    for c in forced_cols:
        points_21.append((forced_row, c))
    assert len(points_21) == 21, len(points_21)

    fig, ax = plt.subplots(figsize=(8.0, 8.5))
    draw_grid(ax, title=None)
    fig.suptitle(
        "Pigeonhole: 21 points on 10 rows force >= 3 in some row\n"
        "21 / 10  =>  ceil(21/10) = 3  =>  three collinear on a horizontal line",
        fontsize=13, y=1.02,
    )

    # Plot the 18 "safe" points from rows 0..8.
    safe = [(r, c) for (r, c) in points_21 if r != forced_row]
    xs = [c for (r, c) in safe]
    ys = [r for (r, c) in safe]
    ax.scatter(
        xs, ys, s=120, facecolor=COLORS["method_good"],
        edgecolor="white", linewidth=1.1, zorder=3,
        label="18 points, rows 0–8 (≤ 2 per row)",
    )

    # Plot the forced-row points in the violation color.
    fr_xs = forced_cols
    fr_ys = [forced_row] * 3
    ax.scatter(
        fr_xs, fr_ys, s=200, facecolor=COLORS["method_bad"],
        edgecolor="white", linewidth=1.5, zorder=4,
        label="3 points forced into row 9 — collinear",
    )
    # Draw the offending line through y = 9 across the board.
    ax.plot(
        [-0.4, N - 0.6], [forced_row, forced_row],
        color=COLORS["method_bad"], lw=2.2, alpha=0.85, zorder=2,
    )

    # Annotation arrow for the forced line — pointing to the endpoint
    # so it does not overlap a point or the line itself.
    ax.annotate(
        "three collinear points\non the line y = 9",
        xy=(9.2, forced_row), xytext=(6.0, forced_row - 2.5),
        fontsize=11, ha="center", color=COLORS["method_bad"],
        arrowprops=dict(arrowstyle="->", color=COLORS["method_bad"], lw=1.1),
    )
    # No in-figure caption — the suptitle states the inequality.

    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.08), fontsize=9, ncol=2)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# results.png — 2x2 canonical results panel.
# ---------------------------------------------------------------------------


def make_results(certificate: dict, out_path: Path):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    (ax_a, ax_b), (ax_c, ax_d) = axes
    fig.suptitle(
        "Orbit 03 — Tight Upper Bound at N = 10  (committed metric = −20)",
        fontsize=14, y=1.02,
    )

    # ----------------------------- (a) search-space comparison (log scale)
    # Three quantities:
    #   naive  = C(100, 21)                                         ≈ 4.4e20
    #   2-per-row enumeration: (sum_{k=0..2} C(10,k))^10 = 56^10     ≈ 3.0e17
    #   actual B&B branches explored at target=21                    = 0
    naive = float(math.comb(100, 21))
    row_capped = float(56 ** 10)
    actual = float(max(certificate["bnb_target_21"]["branches_explored"], 1))
    labels = [
        "naive\nC(100, 21)",
        "row-cap 2\n(per-row enum.)",
        "B&B @ target=21\n(pigeonhole prune)",
    ]
    values = [naive, row_capped, actual]
    colors = [COLORS["baseline"], COLORS["highlight"], COLORS["method_good"]]
    bars = ax_a.bar(labels, values, color=colors, edgecolor="white", linewidth=0.8)
    ax_a.set_yscale("log")
    ax_a.set_ylabel("search-tree size")
    ax_a.set_title("(a) search-space collapse under pigeonhole")
    # Annotate bar tops.
    annotations = [f"{naive:.2e}", f"{row_capped:.2e}", "0"]
    for bar, ann in zip(bars, annotations):
        ax_a.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.6,
            ann, ha="center", va="bottom", fontsize=10, color="#333333",
        )
    ax_a.set_ylim(1e-1, naive * 10)
    ax_a.grid(axis="y", alpha=0.2)
    ax_a.text(
        -0.12, 1.05, "(a)", transform=ax_a.transAxes,
        fontsize=14, fontweight="bold",
    )

    # ----------------------------- (b) B&B branch count: target 20 vs 21
    targets = ["target = 20\n(achievable)", "target = 21\n(upper bound)"]
    counts = [
        certificate["bnb_target_20_sanity"]["branches_explored"],
        max(certificate["bnb_target_21"]["branches_explored"], 0),
    ]
    runtimes = [
        certificate["bnb_target_20_sanity"]["runtime_seconds"],
        certificate["bnb_target_21"]["runtime_seconds"],
    ]
    bcolors = [COLORS["method_good"], COLORS["method_bad"]]
    bars_b = ax_b.bar(targets, [max(c, 0.5) for c in counts],
                       color=bcolors, edgecolor="white", linewidth=0.8)
    ax_b.set_yscale("log")
    ax_b.set_ylabel("branches explored (log)")
    ax_b.set_title("(b) B&B branch counts — target 20 vs 21")
    for bar, count, rt in zip(bars_b, counts, runtimes):
        ax_b.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.6,
            f"{count:,}\n{rt*1000:.2f} ms",
            ha="center", va="bottom", fontsize=10, color="#333333",
        )
    ax_b.set_ylim(0.3, max(counts) * 10 if max(counts) > 0 else 10)
    ax_b.grid(axis="y", alpha=0.2)
    ax_b.text(
        -0.12, 1.05, "(b)", transform=ax_b.transAxes,
        fontsize=14, fontweight="bold",
    )

    # ----------------------------- (c) the 20-point witness on the grid
    draw_grid(ax_c, title="(c) committed 20-point witness (parent orbit)")
    xs = [c for (r, c) in PARENT_POINTS]
    ys = [r for (r, c) in PARENT_POINTS]
    ax_c.scatter(
        xs, ys, s=130, facecolor=COLORS["method_good"],
        edgecolor="white", linewidth=1.2, zorder=3,
    )
    # Shade the 2-per-row structure: every row has exactly 2 points, coloring
    # the 2 bounding columns faintly.
    for r in range(N):
        cols = sorted([c for (rr, c) in PARENT_POINTS if rr == r])
        for c in cols:
            ax_c.add_patch(Rectangle(
                (c - 0.48, r - 0.48), 0.96, 0.96,
                facecolor=COLORS["method_good"], alpha=0.08, zorder=2,
                edgecolor="none",
            ))
    ax_c.text(
        0.02, 0.98, "2 points per row × 10 rows = 20 total",
        transform=ax_c.transAxes, fontsize=10.5, va="top", ha="left",
        color="#333333",
    )
    ax_c.text(
        -0.12, 1.05, "(c)", transform=ax_c.transAxes,
        fontsize=14, fontweight="bold",
    )

    # ----------------------------- (d) metric panel
    metric_names = ["orbit 01\n(SA)", "orbit 02\n(C4 det.)",
                    "orbit 03\n(this — bound)", "target"]
    metric_vals = [-20.0, -20.0, -20.0, -20.0]
    dcolors = [COLORS["baseline"], COLORS["highlight"],
               COLORS["method_good"], COLORS["accent"]]
    bars_d = ax_d.bar(metric_names, metric_vals, color=dcolors,
                      edgecolor="white", linewidth=0.8)
    ax_d.set_ylabel("METRIC (-|POINTS|)")
    ax_d.set_ylim(-22, 2)
    ax_d.axhline(-20, color=COLORS["accent"], lw=1.0, ls="--",
                 label="tight bound = -20")
    ax_d.set_title("(d) metric trajectory - 20 is tight both ways")
    for bar, val in zip(bars_d, metric_vals):
        ax_d.text(
            bar.get_x() + bar.get_width() / 2,
            -10.0,  # centered inside the bar (bar spans 0 to -20)
            f"{val:.1f}", ha="center", va="center", fontsize=12, color="white",
            fontweight="bold",
        )
    ax_d.legend(loc="upper right")
    ax_d.grid(axis="y", alpha=0.2)
    ax_d.text(
        -0.12, 1.05, "(d)", transform=ax_d.transAxes,
        fontsize=14, fontweight="bold",
    )

    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Entrypoint.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    cert_path = HERE / "upper_bound_certificate.json"
    certificate = json.loads(cert_path.read_text())

    narr = FIGDIR / "narrative.png"
    make_narrative(narr)
    print(f"wrote {narr}")

    results = FIGDIR / "results.png"
    make_results(certificate, results)
    print(f"wrote {results}")
