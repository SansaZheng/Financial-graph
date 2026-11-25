#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$CQ_OUTPUT_DIR"
mkdir -p "$CQ_OUTPUT_DIR"
printf '0/3 install\n' > "$CQ_OUTPUT_DIR/progress.txt"
python -m pip install --no-cache-dir --only-binary=:all: -r requirements-kaggle.txt > "$CQ_OUTPUT_DIR/install.txt" 2>&1
# Record provider torch version; do not install a large CUDA wheel for CPU work.
python -c 'import torch; print(torch.__version__)' > "$CQ_OUTPUT_DIR/torch-version.txt"
python -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '%s\n' "${FINANCIAL_GRAPH_REVISION:?}" > "$CQ_OUTPUT_DIR/code-commit.txt"
python -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
if [ "${1:-}" = "qualification" ]; then
 python -c 'import src.modern_baseline' >> "$CQ_OUTPUT_DIR/tests.txt"
 printf '3/3 qualification complete\n' >> "$CQ_OUTPUT_DIR/progress.txt"
else
 python -m src.modern_baseline --data evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv --out "$CQ_OUTPUT_DIR" "$@"
fi
