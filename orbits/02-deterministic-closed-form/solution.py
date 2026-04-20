"""
02-deterministic-closed-form (replica r1)
==========================================

Fully deterministic 20-point no-three-in-line construction on the
10x10 grid. No randomness. No sklearn. No scipy.optimize. No
simulated annealing. No hill-climb.

r1 route: C4-invariant backtracking (90-degree rotational symmetry).
====================================================================

Let tau : (r, c) -> (c, 9 - r) be the 90-degree (clockwise) rotation
of the 10x10 grid about its geometric centre (4.5, 4.5). tau has
order 4; it generates the cyclic group C4 = {id, tau, tau^2, tau^3}.
tau^2 = sigma is the 180-degree rotation (r, c) |-> (9 - r, 9 - c).

Because 9 is odd there is no lattice-cell fixed point, so every
C4 orbit has exactly 4 elements. A C4-invariant subset of the grid
is a disjoint union of such orbits, and 20 points span exactly 5
orbits — which collapses the combinatorial search to:

    choose 5 orbit representatives from the 25 distinct C4 orbits of
    the 10x10 grid, subject to no-three-collinear.

That is only C(25, 5) = 53 130 raw combinations; after the
incremental collinearity pruning the lexicographic depth-first
backtrack terminates in <20 milliseconds on a single CPU core.

Why this is "closed-form deterministic":
  - The sequence of branches explored is fixed: orbits are ordered
    by the lexicographic order of their canonical (smallest) point,
    and the backtrack explores them in that order.
  - The only data structures are integer tuples; no RNG; no heuristic
    tie-breaker; no temperature schedule.
  - build_deterministic() is pure. Given the same enumeration order
    it always returns the same 20 points.

Correctness of the symmetry reduction:
  The integer cross product cross(a, b, c) = (b - a) x (c - a) is an
  affine invariant up to sign, and tau is an affine map of the grid.
  So a set S is no-three-collinear iff no triple {a, b, c} ⊂ S has
  cross(a, b, c) = 0; this property is preserved under tau, so S is
  "C4-symmetric and no-3-collinear" iff the chosen 5 orbit reps
  together with their tau-orbits contain no collinear triple. The
  backtrack checks exactly this at every insertion.

Cross-validation note (this file exists to be READ, not search):
  Three different symmetric closed-form backtracks all reach 20 on
  the 10x10 grid (see enumerate_symmetric.py):

    sigma  (C2, 180-deg) : 10 reps of orbit size 2 — ~1.6 s
    Klein4 (D2, h and v flips) : 5 reps of orbit size 4 — ~0.01 s
    tau    (C4, 90-deg rotation) : 5 reps of orbit size 4 — ~0.01 s

  Of these, C4 is the smallest symmetric family that still admits a
  20-point extremal packing: it has only 25 orbits and only 5 must
  be picked. We adopt the C4 route as the canonical construction
  here because it is the most constrained and most beautiful — the
  solution is literally invariant under 90-degree rotation of the
  board.
"""

from itertools import combinations


N = 10


# ---------------------------------------------------------------------------
# Geometric primitives.
# ---------------------------------------------------------------------------


