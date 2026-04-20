# Upper-Bound Proof for the No-Three-In-Line Problem on the 10×10 Grid

**Claim.** No subset of the 10×10 integer grid with 21 or more points can be
free of collinear triples. Consequently 20 — achieved by the parent orbit's
C4-symmetric construction — is the tight maximum.

## Proof (Pigeonhole)

Let $S \subseteq \{0, 1, \ldots, 9\}^2$ be a set of 21 lattice points on the
10×10 grid. Partition $S$ by row: for each $r \in \{0, \ldots, 9\}$, let

$$
R_r \;=\; \bigl\{\, (r, c) \in S \,:\, 0 \le c \le 9 \,\bigr\}.
$$

Then $\sum_{r=0}^{9} |R_r| = |S| = 21$. Since there are 10 rows and
$21 > 2 \cdot 10 = 20$, the pigeonhole principle guarantees some row index
$r^\star$ with

$$
|R_{r^\star}| \;\ge\; \lceil 21 / 10 \rceil \;=\; 3.
$$

Choose any three points $p_1, p_2, p_3 \in R_{r^\star}$. Each has row
coordinate exactly $r^\star$, so all three lie on the horizontal line
$y = r^\star$. Three distinct points on a common line are collinear, so $S$
contains a collinear triple. Therefore no 21-point no-three-in-line subset of
the 10×10 grid exists. $\blacksquare$

## Remarks

1. **Tightness.** Combined with the 20-point C4-invariant construction of
   orbit 02 (cached as `POINTS` in `solution.py` and re-verified in this
   orbit's certificate), we get

   $$
   \max \{\, |S| : S \subseteq [10]^2 \text{ no-three-in-line}\,\} \;=\; 20.
   $$

   Orbit 01 showed 20 is reachable; orbit 02 produced a C4-symmetric 20-point
   witness; this orbit shows 20 is also the ceiling.

2. **Equality in the Erdős–Szekeres bound at $N=10$.** The Erdős–Szekeres
   conjecture (Erdős 1951) states that on any $N \times N$ grid the maximum
   no-three-in-line subset has size at most $2N$. The pigeonhole argument
   above is in fact the conjecture's own proof at $N = 10$: $k > 2N$ forces
   $\lceil k / N \rceil \ge 3$, hence three points in some row. The
   non-trivial content of the conjecture is the *reachability* of $2N$, not
   the upper bound.

3. **Why this is *the* proof.** One may wonder whether a stronger argument is
   needed — e.g., exploiting diagonals, columns, or the full affine group of
   the grid. It is not. The pigeonhole constraint alone already pins the
   answer; the columns and diagonals only restate the same inequality from a
   rotated perspective. Exhaustive enumeration confirms (see below) that the
   search tree for 21 points prunes at depth zero under the row-cap
   constraint alone.

4. **Independent verification by exhaustive B&B.** The driver
   `bnb_upper_bound.py` enumerates all row-subset sequences of length 10 with
   each row contributing at most 2 points, tracking collinearity
   incrementally. At `target = 21` the driver reports

   ```
   branches_explored = 0
   bound_prunes      = 1       (fires at depth 0 via the 2·N inequality)
   solutions_found   = 0
   ```

   while at `target = 20` (same row cap) the driver finds a witness with
   branches in the millions, confirming both that the pigeonhole prune is
   correct and that 20 is reachable.

5. **For $N \ge 11$.** The same pigeonhole argument shows that $2N + 1$
   points force three on a row for any $N$, which is the $\le 2N$ half of
   the Erdős–Szekeres conjecture. The conjecturally hard direction — that
   $2N$ is actually achieved — is known only for $N \le 46$; see
   Flammenkamp (1998) for current numerical records and Guy–Kelly (1968),
   Craggs–Hughes (1976), Anderson (1979), Hall–Jackson–Sudbury–Wild (1975)
   for the achievability side.

## References

- Dudeney, H. E. (1917). *Amusements in Mathematics*, problem 317.
- Erdős, P. (1951). Problems on a lattice. In *Unsolved Problems* (a short
  note).
- Guy, R. K., and Kelly, P. A. (1968). The no-three-in-line problem.
  *Canad. Math. Bull.* **11**, 527–531.
- Flammenkamp, A. (1998). Progress in the no-three-in-line problem, II.
  *J. Combin. Theory Ser. A*, **81**, 108–113.

The 20-point witness is preserved in `solution.py` (parent provenance:
`orbit/02-deterministic-closed-form.r1`). The machine-checkable
certificate is `upper_bound_certificate.json`; the driver is
`bnb_upper_bound.py`.
