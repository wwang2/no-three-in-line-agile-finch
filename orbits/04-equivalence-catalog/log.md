---
issue: 5
parents: [03-tight-upper-bound, 02-deterministic-closed-form.r1, 01-algebraic-local-search.r1]
eval_version: eval-v1
metric: null
---

# Research Notes — Orbit 04 (Campaign Synthesis)

## Parents
Extends the whole campaign. Preserved parent solutions for cross-reference:
- `parent_orbit01_r1.py` — orbit 01 replica consensus winner (QR + axis-swap + hill-climb, RNG-based)
- `parent_orbit02_primary.py` — orbit 02 primary (Z/2 central-inversion, deterministic)
- `parent_orbit02_r1.py` — orbit 02 replica consensus winner (C4 90°-rotation, deterministic)
- `parent_orbit03.py` — orbit 03 witness (identical to orbit 02 r1)

## Extension Hypothesis
Orbits 01-03 give: (i) a reachable lower bound of 20, (ii) two structurally distinct 20-point constructions, and (iii) a proof that 20 is tight. The remaining natural question: **how many 20-point configurations exist up to grid symmetry (the dihedral group D4)**, and where do the campaign's three distinct solutions fall in that catalog?

Approach: enumerate all 20-point valid configurations modulo the D4 action \{identity, r90, r180, r270, flipH, flipV, flipDiag, flipAntiDiag\}, then for each of the campaign's prior solutions compute its D4 orbit and check which catalog class it lands in. Exhaustive enumeration of ALL 20-point configurations is large but tractable with 2-per-row / 2-per-col pruning and incremental collinearity; if intractable within wall-clock budget, sample-enumerate (enumerate orbits from a set of algebraic seeds + Monte-Carlo fill).

Deliverables:
1. solution.py — the D4-canonical representative of the lex-smallest class that contains the campaign's consensus winner
2. enumerate_classes.py — the enumeration driver (or at least a bounded sample)
3. catalog.json — count of classes enumerated + canonical representative of each
4. cross_reference.md — where each of orbits 01-r1, 02-primary, 02-r1, 03 lands in the catalog
5. figures/narrative.png — gallery of ALL enumerated classes (grid-of-grids)
6. figures/results.png — campaign arc summary (orbit-by-orbit metric + class mapping)
