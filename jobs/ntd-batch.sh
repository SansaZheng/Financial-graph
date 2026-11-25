#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
RUN_ROOT="$CQ_OUTPUT_DIR"
bash jobs/research-cpu.sh qualification
printf '0/3 full seeds\n' > "$RUN_ROOT/progress.txt"
i=0
for seed in 471 472 473; do
 SEED_OUT="$RUN_ROOT/seed$seed"
 mkdir -p "$SEED_OUT"
 cp "$RUN_ROOT/tests.txt" "$RUN_ROOT/freeze.txt" "$RUN_ROOT/code-commit.txt" "$RUN_ROOT/source-hashes.json" "$SEED_OUT/"
 python -m src.ntd_evaluate --data evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv --out "$SEED_OUT" --seed "$seed"
 i=$((i+1))
 printf '%s/3 seed %s complete\n' "$i" "$seed" >> "$RUN_ROOT/progress.txt"
done
