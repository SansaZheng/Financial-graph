# Financial Graph

Research on incremental topology information for volatility forecasting. CCF A quality is a goal, not an achieved claim.

## Verified result — 2026-11-25

CQ completed the frozen **Null-centered Topology Diffusion (NTD)** study: three seeds, each3644 forecasts across2022–2024. Independent recomputation, input/code hashes and time-boundary checks passed. NTD MSE is0.2377171/0.2378833/0.2376406, versus0.2366833 for the validation-selected strong control. All three seeds are worse by0.404–0.507%. The validation gate falls back to the strong control in every year. This is a negative primary result, retained in full.

Three adapted RG-ResMoE/matched-MLP runs and the older CGI run also completed. Better performance than some neural controls does not establish superiority to the strongest tested control. Historical data is development-only; no independent confirmatory holdout is claimed.

- [Verified report with Chinese conclusion](paper/workflow/experiment-report.md)
- [Exact reproduction steps](REPRODUCE.md)
- [Frozen NTD protocol](paper/workflow/protocol-ntd-002.md) and [modern adaptation protocol](paper/workflow/protocol-modern-001.md)
- [Code: graph construction](src/topology.py), [forecast evaluation](src/ntd_evaluate.py), [independent verifier](jobs/summarize_research.py)
- [Full NTD evidence](evidence/cq/j-1125-0c3a7c), [job specification](jobs/20261125-portable-batch/batch.json)
- [State](paper/workflow/state.md), [claim map](paper/workflow/claim-map.md), [limitations](paper/workflow/evidence-audit.md), [next-study decision](paper/workflow/next-study-decision.md)

## Method and archive

NTD constructs past-only factor-residual networks, measures diffusion alignment with held-out shocks, subtracts the exact uniform-permutation expectation, and fits a forward-cross-fitted forecast correction. Established residualization/permutation mathematics is not claimed as a new theorem. The proposed diagnostic has not demonstrated incremental predictive value here.

Derived inputs, predictions, validation selections, environments, job specifications and key code are tracked in this repository. The11GB raw source is archived in a [verified multipart Release](https://github.com/SansaZheng/Financial-graph/releases/tag/raw-stocks-bars-1m-59bc5acc); see [verification receipt](maintenance/raw-release-verification.json). Missing iCloud files are no longer being pursued. Original Mac files remain untouched; this study does not claim those inaccessible files were recovered.

All experiments used CQ with zero paid budget. Large lab files use authorized data disks. NTD and its controls share one environment; software differences from Kaggle modern runs are recorded explicitly. No other users' jobs or environments were modified.

## 中文结论

本轮已完成可复算的真实实验和归档，但NTD未超过最强对照，尚未达到CCF A论文的证据要求。下一阶段须解决时间对齐、节点强度条件对照、独立市场数据和创新性验证，不能用已看过的年份反复调参替代独立确认。
