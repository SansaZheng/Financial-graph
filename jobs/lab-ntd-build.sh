#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}"
ROOT=/home/sudingli/cq-home/financial-graph-ntd
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
ACTUAL=$(readlink -f "$ROOT")
case "$ACTUAL" in /data*/*|/date*/*) ;; *) echo "Refusing non-data-disk home: $ACTUAL"; exit 1;; esac
mkdir -p "$ROOT/cache" "$CQ_OUTPUT_DIR"
export CONDA_PKGS_DIRS="$ROOT/cache/conda" PIP_CACHE_DIR="$ROOT/cache/pip" TMPDIR="$CQ_OUTPUT_DIR"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
printf '0/3 isolated environment\n' > "$CQ_OUTPUT_DIR/progress.txt"
CONDA_CMD=''
if command -v conda >/dev/null; then CONDA_CMD=$(command -v conda); fi
for candidate in /home/sudingli/miniconda3/bin/conda /home/sudingli/anaconda3/bin/conda /opt/conda/bin/conda; do
 if [ -z "$CONDA_CMD" ] && [ -x "$candidate" ]; then CONDA_CMD="$candidate"; fi
done
if [ -z "$CONDA_CMD" ]; then echo 'No conda found'; exit 1; fi
if [ ! -x "$ROOT/env/bin/python" ]; then "$CONDA_CMD" create -y --override-channels -c conda-forge -p "$ROOT/env" python=3.11 pip; fi
printf '1/3 pinned packages\n' >> "$CQ_OUTPUT_DIR/progress.txt"
"$ROOT/env/bin/python" -m pip install --only-binary=:all: -r requirements-kaggle.txt
printf '2/3 tests\n' >> "$CQ_OUTPUT_DIR/progress.txt"
"$ROOT/env/bin/python" -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
"$ROOT/env/bin/python" -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '%s\n' "$ACTUAL" > "$CQ_OUTPUT_DIR/storage-root.txt"
printf '3/3 complete\n' >> "$CQ_OUTPUT_DIR/progress.txt"
