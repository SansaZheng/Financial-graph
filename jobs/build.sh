#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?CQ output required}"
PROJECT_ROOT=/home/sudingli/cq-home/financial-graph
mkdir -p "$PROJECT_ROOT/cache" "$CQ_OUTPUT_DIR"
export CONDA_PKGS_DIRS="$PROJECT_ROOT/cache/conda" PIP_CACHE_DIR="$PROJECT_ROOT/cache/pip" TMPDIR="$CQ_OUTPUT_DIR"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
printf '0/3 environment build\n' > "$CQ_OUTPUT_DIR/progress.txt"
CONDA_CMD=''
if command -v conda >/dev/null; then CONDA_CMD=$(command -v conda); fi
for candidate in /home/sudingli/miniconda3/bin/conda /home/sudingli/anaconda3/bin/conda /opt/conda/bin/conda; do
  if [ -z "$CONDA_CMD" ] && [ -x "$candidate" ]; then CONDA_CMD="$candidate"; fi
done
if [ -z "$CONDA_CMD" ]; then echo 'No conda found'; exit 1; fi
if [ ! -x "$PROJECT_ROOT/env/bin/python" ]; then "$CONDA_CMD" create -y --override-channels -c conda-forge -p "$PROJECT_ROOT/env" python=3.11 pip; fi
printf '1/3 dependencies\n' >> "$CQ_OUTPUT_DIR/progress.txt"
"$PROJECT_ROOT/env/bin/python" -m pip install -r requirements.txt
printf '2/3 tests\n' >> "$CQ_OUTPUT_DIR/progress.txt"
"$PROJECT_ROOT/env/bin/python" -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
"$PROJECT_ROOT/env/bin/python" -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '3/3 complete\n' >> "$CQ_OUTPUT_DIR/progress.txt"
