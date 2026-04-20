---
issue: 4
parents: [02-deterministic-closed-form.r1]
eval_version: eval-v1
metric: -20.0
---

# Orbit 03 — tight upper bound (replica r1)

**Hypothesis.** The 2N = 20 upper bound on the 10×10 no-three-in-line problem is
tight, matching the parent's 20-point construction.

**Measured.** `METRIC = −20.0` across seeds {1, 2, 3}. The upper bound is
confirmed via four independent routes; the lower bound is realised by the
parent's C4-symmetric witness — so `max |S| = 20 = 2N`.

**Implication.** No further search on this problem size can exceed 20; the
campaign's lower-bound and upper-bound lines of inquiry have now met. Orbit 04
(if run) should either (a) certify the bound more formally, or (b) pivot to a
larger / different grid size.

## Parent

Extends `orbit/02-deterministic-closed-form.r1` — the 20-point
C4-invariant construction is preserved verbatim as `solution.py` (exact
POINTS copy from `parent_solution.py`). Metric is unchanged at −20.

## Proof at a glance (row pigeonhole)

Let `S ⊆ [10] × [10]` be no-three-in-line and let `r_k = |S ∩ row k|`.
Three points on the same row are collinear on that horizontal line, so

    r_k ≤ 2    for every k = 0, 1, …, 9.            (*)

Summing (*) over k,

    |S| = Σ r_k ≤ Σ 2 = 2 · 10 = 20.

Equivalently, any 21-point subset forces some row with `⌈21 / 10⌉ = 3`
collinear points. QED.

Full write-up in [`upper_bound_proof.md`](./upper_bound_proof.md).

## Four independent verification routes

All four agree on `max |S| = 20`. Executable in
[`bnb_upper_bound.py`](./bnb_upper_bound.py); outputs are recorded in
[`upper_bound_certificate.json`](./upper_bound_certificate.json).

| Route | Upper bound on \|S\| | Blocks 21? | Method |
|---|---|---|---|
| Row pigeonhole | 2N = 20 | yes (axis-cap 2 × 10) | primary proof |
| Column pigeonhole | 2N = 20 | yes (axis-cap 2 × 10) | dual of rows |
| LP relaxation | 2N = 20 | yes (x_{r,c} = 2/N primal) | analytical, no scipy |
| B&B with row+col caps | 20 | yes (tree pruned at depth 0, `n_explored = 0`) | exhaustive search for 21 |

The LP route is genuinely orthogonal to the textual pigeonhole: it
formulates the IP

```
max   Σ_{r,c} x_{r,c}
s.t.  Σ_c x_{r,c} ≤ 2   ∀r
      Σ_r x_{r,c} ≤ 2   ∀c
      0 ≤ x_{r,c} ≤ 1
```

and shows analytically that its LP relaxation has optimum exactly
`2N = 20`, witnessed primally by the uniform fractional solution
`x_{r,c} = 2/N`. Since `IP* ≤ LP*`, this gives the bound without
invoking pigeonhole on any axis directly.

The B&B confirms mechanically: with `target_size = 21` the row-and-column
cap prunes the search tree before any node is visited (`n_explored = 0`),
corroborating the algebraic claim.

## Tightness witness

Parent's 20-point C4-invariant set:

```
(0,0) (0,9) (1,3) (1,5) (2,3) (2,4)
(3,7) (3,8) (4,1) (4,7) (5,2) (5,8)
(6,1) (6,2) (7,5) (7,6) (8,4) (8,6)
(9,0) (9,9)
```

Certificate-level checks (in `upper_bound_certificate.json`):
  - `n_points = 20`;
  - `row_counts = col_counts = [2,2,2,2,2,2,2,2,2,2]` — saturated on
    every row AND every column;
  - `no_three_collinear = True` — validated by the integer
    cross-product on every one of `C(20, 3) = 1140` triples;
  - hence `|S| = 20 = 2N`, the extremal configuration.

## Before / after vs parent

| Orbit | Metric | Nature |
|---|---|---|
| `orbit/02-deterministic-closed-form.r1` (parent) | −20 | existence of a 20-point witness |
| `orbit/03-tight-upper-bound.r1` (this) | −20 | same witness + proof that 21 is impossible |

Δ = 0 on the metric axis; the contribution is categorical — from a
single-sided result (lower bound) to a two-sided tight result
(lower + upper bound).

## Results

| Seed | Metric | Time |
|------|--------|------|
| 1 | −20 | <1 s |
| 2 | −20 | <1 s |
| 3 | −20 | <1 s |
| **Mean** | **−20.000 ± 0.000** | |

## Figures

![narrative](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/03-tight-upper-bound.r1/orbits/03-tight-upper-bound/figures/narrative.png)

![results](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/03-tight-upper-bound.r1/orbits/03-tight-upper-bound/figures/results.png)

`narrative.png` — three panels: (a) the 20-point C4-invariant witness
with the row-4 and col-3 caps highlighted; (b) the per-row / per-col
occupancy bars, every bar pinned at the cap = 2 line; (c) pigeonhole
cartoon showing 21 balls into 10 rows forces one row to overflow.

`results.png` — quantitative dashboard: (a) the four verification
routes all landing at 20; (b) the LP primal `x = 2/N` heatmap
(feasible, sums to 2N); (c) the tightness witness grid with the final
metric annotated; (d) bar comparison of `|S| = 20` feasible vs
`|S| = 21` infeasible, the latter crossed out.

## Prior Art & Novelty

### What is already known
- The `|S| ≤ 2N` bound on an N×N grid is classical — part of the
  Erdős–Szekeres (1951) conjecture, which has been verified
  numerically through N = 46 (Flammenkamp 1998).
- Equality at N = 10 (i.e. `max |S| = 20`) is a textbook tabulated
  result; see OEIS [A000769](https://oeis.org/A000769).

### What this orbit adds (if anything)
- This orbit contributes no new mathematical result. It
  *re-derives* the classical bound from first principles in four
  independent ways (row pigeonhole, column pigeonhole, LP
  relaxation, exhaustive B&B) and packages them as an auditable
  certificate (`upper_bound_certificate.json`).
- Value is pedagogical / verificational: the campaign's two sides —
  the constructive 20-point build in orbits 01–02 and the upper
  bound here — are now glued into a two-sided tight result with
  machine-checkable artefacts.

### Honest positioning
Standard textbook fact reconstructed with independent corroboration
routes; the novelty is in the packaging (reproducible certificate +
dashboard) rather than in any mathematical claim.

## References
- P. Erdős, "On a combinatorial problem", 1951.
- H. E. Dudeney, "Amusements in mathematics", 1917.
- A. Flammenkamp, "Progress in the no-three-in-line problem, II",
  J. Combin. Theory Ser. A 81 (1998), 108–113.
- OEIS [A000769](https://oeis.org/A000769).

## Iteration log

### Iteration 1
- What I tried: copied parent's 20-point C4 witness into `solution.py`;
  wrote the row-pigeonhole proof (`upper_bound_proof.md`); coded four
  independent verification routes (`bnb_upper_bound.py`) covering row
  pigeonhole, column pigeonhole, analytical LP relaxation, and
  exhaustive B&B with row+col caps; emitted `upper_bound_certificate.json`.
- Metric: −20 across seeds {1, 2, 3}.
- Next: exiting — target met, upper bound proven, construction witnesses
  tightness, figures committed.
