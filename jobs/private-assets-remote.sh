#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${CQ_OUTPUT_DIR:?}" "${FG_RUNTIME_PYTHON:?}" "${HF_HOME:?}" "${FG_PRIVATE_REPO:?}"
: "${FG_PRIVATE_WORKSPACE:?}"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
work_root="$(realpath -e "$FG_PRIVATE_WORKSPACE")"
case "$work_root" in /data/*|/data[0-9]/*|/date/*|/date[0-9]/*) ;; *) echo 'Require authorized data disk'; exit 70;; esac
run_root="$(mktemp -d "$work_root/run.XXXXXXXX")"
export FG_CACHE_ROOT="$run_root/cache" FG_DATA_ROOT="$run_root/assets"
PY="$FG_RUNTIME_PYTHON"
case "${1:-}" in
  upload)
    : "${FG_UPLOAD_SOURCE:?}" "${FG_QUOTA_RECEIPT:?}"
    manifest="$CQ_OUTPUT_DIR/manifest.json"
    cp assets/manifest.json "$manifest"
    for asset in derived-inputs completed-experiments; do
      printf 'Uploading and verifying %s\n' "$asset" >> "$CQ_OUTPUT_DIR/progress.txt"
      "$PY" scripts/assets.py --manifest "$manifest" upload --asset "$asset" \
        --source-root "$FG_UPLOAD_SOURCE" --repo-id "$FG_PRIVATE_REPO" \
        --quota-receipt "$FG_QUOTA_RECEIPT" > "$CQ_OUTPUT_DIR/$asset-readback.json"
    done
    ;;
  replay)
    : "${FINANCIAL_GRAPH_REVISION:?}"
    git init -q "$run_root/code"
    git -C "$run_root/code" remote add origin https://github.com/SansaZheng/Financial-graph.git
    git -C "$run_root/code" fetch --depth=1 --filter=blob:none origin "$FINANCIAL_GRAPH_REVISION"
    git -C "$run_root/code" checkout -q --detach FETCH_HEAD
    cd "$run_root/code"
    test "$(git rev-parse HEAD)" = "$FINANCIAL_GRAPH_REVISION"
    "$PY" - <<'PINS'
from pathlib import Path
from importlib.metadata import version
for filename in ('requirements.txt', 'requirements-assets.txt'):
    for line in Path(filename).read_text().splitlines():
        if line.strip() and not line.startswith('#') and '==' in line:
            name, expected = line.strip().split('==', 1)
            assert version(name) == expected, name + ' version mismatch'
PINS
    "$PY" scripts/check_storage_policy.py > "$CQ_OUTPUT_DIR/git-policy.txt"
    "$PY" scripts/assets.py fetch --asset derived-inputs > "$CQ_OUTPUT_DIR/derived-fetch.json"
    "$PY" scripts/assets.py verify --asset derived-inputs > "$CQ_OUTPUT_DIR/derived-verify.json"
    "$PY" scripts/assets.py fetch --asset completed-experiments \
      --file "$( "$PY" -c 'import json; m=json.load(open("assets/manifest.json")); print(next(f["path"] for a in m["assets"] if a["id"]=="completed-experiments" for f in a["files"] if f["path"].endswith("/metrics.json")))' )" \
      > "$CQ_OUTPUT_DIR/evidence-sample-fetch.json"
    "$PY" scripts/run_experiment.py --method ntd --seed 471 --smoke --output "$run_root/smoke"
    cp "$run_root/smoke/run-provenance.json" "$CQ_OUTPUT_DIR/"
    cp "$run_root/smoke/metrics.json" "$CQ_OUTPUT_DIR/smoke-metrics.json"
    ;;
  *) echo 'Select upload or replay'; exit 2 ;;
esac
