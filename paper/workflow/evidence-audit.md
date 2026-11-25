# Evidence audit — 2026-11-25

## Task and current boundary

Goal: test whether topology-specific information improves market volatility forecasts beyond the strongest applicable controls. CCF A quality is an aspiration; venue is not selected. A confirmed novel mechanism, independent data and strong modern comparisons are required before a paper-quality claim.

| Item | Verified status | Limitation |
|---|---|---|
| Original GAE paper numerical reproduction | Not achieved | Original task/data and new next-hour forecast task differ |
| Raw source archive | Complete, verified GitHub Release | Data ends2024; not untouched2025–26 |
| Legacy full CGI CQ run | j-1125-dd9d4b complete,3644 predictions | Development-only; old graph timestamps unaudited |
| Legacy CGI improvement | Negative:0.2386624 vs0.2370911 MSE | Gate also worse; no safety guarantee |
| Node-level NTD implementation | Implemented, code pinned | Prediction evidence pending until r3 finishes |
| Timing invariants | Local tests and CQ qualification | Raw minute aggregation not rebuilt |
| Missingness |14 observed missing cells; past-window node eligibility | Time-varying stock universe and survivor selection |
| Modern RG-ResMoE | Author code retained under MIT; adapter implemented | Different task/features, not exact paper replication |
| Strong control | Validation selection includes capacity-matched temporal correction | Cannot claim globally strongest possible model |
| Multiple markets | Not achieved | One US panel;100stocks are not100datasets |
| Ten methods / two2026 methods | Planning targets only | RG-ResMoE adapted; Sig-GSPHAR not implemented |
| Statistical confirmation | Exploratory paired block intervals | No multiplicity-adjusted confirmatory test; no untouched holdout |

## Contribution audit

Established ingredients: factor residualization, graph diffusion, permutation null moments, forward cross fitting, residual learning. The exact permutation expectation is a known finite-population identity. The candidate contribution is using null-centered shock-topology alignment as an incremental forecast diagnostic, with capacity and placebo controls. This remains a hypothesis until empirical comparison and a wider related-work review support it. Combining established ingredients or beating a weak GAE does not itself establish CCF A quality.

## Required next discriminating evidence

Complete the frozen NTD and modern CQ runs, including negative/zero-weight outcomes. If NTD cannot beat the capacity-matched temporal control or behaves like its permutation placebo, do not claim graph-specific improvement. If it succeeds, test degree-conditioned permutations, edge rewiring, graph lag/window stability, independent market panels and genuinely new dates with methods frozen before reading them. A switch to a new target must be documented as a new study, not used to conceal failure of the present primary endpoint.

## 中文结论
当前可信结论是旧 CGI 未超过强对照；新 NTD 已实现但须由正在执行的实验验证。论文贡献、跨市场稳定性和独立确认仍有明确缺口，不能把代码完成或任务提交写成顶会水平已经达成。

Additional input boundary: the forecast table was curated by the earlier pipeline and is not regenerated from all raw minutes in this round. New methods share its exact rows. The current audit verifies target alignment and historical rolling/difference features, but not original raw aggregation or universe construction.

## Adversarial implementation review (before full NTD outcomes)

- The temporal residual control matches the18-column target-correction design and its alpha/weight search. It does not match all unsupervised graph/nuisance preprocessing parameters. Call this matching correction capacity, not perfectly equal total pipelines.
- A global shock-permutation null does not remove shock-degree alignment. Strength-conditioned shuffles and edge rewiring remain necessary to distinguish detailed topology from node centrality effects.
- Outer validation chooses the baseline and correction on the same validation year. Outer-year loss remains temporally separated, but the validation gate's interval is post-selection and is not a formal safety certificate.
- Nested forward residuals come from expanding-prefix baselines; their distribution may differ from the final refitted baseline. This is an explicit deployment mismatch to diagnose, not evidence of improvement.
- Provider CPU tests establish executable invariants, not economic value, causal contagion, model novelty or publication readiness.

Float precision audit: the first modern full run initially failed a1e-10 metric check when CSV predictions were parsed as float64 (MSE differences at most7.5e-9). Restoring the original Torch/pandas float32 prediction dtype exactly reproduces all three stored MSE and R² values. The verifier now explicitly restores this dtype for modern-adaptation-001. No metric tolerance was loosened and no predictions were changed.
