# Current research stage

004-intraday-audit | Codex + CQ | prepared 2026-11-28T04:20:40+08:00

Verify the pinned minute-bar file and audit a 2024-only, causally aligned hourly sample. Use metadata for later-date inventory. Venue unspecified, CCF A quality goal. Topic: incremental topology information for market volatility forecasting. See [active task](prompts/004-intraday-audit.md).

## Completed work

003-ntd | Codex + CQ | 2026-11-25T22:06:10.360595+08:00

Completed and independently verified: legacy CGI, three modern RG-ResMoE/MLP seeds, and NTD three-seed batch j-1125-0c3a7c. Each full run has3644 matched forecasts for2022–2024. All NTD input/code hashes and causal-time output checks passed.
Result: NTD loses to validation-selected strong control by0.404–0.507% MSE; gates fall back in all years. No superiority or CCF A readiness established. See experiment-report.md.
All current scientific jobs are terminal. Shared-slot Kaggle batch was cancelled before launch; qualified portable c225 environment completed actual predictions. Core version differences from modern Kaggle runs are documented.
Full CQ fetch succeeded:38 files, approximately7.5MB compressed. A redundant read-only c220 archive-transfer attempt j-1125-6c7e6f failed exit1; no retry needed, no effect on scientific output. Failure status retained.
Transition rationale: next-study-decision.md.
Missing iCloud investigation discontinued. No paid compute, remote originals preserved, no other projects modified.

## Storage migration

Private HF upload and clean 2022 NTD replay passed. See [asset manifest](../../assets/manifest.json) and [migration report](../../reports/storage/migration.md). The replay matched all 13 MSE values for the historical 2022 slice and is excluded from new method comparisons.
