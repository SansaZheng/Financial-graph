#!/usr/bin/env bash
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
: "${CQ_OUTPUT_DIR:?CQ output required}"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
INPUT="$REPO_ROOT/evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv"
PYTHON_BIN="${FINANCIAL_GRAPH_PYTHON:-/home/sudingli/cq-home/financial-graph/env/bin/python}"
"$PYTHON_BIN" -m src.evaluate --data "$INPUT" --out "$CQ_OUTPUT_DIR" "$@"
