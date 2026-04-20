#!/usr/bin/env python3
"""Generator for orbit 01-algebraic-local-search.

Strategy:
    1. Seed the 10x10 grid with a quadratic-residue curve {(x, x^2 mod 11)}.
       This is the classical Erdős-Ko construction — 10 mutually
       non-collinear points (proof via the fact that any line of the affine
       plane over GF(p) meets the parabola y = x^2 in at most two points).
    2. Seed a second complementary algebraic set: a translated/dilated
       parabola {(x, (a*x^2 + b*x + c) mod 11) : x = 0..9}, scanning over
       (a, b, c) in [0, p).
    3. Iteratively greedy-insert the best remaining grid points subject to
       the no-three-collinear constraint.
    4. Hill-climb with 1-swap moves (remove 1 point, try to insert 2),
       accept any net gain. Randomized restarts with different algebraic
       seeds and tie-breaking rules.
    5. Record the best 20-point (or best-found) configuration.

The output of this script is a completely static `solution.py` file with
the found POINTS list. Rerun this generator to reproduce from fresh seeds.
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path


N = 10  # grid size (locked by the benchmark)
P_DEFAULT = 11  # prime near N used for the QR curve seed
MASTER_SEED = 0  # top-level seed; per-restart RNG is random.Random(MASTER_SEED + i).
#                  Note: reproducibility across Python versions depends on
#                  CPython's random.Random implementation (Mersenne Twister).


# --------------------------- collinearity primitives ---------------------------

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def is_valid_add(points, p):
    """True if p can be added without creating a collinear triple."""
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if cross(points[i], points[j], p) == 0:
                return False
    return True


def check_no_collinear(points):
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if cross(points[i], points[j], points[k]) == 0:
                    return (i, j, k)
    return None


# Faster structure: incremental "forbidden" grid based on already-placed points.
# For each pair of placed points (a, b) we mark every grid point that would be
# collinear with (a, b). A candidate q is forbidden iff any pair (a, b) in
# the current set has q on line(a, b).

def build_forbidden(points, N=N):
    """Return a set of (r, c) cells that would form a collinear triple if added."""
    forbidden = set()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            a = points[i]
            b = points[j]
            # enumerate all integer grid cells on the line through (a, b)
            for r in range(N):
                for c in range(N):
                    if (r, c) == a or (r, c) == b:
                        continue
                    if (b[0] - a[0]) * (c - a[1]) == (b[1] - a[1]) * (r - a[0]):
                        forbidden.add((r, c))
    return forbidden


def candidate_cells(points, N=N):
    """Cells that are not in points and not forbidden."""
    forbidden = build_forbidden(points, N)
    placed = set(points)
    return [
        (r, c) for r in range(N) for c in range(N)
        if (r, c) not in placed and (r, c) not in forbidden
    ]


# --------------------------- seed constructions ---------------------------

def qr_curve(a=1, b=0, c=0, p=P_DEFAULT, N=N):
    """Return points {(x, (a*x^2 + b*x + c) mod p) : 0 <= x < N}, clipped
    to the grid."""
    out = []
    for x in range(N):
        y = (a * x * x + b * x + c) % p
        if 0 <= y < N:
            out.append((x, y))
    return out


def seed_from_two_qr_curves(a1=1, b1=0, c1=0,
                             a2=1, b2=0, c2=0,
                             p=P_DEFAULT, N=N):
    """Union of two QR curves; the result may be invalid (collinear), so
    we filter by accepting points only if they preserve no-three-collinear."""
    curve1 = qr_curve(a1, b1, c1, p, N)
    curve2 = qr_curve(a2, b2, c2, p, N)
    combined = []
    for pt in curve1 + curve2:
        if pt in combined:
            continue
        if is_valid_add(combined, pt):
            combined.append(pt)
    return combined


# --------------------------- greedy + local search ---------------------------

def greedy_extend(points, N=N, rng=None):
    """Greedily add cells preserving no-three-collinear until saturation."""
    points = list(points)
    while True:
        cand = candidate_cells(points, N)
        if not cand:
            return points
        if rng is not None:
            rng.shuffle(cand)
        # add first candidate that's still valid (they all are at this point)
        points.append(cand[0])


def try_swap_expand(points, N=N, rng=None, max_iters=2000):
    """Iteratively try to remove one point, then greedily extend.

    If the new configuration strictly improves, keep it. Returns the best
    configuration found (of equal or larger size than the input)."""
    points = list(points)
    best = list(points)
    steps = 0
    plateau = 0
    while steps < max_iters and plateau < 200:
        steps += 1
        # pick a random point to remove (prefer "recently added" style randomness)
        if not points:
            break
        idx = rng.randrange(len(points))
        removed = points[idx]
        trial = points[:idx] + points[idx + 1:]
        # greedily extend
        extended = greedy_extend(trial, N, rng)
        if len(extended) > len(best):
            best = list(extended)
            points = list(extended)
            plateau = 0
        elif len(extended) == len(best):
            # lateral move — accept with probability to escape basin
            if rng.random() < 0.1:
                points = list(extended)
            plateau += 1
        else:
            # reject
            plateau += 1
    return best


def double_swap(points, N=N, rng=None, max_iters=4000):
    """Remove two points, try to insert three. Slower but can escape
    local optima that single-swap can't."""
    points = list(points)
    best = list(points)
    for it in range(max_iters):
        if len(points) < 2:
            break
        i, j = rng.sample(range(len(points)), 2)
        trial = [p for k, p in enumerate(points) if k != i and k != j]
        extended = greedy_extend(trial, N, rng)
        if len(extended) > len(best):
            best = list(extended)
            points = list(extended)
        elif len(extended) == len(points) and rng.random() < 0.05:
            points = list(extended)
    return best


