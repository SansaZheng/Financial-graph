#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}" "${FINANCIAL_GRAPH_REVISION:?}"
cd "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN=/home/sudingli/cq-home/financial-graph/env/bin/python
case "$(readlink -f /home/sudingli/cq-home/financial-graph)" in /data/*|/data[0-9]/*|/date/*|/date[0-9]/*) ;; *) exit 70;; esac
printf '0/4 qualification\n' > "$CQ_OUTPUT_DIR/progress.txt"
"$PYTHON_BIN" -m pip freeze > "$CQ_OUTPUT_DIR/freeze.txt"
printf '%s\n' "$FINANCIAL_GRAPH_REVISION" > "$CQ_OUTPUT_DIR/code-commit.txt"
"$PYTHON_BIN" - <<'HASHES'
import pathlib,hashlib,json,os
files=sorted(pathlib.Path('src').glob('*.py'))+sorted(pathlib.Path('jobs').glob('*.sh'))
pathlib.Path(os.environ['CQ_OUTPUT_DIR'],'source-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
HASHES
"$PYTHON_BIN" -m pytest -p no:cacheprovider tests > "$CQ_OUTPUT_DIR/tests.txt"
printf '1/4 qualification complete\n' >> "$CQ_OUTPUT_DIR/progress.txt"
i=1
for seed in 471 472 473; do
 SEED_OUT="$CQ_OUTPUT_DIR/seed$seed"
 mkdir -p "$SEED_OUT"
 cp "$CQ_OUTPUT_DIR/tests.txt" "$CQ_OUTPUT_DIR/freeze.txt" "$CQ_OUTPUT_DIR/code-commit.txt" "$CQ_OUTPUT_DIR/source-hashes.json" "$SEED_OUT/"
 "$PYTHON_BIN" -m src.ntd_evaluate --data evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv --out "$SEED_OUT" --seed "$seed"
 i=$((i+1))
 printf '%s/4 seed %s complete\n' "$i" "$seed" >> "$CQ_OUTPUT_DIR/progress.txt"
done
