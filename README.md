# FinancialGraph: code on GitHub, assets on HF, execution through CQ

GitHub contains code, configuration, dependencies, documentation, compact evaluation summaries and [asset version manifests](assets/manifest.json). Datasets, predictions, model inputs, weights, environments and caches are excluded from the current Git index. Existing history and the old verified raw-data Release are preserved; this is not a history rewrite.

**Migration status:** the original raw dataset and its card are pinned on HF. Project-derived inputs and selected experiment outputs have complete local hashes but are pending authenticated private upload and quota verification. `revision: null` is deliberate; the downloader refuses unpublished assets. No saved model checkpoint has been identified. Do not create an empty Model repository or claim that weights were preserved. See [migration report](reports/storage/migration.md) and [manifest](assets/manifest.json).

## Repositories and data layout

- Code: https://github.com/SansaZheng/Financial-graph
- CQ code mirror: https://github.com/SuuTTT/financial-graph-cq
- Reused raw source: https://huggingface.co/datasets/CryptoSpartan/stocks_bars_1m
- Raw revision: `0c6f25f287918b1421c2572d2c9e2b75bd8959a9`
- Private project Dataset destination: choose an existing appropriate repository after account inspection; proposed name `<your-namespace>/financial-graph-assets`, **not yet created**.
- Model destination: create a private Model repository only when actual selected checkpoints exist.

The Dataset layout is `derived/`, `splits/`, `provenance/`, and `experiments/<job>/<seed>/`. Small original CSV files are practical logical shards; their bytes and existing audit hashes are preserved. The11GB upstream Parquet is reused rather than downloaded to the Mac or uploaded twice. For a new large derived dataset, make bounded Parquet shards (e.g.128–512MiB) on remote storage and add each explicit shard to the manifest. Do not silently repartition or change existing split membership.

## Install and authenticate

Execution/download/upload commands below belong inside a CQ job on an authorized `/data*` or `/date*` workspace. A local Mac may edit code and inspect manifests; actual asset downloads and uploads are disabled on macOS by default. `--allow-local` is an explicit override for a requested small download, never a default.

```bash
# Inside a CQ job. CQ_OUTPUT_DIR must resolve to the authorized data disk.
export FG_WORK_ROOT="$CQ_OUTPUT_DIR"
export FG_DATA_ROOT="$FG_WORK_ROOT/assets"
export FG_CACHE_ROOT="$FG_WORK_ROOT/cache"
export FG_RUN_ROOT="$FG_WORK_ROOT/runs"
python3 -m venv "$FG_WORK_ROOT/venv"
. "$FG_WORK_ROOT/venv/bin/activate"
python -m pip install --no-cache-dir -r requirements.txt -r requirements-assets.txt
# Optional bounded Parquet streaming:
python -m pip install --no-cache-dir -r requirements-streaming.txt
# Modern neural baseline additionally needs the historically recorded Torch version;
# inspect reports/evaluations/*/freeze.txt before selecting a compatible environment.
```

Use the official interactive login **in your own remote terminal**, not in a CQ JSON spec, chat message or Git file:

```bash
# Use the CQ runtime account and a project-specific credential directory,
# outside the Git checkout, caches, and CQ_OUTPUT_DIR/result archives.
export HF_HOME=/data3/sudingli/cq-home/financial-graph/.hf-auth
umask 077
mkdir -p "$HF_HOME"
chmod 700 "$HF_HOME"
# On the lab hosts, use their administrator-installed trusted roots:
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
hf auth login
hf auth whoami
python scripts/assets.py account
```

`HF_TOKEN` can alternatively be supplied by an authorized runtime secret manager, never as a literal in scripts/specs. Prefer a fine-grained token restricted to this project. Subsequent CQ jobs must receive the same `HF_HOME` (or protected `HF_TOKEN_PATH`) path as configuration; do not alter another project's default login. Use the already-created project runtime's `venv/bin/hf` executable if `hf` is not on PATH. `HF_HOME`/`HF_TOKEN_PATH` may point to a protected existing login; do not copy tokens into this repository. `FG_CACHE_ROOT` configures Hub/Xet caches without changing the authentication location. Linux requests use the administrator-installed system CA bundle by default; `FG_CA_BUNDLE` selects an explicitly trusted alternative. TLS verification is never disabled. The account command lists accessible own/org dataset/model repositories so they can be reused. Fine-grained token permissions are ultimately verified by the actual API operations.

The pinned `huggingface_hub==0.36.0` client exposes no account-wide storage-quota method. Inspect HF billing/storage settings and record available **included, unbilled** headroom in a private runtime receipt (do not commit it):

```json
{
  "namespace": "your-namespace",
  "checked_at": "REPLACE_WITH_CURRENT_ISO8601_TIME_AND_TIMEZONE",
  "source": "hf-billing-settings",
  "remaining_included_bytes": 0,
  "no_paid_overage": true
}
```

