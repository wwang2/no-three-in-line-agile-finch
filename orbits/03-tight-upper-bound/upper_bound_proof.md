# Upper Bound: max no-three-in-line on the 10x10 grid is 20

**Theorem.** Let `S` be a subset of the 10x10 integer grid such that no
three points of `S` are collinear. Then `|S| <= 20`.

## Proof (row pigeonhole)

Let `r_k = |{p in S : p is in row k}|` for `k = 0, 1, ..., 9`.

Three points that share the same row are collinear — they all lie on
that horizontal line. Since `S` contains no collinear triple,

```
    r_k <= 2    for every k in {0, 1, ..., 9}.                (*)
```

Summing (*) over all ten rows,

```
    |S|  =  sum_{k=0}^{9} r_k  <=  sum_{k=0}^{9} 2  =  20.
```

Hence `|S| <= 20`, and equivalently every 21-point subset of `[10] x [10]`
already contains three collinear points — in fact contains some row
housing at least `ceil(21 / 10) = 3` of them.

QED.

Combined with the 20-point construction on the parent branch
(`parent_solution.py` / `solution.py`), the bound is tight: `max |S| = 20`.

## Remarks

- The only structural fact used is that three points on a horizontal
  line are collinear; we did not need the full no-three-in-line
  predicate for arbitrary lines. The stronger constraint only makes
  the bound tighter (or at least not looser).
- The argument is symmetric in rows and columns. The same proof with
  columns replacing rows also gives `|S| <= 20`.
- Pigeonhole on any single direction (rows, columns, or a diagonal)
  that partitions the board into 10 lines of width 2 suffices.

## Independent verifications (see `bnb_upper_bound.py`)

Three corroborating routes are executed by `bnb_upper_bound.py`, each
landing at the same 20 from a different direction:

1. **Row-pigeonhole restatement** — the theorem above, executable
   check: any `|S| >= 21` on 10 rows implies some row has `>=3`
   collinear points.

2. **Column-pigeonhole (dual)** — the same argument on columns.
   Together with the row axis this is a "two-witness" proof: the
   bound holds regardless of which axis you apply pigeonhole to.

3. **LP relaxation of the no-three-in-line IP (analytical, no scipy).**
   Formulate

   ```
   max   sum_{r,c} x_{r,c}
   s.t.  sum_c x_{r,c} <= 2     for every row r
         sum_r x_{r,c} <= 2     for every col c
         0 <= x_{r,c} <= 1
   ```

   Summing either family of constraints gives `sum x <= 2N = 20`. The
   uniform primal `x_{r,c} = 2/N` is feasible and attains 20, so LP* =
   20 exactly. Therefore `IP* <= LP* = 20` — even without invoking
   collinearity for arbitrary (non-axis-aligned) lines, the LP bound
   is already tight.

4. **Exhaustive branch-and-bound with row + column caps.** A
   depth-first search that (a) processes rows in order, (b) places 0,
   1, or 2 points per row, (c) enforces the column-cap `col_j <= 2`,
   and (d) applies the full integer-cross-product collinearity filter.
   With `target_size = 21` the recursion *never starts* — the row-cap
   prunes it at depth 0, with `n_explored = 0`. This is a mechanical
   confirmation that 21 is ruled out by the axis caps alone.

All four routes are coded in `bnb_upper_bound.py` and their outputs
are committed as `upper_bound_certificate.json`.

## Lower-bound witness

The parent 20-point construction (C4-invariant backtrack) in
`solution.py` achieves the bound. Its verification in
`upper_bound_certificate.json` confirms:

- `n_points = 20`
- `row_counts = col_counts = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]`  (every row
  and every column is saturated at the pigeonhole maximum)
- `no_three_collinear = True`

Every row and every column contains exactly 2 points: the construction
is extremal in every axis simultaneously. This is the equality case of
the Erdős–Szekeres bound `|S| <= 2N`, and matches the classical
tabulation of the 10x10 no-three-in-line problem (Flammenkamp 1998;
OEIS A000769). The campaign metric `-len(POINTS) = -20` is therefore
optimal.

## References

- P. Erdős, "On a combinatorial problem", 1951. (Conjecture `|S| <= 2N`.)
- H. E. Dudeney, "Amusements in mathematics", 1917. (Original puzzle
  formulation.)
- A. Flammenkamp, "Progress in the no-three-in-line problem, II",
  J. Combin. Theory Ser. A 81 (1998), 108–113. (Tabulation of
  solutions through N = 46, confirming tightness for N = 10.)
- OEIS [A000769](https://oeis.org/A000769): Maximum no-3-in-line on
  NxN grid.
