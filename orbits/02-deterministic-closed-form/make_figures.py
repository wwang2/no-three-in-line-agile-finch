"""Generate narrative.png and results.png for orbit 02 replica r1.

No randomness — pure deterministic plotting of the C4-invariant
20-point construction from solution.py, with supplementary panels
showing the sigma and Klein-4 alternative routes.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from solution import POINTS, N, _sigma, _tau, _orbit_tau  # noqa: E402
from enumerate_symmetric import (  # noqa: E402
    backtrack_sigma,
    backtrack_klein4,
    backtrack_tau,
)


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "medium",
        "axes.labelsize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 10,
        "axes.grid": False,
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
    }
)


FIG_DIR = os.path.join(HERE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


# Orbit-color palette (5 C4 orbits of size 4).
ORBIT_PALETTE = [
    "#4C72B0",  # blue — corners
    "#DD8452",  # orange
    "#55A868",  # green
    "#C44E52",  # red
    "#8172B3",  # purple
]
COLOR_CENTER = "#222222"
COLOR_BASELINE = "#C44E52"


def _grid_axes(ax, title=None, small_ticks=False):
    ax.set_xlim(-0.7, N - 0.3)
    ax.set_ylim(-0.7, N - 0.3)
    ax.set_aspect("equal")
    for k in range(N + 1):
        ax.axhline(k - 0.5, color="#DDDDDD", linewidth=0.5, zorder=0)
        ax.axvline(k - 0.5, color="#DDDDDD", linewidth=0.5, zorder=0)
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    lbl = 8 if small_ticks else 9
    ax.set_xticklabels([str(c) for c in range(N)], fontsize=lbl)
    ax.set_yticklabels([str(N - 1 - r) for r in range(N)], fontsize=lbl)
    if title:
        ax.set_title(title)


def _c4_orbits(points):
    """Partition points into C4 orbits in deterministic order."""
    out = []
    seen = set()
    for p in sorted(points):
        if p in seen:
            continue
        orb = _orbit_tau(p)
        for q in orb:
            seen.add(q)
        out.append(orb)
    return out


def _plot_c4_solution(ax, points, annotate_center=True, orbit_lines=True):
    """Plot a C4-invariant point set, colouring each orbit distinctly."""
    orbits = _c4_orbits(points)
    cx, cy = (N - 1) / 2, (N - 1) / 2
    for i, orb in enumerate(orbits):
        col = ORBIT_PALETTE[i % len(ORBIT_PALETTE)]
        xs = [p[1] for p in orb]
        ys = [N - 1 - p[0] for p in orb]
        # Polygon connecting the 4 orbit points: order them around the center.
        angles = np.arctan2(
            np.array(ys) - cy, np.array(xs) - cx
        )
        idx = np.argsort(angles)
        xs_p = [xs[j] for j in idx] + [xs[idx[0]]]
        ys_p = [ys[j] for j in idx] + [ys[idx[0]]]
        if orbit_lines:
            ax.plot(
                xs_p, ys_p, color=col, linewidth=0.9, alpha=0.35, zorder=1
            )
        ax.scatter(
            xs, ys, s=140, color=col, zorder=4,
            edgecolor="white", linewidth=1.2,
        )
    if annotate_center:
        ax.scatter(
            [cx], [cy], marker="+", color=COLOR_CENTER,
            s=160, zorder=5, linewidth=1.8,
        )


def narrative_figure():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.3))

    # (a) Baseline: the trivial main diagonal — all 10 collinear.
    ax = axes[0]
    _grid_axes(ax, title="Baseline: main diagonal (10 pts, all collinear, INVALID)")
    diag = [(i, i) for i in range(N)]
    ax.plot(
        [p[1] for p in diag], [N - 1 - p[0] for p in diag],
        color=COLOR_BASELINE, linewidth=1.4, alpha=0.75, zorder=2,
        linestyle="--",
    )
    ax.scatter(
        [p[1] for p in diag], [N - 1 - p[0] for p in diag],
        s=110, color=COLOR_BASELINE,
        edgecolor="white", linewidth=1.0, zorder=3,
    )
    ax.text(0.02, 0.98, "(a)", transform=ax.transAxes,
            fontsize=15, fontweight="bold", va="top")
    ax.text(
        0.5, -0.11, "metric = 0  (collinear => invalid)", ha="center",
        transform=ax.transAxes, fontsize=11, color=COLOR_BASELINE,
    )

    # (b) Our 20-point C4-invariant construction.
    ax = axes[1]
    _grid_axes(
        ax,
        title="r1 construction: C4-invariant (5 orbits of 4) -> 20 pts, no 3 collinear",
    )
    _plot_c4_solution(ax, POINTS)
    ax.text(
        0.02, 0.98, "(b)", transform=ax.transAxes,
        fontsize=15, fontweight="bold", va="top",
    )
    ax.text(
        0.5, -0.11, "metric = -20  (target met, fully deterministic)",
        ha="center", transform=ax.transAxes, fontsize=11, color="#3d7c47",
    )

    fig.suptitle(
        "Orbit 02 / r1 -- deterministic closed-form 20-point "
        "no-three-in-line on 10x10 via C4 rotation",
        fontsize=14.5, y=1.03,
    )
    out = os.path.join(FIG_DIR, "narrative.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def results_figure():
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(
        2, 3, height_ratios=[1, 1.25], width_ratios=[1, 1, 1],
    )

    # (a) Method comparison bar chart.
    ax_a = fig.add_subplot(gs[0, 0])
    methods = [
        "naive\ndiagonal", "row-only\n(10 pts)", "QR curve\np=11",
        "orbit 01\n(RNG search)", "orbit 02 / r1\n(C4 closed-form)",
    ]
    metrics = [0.0, -10.0, -10.0, -20.0, -20.0]
    colors = ["#C44E52", "#8C8C8C", "#CCB974", "#55A868", "#4C72B0"]
    bars = ax_a.bar(
        range(len(methods)), metrics, color=colors,
        edgecolor="white", linewidth=1.0,
    )
    ax_a.axhline(
        -20, color="#888888", linestyle="--", linewidth=1.0,
        label="target = -20",
    )
    for b, m in zip(bars, metrics):
        ax_a.text(
            b.get_x() + b.get_width() / 2, m - 0.8,
            f"{m:.0f}", ha="center", va="top", fontsize=10,
            color="#222222",
        )
    ax_a.set_xticks(range(len(methods)))
    ax_a.set_xticklabels(methods, fontsize=9)
    ax_a.set_ylabel("metric (negative point count)")
    ax_a.set_title("Metric vs. target")
    ax_a.set_ylim(-22, 2)
    ax_a.legend(loc="upper right")
    ax_a.text(-0.14, 1.06, "(a)", transform=ax_a.transAxes,
              fontsize=15, fontweight="bold")

    # (b) Seed determinism.
    ax_b = fig.add_subplot(gs[0, 1])
    seeds = [1, 2, 3]
    seed_metrics = [-20.0, -20.0, -20.0]
    ax_b.scatter(
        seeds, seed_metrics, s=180, color="#4C72B0",
        edgecolor="white", linewidth=1.3, zorder=3,
    )
    ax_b.axhline(
        -20, color="#888888", linestyle="--", linewidth=1.0,
        label="target = -20",
    )
    for s, m in zip(seeds, seed_metrics):
        ax_b.annotate(
            f"{m:.1f}", (s, m), xytext=(0, 12),
            textcoords="offset points", ha="center", fontsize=11,
        )
    ax_b.set_xticks(seeds)
    ax_b.set_xlabel("eval seed")
    ax_b.set_ylabel("metric")
    ax_b.set_title("Seed determinism: zero variance")
    ax_b.set_ylim(-22, -18)
    ax_b.set_xlim(0.4, 3.6)
    ax_b.legend(loc="lower right")
    ax_b.text(-0.17, 1.06, "(b)", transform=ax_b.transAxes,
              fontsize=15, fontweight="bold")

    # (c) Search-space reduction log-scale.
    ax_c = fig.add_subplot(gs[0, 2])
    categories = [
        "full\nC(100, 20)", "sigma reps\nC(50, 10)",
        "Klein4 reps\nC(25, 5)", "C4 reps\nC(25, 5)",
    ]
    sizes = [5.36e20, 1.03e10, 53130, 53130]
    log_sizes = [np.log10(v) for v in sizes]
    bars = ax_c.bar(
        range(len(categories)), log_sizes,
        color=["#C44E52", "#DD8452", "#CCB974", "#4C72B0"],
        edgecolor="white", linewidth=1.0,
    )
    for b, v, raw in zip(bars, log_sizes, ["5.4e20", "1.0e10", "53 130", "53 130"]):
        ax_c.text(
            b.get_x() + b.get_width() / 2, v + 0.35,
            raw, ha="center", fontsize=10,
        )
    ax_c.set_xticks(range(len(categories)))
    ax_c.set_xticklabels(categories, fontsize=9)
    ax_c.set_ylabel("log10(raw search space)")
    ax_c.set_title("Symmetry shrinks the state space")
    ax_c.set_ylim(0, 23)
    ax_c.text(-0.14, 1.06, "(c)", transform=ax_c.transAxes,
              fontsize=15, fontweight="bold")

    # (d) C4 solution with orbit coloring (primary construction).
    ax_d = fig.add_subplot(gs[1, 0])
    _grid_axes(
        ax_d,
        title="Primary: C4 (90-deg rotation) -- 5 orbits of 4",
        small_ticks=True,
    )
    _plot_c4_solution(ax_d, POINTS)
    # Annotate one orbit
    orbits = _c4_orbits(POINTS)
    # corners orbit: ((0,0),(0,9),(9,9),(9,0)) gets drawn first.
    ax_d.annotate(
        "corners orbit\n{(0,0),(0,9),(9,0),(9,9)}",
        xy=(0, N - 1), xytext=(1.3, N - 0.2),
        fontsize=9, color=ORBIT_PALETTE[0],
        arrowprops=dict(arrowstyle="->", color=ORBIT_PALETTE[0],
                         lw=0.8, alpha=0.9),
    )
    ax_d.text(
        -0.15, 1.06, "(d)", transform=ax_d.transAxes,
        fontsize=15, fontweight="bold",
    )

    # (e) sigma (C2) alternative.
    ax_e = fig.add_subplot(gs[1, 1])
    sigma_sol = backtrack_sigma(target_size=20, limit_solutions=1)[0]
    _grid_axes(
        ax_e,
        title="Alt route: sigma (180-deg rotation) -- 10 orbits of 2",
        small_ticks=True,
    )
    # Color sigma pairs
    sigma_palette = [
        "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
        "#937860", "#DA8BC3", "#CCB974", "#64B5CD", "#E07A5F",
    ]
    seen_s = set()
    pair_i = 0
    cx, cy = (N - 1) / 2, (N - 1) / 2
    for p in sorted(sigma_sol):
        if p in seen_s:
            continue
        q = _sigma(p)
        seen_s.add(p)
        seen_s.add(q)
        col = sigma_palette[pair_i % len(sigma_palette)]
        pair_i += 1
        xs = [p[1], q[1]]
        ys = [N - 1 - p[0], N - 1 - q[0]]
        ax_e.plot(xs, ys, color=col, linewidth=0.9, alpha=0.35, zorder=1)
        ax_e.scatter(
            xs, ys, s=120, color=col, zorder=3,
            edgecolor="white", linewidth=1.2,
        )
    ax_e.scatter([cx], [cy], marker="+", color=COLOR_CENTER,
                 s=160, zorder=5, linewidth=1.8)
    ax_e.text(
        -0.15, 1.06, "(e)", transform=ax_e.transAxes,
        fontsize=15, fontweight="bold",
    )

    # (f) Klein-4 alternative.
    ax_f = fig.add_subplot(gs[1, 2])
    k4_sol = backtrack_klein4(target_size=20, limit_solutions=1)[0]
    _grid_axes(
        ax_f,
        title="Alt route: Klein-4 (h-flip, v-flip) -- 5 orbits of 4",
        small_ticks=True,
    )
    # Group into Klein4 orbits
    def k4_orbit(p):
        r, c = p
        return ((r, c), (r, N - 1 - c), (N - 1 - r, c), (N - 1 - r, N - 1 - c))
    seen_k = set()
    k4_palette = ORBIT_PALETTE
    i_k = 0
    for p in sorted(k4_sol):
        if p in seen_k:
            continue
        orb = k4_orbit(p)
        for q in orb:
            seen_k.add(q)
        col = k4_palette[i_k % len(k4_palette)]
        i_k += 1
        xs = [q[1] for q in orb]
        ys = [N - 1 - q[0] for q in orb]
        # polygon ordering around centre
        cx_, cy_ = (N - 1) / 2, (N - 1) / 2
        ang = np.arctan2(np.array(ys) - cy_, np.array(xs) - cx_)
        idx = np.argsort(ang)
        xs_p = [xs[j] for j in idx] + [xs[idx[0]]]
        ys_p = [ys[j] for j in idx] + [ys[idx[0]]]
        ax_f.plot(xs_p, ys_p, color=col, linewidth=0.9, alpha=0.35, zorder=1)
        ax_f.scatter(xs, ys, s=120, color=col, zorder=3,
                     edgecolor="white", linewidth=1.2)
    ax_f.scatter([(N - 1) / 2], [(N - 1) / 2], marker="+",
                 color=COLOR_CENTER, s=160, zorder=5, linewidth=1.8)
    ax_f.text(-0.15, 1.06, "(f)", transform=ax_f.transAxes,
              fontsize=15, fontweight="bold")

    fig.suptitle(
        "Orbit 02 / r1 -- deterministic closed-form "
        "20-point no-three-in-line (10x10), with three independent "
        "symmetric routes verifying the same optimum.",
        fontsize=14, y=1.015,
    )
    out = os.path.join(FIG_DIR, "results.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    narrative_figure()
    results_figure()
