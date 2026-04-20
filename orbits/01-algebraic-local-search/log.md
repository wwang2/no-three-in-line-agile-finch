---
issue: 2
parents: []
eval_version: eval-v1
metric: null
---

# Research Notes

## Strategy
Quadratic-residue curve seed $\{(x, x^2 \bmod 11)\}$ on p=11 as base construction (guarantees 10 non-collinear points by the standard Erdős–Ko argument), then augment with a complementary algebraic set (affine shift) + local search to push toward the known optimum of 20 points.
