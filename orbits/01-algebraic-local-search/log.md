---
issue: 2
parents: []
eval_version: eval-v1
metric: -20.0
---

# Research Notes

**Hypothesis:** Seed the 10x10 grid with a quadratic-residue (QR) curve
{(x, x^2 mod 11)}, augment with a second algebraic curve, then hill-climb
with single-point removal + greedy re-extension to reach the known optimum
of 20 points. **Measured:** metric = -20.0 on all three seeds (evaluator
is deterministic in POINTS). **Implication:** the 2N ceiling is reachable
from a purely algebraic seed plus single-swap local search; no simulated
annealing, no exotic moves required.

## Approach

The problem is the classical Dudeney / Erdős extremal: place as many
integer grid points on a 10x10 board as possible with no three collinear.
The known optimum is **20 = 2N**, matching the Erdős-Szekeres conjecture
for this N.

Pipeline:

1. **Algebraic seed.** Build two quadratic-residue curves of the form
   C(a, b, c) = {(x, (a*x^2 + b*x + c) mod 11) : x = 0..9}. Each single
   curve has at most 2 points on any line (because a non-degenerate
   quadratic has at most 2 roots modulo a prime), so each gives up to 10
   mutually non-collinear points when clipped to the grid.
2. **Sanitized union.** Walk the union of the two curves and only
   accept a point if it preserves the no-three-collinear property against
   the set accumulated so far. Typical output: 12-14 points.
3. **Greedy extension.** Incrementally add any grid cell that doesn't
   break the invariant. With randomized order + 32 tries per restart,
   this usually produces 17-19 points.
4. **Single-swap hill climb.** Remove one random point, then greedily
   re-extend. Accept if the new configuration is strictly larger.
   Lateral moves accepted with probability 0.1 to escape plateaus.
5. **Double-swap hill climb.** Same idea, but remove two points.
   Slower, but escapes basins the single-swap can't.
6. **Randomized restarts** over a 500-restart budget on seeds (a1, b1,
   c1, a2, b2, c2). Stop early when 20 points is reached.

## Method

- **No simulated annealing, no scipy, no sklearn** — pure combinatorial
  search, as the problem spec requires.
- Collinearity check is the integer cross product
  (p_j - p_i) x (p_k - p_i) == 0, matching the evaluator exactly.
- Candidate-cell enumeration precomputes the "forbidden" set: for each
  pair of placed points (a, b), every grid cell on the line through
  (a, b) is blocked. Candidates are `{grid} \ {placed} \ {forbidden}`.
- Python 3 standard library only (`random`, `pathlib`, `argparse`).
  `matplotlib` is used only for figure generation, not for the search.
- `solution_generator.py` is deterministic given the restart seed; the
  committed `solution.py` is the first 20-point configuration the
  generator found (restart 8).
- Top-level determinism is keyed on the `MASTER_SEED = 0` constant in
  `solution_generator.py`; per-restart RNG is
  `random.Random(MASTER_SEED + i)` for restart `i`. Reproducibility
  across Python versions depends on CPython's `random.Random`
  (Mersenne Twister) implementation — the committed `solution.py`
  and `trace.csv` were produced under CPython 3.

### Convergence trace

The committed `trace.csv` was produced by running
`python3 solution_generator.py` with the code defaults
(`--n-restarts 500 --inner-iters 2500`); the run exited early at
restart 8 when the 20-point target was reached, so `trace.csv`
contains only the first 9 restart-groups:

```
[restart 0] new best = 18 points (t=9.8s)
[restart 1] new best = 19 points (t=20.6s)
[restart 8] new best = 20 points (t=100.5s)
[restart 8] target 20 reached — stopping
```

Reading the 8 pre-success restart-end rows in `trace.csv`, single-
plus-double-swap hill-climb plateaus at 19 in 6 of 8 restarts (75%)
and at 18 in 2 of 8 (25%). The jump to 20 is rare (one success in
the first 9 restarts on this schedule) and requires the double-swap
stage to escape the "19-point basin".

## Results

**Evaluator output (pasted verbatim):**

```
$ python3 research/eval/evaluator.py --solution orbits/01-algebraic-local-search/solution.py --seed 1
METRIC=-20.000000
$ python3 research/eval/evaluator.py --solution orbits/01-algebraic-local-search/solution.py --seed 2
METRIC=-20.000000
$ python3 research/eval/evaluator.py --solution orbits/01-algebraic-local-search/solution.py --seed 3
METRIC=-20.000000
```

| Seed | Metric  | Wall time |
|------|---------|-----------|
| 1    | -20.000 | <1s (eval alone) |
| 2    | -20.000 | <1s |
| 3    | -20.000 | <1s |
| **Median** | **-20.000** | — |

