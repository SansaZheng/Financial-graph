# Frozen-node correction for intraday graph forecasts

The correction recovered **90.4%** of the previous excess MSE. It reached **0.24801502** on the same 2,912 decisions. The frozen node control reached **0.24781955**. The paired interval includes zero.

## Diagnosis

The original node → density step adds graph density and mean edge weight together. It accounts for 88.2% of the original pooled graph MSE penalty. The archived step includes validation-selected penalty differences. At the original node ridge penalty within each year, adding the same two variables still raised MSE in every year. The table also gives the fixed-penalty effect of appending only the previous graph surplus, leaving out density and mean weight.

| Evaluation year | Archived density − node | Fixed-penalty density − node | Fixed-penalty graph surplus only − node | Prior-year validation residual correlation |
|---|---:|---:|---:|---:|
| 2022 | +0.00163867 | +0.00163867 | +0.00081747 | +0.0653 |
| 2023 | +0.00045500 | +0.00132310 | +0.00012064 | -0.0424 |
| 2024 | +0.00334747 | +0.00334747 | -0.00020846 | -0.0057 |

The node-orthogonal graph surplus has weak validation correlations of varying sign. The 128-shuffle approximation error was 6.8%–8.1% of the exact surplus standard deviation in the test-year diagnostics. The experiment evaluates the resulting correction as a bundle. It does not estimate the separate causal contribution of removing Monte Carlo error.

## Matched correction

We kept the frozen node predictor, removed density and mean weight from the correction, and replaced the sampled graph null by its exact expectation. An earlier-sample regression subtracts the part of the graph feature predictable from node inputs. A shrunk scalar correction forecasts the remaining node-model residual. The previous validation year selects the correction weight from 0, 0.25, 0.5, and 1. The full-weight version is a diagnostic.

| Year | Matched decisions | Validation weight | Frozen node MSE ↓ | Old graph MSE ↓ | Corrected MSE ↓ |
|---|---:|---:|---:|---:|---:|
| 2022 | 986 | 1 | 0.23893179 | 0.24139243 | 0.23950907 |
| 2023 | 983 | 0 | 0.25865817 | 0.25922979 | 0.25865817 |
| 2024 | 943 | 0 | 0.24581422 | 0.24891945 | 0.24581422 |
| Pooled | 2,912 | — | 0.24781955 | 0.24985126 | 0.24801502 |

Gain is control MSE minus corrected MSE. Positive gain favors the correction. Ten thousand moving-block draws keep all predictions within each trading day and resample separately within each year.

| Block length (trading days) | Gain | 95% interval | Two-sided p |
|---:|---:|---:|---:|
| 5 | -0.00019546 | [-0.00051871, +0.00004181] | 0.1621 |
| 10 | -0.00019546 | [-0.00053184, +0.00003502] | 0.1804 |
| 20 | -0.00019546 | [-0.00054241, +0.00003405] | 0.1923 |

CQ `j-1128-1fd048` ran on c225. We verified all 2,912 timestamps, targets, and baseline predictions against 005 and independently recomputed the pooled MSE and the primary five-day interval. The predictions are on the remote data disk at `/home/sudingli/cq-home/financial-graph-intraday-005/results/residual-006/predictions.csv`. See [code](../../src/intraday_residual.py), [CQ spec](../../jobs/20261128-residual/experiment.json), [diagnosis](diagnosis.json), [metrics](metrics.json), [selection](selection.json), and [verification](verification.json).

This correction was designed after viewing 005. The 2022–2024 results are post-diagnosis development evidence on a fixed nine-stock cohort and require an untouched period for confirmation.

中文结论：固定正则化后，图密度和平均边权仍在三个年份都增加误差。残差修正缩小了原图模型与节点对照的差距，挽回约 90.4% 的超额 MSE。相对同一节点对照，修正版 MSE 仍高约 0.079%，配对区间跨零。
