---
issue: 4
parents: [02-deterministic-closed-form.r1]
eval_version: eval-v1
metric: -20.0
---

# Research Notes — Orbit 03 (Tight Upper Bound)

**Hypothesis:** 20 is not only reachable on the 10x10 grid (orbits 01 and 02) but is also the tight upper bound — no 21-point no-three-in-line subset exists.

**Measured:** proved by horizontal pigeonhole + exhaustive B&B (0 branches at target=21; 1.1M branches at target=20 to confirm reachability). Metric preserved at -20 via the parent's C4-symmetric witness.

**Implication:** the Erdős-Szekeres bound 2N is tight at N=10 in both directions; further orbits on this campaign add nothing to the raw metric, so scientific value now shifts to *structural* questions (count of inequivalent 20-point configurations, symmetry classes, reachability for other N).

## Parent

Extends `orbit/02-deterministic-closed-form.r1`. The 20 points committed here are byte-identical to the parent's C4-invariant set, preserved so the metric remains -20. The scientific contribution of this orbit is the **upper-bound proof**, not a new configuration.

Parent → this orbit: metric = -20 → -20, Delta = 0 (by design — this orbit certifies the bound, it does not try to break it).

## Result — the tight bound

$$\max \{\, |S| : S \subseteq [10]^2 \text{ no-three-in-line}\,\} \;=\; 20.$$

The lower side (achievability) is the parent's construction. The upper side is proven in this orbit.

## Proof — one line

Distribute 21 points over 10 rows. By pigeonhole some row holds at least $\lceil 21/10 \rceil = 3$ points. Those 3 points lie on the same horizontal line and are therefore collinear. $\blacksquare$

Full proof with remarks, tightness discussion, and references is in [`upper_bound_proof.md`](upper_bound_proof.md).

## Method — exhaustive B&B

The driver [`bnb_upper_bound.py`](bnb_upper_bound.py) enumerates configurations row-by-row with a 2-per-row cap (P1 = horizontal pigeonhole) plus incremental collinearity checking (P2) and a residual-bound prune (P3).

- **`target = 21, row_cap = 2`:** the driver prunes at depth 0 via the pigeonhole inequality $21 > 2 \cdot 10$. **Branches explored = 0. Runtime = 11 microseconds.** Certificate: "no configuration with at most 2 points per row can reach 21".
- **`target = 20, row_cap = 2`:** 1,103,883 branches, 2.13 s, finds a 20-point witness. Confirms the cap is tight: 20 is reachable under the same constraint.
- **Parent check:** the 20-point committed configuration is re-verified to be no-3-collinear by pairwise cross-product.

The machine-readable summary is [`upper_bound_certificate.json`](upper_bound_certificate.json):

```json
{
  "N": 10,
  "claim": "no 21-point no-three-in-line subset of the 10x10 grid exists",
  "proof_method": "horizontal-pigeonhole + exhaustive branch-and-bound",
  "bnb_target_21": {"branches_explored": 0, "bound_proven": true, "runtime_seconds": 1.14e-5},
  "bnb_target_20_sanity": {"branches_explored": 1103883, "first_solution_size": 20, "runtime_seconds": 2.13},
  "verified": true
}
```

## Connection to the Erdős–Szekeres conjecture

The Erdős–Szekeres no-three-in-line conjecture (1951) asserts that on any $N \times N$ grid the maximum no-three-in-line subset has size at most $2N$. The pigeonhole argument above is literally the $\le 2N$ half of the conjecture specialized to $N = 10$: it works for every $N$ (take 2N+1 points over N rows, pigeonhole forces $\ge 3$ in some row, which are collinear on $y = r^\star$). The *non-trivial* direction of the conjecture is reachability: whether 2N is actually attained. Reachability is known numerically for $N \le 46$ (Flammenkamp 1998); the general case is still open. At $N = 10$, orbit 02 supplied the 20-point witness and so closed the loop.

## Prior Art & Novelty

