## Active research — 2026-11-25

Missing iCloud investigation has been discontinued at the user's request. Research uses verified GitHub/c220 inputs.

- [Live checked status](paper/workflow/current.md) and [CQ job snapshot](paper/workflow/cq-status.json).
- [NTD mechanism and frozen protocol](paper/workflow/protocol-ntd-002.md).
- [Modern RG-ResMoE adaptation](paper/workflow/protocol-modern-001.md).
- [Verified experiment report, ending in Chinese](paper/workflow/experiment-report.md).
- [Reproduction steps](REPRODUCE.md), [claim map](paper/workflow/claim-map.md), [evidence limitations](paper/workflow/evidence-audit.md).

The completed legacy CGI run failed to beat its strong control. New method claims require actual CQ outcomes; CCF A readiness is not established.

# Financial Graph

Research on incremental graph information for volatility forecasting. Target: CCF A research quality, not a claim of achieved novelty, superiority or acceptance.

The previous independent GAE experiment did **not** beat its strongest density control (R² 0.761135 vs 0.760100). Existing 2018–2024 results are consumed development data, never fresh confirmation.

## Current method
Conditional Graph Innovation (CGI) removes the part of graph scores predictable from strong temporal/density controls using forward cross fitting, then learns a residual forecast correction. A development-only gate may reject the correction. Residualization is predictive, not structural causal identification. This is an initial hypothesis, not established novelty.

## Reproduction
Install `requirements.txt`; run `python -m pytest tests`. Run experiments only through CQ using the pinned specs under `jobs/`. Scientific outputs go to `CQ_OUTPUT_DIR`. Follow `paper/workflow/state.md` for actual job IDs, evidence and blockers.

## Archive scope
The legacy Mac checkout is preserved at `/Users/zyy/Documents/ChatGPT/FinancialAD/financial-graph-research`; iCloud currently prevents reliable reads. This recovery checkout publishes small source files from `/Users/zyy/.local/share/financial-graph`. No original file was deleted or overwritten. Legacy evidence and the 10.9 GB raw archive are **not yet uploaded**; the data audit must recover and verify them before claiming a complete archive.

## 中文结论
本研究首先检验图信号能否在强时间序列和图密度对照之外提供增益。尚未产生新实验结论。全部结果，包括失败结果，必须保存；完整原始数据归档、独立确认和创新性验证仍未完成。
