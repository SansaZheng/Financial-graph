#!/usr/bin/env bash
set -euo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
: "${CQ_OUTPUT_DIR:?CQ output required}"
INPUT=/home/sudingli/cq-home/financial-graph/results/input-audit-20261123/root0/results/forecast_data.csv
python -m src.evaluate --data "$INPUT" --out "$CQ_OUTPUT_DIR" "$@"