# --------------------------- trace recorder ---------------------------

class Trace:
    """Record (step, best_size, current_size) over the search."""
    def __init__(self):
        self.rows = []  # list of (global_step, best_size, current_size, event)

    def record(self, step, best_size, current_size, event=""):
        self.rows.append((step, best_size, current_size, event))


def searched_restart(seed, p=P_DEFAULT, N=N, inner_iters=2000, verbose=False,
                     trace=None, trace_offset=0):
    """One full restart: pick random (a1..c2), seed, extend, swap.

    Returns (points, colors) where colors labels each point by source:
        0 = main QR curve seed
        1 = second QR curve seed
        2 = greedy extension
        3 = swap-inserted
    """
    rng = random.Random(seed)

    # Pick two distinct QR curves, a1 != 0 and a2 != 0.
    a1 = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    b1 = rng.randrange(p)
    c1 = rng.randrange(p)
    a2 = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    b2 = rng.randrange(p)
    c2 = rng.randrange(p)

    curve1 = qr_curve(a1, b1, c1, p, N)
    curve2 = qr_curve(a2, b2, c2, p, N)
    source = {}
    for pt in curve1:
        source[pt] = 0
    # combine
    combined = list(curve1)
    for pt in curve2:
        if pt in source:
            continue
        if is_valid_add(combined, pt):
            combined.append(pt)
            source[pt] = 1

    # greedy extend up to local saturation — multiple random orders, pick best
    extended_candidates = []
    for _ in range(32):
        e = greedy_extend(list(combined), N, rng)
        extended_candidates.append(e)
    extended = max(extended_candidates, key=len)
    for pt in extended:
        if pt not in source:
            source[pt] = 2

    # swap-and-extend to grind higher
    post_swap = try_swap_expand(list(extended), N, rng, max_iters=inner_iters)
    post_swap = double_swap(list(post_swap), N, rng, max_iters=inner_iters)
    # re-assert final source labels: any new points after swap get label=3,
    # surviving points retain their earlier label
    final_source = {}
    for pt in post_swap:
        if pt in source:
            final_source[pt] = source[pt]
        else:
            final_source[pt] = 3

    if verbose:
        print(
            f"seed={seed} a1={a1} b1={b1} c1={c1} a2={a2} b2={b2} c2={c2} "
            f"-> seeded={len(combined)} greedy={len(extended)} "
            f"final={len(post_swap)}"
        )

    if trace is not None:
        trace.record(trace_offset + 1, len(post_swap), len(combined), f"seed{seed}-seed")
        trace.record(trace_offset + 2, len(post_swap), len(extended), f"seed{seed}-greedy")
        trace.record(trace_offset + 3, len(post_swap), len(post_swap), f"seed{seed}-swap")

    return post_swap, final_source


# --------------------------- main driver ---------------------------

# (No hard-coded literature fallback — we only commit configurations that
#  our own search actually discovers and verifies to be no-three-collinear.)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-restarts", type=int, default=500,
                    help="number of random restarts of the algebraic seed + hill climb")
    ap.add_argument("--inner-iters", type=int, default=2500,
                    help="max iterations of swap-and-extend per restart")
    ap.add_argument("--p", type=int, default=P_DEFAULT, help="prime for QR curve")
    ap.add_argument("--target", type=int, default=20, help="stop early when reached")
    ap.add_argument("--out", type=str, default="solution.py",
                    help="output path for solution.py (relative to this script)")
    ap.add_argument("--trace-out", type=str, default="trace.csv",
                    help="csv of (step, best_size, current_size, event)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    best_points = []
    best_source = {}
    trace = Trace()
    for i in range(args.n_restarts):
        pts, src = searched_restart(
            seed=MASTER_SEED + i,
            p=args.p,
            N=N,
            inner_iters=args.inner_iters,
            verbose=args.verbose,
            trace=trace,
            trace_offset=i * 4,
        )
        trace.record(i * 4 + 4, max(len(best_points), len(pts)), len(pts),
                     f"restart{i}-end")
        if len(pts) > len(best_points):
            best_points = list(pts)
            best_source = dict(src)
            print(f"[restart {i}] new best = {len(best_points)} points "
                  f"(t={time.time() - t0:.1f}s)")
        if len(best_points) >= args.target:
            print(f"[restart {i}] target {args.target} reached — stopping")
            break

    # final verification
    triple = check_no_collinear(best_points)
    if triple is not None:
        raise SystemExit(f"INTERNAL ERROR: best config has collinear triple {triple}")

    # write solution.py
    here = Path(__file__).parent
    out_path = here / args.out
    body = ["# Auto-generated by solution_generator.py — do not edit by hand.",
            "# Orbit: 01-algebraic-local-search",
            f"# Points: {len(best_points)} (target = 20)",
            "",
            "N = 10",
            "POINTS = ["]
    for pt in best_points:
        body.append(f"    ({pt[0]}, {pt[1]}),")
    body.append("]")
    body.append("")
    out_path.write_text("\n".join(body))
    print(f"wrote {out_path} ({len(best_points)} points)")

    # write source labels
    (here / "solution_sources.py").write_text(
        "# source label per point (0=qr1, 1=qr2, 2=greedy, 3=swap, 4=curated)\n"
        "POINT_SOURCE = {\n"
        + "".join(f"    ({r}, {c}): {s},\n"
                 for (r, c), s in sorted(best_source.items()))
        + "}\n"
    )

    # write trace csv
    trace_path = here / args.trace_out
    with trace_path.open("w") as f:
        f.write("step,best_size,current_size,event\n")
        for step, bs, cs, ev in trace.rows:
            f.write(f"{step},{bs},{cs},{ev}\n")
    print(f"wrote {trace_path} with {len(trace.rows)} rows")


if __name__ == "__main__":
    main()
