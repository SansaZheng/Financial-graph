#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}" "${FINANCIAL_GRAPH_REVISION:?}"
RUN_ROOT="$(readlink -f "$CQ_OUTPUT_DIR")"
case "$RUN_ROOT" in /data/*|/data[0-9]/*|/date/*|/date[0-9]/*) ;; *) echo 'Require authorized /data or /date workspace'; exit 70;; esac
export FG_DATA_ROOT="$RUN_ROOT/assets" FG_CACHE_ROOT="$RUN_ROOT/cache"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
printf '0/4 clean checkout\n' > "$RUN_ROOT/progress.txt"
mkdir -p "$RUN_ROOT/clean-code"
git -C "$RUN_ROOT/clean-code" init -q
git -C "$RUN_ROOT/clean-code" remote add origin https://github.com/SansaZheng/Financial-graph.git
git -C "$RUN_ROOT/clean-code" fetch --depth=1 --filter=blob:none origin "$FINANCIAL_GRAPH_REVISION" > "$RUN_ROOT/git-fetch.txt" 2>&1
git -C "$RUN_ROOT/clean-code" checkout -q --detach FETCH_HEAD
cd "$RUN_ROOT/clean-code"
/home/sudingli/cq-home/financial-graph/env/bin/python -m venv "$RUN_ROOT/venv"
PY="$RUN_ROOT/venv/bin/python"
"$PY" -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt -r requirements-assets.txt -r requirements-streaming.txt > "$RUN_ROOT/install.txt" 2>&1
"$PY" -m pip freeze > "$RUN_ROOT/environment.txt"
printf '1/4 dependencies\n' >> "$RUN_ROOT/progress.txt"
"$PY" scripts/check_storage_policy.py > "$RUN_ROOT/git-policy.txt"
"$PY" scripts/assets.py validate > "$RUN_ROOT/manifest-validation.json"
"$PY" scripts/assets.py fetch --asset upstream-card > "$RUN_ROOT/hf-download.json"
"$PY" scripts/assets.py verify --asset upstream-card > "$RUN_ROOT/hf-integrity.json"
"$PY" scripts/assets.py stream --asset raw-minute-bars --file stocks_bars_1m.parquet --columns timestamp ticker close --rows 5 > "$RUN_ROOT/stream-sample.json"
printf '2/4 pinned HF asset\n' >> "$RUN_ROOT/progress.txt"
"$PY" -m pytest -p no:cacheprovider tests -q > "$RUN_ROOT/tests.txt"
"$PY" scripts/assets.py account > "$RUN_ROOT/hf-account.json"
"$PY" - <<'PY'
import json,os,subprocess
from pathlib import Path
root=Path(os.environ['CQ_OUTPUT_DIR']);m=json.loads(Path('assets/manifest.json').read_text())
sample=json.loads((root/'stream-sample.json').read_text())
ready=next(a for a in m['assets'] if a['id']=='derived-inputs')['status']=='published'
report={'status':'passed-public-workflow','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'clean_checkout':True,'tracked_payload_policy':'passed','pinned_hf_card':json.loads((root/'hf-integrity.json').read_text()),'test_log':'tests.txt','derived_hf_upload_ready':ready,'scientific_data_reproduction':'not run: derived asset unpublished' if not ready else 'available for next dependent smoke','runtime_root':str(root),'cache_root':os.environ['FG_CACHE_ROOT'],'raw_stream':{'rows':len(sample['rows']),'columns':['timestamp','ticker','close'],'integrity':sample['integrity'],'full_raw_download':False},'private_upload_verification':'not performed without authentication and confirmed quota'}
(root/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
PY
printf '4/4 public path and tests complete\n' >> "$RUN_ROOT/progress.txt"
