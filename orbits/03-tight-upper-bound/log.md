---
issue: 4
parents: [02-deterministic-closed-form.r1]
eval_version: eval-v1
metric: null
---

# Research Notes — Orbit 03

## Parent
Extends `orbit/02-deterministic-closed-form.r1` (consensus winner of orbit 02; C4-symmetric deterministic 20-point construction, metric = -20). Parent solution preserved in `parent_solution.py`.

## Extension Hypothesis
Orbits 01 and 02 together establish that at least two structurally distinct 20-point no-three-in-line configurations exist on the 10×10 grid (the lower bound is tight in the sense of being reachable). This orbit asks the complementary question: is 20 the **upper** bound? That is, can we **prove** that no 21-point no-three-in-line configuration exists on the 10×10 grid?

Approach: exhaustive branch-and-bound with aggressive pruning. Key constraints that limit the search:
  1. Each row contains at most 2 points (else 3-on-a-row is collinear).
  2. Each column contains at most 2 points (symmetric argument).
  3. For every pair of placed points, the line they determine excludes all other grid cells on that line from future placement.

With 2-per-row and 2-per-col constraints, 21+ points on a 10×10 grid already violate the pigeonhole at 2 × 10 = 20 per dimension — so the search is for whether 21 points can be placed under the collinearity constraint alone (relaxing 2-per-row/col). Full exhaustive DFS with collinearity pruning is tractable on modern hardware in minutes.

Deliverable: either (a) a 21-point valid configuration (which would be a mathematical result overturning the known bound, therefore extremely suspicious — require independent verification), or (b) a certificate-style "no such configuration exists; X branches explored" result. Commit a 20-point solution to keep the metric at -20, and report the certificate in log.md + figures.
