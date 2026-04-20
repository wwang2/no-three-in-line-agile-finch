#!/usr/bin/env bash
# Reproduce orbit 02 from scratch.  Produces the same POINTS every time.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

cd "$HERE"
echo "[1/3] running deterministic constructor ..."
python3 constructor.py

echo "[2/3] evaluating on 3 seeds ..."
for SEED in 1 2 3; do
  python3 "$REPO/research/eval/evaluator.py" --solution "$HERE/solution.py" --seed "$SEED"
done

echo "[3/3] regenerating figures ..."
python3 figures/make_figures.py

echo "done."