### What is already known
- The $\le 2N$ upper bound via horizontal (or vertical) pigeonhole is a folklore observation going back to Dudeney (1917) and Erdős (1951). No mathematician claims it is deep; it is usually stated as a one-line remark when introducing the problem. See, e.g., [Brass, Moser & Pach, "Research Problems in Discrete Geometry" (2005), §10.1](https://link.springer.com/book/10.1007/0-387-29929-7).
- Reachability of $2N$ at $N = 10$ was established by Craggs–Hughes (1976) and extended by Flammenkamp (1992, 1998) who enumerated numerous 20-point configurations. See [Flammenkamp (1998)](https://doi.org/10.1006/jcta.1997.2823).
- The C4-symmetric 20-point set committed here is the same family of configurations enumerated in Flammenkamp's tables.

### What this orbit adds
- A **machine-checked certificate** (`upper_bound_certificate.json`) unifying the pigeonhole argument with an exhaustive B&B whose branch count at target=21 is provably zero.
- A clear write-up that separates the (trivial) upper bound from the (non-trivial) achievability direction, useful pedagogically within the campaign.
- **No novel mathematical claim.** The pigeonhole proof is textbook; the orbit's role is to close the campaign loop by certifying that 20 is tight, so future orbits can focus on structural enumeration rather than attempted improvements that cannot exist.

### Honest positioning
This is a consolidation orbit, not a discovery orbit. The upper bound was never open; orbits 01 and 02 established the lower bound; orbit 03 spells out the matching upper bound formally so the campaign can declare the N=10 case fully resolved. The metric is unchanged by design (a 21-point "improvement" would be impossible, so the orbit's job is to *prove* that impossibility, not to chase a metric).

## Figures

- `figures/narrative.png` — pigeonhole visualization: 21 points distributed over 10 rows, with the forced 3-on-a-row collision highlighted (three red points on $y = 9$, joined by the red line).
- `figures/results.png` — 2×2 canonical results panel: (a) search-space collapse from naive $\binom{100}{21} \approx 2 \times 10^{20}$ through row-capped $56^{10} \approx 3 \times 10^{17}$ down to 0 branches under the pigeonhole prune; (b) B&B branch counts at target=20 vs target=21; (c) the committed 20-point witness on the grid; (d) metric trajectory across orbits 01–03, all at -20, with the tight-bound line.

![narrative](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/03-tight-upper-bound/orbits/03-tight-upper-bound/figures/narrative.png)

![results](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/03-tight-upper-bound/orbits/03-tight-upper-bound/figures/results.png)

## Iteration 1
- What I tried: copied parent's 20-point POINTS; wrote pigeonhole proof + B&B driver + certificate + figures.
- Metric: -20.0 (mean across seeds 1, 2, 3 — all identical).
- Next: exiting — metric target (-20) met and upper bound proven; N=10 case is fully resolved.

## Results table

| Seed | Metric | Time |
|------|--------|------|
| 1    | -20.000000 | negligible (deterministic) |
| 2    | -20.000000 | negligible (deterministic) |
| 3    | -20.000000 | negligible (deterministic) |
| **Mean** | **-20.000 ± 0.000** | |

B&B certificate runtimes (separate from eval):

| Search                | Branches  | Runtime      |
|-----------------------|-----------|--------------|
| target=21, row_cap=2  | 0         | 11 microsec  |
| target=20, row_cap=2  | 1,103,883 | 2.13 s       |

## References

- Dudeney, H. E. (1917). *Amusements in Mathematics*, problem 317.
- Erdős, P. (1951). Problem on a lattice. In *Unsolved Problems*.
- Guy, R. K., & Kelly, P. A. (1968). The no-three-in-line problem. *Canad. Math. Bull.* **11**, 527–531.
- Flammenkamp, A. (1998). [Progress in the no-three-in-line problem, II](https://doi.org/10.1006/jcta.1997.2823). *J. Combin. Theory Ser. A* **81**, 108–113.
- Brass, P., Moser, W., & Pach, J. (2005). *Research Problems in Discrete Geometry*, §10.1.

## Glossary

- **No-three-in-line:** no three points in the set are collinear (lie on a common straight line in the plane).
- **Pigeonhole principle:** if $k$ items are placed into $n$ bins with $k > m \cdot n$, some bin has $> m$ items.
- **Cross product test:** three integer points $p, q, r$ are collinear iff $(q - p) \times (r - p) = 0$ where $\times$ denotes the 2D integer cross product.
- **C4-symmetric:** invariant under the 90-degree rotation $\tau(r, c) = (c, N - 1 - r)$ about the grid centre.
- **B&B (branch-and-bound):** recursive search that prunes subtrees unable to reach the target.
