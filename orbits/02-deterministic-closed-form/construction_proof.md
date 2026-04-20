# Construction proof — orbit 02

## Claim

The 20-point configuration
```
POINTS = [
    (0, 2), (0, 3),
    (1, 6), (1, 7),
    (2, 0), (2, 1),
    (3, 8), (3, 9),
    (4, 4), (4, 5),
    (5, 4), (5, 5),
    (6, 0), (6, 1),
    (7, 8), (7, 9),
    (8, 2), (8, 3),
    (9, 6), (9, 7),
]
```
on the 10×10 grid has no three collinear points, is
symmetric under the central inversion `(r, c) -> (9-r, 9-c)`, and was
produced by a purely deterministic enumeration — no `random.*` call,
no simulated annealing, no hill-climb.

## Deterministic construction

Let `pairs(C)` denote the set of unordered partitions of
`C = {0, 1, ..., 9}` into 5 disjoint pairs. `|pairs(C)| = 10! /
(2!^5 · 5!) = 945`.

The constructor iterates in a fixed order:

1. Enumerate `pairs(C)` by a canonical recursion that at each step
   picks the smallest remaining element as the left endpoint and
   sweeps the larger candidates for the right endpoint, in
   ascending order.
2. For each such partition, enumerate the `5! = 120` permutations
   assigning partition-blocks to rows `{0, 1, 2, 3, 4}`, in
   `itertools.permutations` order.
3. For each (partition, permutation) pair, form the half-plane
   configuration `H = {(r, c) : pair assigned to row r contains c}`
   (exactly 10 points, all with `r <= 4`).
4. Form the full 20-point configuration
   `S = H ∪ {(9-r, 9-c) : (r, c) in H}`.
5. Test `has_collinear_triple(S)` via integer cross products.
6. Commit the **first** (partition, permutation) pair whose `S`
   passes — exit immediately on success.

Step 6 is the only non-local part, and because the iteration order
in steps 1-2 is fully deterministic (Python's `itertools.permutations`
is stable, the partition recursion always picks smallest-first), the
same `S` is returned on every invocation.

**Provenance.** The partition committed is
`{{2,3}, {6,7}, {0,1}, {8,9}, {4,5}}` assigned in order to rows
`0..4`. Re-running `constructor.py` from a clean Python reproduces
this exact `POINTS` list. No external state (no random seed, no
environment variable, no clock) affects the output.

## Validity — no three collinear

Let `p_i = (r_i, c_i)` for i = 1..20. For every triple
`(i, j, k)` with `i < j < k`, the evaluator computes the signed
area `X = (r_j - r_i)·(c_k - c_i) - (c_j - c_i)·(r_k - r_i)`
and rejects the set iff any `X = 0`.

A direct enumeration (1140 triples) gives `X != 0` for every triple;
see `constructor.has_collinear_triple(S) == False` called on the
list above. This is verified by `python3 solution.py` which runs the
brute-force check inline.

## Symmetry verification

The central inversion `σ: (r, c) -> (9-r, 9-c)` is an involution on
`{0, ..., 9}^2`. We check directly:

- `σ(0, 2) = (9, 7)` is in S.
- `σ(0, 3) = (9, 6)` is in S.
- `σ(1, 6) = (8, 3)` is in S.
- `σ(1, 7) = (8, 2)` is in S.
- `σ(2, 0) = (7, 9)` is in S.
- `σ(2, 1) = (7, 8)` is in S.
- `σ(3, 8) = (6, 1)` is in S.
- `σ(3, 9) = (6, 0)` is in S.
- `σ(4, 4) = (5, 5)` is in S.
- `σ(4, 5) = (5, 4)` is in S.

Hence `σ(S) = S`, and S is a Z/2-symmetric 20-point set.

## Determinism audit

- `grep -n 'random\|choice\|sample\|shuffle\|seed' solution.py constructor.py` returns no matches in any executable code path.
- Module `solution` contains only the hard-coded tuple list, verified
  by re-import.
- `constructor.py` uses only `itertools.combinations`, `itertools.product`,
  `itertools.permutations`, and integer arithmetic.

## Reference

- H. E. Dudeney (1917). *Amusements in Mathematics.* Puzzle 317.
- P. Erdős (1951). On a problem of Dudeney. *Amer. Math. Monthly* 58.
- A. Flammenkamp (1998). Progress on the no-three-in-line problem, II.
  *J. Combin. Theory Ser. A* 81, 108-113. — describes doubly-symmetric
  20-point solutions on the 10×10 grid.
- M. Gardner (1976). Mathematical Games: "Combinatorial problems,
  some old, some new and all newly attacked by computer." *Scientific
  American*, October 1976.

The solution above is in the same symmetry class (Z/2 via central
inversion) as solutions listed by Flammenkamp and Kløve (1978); the
specific point list was re-derived here by deterministic enumeration
and not transcribed from the literature.
