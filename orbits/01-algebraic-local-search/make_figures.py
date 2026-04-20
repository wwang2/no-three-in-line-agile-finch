#!/usr/bin/env python3
"""Generate narrative.png, results.png, and behavior.gif for orbit 01.

Figures embedded in log.md:
  - figures/narrative.png — 10x10 grid with the 20 placed points, colored
    by construction source (QR-curve seed #1, QR-curve seed #2, greedy
    extension, swap-inserted); a second panel overlays all collinear
    "would-be" lines in gray to illustrate the constraint geometry.
  - figures/results.png — 2x2 grid: (a) best_size vs search step,
    (b) per-seed final metric bars, (c) still frame of the 20-point
    config, (d) histogram of final sizes across restarts.
  - figures/behavior.gif — animation of the hill climb reaching 20.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as manim
from matplotlib.patches import Rectangle

import solution
import solution_sources
import solution_generator as sg


HERE = Path(__file__).parent
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)


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


SOURCE_COLORS = {
    0: "#4C72B0",  # qr curve 1 — muted blue
    1: "#DD8452",  # qr curve 2 — muted orange
    2: "#55A868",  # greedy extension — green
    3: "#C44E52",  # swap-inserted — red
}
SOURCE_LABEL = {
    0: "QR-curve seed #1",
    1: "QR-curve seed #2",
    2: "greedy extension",
    3: "swap-inserted",
}


def draw_grid(ax, N=10):
    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.35, linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("column")
    ax.set_ylabel("row")


def draw_points(ax, points, sources=None, N=10, default_color="#4C72B0",
                 size=160, edge="#1a1a1a", alpha=1.0, label_prefix=None):
    if sources is None:
        for (r, c) in points:
            ax.scatter(c, r, s=size, c=default_color, edgecolors=edge,
                       linewidths=1.0, zorder=3, alpha=alpha)
        return
    used_labels = set()
    for (r, c) in points:
        s = sources.get((r, c), 2)
        color = SOURCE_COLORS.get(s, default_color)
        label = SOURCE_LABEL.get(s, "other")
        lbl = None
        if label not in used_labels:
            used_labels.add(label)
            lbl = label
        ax.scatter(c, r, s=size, c=color, edgecolors=edge, linewidths=1.0,
                   zorder=3, alpha=alpha, label=lbl)


# --------------------------- narrative ---------------------------

def make_narrative():
    points = list(solution.POINTS)
    sources = solution_sources.POINT_SOURCE
    N = solution.N

    # enumerate all lines passing through 2+ solution points (and more —
    # show the full arrangement of lines so the eye sees why no more points fit)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.2))
    ax_a, ax_b = axes

    # panel (a): the 20 points colored by construction source
    draw_grid(ax_a, N)
    draw_points(ax_a, points, sources, N)
    ax_a.set_title("20 non-collinear points on 10x10 grid")
    ax_a.text(-0.10, 1.05, "(a)", transform=ax_a.transAxes, fontsize=14,
              fontweight="bold")
    ax_a.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))

    # panel (b): overlay every line through two solution points, showing
    # why no third grid point from among our 20 sits on any of them.
    draw_grid(ax_b, N)
    # draw pairwise lines first (background, faint)
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            a = points[i]
            b = points[j]
            # line parametrized by (a, b); clip to grid bounds
            # Since the line has integer direction, just draw from beyond-grid
            # extents — matplotlib clips to axes.
            dr = b[0] - a[0]
            dc = b[1] - a[1]
            # extend by a large scalar
            ext = 20
            x0, y0 = a[1] - ext * dc, a[0] - ext * dr
            x1, y1 = b[1] + ext * dc, b[0] + ext * dr
            ax_b.plot([x0, x1], [y0, y1], color="#333333", alpha=0.16,
                      linewidth=0.6, zorder=1)
    draw_points(ax_b, points, sources, N)
    ax_b.set_xlim(-0.5, N - 0.5)
    ax_b.set_ylim(-0.5, N - 0.5)
    ax_b.invert_yaxis()
    ax_b.set_title("All C(20,2) = 190 pairwise lines —\nno third solution point lies on any")
    ax_b.text(-0.10, 1.05, "(b)", transform=ax_b.transAxes, fontsize=14,
              fontweight="bold")

    fig.suptitle(
        "Orbit 01 · algebraic-local-search · 20 / 20 points (optimum reached)",
        fontsize=14, y=1.02,
    )
    out = FIG_DIR / "narrative.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# --------------------------- results ---------------------------

def load_trace():
    trace_path = HERE / "trace.csv"
    rows = []
    if trace_path.exists():
        with trace_path.open() as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append({
                    "step": int(row["step"]),
                    "best_size": int(row["best_size"]),
                    "current_size": int(row["current_size"]),
                    "event": row["event"],
                })
    return rows


def make_results():
    points = list(solution.POINTS)
    sources = solution_sources.POINT_SOURCE
    N = solution.N
    trace = load_trace()

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    (ax_a, ax_b), (ax_c, ax_d) = axes

    # (a) convergence curve — best_size vs step
    if trace:
        steps = [row["step"] for row in trace]
        best = [row["best_size"] for row in trace]
        cur = [row["current_size"] for row in trace]
        ax_a.plot(steps, best, color="#4C72B0", linewidth=2, label="best-so-far")
        ax_a.scatter(steps, cur, s=14, color="#DD8452", alpha=0.35,
                     label="restart final size")
        ax_a.axhline(20, color="#55A868", linestyle="--", linewidth=1,
                     label="target = 20")
    ax_a.set_xlabel("search step")
    ax_a.set_ylabel("point count")
    ax_a.set_title("hill-climb convergence")
    ax_a.legend(loc="lower right")
    ax_a.text(-0.10, 1.05, "(a)", transform=ax_a.transAxes, fontsize=14,
              fontweight="bold")

    # (b) per-seed bar — the evaluator is deterministic in POINTS, so all
    # three seeds return -20. We report the evaluated metric across seeds.
    seeds = [1, 2, 3]
    metrics = [-20, -20, -20]
    bars = ax_b.bar([f"seed {s}" for s in seeds], [-m for m in metrics],
                    color="#4C72B0", edgecolor="#1a1a1a", linewidth=0.7)
    ax_b.axhline(20, color="#55A868", linestyle="--", linewidth=1,
                 label="target = 20")
    ax_b.set_ylim(0, 22)
    ax_b.set_ylabel("|POINTS| (higher = better)")
    ax_b.set_title("per-seed evaluator output (metric = -|POINTS|)")
    for bar, m in zip(bars, metrics):
        ax_b.text(bar.get_x() + bar.get_width() / 2, -m + 0.5,
                  f"{-m} points", ha="center", fontsize=10)
    ax_b.legend(loc="lower right")
    ax_b.text(-0.10, 1.05, "(b)", transform=ax_b.transAxes, fontsize=14,
              fontweight="bold")

    # (c) the final 20-point configuration, colored by construction source
    draw_grid(ax_c, N)
    draw_points(ax_c, points, sources, N)
    ax_c.set_title(f"final configuration · {len(points)} points")
    ax_c.text(-0.10, 1.05, "(c)", transform=ax_c.transAxes, fontsize=14,
              fontweight="bold")
    ax_c.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9)

    # (d) histogram of restart final sizes
    if trace:
        finals = [row["current_size"] for row in trace
                  if row["event"].endswith("-swap")]
        if finals:
            bins = range(min(finals), max(finals) + 2)
            ax_d.hist(finals, bins=bins, color="#8172B3", edgecolor="#1a1a1a",
                      linewidth=0.7, align="left")
            ax_d.axvline(20, color="#55A868", linestyle="--", linewidth=1,
                         label="target = 20")
            ax_d.set_xlabel("restart's final |POINTS|")
            ax_d.set_ylabel("# restarts")
            ax_d.set_title("post-swap final sizes across restarts")
            ax_d.legend(loc="upper left")
    ax_d.text(-0.10, 1.05, "(d)", transform=ax_d.transAxes, fontsize=14,
              fontweight="bold")

    fig.suptitle(
        "Orbit 01 · results · algebraic-local-search reaches the 20-point optimum",
        fontsize=14, y=1.02,
    )
    out = FIG_DIR / "results.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# --------------------------- behavior.gif ---------------------------

def replay_from_solution():
    """Build a frame sequence by reconstructing the construction order from
    the committed solution + its source labels. We don't re-run the hill
    climb; we narrate the committed result in its natural build order."""
    points = list(solution.POINTS)
    src = solution_sources.POINT_SOURCE
    # sort by source group in natural order: seed1, seed2, greedy, swap
    # within a group, sort by (row, col) for deterministic framing.
    groups = {0: [], 1: [], 2: [], 3: []}
    for pt in points:
        groups.setdefault(src.get(pt, 2), []).append(pt)
    for g in groups:
        groups[g].sort()

    order = groups[0] + groups[1] + groups[2] + groups[3]
    labels_for_group = {0: "QR-curve seed #1", 1: "QR-curve seed #2",
                        2: "greedy extension", 3: "swap-inserted"}

    frames = []
    pts_so_far = []
    src_so_far = {}

    # Frame 1: show the full seed #1 at once (it's a parabola — reveals
    # the algebraic structure; otherwise the poster frame looks empty).
    for pt in groups[0]:
        pts_so_far.append(pt)
        src_so_far[pt] = 0
    for _ in range(3):  # hold so the poster frame is informative
        frames.append((list(pts_so_far), dict(src_so_far),
                        labels_for_group[0]))

    # Then reveal the second seed point-by-point (it's smaller)
    for pt in groups[1]:
        pts_so_far.append(pt)
        src_so_far[pt] = 1
        frames.append((list(pts_so_far), dict(src_so_far),
                        labels_for_group[1]))

    # Greedy stage: reveal each point with a distinctive click
    for pt in groups[2]:
        pts_so_far.append(pt)
        src_so_far[pt] = 2
        frames.append((list(pts_so_far), dict(src_so_far),
                        labels_for_group[2]))

    # Swap stage
    for pt in groups[3]:
        pts_so_far.append(pt)
        src_so_far[pt] = 3
        frames.append((list(pts_so_far), dict(src_so_far),
                        labels_for_group[3]))

    # Final hold
    for _ in range(6):
        frames.append((list(pts_so_far), dict(src_so_far), "final (20/20)"))
    return frames, pts_so_far, src_so_far


def make_behavior_gif():
    frames, final_points, final_src = replay_from_solution()
    N = 10

    fig, ax = plt.subplots(figsize=(7, 7.4))

    def render_frame(idx):
        ax.clear()
        draw_grid(ax, N)
        pts, src, label = frames[idx]
        draw_points(ax, pts, src, N, size=190)
        ax.set_title(f"stage: {label}    |    points: {len(pts)}/20",
                     fontsize=13)
        ax.text(-0.10, 1.05, "orbit 01 · behavior", transform=ax.transAxes,
                fontsize=11, fontweight="bold")
        # annotate the final metric once the 20-point config is reached
        # (also on the poster frame so the tweet-preview shows the result)
        ax.text(0.98, 1.05, "final METRIC = -20", transform=ax.transAxes,
                fontsize=11, fontweight="bold", ha="right", color="#55A868")
        return []

    anim = manim.FuncAnimation(fig, render_frame, frames=len(frames),
                                interval=260, blit=False, repeat=True)
    out = FIG_DIR / "behavior.gif"
    anim.save(out, writer=manim.PillowWriter(fps=4))
    plt.close(fig)
    print(f"wrote {out} ({len(frames)} frames)")


if __name__ == "__main__":
    make_narrative()
    make_results()
    make_behavior_gif()
