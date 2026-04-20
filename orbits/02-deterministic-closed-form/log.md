---
issue: 3
parents: [01-algebraic-local-search.r1]
eval_version: eval-v1
metric: -20.0
---

# Research Notes — Orbit 02  (deterministic closed-form)

**Hypothesis:** the 2N = 20 bound on the 10×10 no-three-in-line grid
can be reached by a *purely deterministic* enumeration over the
finite space of doubly-symmetric 20-point configurations — no RNG,
no hill-climb.  **Measured:** `METRIC = -20.000000` on seeds 1, 2, 3
(same as parent orbit 01, which used a randomised hill-climb).
**Implication:** the "search-free" 20-point construction exists and
fits in a one-page enumeration; RNG is *not* required for this
problem size.

## Before/After vs Parent
`orbit/01-algebraic-local-search.r1`: metric = -20 via a 400-restart
stochastic hill-climb seeded from the Erdős-Ko QR p=11 curve (depends
on `random.Random(20260420)` byte-for-byte).  **This orbit**:
metric = -20 via a 945-way partition enumeration in `< 2 ms` of
wall-clock, no randomness.  Δ = 0 on the raw metric axis, but the
construction is now closed-form and reproducible without CPython RNG
determinism guarantees.

## Approach

Doubly-symmetric configurations under central inversion
`σ: (r, c) ↦ (9-r, 9-c)`.  Because the centre `(4.5, 4.5)` is not on
the lattice, σ has no fixed point, so every configuration closed
under σ has even cardinality — pairs of points related by σ.  Any
20-point doubly-symmetric set is therefore determined by its
10-point *upper half* `H` (rows 0..4).

For the extremal case `|S| = 2N = 20`, standard counting arguments
(see e.g. Erdős 1951) force **exactly 2 points per row and 2 per
column**.  The 2-per-row constraint on the upper half means each of
rows 0..4 contributes a pair of columns, and the 2-per-column
constraint (combined with σ-symmetry) means the 10 upper-half
columns form a partition of `{0,...,9}` into 5 disjoint pairs.

The search space is therefore:

| Step | Choice                     | Size         |
|------|----------------------------|--------------|
| 1    | partition cols into 5 pairs | `10!/(2!^5·5!) = 945` |
| 2    | assign pairs to rows 0..4   | `5! = 120`   |
| **Total**  | upper-half configurations | **113 400** |

113 400 configurations, each with a 1140-triple collinearity check,
is about `1.3·10^8` integer operations — a fraction of a second in
Python.  No pruning required.

## Method  (closed-form enumeration)

Implemented in `constructor.py::sweep_doubly_symmetric()`.  Iteration
order is fixed by:

1. Recursive partitioning that always picks the smallest remaining
   column as the pair's left endpoint and sweeps right endpoints in
   ascending order.
2. `itertools.permutations` for the 5! row-assignments.

First partition/permutation whose mirror-completion passes the
integer-cross-product no-three-collinear check is returned.  The
first hit is

```
rows 0..4 get pairs (2,3), (6,7), (0,1), (8,9), (4,5)
```

which mirror-completes to the 20-point set

```
(0,2) (0,3)   (1,6) (1,7)   (2,0) (2,1)   (3,8) (3,9)   (4,4) (4,5)
(5,4) (5,5)   (6,0) (6,1)   (7,8) (7,9)   (8,2) (8,3)   (9,6) (9,7)
```

See `construction_proof.md` for the determinism audit and a direct
check of all 1 140 triples.

Because the iteration order is deterministic (no `random.*` anywhere
— see `grep` audit in `construction_proof.md`), running
`python3 constructor.py` produces this exact list on every
invocation, independent of Python version, clock, or environment.

### Enumeration of attempted deterministic approaches

| # | Family                                      | Sweep size           | 20-point?    |
|---|---------------------------------------------|----------------------|--------------|
| 1 | Pairs of quadratic curves `y = ax^2+bx+c` on GF(11) (+ axis-swap) | ~210 curve-pairs | ❌ |
| 2 | Pairs of modular hyperbolas `xy ≡ a (mod 11)`                    | 10 curves          | ❌ |
| 3 | Doubly-symmetric enumeration (this approach)                      | 113 400            | ✅ |

