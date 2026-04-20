"""
bnb_upper_bound.py
==================

Exhaustive branch-and-bound driver that confirms the pigeonhole upper
bound: no 21-point no-three-in-line subset of the 10x10 grid exists.

The search is organized row-by-row. Candidate solutions are built by
deciding, for each row r = 0, 1, ..., N-1, which subset of the N = 10
column positions to use in that row. Three prunes fire in cascade:

  (P1) **Horizontal pigeonhole.** Any row with 3 or more points
       already contains 3 collinear (they all lie on the horizontal
       line y = r). So each row contributes at most 2 points. With 10
       rows, the total is at most 2 * 10 = 20. The search for 21
       points therefore prunes at depth 0 once the pigeonhole is
       enforced.

  (P2) **General collinearity.** Before accepting a candidate column
       set for row r, verify that no collinear triple arises with the
       already-placed points from rows 0..r-1.

  (P3) **Target bound.** If points_placed + 2 * rows_remaining <
       target, the subtree cannot reach the target.

(P1) alone proves the result: the branching factor of a search that
asks "can 21 points be placed under the 2-per-row cap?" is zero,
because 2 * 10 = 20 < 21. The B&B in this file records this fact as a
search-tree event rather than a free-form argument — the driver
terminates with "branches_explored = 0" at the 21-point target.

For completeness the driver also runs the target = 20 search up to
first-hit to demonstrate that the 20-point bound is reachable under
the same 2-per-row cap; this is the sanity-check branch.

Runtime: <50 ms on any modern machine; the 21-point tree is empty.
"""

from __future__ import annotations

import json
import time
from itertools import combinations
from pathlib import Path


N = 10


# ---------------------------------------------------------------------------
# Geometry primitives (integer arithmetic only).
# ---------------------------------------------------------------------------


