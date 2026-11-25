#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$CQ_OUTPUT_DIR"
export TMPDIR="$CQ_OUTPUT_DIR" PIP_CACHE_DIR="$CQ_OUTPUT_DIR/pip-cache"
python -m pip install --only-binary=:all: -r requirements-kaggle.txt > "$CQ_OUTPUT_DIR/install.txt" 2>&1
python -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
git rev-parse HEAD > "$CQ_OUTPUT_DIR/code-commit.txt"
python -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
if [ "${1:-}" = "qualification" ]; then
  printf '1/1 qualification complete\n' > "$CQ_OUTPUT_DIR/progress.txt"
else
  module="$1"; shift
  python -m "$module" --data evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv --out "$CQ_OUTPUT_DIR" "$@"
fi
