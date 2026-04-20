"""
03-tight-upper-bound — solution.py
==================================

This orbit's scientific contribution is the *upper-bound proof* that no
21-point no-three-in-line configuration exists on the 10x10 grid (i.e.
20 is both lower- and upper-tight, matching the Erdős-Szekeres
conjectural bound 2N at N=10). The committed solution here is the
parent orbit's 20-point C4-symmetric configuration, preserved verbatim
so that the metric remains -20.

The proof artifacts live alongside:
  * upper_bound_proof.md      — one-page pigeonhole argument
  * bnb_upper_bound.py        — exhaustive branch-and-bound driver
  * upper_bound_certificate.json — machine-readable certificate
  * figures/narrative.png     — pigeonhole visualization
  * figures/results.png       — search-space comparison + metric panel

Parent provenance (orbit/02-deterministic-closed-form.r1): the 20
points are the C4-invariant lex-first extremal set. Five tau-orbit
representatives {(0,0),(1,3),(1,5),(2,3),(2,4)} generate the full
configuration under tau(r,c) = (c, N-1-r). See parent_solution.py for
the full derivation.
"""

from itertools import combinations


N = 10


def _cross(o, a, b):
    """Integer cross product of (a - o) and (b - o). Zero iff collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _tau(p):
    """90-degree clockwise rotation about the centre of the grid."""
    return (p[1], N - 1 - p[0])


def _sigma(p):
    """180-degree rotation about the centre (= tau^2)."""
    return (N - 1 - p[0], N - 1 - p[1])


def _no_three_collinear(points):
    for i, j, k in combinations(range(len(points)), 3):
        if _cross(points[i], points[j], points[k]) == 0:
            return False
    return True


# ---------------------------------------------------------------------------
# The 20 points — copied verbatim from orbit/02-deterministic-closed-form.r1.
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


if __name__ == "__main__":
    assert len(POINTS) == 20
    assert len(set(POINTS)) == 20, "duplicate point"
    assert all(0 <= r < N and 0 <= c < N for r, c in POINTS)
    # C4 invariance (proof of parent provenance).
    S = set(POINTS)
    assert all(_tau(p) in S for p in S), "not tau-invariant"
    assert all(_sigma(p) in S for p in S), "not sigma-invariant"
    # No three collinear.
    assert _no_three_collinear(POINTS), "collinear triple present"
    print(f"OK: {len(POINTS)} points, C4-invariant, no-3-collinear.")
