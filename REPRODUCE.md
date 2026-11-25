# Reproduce the research

Primary archive: https://github.com/SansaZheng/Financial-graph
CQ compute mirror: https://github.com/SuuTTT/financial-graph-cq

## Inputs

Small, hash-recorded derived inputs are tracked under evidence/cq/j-1123-b41d82/root0. Their provenance is in audit.json. The11GB raw parquet is a multipart Release, not a local Mac prerequisite: https://github.com/SansaZheng/Financial-graph/releases/tag/raw-stocks-bars-1m-59bc5acc. Consult maintenance/raw-release-verification.json before reconstruction. Missing iCloud placeholders are not required for these experiments and are no longer being pursued.

## Exact execution

1. Read paper/workflow/protocol-ntd-002.md and protocol-modern-001.md. Do not treat old development years as untouched tests.
2. Inspect `cq jobs --work FinancialGraph` and the job IDs in jobs/20261125-batch and jobs/20261125-modern before submitting anything. Avoid duplicate experiments.
3. Each spec records a full pushed Git SHA, resources, command, dependency and unique output directory. The final NTD batch is j-1125-a08289, pinned to32a4480cd7a739a345abddf0691a5900ceddb9e8; its scientific implementation is unchanged from9f343af. Superseded unstarted per-seed jobs are cancelled. Use `cq show ID` and `cq logs ID`; each full run requires successful environment and smoke gates.
4. `cq fetch ID --to evidence/cq` retrieves successful outputs. Failure records are retained separately when no output directory exists.
5. `python -m jobs.summarize_research` recomputes MSE/R² from predictions, verifies source hashes against pinned Git commits, writes per-run manifests and the bilingual report. It does not train models. The report ends with a Chinese conclusion.
6. Commit and push evidence, job specifications and report to both remotes. For each completed run preserve metrics, predictions, validation selection, input/source hashes, package freeze and logs. Large future outputs belong in verified GitHub Releases.

Training commands are implemented in jobs/research-cpu.sh and jobs/modern-cpu.sh. jobs/ntd-batch.sh runs qualification followed by seeds471/472/473 sequentially; fetched artifacts are nested under seed471, seed472 and seed473. All scientific outputs go to CQ_OUTPUT_DIR. The provider supplies Torch for the modern CPU model; its exact version is captured in freeze.txt/torch-version.txt. School execution uses the isolated project environment and big-disk workspace; do not modify shared environments or unrelated jobs. No paid rental is enabled.

## Interpret the result

“Strongest control” means the best candidate chosen using the specified validation set, including an equally sized temporal residual branch. The report additionally exposes every control and seed; it is not a claim that every possible state-of-the-art model was tested. Three random seeds are not three independent datasets. RG-ResMoE is an explicitly documented architecture adaptation; it must not be called exact reproduction of its original five-day cross-sectional task.
