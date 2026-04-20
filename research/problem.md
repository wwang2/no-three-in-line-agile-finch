# No-Three-In-Line Problem on 10×10 Grid (Erdős extremal)

## Problem Statement

Classical Erdős extremal problem (Dudeney 1917, Erdős 1951): place as many points
as possible on a 10×10 integer grid such that **no three of them are collinear**.

The Erdős–Szekeres conjecture states the maximum is 2N on an N×N grid. For
N=10 the known optimum is **20**. Anything less does not meet the target —
this campaign's target is exactly the known optimum.

## Solution Interface

Submit a Python file `orbits/<name>/solution.py` exporting:

```python
N = 10
POINTS = [(r, c), ...]  # integer tuples, 0 <= r, c < 10
```

No `solve()` function needed — the evaluator reads these two module
attributes directly.

Constraints:
- **No sklearn, no `scipy.optimize`.** The search is discrete.
- Use local search, simulated annealing, algebraic constructions
  (quadratic residues mod a prime near 10, modular hyperbolas
  `{(x, 1/x mod p)}`), or hybrids.
- The evaluator is `research/eval/evaluator.py` — DO NOT rebuild it.

## Success Metric

**Negative point count** (direction: **minimize**).

- `METRIC = -len(POINTS)` when no three are collinear.
- `METRIC = 0.0` when the submission is invalid (any collinear triple,
  duplicate point, out-of-range coord, or wrong `N`).

Target: **-20** (20 points, the known optimum).
Anything weaker than -20 does not meet the campaign goal.

## Strategy Hints (for orbit design)

- **Naive lattices / rows / diagonals** saturate around 10–14 points.
- **Quadratic-residue curves** `(x, x² mod p)` for a prime `p ≥ 10` give
  good algebraic starting sets. For p=11: `{(x, x² mod 11) : 0 ≤ x ≤ 9}`
  has no three collinear (a famous Erdős–Ko construction), giving 10
  points; pairs of such curves can reach 2N.
- **Modular hyperbolas** `{(x, y) : xy ≡ a (mod p)}` give N−1 points.
- **Local search from a strong algebraic seed** (swap one point at a time,
  keep only moves that preserve no-three-collinear) reliably pushes
  good seeds from 16–18 up to 20.
- **Simulated annealing** on the full board (with the collinearity
  constraint as a hard filter plus soft penalty) is a proven route to
  the 2N ceiling.

## Budget

- max_orbits: 4 (hard cap — this problem is designed to need iteration).
- parallel_agents: 2 (two cross-validation replicas per orbit).
- Each orbit after orbit 01 must **extend** the best prior construction,
  not restart from scratch. Reference the parent orbit in `log.md` and
  in the Issue body.
