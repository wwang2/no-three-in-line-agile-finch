#!/usr/bin/env bash
# Reproduce orbit 01-algebraic-local-search from scratch.
# - regenerates solution.py via the hill-climb
# - regenerates figures
# - re-evaluates on all 3 seeds

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/../.." && pwd)"

cd "${HERE}"
python3 solution_generator.py --n-restarts 500 --inner-iters 2500
python3 make_figures.py

cd "${REPO_ROOT}"
for SEED in 1 2 3; do
  python3 research/eval/evaluator.py \
    --solution orbits/01-algebraic-local-search/solution.py \
    --seed "${SEED}"
done
