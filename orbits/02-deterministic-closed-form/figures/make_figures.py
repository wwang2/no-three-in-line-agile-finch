"""Generate narrative.png and results.png for orbit 02.

Requires: matplotlib, numpy.
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ORBIT = os.path.dirname(HERE)
sys.path.insert(0, ORBIT)

from solution import POINTS as SOL
# parent_solution is next to us in the same orbit dir, for comparison.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "parent_solution", os.path.join(ORBIT, "parent_solution.py")
)
_parent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parent)
PARENT = list(_parent.POINTS)


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
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
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "figure.constrained_layout.use": True,
})


# ---- colors ---------------------------------------------------------- #
C_UPPER = "#4C72B0"   # chosen half
C_MIRROR = "#DD8452"  # mirrored half
C_CENTER_DOT = "#55A868"
C_LINE = "#c9c9c9"
C_GRID_LINE = "#dddddd"


def decorate(ax):
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.5, 9.5)
    ax.set_xticks(range(10))
    ax.set_yticks(range(10))
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.grid(True, which="both", color=C_GRID_LINE, linewidth=0.7)
    for s in ax.spines.values():
        s.set_color("#aaaaaa")
    ax.set_xlabel("column c")
    ax.set_ylabel("row r")


def draw_symmetry_axes(ax):
    # Center of symmetry at (4.5, 4.5).  Draw faint 180° rotation marker.
    ax.plot(4.5, 4.5, marker="+", color=C_CENTER_DOT, markersize=18, mew=2, zorder=5)


def plot_solution(ax, pts, highlight_upper=True, title=None, metric_text=None):
    decorate(ax)
    S = set(pts)
    for (r, c) in pts:
        mirror = (9 - r, 9 - c)
        # Upper half (r <= 4) vs lower half.
        if highlight_upper and r <= 4:
            color = C_UPPER
        else:
            color = C_MIRROR
        ax.plot(c, r, "o", color=color, markersize=14, markeredgecolor="white", mew=1.5, zorder=6)
    # Draw dashed segments connecting each chosen upper point to its mirror,
    # to visually cue the symmetry (only when this is the symmetric solution).
    if highlight_upper:
        for (r, c) in pts:
            if r <= 4:
                ax.plot([c, 9 - c], [r, 9 - r], color=C_LINE, lw=0.8, ls="--", zorder=2)
    draw_symmetry_axes(ax)
    if title:
        ax.set_title(title)
    if metric_text:
        # Place above the plot, left-justified.
        ax.text(0.0, 1.02, metric_text, transform=ax.transAxes,
                fontsize=11, fontweight="bold", va="bottom", ha="left",
                color="#333333")


# -------------------------------------------------------------------- #
# narrative.png - construction diagram                                   #
# -------------------------------------------------------------------- #
def make_narrative():
    fig = plt.figure(figsize=(16, 6.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 3.0], hspace=0.35, wspace=0.22)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[1, 2])
    axes = [ax_a, ax_b, ax_c, ax_d]

    # (a) 10 columns partitioned into 5 disjoint pairs.
    ax = ax_a
    pairs = [(2, 3), (6, 7), (0, 1), (8, 9), (4, 5)]  # partition used by solver
    ax.set_title("(a) Step 1: partition 10 columns into 5 disjoint pairs")
    palette = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
    for r in range(5):
        c1, c2 = pairs[r]
        ax.plot([c1, c2], [0, 0], "-", color=palette[r], lw=3, alpha=0.35, zorder=2)
    for r in range(5):
        c1, c2 = pairs[r]
        for c in (c1, c2):
            ax.plot(c, 0, "o", color=palette[r], markersize=14, markeredgecolor="white",
                    mew=1.2, zorder=4)
            ax.text(c, 0.55, str(c), ha="center", va="bottom", fontsize=9,
                    color=palette[r], fontweight="bold")
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-1.0, 1.5)
    ax.set_xticks(range(10))
    ax.set_yticks([])
    ax.set_xlabel("column index c  in  {0..9}")
    ax.set_ylabel("")
    ax.grid(False)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)

    # (b) Upper half: each pair assigned to one row 0..4.
    ax = ax_b
    decorate(ax)
    ax.set_title("(b) Step 2: assign pair k to row k (upper half)")
    upper = []
    for r, (c1, c2) in enumerate(pairs):
        upper.append((r, c1))
        upper.append((r, c2))
        ax.plot([c1, c2], [r, r], "-", color=palette[r], lw=2, alpha=0.5, zorder=2)
        ax.plot(c1, r, "o", color=palette[r], markersize=12, markeredgecolor="white", mew=1.2)
        ax.plot(c2, r, "o", color=palette[r], markersize=12, markeredgecolor="white", mew=1.2)
    # show empty lower half
    ax.axhline(4.5, color="#cccccc", lw=0.8, ls=":")

    # (c) Mirror completion: (r, c) <-> (9-r, 9-c).
    ax = ax_c
    plot_solution(
        ax,
        SOL,
        highlight_upper=True,
        title="(c) Step 3: mirror-complete  (r,c) <-> (9-r,9-c)",
        metric_text=None,
    )
    # (d) Final 20 points, colored by symmetry orbit (all pairs identical color).
    ax = ax_d
    decorate(ax)
    S = set(SOL)
    orbit_colors = {}
    palette10 = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
                 "#937860", "#DA8BC3", "#8c8c8c", "#CCB974", "#64B5CD"]
    idx = 0
    for (r, c) in sorted(SOL):
        if (r, c) in orbit_colors:
            continue
        mirror = (9 - r, 9 - c)
        col = palette10[idx % len(palette10)]
        orbit_colors[(r, c)] = col
        orbit_colors[mirror] = col
        idx += 1
    for (r, c) in SOL:
        col = orbit_colors[(r, c)]
        ax.plot(c, r, "o", color=col, markersize=14,
                markeredgecolor="white", mew=1.5, zorder=6)
    draw_symmetry_axes(ax)
    ax.set_title("(d) Final 20 points, colored by orbit under Z/2 inversion")

    fig.suptitle(
        "Deterministic construction of 20-point no-three-in-line set on 10x10   |   METRIC = -20   (seeds 1,2,3)",
        fontsize=14, y=1.02,
    )
    out = os.path.join(HERE, "narrative.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# -------------------------------------------------------------------- #
# results.png - quantitative comparison                                 #
# -------------------------------------------------------------------- #
def make_results():
    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.1], hspace=0.35, wspace=0.25)

    # ---- top row: quantitative ---------------------------------------- #
    # (a) metric bar-chart: orbit 02 vs orbit 01 vs baseline.
    ax = fig.add_subplot(gs[0, 0])
    methods = ["baseline\n(diag)", "orbit 01\n(RNG search)", "orbit 02\n(this)", "target\n(2N)"]
    metrics = [0.0, -20.0, -20.0, -20.0]
    colors = ["#888888", "#DD8452", "#4C72B0", "#55A868"]
    bars = ax.bar(methods, metrics, color=colors, edgecolor="white", linewidth=1.2)
    for bar, m in zip(bars, metrics):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, y - 0.6,
                f"{m:.0f}", ha="center", va="top", fontsize=12, fontweight="bold",
                color="white")
    ax.axhline(-20.0, color="#55A868", lw=1.2, ls="--", alpha=0.7)
    ax.set_ylabel("METRIC  (negative point count)")
    ax.set_ylim(-23, 1)
    ax.text(-0.12, 1.05, "(a)", transform=ax.transAxes, fontsize=14, fontweight="bold")
    ax.set_title("Metric vs baselines (seed-averaged)")

    # (b) determinism panel: 3 seeds × 2 solutions.
    ax = fig.add_subplot(gs[0, 1])
    seeds = [1, 2, 3]
    x = np.arange(len(seeds))
    width = 0.35
    ax.bar(x - width / 2, [-20, -20, -20], width=width,
           color="#DD8452", label="orbit 01 (RNG-dep)")
    ax.bar(x + width / 2, [-20, -20, -20], width=width,
           color="#4C72B0", label="orbit 02 (this)")
    for xi, v in zip(x - width / 2, [-20, -20, -20]):
        ax.text(xi, v - 0.6, "-20", ha="center", va="top", color="white",
                fontweight="bold", fontsize=10)
    for xi, v in zip(x + width / 2, [-20, -20, -20]):
        ax.text(xi, v - 0.6, "-20", ha="center", va="top", color="white",
                fontweight="bold", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed {s}" for s in seeds])
    ax.set_ylabel("METRIC")
    ax.set_ylim(-23, 1)
    ax.legend(loc="upper right")
    ax.text(-0.12, 1.05, "(b)", transform=ax.transAxes, fontsize=14, fontweight="bold")
    ax.set_title("Reproducibility across seeds (both hit -20)")

    # (c) "which 20 points changed" Venn-style count panel.
    ax = fig.add_subplot(gs[0, 2])
    S1 = set(PARENT)
    S2 = set(SOL)
    only1 = S1 - S2
    both = S1 & S2
    only2 = S2 - S1
    cats = ["only in\norbit 01", "shared", "only in\norbit 02"]
    vals = [len(only1), len(both), len(only2)]
    barcolors = ["#DD8452", "#888888", "#4C72B0"]
    bars = ax.bar(cats, vals, color=barcolors, edgecolor="white", linewidth=1.2)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(v), ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylabel("points")
    ax.set_ylim(0, max(vals) + 3)
    ax.text(-0.12, 1.05, "(c)", transform=ax.transAxes, fontsize=14, fontweight="bold")
    ax.set_title("How many of the 20 points differ")

    # ---- bottom row: qualitative -------------------------------------- #
    # (d) orbit 01 solution.
    ax = fig.add_subplot(gs[1, 0])
    plot_solution(ax, PARENT, highlight_upper=False,
                  title="orbit 01 (RNG-dependent) - METRIC=-20",
                  metric_text=None)
    # Recolor: orbit 01 uses one color because it's not symmetric.
    for line in ax.lines:
        if line.get_marker() == "o":
            line.set_color("#DD8452")
    ax.text(-0.18, 1.08, "(d)", transform=ax.transAxes, fontsize=14, fontweight="bold")

    # (e) orbit 02 solution with mirror highlighting.
    ax = fig.add_subplot(gs[1, 1])
    plot_solution(ax, SOL, highlight_upper=True,
                  title="orbit 02 (deterministic) - METRIC=-20",
                  metric_text=None)
    ax.text(-0.18, 1.08, "(e)", transform=ax.transAxes, fontsize=14, fontweight="bold")

    # (f) set-difference overlay.
    ax = fig.add_subplot(gs[1, 2])
    decorate(ax)
    for (r, c) in only1:
        ax.plot(c, r, "o", color="#DD8452", markersize=14,
                markeredgecolor="white", mew=1.5, zorder=5)
    for (r, c) in only2:
        ax.plot(c, r, "o", color="#4C72B0", markersize=14,
                markeredgecolor="white", mew=1.5, zorder=5)
    for (r, c) in both:
        ax.plot(c, r, "o", color="#888888", markersize=12,
                markeredgecolor="white", mew=1.5, zorder=4, alpha=0.8)
    ax.set_title(f"set diff: {len(only1)} orange-only, {len(only2)} blue-only, {len(both)} shared")
    ax.text(-0.18, 1.08, "(f)", transform=ax.transAxes, fontsize=14, fontweight="bold")

    fig.suptitle(
        "Orbit 02 (this) vs Orbit 01 (parent): same metric, deterministic vs randomized",
        fontsize=14, y=1.01,
    )
    out = os.path.join(HERE, "results.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    n = make_narrative()
    r = make_results()
    print(f"wrote {n}")
    print(f"wrote {r}")
