# Matched intraday graph comparison

The graph increased MSE by **0.82%** versus the validation-selected control on 2,912 common forecasts across 748 trading days.

| Model | Pooled MSE ↓ |
|---|---:|
| Historical temporal features | 0.24909360 |
| Temporal + node summaries | 0.24781955 |
| Node summaries + density | 0.24961202 |
| Raw graph diffusion | 0.24962387 |
| Strength-conditioned shuffle | 0.24960671 |
| Degree-preserving rewiring | 0.24960349 |
| New graph diffusion surplus | 0.24985126 |

| Development year | Common rows | Selected control | Control MSE ↓ | Graph MSE ↓ |
|---|---:|---|---:|---:|
| 2022 | 986 | Node summaries + ridge (alpha 1) | 0.23893179 | 0.24139243 |
| 2023 | 983 | Node summaries + ridge (alpha 10) | 0.25865817 | 0.25922979 |
| 2024 | 943 | Node summaries + ridge (alpha 1000) | 0.24581422 | 0.24891945 |

Gain is control MSE minus graph MSE. Positive values favor the graph. We resampled complete trading-day blocks within each evaluation year and kept the hourly weighting.

| Block length (trading days) | Paired MSE gain | 95% interval | Centered bootstrap p (two sided) |
|---:|---:|---:|---:|
| 5 | -0.00203171 | [-0.00350821, -0.00074220] | 0.0042 |
| 10 | -0.00203171 | [-0.00354007, -0.00063814] | 0.0063 |
| 20 | -0.00203171 | [-0.00355815, -0.00047678] | 0.0094 |

The fixed nine-stock panel used one-hour returns at the archived New York 11:31, 12:31, 13:31, and 14:31 decision times. The graph used the preceding 60 complete observations at the same clock time. Each outer year selected its own control and hyperparameters on the preceding validation year. Every family used the same learner grid and evaluation rows. See the [protocol](../../paper/workflow/prompts/005-intraday-matched.md).

CQ `j-1128-b367d3` built the panel and `j-1128-cd5685` ran the comparison on c225. The row-level predictions stay on the remote data disk at `/home/sudingli/cq-home/financial-graph-intraday-005/results/evaluation-v2/predictions.csv`. Their SHA-256 and independently recomputed MSE are in [verification.json](verification.json). The [panel builder](../../src/intraday_panel.py), [evaluator](../../src/intraday_compare.py), [job specs](../../jobs/20261128-matched), [metrics](metrics.json), and [validation selections](selection.json) reproduce the table.

These are previously used development years. The fixed nine-stock cohort and inherited target do not establish performance on a new market or untouched dates. The interval conditions on the fitted model choices.

中文结论：按纽约时间 11:31–14:31 对齐后，节点汇总对照在三个年份均由验证集选中。加入图扩散偏离量后，MSE 在三年都上升。主检验与两种区块长度的敏感性检验均支持图模型在此开发样本上表现更差。
