#!/usr/bin/env bash
# run.sh — reproduce orbit/03-tight-upper-bound from seed.
#
# Runs three things:
#   1. Self-test on solution.py (C4 invariance + no-3-collinear).
#   2. B&B driver producing upper_bound_certificate.json.
#   3. Evaluator across seeds 1-3 (expected METRIC=-20 on each).
#   4. Figure regeneration.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== 1/4 self-test solution.py =="
uv run python3 orbits/03-tight-upper-bound/solution.py

echo "== 2/4 exhaustive B&B =="
uv run python3 orbits/03-tight-upper-bound/bnb_upper_bound.py

echo "== 3/4 evaluator seeds 1-3 =="
for SEED in 1 2 3; do
    uv run python3 research/eval/evaluator.py \
        --solution orbits/03-tight-upper-bound/solution.py \
        --seed "$SEED"
done

echo "== 4/4 regenerate figures =="
uv run --with matplotlib --with numpy python3 \
    orbits/03-tight-upper-bound/make_figures.py

echo "== done =="
