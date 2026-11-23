#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$CQ_OUTPUT_DIR"
printf '0/2 install\n' > "$CQ_OUTPUT_DIR/progress.txt"
python -m pip install --only-binary=:all: -r requirements-kaggle.txt
printf '1/2 invariant tests\n' >> "$CQ_OUTPUT_DIR/progress.txt"
python -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
python -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '2/2 complete\n' >> "$CQ_OUTPUT_DIR/progress.txt"