Target `-20.0` reached on all three evaluator seeds. The evaluator is
deterministic in the committed POINTS list, so all three seeds return
the same value — this is expected and documented in
`research/eval/evaluator.py`.

### Committed configuration

20 points, two per row and two per column (verified by hand), with
source labels (counts taken directly from `solution_sources.py`):

- **QR-curve seed #1** (blue): 6 points from a parabola mod 11.
- **QR-curve seed #2** (orange): 1 additional point from a second
  parabola that was compatible with the running set.
- **greedy extension** (green): 8 points added by the greedy stage.
- **swap-inserted** (red): 5 points that only fit after the
  single-swap stage removed an earlier point.

The `swap-inserted` group (red) is the critical piece — without it the
construction plateaus at 15 (= 6 + 1 + 8, the combined QR-seed +
greedy contributions). That the hill-climb can promote five points
through a swap-and-re-extend cycle is the whole reason this orbit
reaches 20 rather than 15.

## Figures

![narrative — 20 points and pairwise lines](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/01-algebraic-local-search/orbits/01-algebraic-local-search/figures/narrative.png)

![results — convergence, per-seed, configuration, histogram](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/01-algebraic-local-search/orbits/01-algebraic-local-search/figures/results.png)

![behavior — build order seed1 → seed2 → greedy → swap](https://raw.githubusercontent.com/wwang2/no-three-in-line-agile-finch/refs/heads/orbit/01-algebraic-local-search/orbits/01-algebraic-local-search/figures/behavior.gif)

## Prior Art & Novelty

### What is already known

- **Dudeney (1917)** posed the problem. **Erdős (1951)** conjectured
  that the maximum on an N x N grid is 2N.
- **Erdős–Ko (1970s)** gave the quadratic-residue curve construction:
  {(x, x^2 mod p)} for a prime p places N mutually non-collinear
  points on an N x N grid whenever p is near N, providing the
  algebraic seed used here.
- The 20-point optima on the 10 x 10 grid were enumerated
  numerically in the 1980s–1990s (see Flammenkamp's and Guy's
  compilations in the "no three in line problem" literature).

### What this orbit adds (if anything)

- **Nothing novel.** This is a textbook QR-curve + hill-climb
  reproduction. The contribution is the working reproduction:
  a self-contained pure-Python generator that reliably finds a
  20-point configuration from a random seed.

### Honest positioning

This orbit establishes a baseline for the campaign: the target is
reachable with a simple algebraic-seed + local-search hybrid, and the
evaluator scores the committed 20-point configuration at -20.0.
Subsequent orbits that extend this should aim at structural properties
(e.g. symmetries, double-symmetric 20-point configurations) rather than
at raising the count, since 20 is the Erdős-Szekeres target for N=10.

## References

- Erdős, P. (1951). *Problems and results in combinatorial analysis.*
- Dudeney, H. E. (1917). *Amusements in Mathematics*, problem 317.
- Flammenkamp, A. (1998). *Progress in the no-three-in-line problem.*
  J. Combinatorial Theory A 81, 108–113.
- Guy, R. K. (2004). *Unsolved Problems in Number Theory*, problem F4.

## Iteration log

### Iteration 1
- What I tried: single QR-curve seed + greedy extension only.
- Best sampled (internally during development): ~15 points.
- Next: add a second QR curve + hill climb with single + double swaps.

### Iteration 2
- What I tried: two QR curves + greedy + single-swap + double-swap,
  randomized restarts.
- Metric: -20.000 (target reached at restart 8 / seed 8).
- Next: exit — target met.

### Iteration 3 (round-2 polish — no search changes)
- What I tried: addressed reviewer findings on documentation honesty
  and code hygiene. Corrected per-source counts (qr1=6, qr2=1,
  greedy=8, swap=5 — taken directly from `solution_sources.py`) and
  the "without swap" floor (15 rather than 16). Corrected the
  plateau-frequency claim to match `trace.csv` exactly (6/8 = 75%
  at 19, 2/8 = 25% at 18). Recorded the actual run command
  (`--n-restarts 500 --inner-iters 2500` with early exit at restart
  8) that produced `trace.csv`. Deleted dead functions
  `greedy_extend_all_orders` and `affine_transform` from
  `solution_generator.py`. Pinned `MASTER_SEED = 0` for
  restart-index keying and noted CPython dependence. Simplified
  `results.png` panel (b) bar annotation to "20 points" and added a
  "final METRIC = -20" annotation to every `behavior.gif` frame
  (including the poster frame).
- Metric: -20.000 (unchanged — `solution.py` was not modified).
- Next: exit — target met, documentation reconciled with committed
  artifacts.
