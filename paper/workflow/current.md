# Current research stage

006-intraday-residual | Codex + CQ | prepared 2026-11-28T05:09:10+08:00

Diagnose the previous graph MSE penalty, then test a residual correction on the frozen 005 predictions. See [active task](prompts/006-intraday-residual.md). Topic: incremental topology information for market volatility forecasting. Venue unspecified. Original source audit remains a separate CQ job.

## Previous stage

005-intraday-matched | Codex + CQ | requested 2026-11-28

Build the matched 11:31–14:31 New York panel and compare conditional-null graph diffusion with the strongest validation-selected control. See [active task](prompts/005-intraday-matched.md). Venue unspecified. Topic: incremental topology for market volatility forecasting.

CQ completed the matched study on c225. On 2,912 identical 2022–2024 decisions, the graph reached MSE 0.249851 and the validation-selected node-only control reached 0.247820. The graph increased MSE by 0.82%. Five-day paired gain was −0.002032 (95% interval [−0.003508, −0.000742]). The 10- and 20-day sensitivity intervals remained negative. The next scientific stage needs a qualified untouched period and a fresh mechanism before claiming topology helps. See the [report](../../reports/intraday-matched/report.md).

## Earlier data qualification

Full source audit `j-1128-99bea1` awaits a c220 CPU slot. It verifies the 10.93 GB archive by SHA-256 and checks all source symbols in five 2024 sessions. CQ is reserving the last eight c220 CPU slots for GPU jobs. See the [task](prompts/004-intraday-audit.md).

The bounded HF timing pilot `j-1128-cbd585` completed on c225. It returned 17,550 unique valid bars across nine requested equities. All 25 decisions had nine eligible nodes. SPY was absent in the pilot, leaving zero forward SPY realized-variance labels. Raw metadata spans through 2026-07-07 UTC. Later-date observations still need qualification. See the [pilot report](../../reports/intraday-audit/bounded-pilot.json).

The five-day slice of the archived NTD target has hourly New York cutoffs at 10:31, 11:31, 12:31, 13:31 and 14:31. None match the exact-hour timing pilot. Twenty rows have enough regular-session history for the new lagged return. Align the development pipeline to the archived cutoffs and verify the assembled panel before fitting any model. See the [alignment receipt](../../reports/intraday-audit/legacy-label-alignment.json).

## Completed work

003-ntd | Codex + CQ | 2026-11-25T22:06:10.360595+08:00

Completed and independently verified: legacy CGI, three modern RG-ResMoE/MLP seeds, and NTD three-seed batch j-1125-0c3a7c. Each full run has3644 matched forecasts for2022–2024. All NTD input/code hashes and causal-time output checks passed.
Result: NTD loses to validation-selected strong control by0.404–0.507% MSE; gates fall back in all years. No superiority or CCF A readiness established. See experiment-report.md.
All NTD-002 and modern comparison jobs are terminal. Shared-slot Kaggle batch was cancelled before launch; qualified portable c225 environment completed actual predictions. Core version differences from modern Kaggle runs are documented.
Full CQ fetch succeeded:38 files, approximately7.5MB compressed. A redundant read-only c220 archive-transfer attempt j-1125-6c7e6f failed exit1; no retry needed, no effect on scientific output. Failure status retained.
Transition rationale: next-study-decision.md.
Missing iCloud investigation discontinued. No paid compute, remote originals preserved, no other projects modified.

## Storage migration

Private HF upload and clean 2022 NTD replay passed. See [asset manifest](../../assets/manifest.json) and [migration report](../../reports/storage/migration.md). The replay matched all 13 MSE values for the historical 2022 slice and is excluded from new method comparisons.
