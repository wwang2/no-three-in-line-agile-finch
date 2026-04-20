---
issue: 3
parents: [01-algebraic-local-search.r1]
eval_version: eval-v1
metric: null
---

# Research Notes — Orbit 02

## Parent Orbit
Extends `orbit/01-algebraic-local-search.r1` (consensus winner of orbit 01). Parent construction: QR p=11 curve + axis-swap curve + greedy expansion + layered k-swap hill-climb with pinned RNG seed 20260420, score = -20. The parent solution is preserved here as `parent_solution.py` for reference.

## Extension Hypothesis
Orbit 01's 20-point solutions were found by randomized local search on top of an algebraic seed — reproducibility depends on CPython `random.Random` byte-for-byte determinism. This orbit seeks a **fully deterministic, search-free** construction: systematically sweep algebraic curves on GF(p) for small p ∈ {7, 11, 13}, modular hyperbolas $\{(x, a/x \bmod p)\}$, and doubly-symmetric constructions, enumerating candidate 20-point configurations without any randomness. If a 20-point construction exists as a closed-form expression, commit it as the new canonical solution.

