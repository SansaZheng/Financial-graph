#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN=/home/sudingli/cq-home/financial-graph-ntd/env/bin/python
"$PYTHON_BIN" -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '%s\n' "${FINANCIAL_GRAPH_REVISION:?}" > "$CQ_OUTPUT_DIR/code-commit.txt"
"$PYTHON_BIN" -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
"$PYTHON_BIN" -m src.ntd_evaluate --data evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv --out "$CQ_OUTPUT_DIR" "$@"
