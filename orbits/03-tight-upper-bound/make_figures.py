"""Generate narrative.png and results.png for orbit 03 (r1 replica)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


HERE = Path(__file__).parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)


# ---- style -------------------------------------------------------------

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
    "legend.borderpad": 0.3,
    "legend.handletextpad": 0.5,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "figure.constrained_layout.use": True,
})


COLOR_BASELINE = "#888888"
COLOR_METHOD = "#4C72B0"
COLOR_ACCENT = "#C44E52"
COLOR_SOFT = "#55A868"


N = 10
POINTS = [
    (0, 0), (0, 9), (1, 3), (1, 5), (2, 3), (2, 4),
    (3, 7), (3, 8), (4, 1), (4, 7), (5, 2), (5, 8),
    (6, 1), (6, 2), (7, 5), (7, 6), (8, 4), (8, 6),
    (9, 0), (9, 9),
]


def draw_grid(ax, highlight_row=None, highlight_col=None, *, title=""):
    """Draw a 10x10 grid with the 20-point witness on it."""
    # grid
    for k in range(N + 1):
        ax.plot([0, N], [k, k], lw=0.6, color="#e0e0e0", zorder=0)
        ax.plot([k, k], [0, N], lw=0.6, color="#e0e0e0", zorder=0)
    # highlights
    if highlight_row is not None:
        ax.add_patch(
            Rectangle(
                (0, highlight_row),
                N, 1,
                facecolor=COLOR_ACCENT,
                alpha=0.12,
                edgecolor=COLOR_ACCENT,
                lw=1.0,
                zorder=1,
            )
        )
    if highlight_col is not None:
        ax.add_patch(
            Rectangle(
                (highlight_col, 0),
                1, N,
                facecolor=COLOR_SOFT,
                alpha=0.12,
                edgecolor=COLOR_SOFT,
                lw=1.0,
                zorder=1,
            )
        )
    # points
    xs = [c + 0.5 for (_, c) in POINTS]
    ys = [r + 0.5 for (r, _) in POINTS]
    ax.scatter(xs, ys, s=70, color=COLOR_METHOD, edgecolor="white", lw=1.2, zorder=3)

    ax.set_xlim(0, N)
    ax.set_ylim(N, 0)  # invert y so row 0 is at top (grid convention)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(N) + 0.5)
    ax.set_yticks(np.arange(N) + 0.5)
    ax.set_xticklabels([str(i) for i in range(N)])
    ax.set_yticklabels([str(i) for i in range(N)])
    ax.tick_params(length=0)
    ax.set_xlabel("column")
    ax.set_ylabel("row")
    ax.grid(False)
    for s in ("top", "right", "bottom", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title(title)


# ---------------------------------------------------------------------------
# narrative.png — the proof at a glance.
#
# Layout: 1 x 3
#   (a) The 20-point witness with highlighted saturated row+column
#   (b) Row/column occupancy bar chart — every row and column caps at 2
#   (c) Pigeonhole cartoon: 21 balls into 10 bins => some bin has >=3
# ---------------------------------------------------------------------------


def make_narrative():
    fig = plt.figure(figsize=(16, 6.0), dpi=170)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.05])

    # (a) witness grid
    ax_a = fig.add_subplot(gs[0, 0])
    draw_grid(ax_a, highlight_row=4, highlight_col=3,
              title="(a) 20-point C4-symmetric witness")
    ax_a.text(-0.14, 1.08, "(a)", transform=ax_a.transAxes,
              fontsize=14, fontweight="bold")
    ax_a.annotate(
        "row 4 contains\n2 points (cap)",
        xy=(1.6, 4.5), xytext=(5.6, 5.7),
        fontsize=9.5, color=COLOR_ACCENT,
        arrowprops=dict(arrowstyle='->', color=COLOR_ACCENT, lw=0.9),
        va="center", ha="left",
    )
    ax_a.annotate(
        "col 3 contains\n2 points (cap)",
        xy=(3.5, 2.2), xytext=(5.2, 1.1),
        fontsize=9.5, color=COLOR_SOFT,
        arrowprops=dict(arrowstyle='->', color=COLOR_SOFT, lw=0.9),
        va="center", ha="left",
    )

    # (b) row / column occupancy
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.text(-0.14, 1.08, "(b)", transform=ax_b.transAxes,
              fontsize=14, fontweight="bold")
    row_counts = [0] * N
    col_counts = [0] * N
    for r, c in POINTS:
        row_counts[r] += 1
        col_counts[c] += 1
    idx = np.arange(N)
    w = 0.38
    ax_b.bar(idx - w / 2, row_counts, width=w, color=COLOR_METHOD, label="row count")
    ax_b.bar(idx + w / 2, col_counts, width=w, color=COLOR_SOFT, label="col count")
    ax_b.axhline(2, color=COLOR_ACCENT, lw=1.2, ls="--")
    ax_b.text(9.35, 2.06, "cap = 2", color=COLOR_ACCENT, fontsize=9,
              ha="right", va="bottom")
    ax_b.axhline(3, color="#bbbbbb", lw=0.8, ls=":")
    ax_b.text(9.35, 3.06, "3 -> collinear", color="#888888", fontsize=9,
              ha="right", va="bottom")
    ax_b.set_xticks(idx)
    ax_b.set_yticks([0, 1, 2, 3])
    ax_b.set_xlabel("row / column index")
    ax_b.set_ylabel("points")
    ax_b.set_ylim(0, 3.4)
    ax_b.set_title("(b) Every row and column saturates at 2")
    ax_b.legend(loc="upper right", ncol=2)
    ax_b.grid(axis="y", alpha=0.15)

    # (c) pigeonhole cartoon: 10 bins, 21 balls
    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.text(-0.06, 1.08, "(c)", transform=ax_c.transAxes,
              fontsize=14, fontweight="bold")
    # 10 bins as vertical slots
    np.random.seed(0)
    bin_xs = np.arange(10)
    balls_per_bin = [2] * 10
    # Force one bin to hold 3 — the pigeonhole collision
    balls_per_bin[4] = 3
    # Total 21 balls
    assert sum(balls_per_bin) == 21
    for b, k in enumerate(balls_per_bin):
        ax_c.add_patch(
            Rectangle((b - 0.42, 0), 0.84, 3.6,
                      facecolor="#f5f5f5", edgecolor="#cccccc", lw=0.8)
        )
        colour = COLOR_ACCENT if k >= 3 else COLOR_METHOD
        for i in range(k):
            ax_c.scatter(
                b, 0.35 + i * 0.7,
                s=220, color=colour,
                edgecolor="white", lw=1.2, zorder=3,
            )
        ax_c.text(b, -0.35, f"row {b}", ha="center", va="top", fontsize=8,
                  color="#444444", rotation=0)
    ax_c.axhline(2 * 0.7 + 0.35, color=COLOR_ACCENT, lw=1.2, ls="--", alpha=0.55)
    ax_c.text(
        9.6, 2 * 0.7 + 0.35 + 0.08,
        "cap = 2", fontsize=9, color=COLOR_ACCENT, ha="right", va="bottom",
    )
    ax_c.annotate(
        "3rd ball:\ncollinear!",
        xy=(4, 0.35 + 2 * 0.7), xytext=(6.5, 3.3),
        fontsize=10, color=COLOR_ACCENT, ha="left",
        arrowprops=dict(arrowstyle='->', color=COLOR_ACCENT, lw=1.0),
    )
    ax_c.set_xlim(-0.8, 9.8)
    ax_c.set_ylim(-0.9, 3.8)
    ax_c.set_xticks([])
    ax_c.set_yticks([])
    for s in ("top", "right", "bottom", "left"):
        ax_c.spines[s].set_visible(False)
    ax_c.grid(False)
    ax_c.set_title("(c) 21 points into 10 rows: some row holds ≥ 3")

    fig.suptitle(
        "Upper bound = 20 on the 10x10 grid (row-pigeonhole proof)",
        y=1.04, fontsize=14,
    )
    out = FIG / "narrative.png"
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# results.png — quantitative verification dashboard.
#
# Layout: 2 x 2
#   (a) Four verification routes and their verdicts
#   (b) LP feasible polytope cartoon: uniform fractional primal hits 2N
#   (c) Witness grid (copy of narrative.png's (a))
#   (d) 20 vs 21 — bound is tight
# ---------------------------------------------------------------------------


def make_results():
    # load certificate for numbers
    cert_path = HERE / "upper_bound_certificate.json"
    cert = json.loads(cert_path.read_text())
    ub = cert["upper_bound"]
    lp = cert["upper_bound_proofs"]["lp_relaxation"]
    bnb = cert["upper_bound_proofs"]["bnb_row_col_capped_21_point_search"]

    fig = plt.figure(figsize=(14.5, 11.5), dpi=170)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05])

    # (a) verification routes summary
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.text(-0.12, 1.05, "(a)", transform=ax_a.transAxes,
              fontsize=14, fontweight="bold")
    routes = [
        ("Row pigeonhole", 20, "blocks 21"),
        ("Col pigeonhole", 20, "blocks 21"),
        ("LP relaxation", lp["lp_bound_joint"], "LP* = 2N"),
        ("B&B 21-search", 20,
         f"explored {bnb['n_explored']}, no witness"),
    ]
    names = [r[0] for r in routes]
    vals = [r[1] for r in routes]
    notes = [r[2] for r in routes]
    y = np.arange(len(routes))[::-1]
    ax_a.barh(y, vals, color=COLOR_METHOD, edgecolor="white", height=0.6)
    ax_a.axvline(20, color=COLOR_ACCENT, lw=1.4, ls="--")
    ax_a.text(20.2, 3.4, "tight bound\n2N = 20",
              color=COLOR_ACCENT, fontsize=10, va="top")
    for yi, (val, note) in enumerate(zip(vals, notes)):
        ax_a.text(val - 0.4, y[yi], note, color="white", fontsize=9.5,
                  ha="right", va="center", fontweight="medium")
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(names)
    ax_a.set_xlim(0, 24)
    ax_a.set_xlabel("upper bound on |S|")
    ax_a.set_title("(a) Four independent upper-bound routes")
    ax_a.grid(axis="x", alpha=0.15)

    # (b) LP uniform-fractional primal as a heatmap (x_{r,c} = 2/N)
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.text(-0.18, 1.05, "(b)", transform=ax_b.transAxes,
              fontsize=14, fontweight="bold")
    X = np.full((N, N), 2.0 / N)
    im = ax_b.imshow(X, cmap="Blues", vmin=0, vmax=1, aspect="equal")
    ax_b.set_title("(b) LP primal x = 2/N\nrow sum = col sum = 2, total = 2N = 20")
    ax_b.set_xticks(range(N))
    ax_b.set_yticks(range(N))
    ax_b.set_xlabel("column")
    ax_b.set_ylabel("row")
    ax_b.grid(False)
    for r in range(N):
        for c in range(N):
            ax_b.text(c, r, "0.2", ha="center", va="center",
                      color="#444444", fontsize=7.5)
    cbar = fig.colorbar(im, ax=ax_b, fraction=0.046, pad=0.04)
    cbar.set_label("x_{r,c}")

    # (c) 20-point witness
    ax_c = fig.add_subplot(gs[1, 0])
    draw_grid(ax_c, highlight_row=None, highlight_col=None,
              title="(c) Tightness witness - 20 points, C4-invariant")
    ax_c.text(-0.12, 1.05, "(c)", transform=ax_c.transAxes,
              fontsize=14, fontweight="bold")
    ax_c.text(
        0.98, -0.15, "metric = -20  (= -2N, campaign target)",
        transform=ax_c.transAxes,
        ha="right", va="top", fontsize=10, color="#333333",
    )

    # (d) bound-tightness bars: 20 feasible, 21 infeasible
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.text(-0.12, 1.05, "(d)", transform=ax_d.transAxes,
              fontsize=14, fontweight="bold")
    labels = ["20 (this orbit)", "21 (impossible)"]
    heights = [20, 21]
    colors = [COLOR_METHOD, COLOR_ACCENT]
    # Outline the impossible bar, filled the feasible one
    bars = ax_d.bar(
        labels, heights,
        color=[colors[0], "none"],
        edgecolor=[colors[0], colors[1]],
        hatch=[None, "///"],
        width=0.55,
        linewidth=2.2,
    )
    ax_d.axhline(20, color=COLOR_BASELINE, ls="--", lw=1.2, zorder=0)
    # Big X across the infeasible bar
    x0 = bars[1].get_x()
    w = bars[1].get_width()
    ax_d.plot([x0 + 0.05, x0 + w - 0.05], [0.5, 20.5],
              color=COLOR_ACCENT, lw=2.6, solid_capstyle="round")
    ax_d.plot([x0 + w - 0.05, x0 + 0.05], [0.5, 20.5],
              color=COLOR_ACCENT, lw=2.6, solid_capstyle="round")
    # Reference line label placed safely at right
    ax_d.text(
        1.52, 20.1, "2N = 20",
        color="#555555", fontsize=10, ha="right", va="bottom",
    )
    # Value labels above each bar
    ax_d.text(
        bars[0].get_x() + bars[0].get_width() / 2,
        23.0,
        "|S| = 20\nfeasible\n(C4 witness)",
        ha="center", va="center", fontsize=10, color="#333333",
    )
    ax_d.text(
        bars[1].get_x() + bars[1].get_width() / 2,
        23.0,
        "|S| = 21\nINFEASIBLE",
        ha="center", va="center", fontsize=10, color=COLOR_ACCENT,
        fontweight="medium",
    )
    ax_d.set_ylabel("|S|")
    ax_d.set_ylim(0, 26)
    ax_d.set_title("(d) Bound is tight: 20 achieved, 21 ruled out")
    ax_d.grid(axis="y", alpha=0.15)

    fig.suptitle(
        "max no-three-in-line on 10x10  =  2N  =  20  (metric = -20)",
        y=1.03, fontsize=14,
    )
    out = FIG / "results.png"
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    make_narrative()
    make_results()