The algebraic-curve families (1, 2) were swept exhaustively in
`constructor.sweep_quad_curve_pairs()` and
`constructor.sweep_hyperbola_pairs()` and produced no 20-point
configuration — the 10 curves in each family, when pair-unioned,
always leave a collinear triple in the 10×10 window.  This is a
mildly interesting *negative* result on its own: a "famous curve
pair" closed-form à la Erdős-Ko does not extend to 2N on the 10×10
grid.

## Results

| Seed | METRIC     | Wall-clock (enum only) |
|------|-----------|------------------------|
| 1    | -20.000000 | 1.4 ms                 |
| 2    | -20.000000 | 1.4 ms                 |
| 3    | -20.000000 | 1.4 ms                 |
| **Median** | **-20.000000** |                     |

(Seeds have no effect here because `POINTS` is a static module
attribute — the determinism check is that every seed returns the
identical metric, which it does.)

Per-row / per-column histogram on `POINTS`:
- Each row `r ∈ {0..9}` has exactly 2 points.
- Each column `c ∈ {0..9}` has exactly 2 points.

Mirror-symmetry check (all 20 pairs exhibit `σ(p) ∈ S`): see
`construction_proof.md`.

## Figures

- `figures/narrative.png` — 4-panel construction: (a) partition 10
  columns into 5 disjoint pairs; (b) assign each pair to a row
  `0..4`; (c) mirror-complete via central inversion; (d) the final
  20 points colour-coded by Z/2 orbit (10 orbits × 2 points each).

- `figures/results.png` — 6-panel comparison to parent orbit 01:
  (a) metric vs baselines; (b) metric across seeds (both hit -20);
  (c) point-overlap count (19/19/1); (d) orbit 01 RNG-dependent
  solution; (e) orbit 02 deterministic solution with symmetry axes;
  (f) set-difference overlay.

## Prior Art & Novelty

### What is already known
- The 2N bound for n=10 is achieved by 20-point doubly-symmetric
  configurations; explicit solutions in this symmetry class have
  been published since at least [Flammenkamp (1998)](https://wwwhomes.uni-bielefeld.de/achim/no3in.html)
  and [Kløve (1978)].
- The RNG-hill-climb approach used by orbit 01 is folklore for this
  benchmark.

### What this orbit adds
- A **specific**, **timed** deterministic enumeration that produces
  a 20-point no-three-in-line set on the 10×10 grid in under 2 ms.
- Negative result: pairs of algebraic curves on GF(11) — the
  natural extension of the Erdős-Ko construction — do **not**
  extend to a full 20-point set within the 10×10 window.

### Honest positioning
The *existence* of doubly-symmetric 20-point solutions is
well-established (1970s-90s literature).  The *novelty* here is
operational: replacing orbit 01's RNG dependency with a closed-form
enumeration whose output is stable under any Python interpreter
change.  For campaign purposes this is strictly better than the
parent on the reproducibility axis at no cost on the metric axis.

## References

- Dudeney, H. E. (1917). *Amusements in Mathematics*, Puzzle 317.
- Erdős, P. (1951). On a problem of Dudeney. *Amer. Math. Monthly* 58.
- Flammenkamp, A. (1998). Progress on the no-three-in-line problem, II.
  *J. Combin. Theory Ser. A* 81, 108-113.
  [URL](https://wwwhomes.uni-bielefeld.de/achim/no3in.html)
- Gardner, M. (1976). Mathematical Games column, *Scientific
  American*, October 1976.

## Figure embeds

![narrative](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/02-deterministic-closed-form/orbits/02-deterministic-closed-form/figures/narrative.png)

![results](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/02-deterministic-closed-form/orbits/02-deterministic-closed-form/figures/results.png)

## Iteration log

### Iteration 1
- What I tried: pairs of quadratic curves `a x^2 + b x + c (mod 11)`.
- Metric: n/a (no 20-point union found across 210 curve pairs).
- Next: try doubly-symmetric enumeration.

### Iteration 2
- What I tried: pairs of modular hyperbolas `xy ≡ a (mod 11)`.
- Metric: n/a (no 20-point union found).
- Next: doubly-symmetric 113 400-way enumeration.

### Iteration 3
- What I tried: doubly-symmetric 10+10 construction, first hit in
  lex order.
- Metric: **-20.000000** on seeds 1, 2, 3.
- Next: exiting — target met and the construction is strictly more
  reproducible than the parent orbit.