def cross(o, a, b):
    """Integer cross product of (a - o) and (b - o). Zero iff collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def is_collinear_with_existing(new_point, placed):
    """True iff some pair (p, q) in placed is collinear with new_point."""
    n = len(placed)
    for i in range(n):
        p = placed[i]
        for j in range(i + 1, n):
            q = placed[j]
            if cross(p, q, new_point) == 0:
                return True
    return False


def any_collinear_triple(points):
    """Sanity check: does this set have a collinear triple?"""
    for i, j, k in combinations(range(len(points)), 3):
        if cross(points[i], points[j], points[k]) == 0:
            return (i, j, k)
    return None


# ---------------------------------------------------------------------------
# Branch-and-bound with horizontal-pigeonhole pruning.
# ---------------------------------------------------------------------------


class BnBStats:
    __slots__ = ("branches", "placements", "collinearity_prunes", "bound_prunes")

    def __init__(self):
        self.branches = 0
        self.placements = 0
        self.collinearity_prunes = 0
        self.bound_prunes = 0


def row_choices_with_cap(row_cap, ncols=N):
    """All column subsets of size 0, 1, ..., row_cap for a single row.

    Returns them as tuples of column indices, lex-ordered by size then
    column. Used by the driver below to enumerate row content.
    """
    out = []
    for k in range(row_cap + 1):
        for combo in combinations(range(ncols), k):
            out.append(combo)
    return out


def bnb_search(target, row_cap, stop_on_first=True, max_solutions=1):
    """Exhaustive B&B with horizontal-pigeonhole prune.

    Args:
        target: how many points we are looking for.
        row_cap: max points per row (P1). Set to 2 for the actual
            pigeonhole statement; set to N to disable P1 entirely
            (which would be necessary only if P1 is wrong).
        stop_on_first: if True, return as soon as one placement of
            size `target` is found.
        max_solutions: if stop_on_first is False, return up to this
            many witnesses.

    Returns:
        dict with 'branches', 'placements', 'collinearity_prunes',
        'bound_prunes', 'solutions' (list of point sets), and
        'proof_note' explaining the outcome.
    """
    stats = BnBStats()
    solutions: list[list[tuple[int, int]]] = []
    row_candidates = row_choices_with_cap(row_cap)

    # Early-termination pigeonhole check. This is P1 applied globally.
    if target > row_cap * N:
        # The search tree is provably empty; record zero branches.
        proof_note = (
            f"pigeonhole prune at depth 0: target={target} exceeds "
            f"{row_cap} * {N} = {row_cap * N}, so no configuration "
            f"with at most {row_cap} points per row can reach {target}"
        )
        return {
            "target": target,
            "row_cap": row_cap,
            "branches": 0,
            "placements": 0,
            "collinearity_prunes": 0,
            "bound_prunes": 1,
            "solutions": [],
            "proof_note": proof_note,
            "bound_proven": True,
        }

    placed: list[tuple[int, int]] = []

    def recurse(row):
        if len(solutions) >= max_solutions and stop_on_first:
            return
        remaining_rows = N - row
        # (P3) Bound prune.
        if len(placed) + row_cap * remaining_rows < target:
            stats.bound_prunes += 1
            return
        if row == N:
            if len(placed) >= target:
                solutions.append(list(placed))
            return
        for combo in row_candidates:
            stats.branches += 1
            # Accept combo only if incrementally non-collinear with all
            # previously placed points.
            added: list[tuple[int, int]] = []
            ok = True
            for c in combo:
                p = (row, c)
                if is_collinear_with_existing(p, placed + added):
                    stats.collinearity_prunes += 1
                    ok = False
                    break
                added.append(p)
            if not ok:
                continue
            placed.extend(added)
            stats.placements += len(added)
            recurse(row + 1)
            for _ in range(len(added)):
                placed.pop()
            if len(solutions) >= max_solutions and stop_on_first:
                return

    recurse(0)

    if solutions:
        proof_note = (
            f"found {len(solutions)} configuration(s) of size >= {target} "
            f"with at most {row_cap} points per row"
        )
    else:
        proof_note = (
            f"exhaustively searched all configurations with at most "
            f"{row_cap} points per row; no configuration of size "
            f">= {target} exists on a {N}x{N} grid"
        )
    return {
        "target": target,
        "row_cap": row_cap,
        "branches": stats.branches,
        "placements": stats.placements,
        "collinearity_prunes": stats.collinearity_prunes,
        "bound_prunes": stats.bound_prunes,
        "solutions": solutions,
        "proof_note": proof_note,
        "bound_proven": not solutions,
    }


# ---------------------------------------------------------------------------
# Certificate generation.
# ---------------------------------------------------------------------------


def prove_upper_bound_21(out_path: Path | None = None) -> dict:
    """The headline result: no 21-point configuration exists on N=10."""
    t0 = time.perf_counter()
    # P1 pigeonhole: a row cap of 2 captures the horizontal-pigeonhole
    # constraint (3 on the same row would be 3 collinear). With 10 rows,
    # 2 per row = 20 points. So target=21 is unreachable, and the B&B
    # prunes at depth 0.
    result_pigeonhole = bnb_search(target=21, row_cap=2)
    t_pigeonhole = time.perf_counter() - t0

    # Sanity check: also run target=20 at row_cap=2 with first-hit to
    # confirm the 20-bound is actually achievable under the same cap.
    t1 = time.perf_counter()
    result_achievable = bnb_search(target=20, row_cap=2, stop_on_first=True)
    t_achievable = time.perf_counter() - t1

    # Independent verification of the 20-point parent configuration.
    # The parent's C4 set is no-3-collinear and reaches the bound.
    parent_points = [
        (0, 0), (0, 9), (1, 3), (1, 5), (2, 3), (2, 4),
        (3, 7), (3, 8), (4, 1), (4, 7), (5, 2), (5, 8),
        (6, 1), (6, 2), (7, 5), (7, 6), (8, 4), (8, 6),
        (9, 0), (9, 9),
    ]
    parent_triple = any_collinear_triple(parent_points)
    parent_valid = parent_triple is None and len(parent_points) == 20

    certificate = {
        "N": N,
        "claim": "no 21-point no-three-in-line subset of the 10x10 grid exists",
        "proof_method": "horizontal-pigeonhole + exhaustive branch-and-bound",
        "pigeonhole_statement": (
            "with 21 points distributed over 10 rows, some row contains "
            "at least 3 points by the pigeonhole principle (ceil(21/10) = 3); "
            "those 3 points are collinear on the horizontal line y = row."
        ),
        "bnb_target_21": {
            "target": 21,
            "row_cap": 2,
            "branches_explored": result_pigeonhole["branches"],
            "placements": result_pigeonhole["placements"],
            "bound_prunes": result_pigeonhole["bound_prunes"],
            "collinearity_prunes": result_pigeonhole["collinearity_prunes"],
            "solutions_found": len(result_pigeonhole["solutions"]),
            "bound_proven": result_pigeonhole["bound_proven"],
            "runtime_seconds": t_pigeonhole,
            "proof_note": result_pigeonhole["proof_note"],
        },
        "bnb_target_20_sanity": {
            "target": 20,
            "row_cap": 2,
            "branches_explored": result_achievable["branches"],
            "solutions_found": len(result_achievable["solutions"]),
            "first_solution_size": (
                len(result_achievable["solutions"][0])
                if result_achievable["solutions"]
                else 0
            ),
            "runtime_seconds": t_achievable,
        },
        "parent_check": {
            "points_count": len(parent_points),
            "no_three_collinear": parent_valid,
            "collinear_triple": parent_triple,
        },
        "verified": result_pigeonhole["bound_proven"] and parent_valid,
        "references": [
            "Dudeney, H. E. (1917). Amusements in Mathematics, problem 317.",
            "Erdős, P. (1951). Problem on a nxn lattice. In unsolved problems.",
            "Flammenkamp, A. (1992, 1998). No-three-in-line problem records.",
        ],
    }
    if out_path is not None:
        out_path.write_text(json.dumps(certificate, indent=2, sort_keys=True))
    return certificate


# ---------------------------------------------------------------------------
# CLI entry point.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = here / "upper_bound_certificate.json"
    cert = prove_upper_bound_21(out_path=out)
    print(f"verified = {cert['verified']}")
    print(f"branches(target=21) = {cert['bnb_target_21']['branches_explored']}")
    print(f"runtime(target=21)  = {cert['bnb_target_21']['runtime_seconds']:.6f} s")
    print(f"branches(target=20) = {cert['bnb_target_20_sanity']['branches_explored']}")
    print(f"runtime(target=20)  = {cert['bnb_target_20_sanity']['runtime_seconds']:.6f} s")
    print(f"parent 20-point set valid = {cert['parent_check']['no_three_collinear']}")
    print(f"certificate written to {out}")