Replace zero with the observed remaining included bytes; zero deliberately blocks upload. The receipt expires after24hours and must cover at least twice the selected asset bytes conservatively. Unknown quota blocks upload; the workflow never upgrades a plan, enables paid storage, publishes private assets, or changes a license. Current [HF storage policies](https://huggingface.co/docs/hub/storage-limits) do not prove any particular account's free headroom.

## Retrieve only required, immutable assets

```bash
python scripts/assets.py validate
# Small public metadata qualification; 1,272 bytes, not the full dataset:
python scripts/assets.py fetch --asset upstream-card
python scripts/assets.py verify --asset upstream-card

# After private upload has populated a full HF SHA in assets/manifest.json:
python scripts/assets.py fetch --asset derived-inputs
python scripts/assets.py verify --asset derived-inputs

# One selected file only (exact manifest path, no whole-repo snapshot):
python scripts/assets.py fetch --asset completed-experiments \
  --file experiments/j-1125-0c3a7c/seed471/predictions.csv

# Optional remote range read; downloads selected columns of one bounded row group:
python scripts/assets.py stream --asset raw-minute-bars \
  --file stocks_bars_1m.parquet --columns timestamp ticker close --rows 5
```

Each asset materializes under `$FG_DATA_ROOT/<asset-id>/<local_path>`. `--data-root` and the global `--cache-root` arguments override the corresponding environment variables. Downloads require a full40-character revision and SHA256; they validate existing files rather than overwriting mismatched originals. For the observed server HEAD/cache zero-byte failure, the downloader falls back to the official `HfFileSystem` pinned range API. Its project-owned content-addressed partial file supports seeking/resumption under a lock and is promoted only after full size/SHA256 checks. The damaged original cache and any existing user file are left intact; nonempty checksum mismatches still fail. Streaming is revision-pinned but **does not** verify a whole-file checksum; a full remote download plus `verify` is needed for that. Do not invoke `fetch --asset raw-minute-bars` unless the full11GB file is actually required on remote storage.

## Execute reproducibly

```bash
python scripts/run_experiment.py --method ntd --seed 471 --smoke \
  --output "$FG_RUN_ROOT/ntd-smoke-471"
# Full run, fresh output directory:
python scripts/run_experiment.py --method ntd --seed 471 \
  --output "$FG_RUN_ROOT/ntd-full-471"
```

The wrapper rejects Mac execution, unpublished input assets, dirty tracked code, corrupted inputs and output inside the checkout. It records code commit, HF revision, split configuration, seed, dependency freeze and metrics digest. Modern runs use `--method modern` once Torch is installed in the selected remote environment. The existing evaluators do not save trained weights; do not invent checkpoints from prediction files.

For a clean remote infrastructure qualification, submit the pinned CQ spec under `jobs/storage-20261127/` (inspect existing IDs first to avoid duplicates). `jobs/remote-assets-check.sh` makes a shallow clean GitHub checkout, installs an isolated environment, validates storage policy, fetches the pinned HF card, performs a bounded raw Parquet read, and runs the science/asset tests. Private-data scientific reproduction remains blocked until authenticated uploads and pinned revisions exist. Fetch only `validation-report.json`, `tests.txt` and other small receipts from CQ; never fetch the entire runtime directory containing its environment and caches.

## Upload new versions and update the manifest

Edit the manifest with **explicit** authorized files, paths, byte sizes and SHA256 values. A pending asset has `repo_id: null`, `revision: null` until upload. Reuse one private Dataset repository for project-derived inputs and result tables. Review existing names using `account`; if another financial repository exists, record the reviewed names in `reuse_reviewed_repos` rather than creating suffixed duplicates.

Historical sources can be staged selectively on a remote host without using the Mac:

```bash
# Transitional read-only source; Git history is not rewritten.
LEGACY_COMMIT=$(python -c 'import json; print(json.load(open("assets/provenance/derived.json"))["source_evidence_commit"])')
git fetch --depth=1 --filter=blob:none origin "$LEGACY_COMMIT"
python scripts/stage_upload.py --asset derived-inputs \
  --source-root "$FG_WORK_ROOT/upload-source" --legacy-commit "$LEGACY_COMMIT"
python scripts/stage_upload.py --asset completed-experiments \
  --source-root "$FG_WORK_ROOT/upload-source" --legacy-commit "$LEGACY_COMMIT"

cp assets/manifest.json "$FG_WORK_ROOT/manifest.json"
python scripts/assets.py --manifest "$FG_WORK_ROOT/manifest.json" upload --asset derived-inputs \
  --source-root "$FG_WORK_ROOT/upload-source" \
  --repo-id your-namespace/financial-graph-assets \
  --quota-receipt "$FG_WORK_ROOT/quota.json"
python scripts/assets.py --manifest "$FG_WORK_ROOT/manifest.json" upload --asset completed-experiments \
  --source-root "$FG_WORK_ROOT/upload-source" \
  --repo-id your-namespace/financial-graph-assets \
  --quota-receipt "$FG_WORK_ROOT/quota.json"
python scripts/assets.py --manifest "$FG_WORK_ROOT/manifest.json" validate
```

Then retrieve only the small manifest on the Mac (replace `UPLOAD_JOB_ID` with the actual successful upload job; no token file or data transfer):

```bash
cq fetch UPLOAD_JOB_ID --path manifest.json --to /tmp/financial-graph-pins
# In the GitHub code checkout, preserve unrelated changes and review this small-file replacement:
cp /tmp/financial-graph-pins/UPLOAD_JOB_ID/manifest.json assets/manifest.json
git diff -- assets/manifest.json
git add assets/manifest.json
git commit -m 'Pin verified HF asset revisions'
git push
```

`jobs/stage-assets-remote.sh` prepares these exact allowlisted sources and a SHA256 receipt in a separate CQ data-disk directory. It does not upload or duplicate entire working directories. Use the full legacy SHA from `assets/provenance/derived.json`, never an unresolved short SHA in a shallow checkout. Upload uses official `HfApi.create_commit`, at most50files per commit, remote content deduplication and parent-commit checks. Rerun the same command after interruption: already committed matching files are skipped. For genuinely large uploads, add `--large`; official `upload_large_folder` keeps resumable hash/preupload/commit task metadata under the staging folder's `.cache/huggingface`. Keep that metadata until transfer completes. It is not a promise that every interrupted HTTP request resumes byte-for-byte. Do not change staged source bytes mid-transfer.

Every upload reads back the pinned revision and verifies all listed files before writing the new manifest.

To rebuild the detailed report on the remote server, fetch both `derived-inputs` and `completed-experiments`, then run `python -m jobs.summarize_research --out "$FG_RUN_ROOT/summary"`. In a shallow clone, first fetch the exact training-code commits listed in the manifest/run records using `git fetch --depth=1 --filter=blob:none origin FULL_CODE_SHA`; the verifier reads only the named source files from those commits. It refuses missing evidence instead of overwriting the report with an empty result. Copy only the final Markdown and lightweight summary tables back to GitHub; aligned per-row predictions stay in remote/HF storage.
 The destination must be private; the tool refuses to overwrite a different existing root dataset card. It never deletes remote files. For models, set `repo_type: model`, an actual model `repo_id`, full `code_revision`, `dataset_revisions`, `random_seeds`, `configuration` and `evaluation` paths; every checkpoint must declare `roles: [best]`, `[final]`, `[recovery]`, or a combination. Retain best/final and needed recovery state, not every epoch. Reuse the same upload command with the model asset ID. Prefer safe weight formats; this tool never deserializes uploaded weights.

## Local retention, Git history and cache cleanup

`git rm --cached` removed assets from tracking **without deleting local originals**. The old Git history still contains data; new users should use a shallow clone. `reports/storage/untracked-assets.json` records the retained local paths. No shared history rewrite, force push, shared-cache deletion, Release deletion or original-file deletion was performed. See [migration/cleanup gates](reports/storage/migration.md).

After a pinned remote download and checksum verification, an independent backup, and explicit approval for the particular original files, local originals can be considered for removal. **No originals are eligible under the current incomplete HF migration.** A dry run of dependency/cache tools is not proof of backup.

For an explicitly approved disposable **project-owned remote cache**, inspect then interactively choose HF revisions; do not point this at a shared cache:

```bash
hf cache scan --dir "$FG_CACHE_ROOT/hub"
hf cache delete --dir "$FG_CACHE_ROOT/hub" --disable-tui
```

These commands are provided for future approved cleanup; they were not run. Active runs may need cached files. Keep selected materialized assets, completed results, credentials and interrupted-upload metadata separate. There is intentionally no blanket `rm -rf` cleanup command.

## Research result and Chinese conclusion

[Verified research report](paper/workflow/experiment-report.md), [compact evaluation records](reports/evaluations), [frozen NTD protocol](paper/workflow/protocol-ntd-002.md), and [next research decision](paper/workflow/next-study-decision.md).

NTD MSE0.2377171/0.2378833/0.2376406 versus strongest validation-selected control0.2366833: all three seeds are worse by0.404–0.507%. Historical data is development-only, not independent confirmation; no SOTA or CCF A claim is made.

**中文结论：** 本次重组将代码与数据职责分离，默认在远端按固定版本取用资产，保留本地原件和已有备份。HF私有上传尚须有效账号权限及免费存储余额确认，未完成的上传不会伪造版本号或宣称迁移成功。科研结论不因存储重组而改变：当前NTD未超过最强对照。