def _cross(o, a, b):
    """Integer cross product of (a - o) and (b - o). Zero iff collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _tau(p):
    """90-degree clockwise rotation about the centre of the grid."""
    return (p[1], N - 1 - p[0])


def _sigma(p):
    """180-degree rotation about the centre (= tau^2)."""
    return (N - 1 - p[0], N - 1 - p[1])


def _orbit_tau(p):
    """The full C4 orbit of p under tau (always size 4 on this grid)."""
    out = [p]
    q = _tau(p)
    while q != p:
        out.append(q)
        q = _tau(q)
    return tuple(out)


def _no_three_collinear(points):
    for i, j, k in combinations(range(len(points)), 3):
        if _cross(points[i], points[j], points[k]) == 0:
            return False
    return True


# ---------------------------------------------------------------------------
# Deterministic C4-invariant backtrack.
# ---------------------------------------------------------------------------


def build_deterministic(target_size=20):
    """Return the lex-first C4-invariant no-3-collinear set of target_size.

    No randomness of any kind. Branches are explored in the
    lexicographic order of the canonical (smallest) point of each
    tau-orbit.
    """
    assert target_size % 4 == 0, "tau has order 4 and no fixed cells on 10x10"
    K = target_size // 4

    # Enumerate all 25 C4 orbits, each represented by its lex-smallest point.
    seen = set()
    reps = []       # canonical rep of each orbit (the lex-smallest)
    orbits = []     # the 4 points of each orbit, stored as tuple
    for r in range(N):
        for c in range(N):
            if (r, c) in seen:
                continue
            orb = _orbit_tau((r, c))
            assert len(orb) == 4
            rep = min(orb)
            for q in orb:
                seen.add(q)
            reps.append(rep)
            orbits.append(orb)
    # Sort by canonical rep so the enumeration is lex-deterministic.
    order = sorted(range(len(reps)), key=lambda i: reps[i])
    reps = [reps[i] for i in order]
    orbits = [orbits[i] for i in order]

    chosen_pts = []
    result = []

    def _triple_ok(old, new_orbit):
        """Check: adding 4 new points to old yields no 3-collinear triple.

        Only triples that involve at least one new point need checking
        (old was already valid).
        """
        new = new_orbit
        n_old = len(old)
        # (old_a, old_b, new_i)
        for i in range(n_old):
            oa = old[i]
            for j in range(i + 1, n_old):
                ob = old[j]
                for ni in new:
                    if _cross(oa, ob, ni) == 0:
                        return False
        # (old_a, new_i, new_j)
        for i_ in range(4):
            for j_ in range(i_ + 1, 4):
                ni, nj = new[i_], new[j_]
                for oa in old:
                    if _cross(ni, nj, oa) == 0:
                        return False
        # (new_i, new_j, new_k)
        for i_ in range(4):
            for j_ in range(i_ + 1, 4):
                for k_ in range(j_ + 1, 4):
                    if _cross(new[i_], new[j_], new[k_]) == 0:
                        return False
        return True

    def recurse(start):
        if result:
            return
        if len(chosen_pts) == target_size:
            result.extend(chosen_pts)
            return
        remaining_orbits_needed = K - len(chosen_pts) // 4
        for idx in range(start, len(orbits) - remaining_orbits_needed + 1):
            orb = orbits[idx]
            if not _triple_ok(chosen_pts, orb):
                continue
            chosen_pts.extend(orb)
            recurse(idx + 1)
            if result:
                return
            for _ in range(4):
                chosen_pts.pop()

    recurse(0)
    return result


# ---------------------------------------------------------------------------
# Cached 20-point solution from build_deterministic().
#
# Provenance (fully deterministic — no RNG, reproducible by anyone):
#   >>> from solution import build_deterministic
#   >>> build_deterministic(20)
#
# Returns the same 20 points on every machine and every Python version
# (only integer arithmetic is used). The 5 orbit representatives are:
#   (0, 0) (1, 3) (1, 5) (2, 3) (2, 4)
# and the full set is their C4-closure.
# ---------------------------------------------------------------------------


POINTS = [
    (0, 0),
    (0, 9),
    (1, 3),
    (1, 5),
    (2, 3),
    (2, 4),
    (3, 7),
    (3, 8),
    (4, 1),
    (4, 7),
    (5, 2),
    (5, 8),
    (6, 1),
    (6, 2),
    (7, 5),
    (7, 6),
    (8, 4),
    (8, 6),
    (9, 0),
    (9, 9),
]


# ---------------------------------------------------------------------------
# Self-test: verify the cached POINTS matches build_deterministic, and that
# the set is C4-invariant and no-3-collinear.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    assert len(POINTS) == 20
    assert len(set(POINTS)) == 20, "duplicate point"
    assert all(0 <= r < N and 0 <= c < N for r, c in POINTS)
    # C4-invariance
    S = set(POINTS)
    assert all(_tau(p) in S for p in S), "not tau-invariant"
    assert all(_sigma(p) in S for p in S), "not sigma-invariant"
    # no three collinear
    assert _no_three_collinear(POINTS), "collinear triple present"
    # cache matches derivation
    fresh = build_deterministic(20)
    assert sorted(fresh) == sorted(POINTS), "cache drift vs build_deterministic"
    print(f"OK: {len(POINTS)} points, C4-invariant, no-3-collinear, cache matches.")
