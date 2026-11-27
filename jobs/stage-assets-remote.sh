#!/usr/bin/env bash
set -euo pipefail
: "${CQ_OUTPUT_DIR:?}" "${FINANCIAL_GRAPH_REVISION:?}"
ROOT="$(readlink -f "$CQ_OUTPUT_DIR")"
case "$ROOT" in /data/*|/data[0-9]/*|/date/*|/date[0-9]/*) ;; *) exit 70;; esac
printf '0/3 clean source\n' > "$ROOT/progress.txt"
mkdir -p "$ROOT/clean-code"
git -C "$ROOT/clean-code" init -q
git -C "$ROOT/clean-code" remote add origin https://github.com/SansaZheng/Financial-graph.git
git -C "$ROOT/clean-code" fetch --depth=1 --filter=blob:none origin "$FINANCIAL_GRAPH_REVISION" > "$ROOT/git-fetch.txt" 2>&1
git -C "$ROOT/clean-code" checkout -q --detach FETCH_HEAD
cd "$ROOT/clean-code"
PY=/home/sudingli/cq-home/financial-graph/env/bin/python
LEGACY_COMMIT="$("$PY" -c 'import json; print(json.load(open("assets/provenance/derived.json"))["source_evidence_commit"])')"
git fetch --depth=1 --filter=blob:none origin "$LEGACY_COMMIT" >> "$ROOT/git-fetch.txt" 2>&1
"$PY" scripts/stage_upload.py --asset derived-inputs --source-root "$ROOT/source" --legacy-commit "$LEGACY_COMMIT"
printf '1/3 derived inputs\n' >> "$ROOT/progress.txt"
"$PY" scripts/stage_upload.py --asset completed-experiments --source-root "$ROOT/source" --legacy-commit "$LEGACY_COMMIT"
printf '2/3 selected results\n' >> "$ROOT/progress.txt"
cp assets/manifest.json "$ROOT/manifest.json"
"$PY" - <<'PY'
import json,os,sys
from pathlib import Path
sys.path.insert(0,'scripts')
from assets import load_manifest,under,verify_file
root=Path(os.environ['CQ_OUTPUT_DIR']);m=load_manifest();records=[]
for a in m['assets']:
    if a.get('read_only'):continue
    for f in a['files']:
        verify_file(under(root/'source',f['source_path']),f)
        records.append({'asset':a['id'],'path':f['source_path'],'sha256':f['sha256'],'bytes':f['bytes']})
(root/'staging-receipt.json').write_text(json.dumps({'status':'verified-remote-staging-only','hf_upload_complete':False,'code_revision':os.environ['FINANCIAL_GRAPH_REVISION'],'source_root':str(root/'source'),'files':len(records),'bytes':sum(x['bytes'] for x in records),'checks':records},indent=2)+'\n')
PY
printf '3/3 all source hashes verified\n' >> "$ROOT/progress.txt"
