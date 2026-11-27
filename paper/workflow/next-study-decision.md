# Decision after NTD-002 development results

## Observed result and stopping rule
All three remote CQ metrics put NTD behind the validation-selected strong control on the primary pooled hourly MSE. Gate fallback is exactly the strong control, not an improved model. Full local prediction, input/code hash and timing verification has now passed for all three seeds. Do not retune NTD on2022–2024 and relabel those years as independent tests.

## Research direction requiring new evidence
The current diagnostic asks whether yesterday's topology-aligned residual shock adds information about the next hour. A negative result may reflect no incremental information, graph/shock temporal mismatch, or estimation noise; it does not identify which explanation is true.

A next protocol should separate these mechanisms, rather than add neural capacity:
1. Rebuild causal intraday node returns from the already archived raw-minute data on a /data or /date server. Verify each forecast's actual availability and build universe membership without future survival filtering.
2. Compare equal-lag node-only, graph-density, strength-conditioned shuffle, and edge-rewired controls. A stratified permutation should preserve the relationship of shock magnitude to node strength while destroying finer topological alignment. This is a mechanism test, not automatically a novel method or a guaranteed improvement.
3. Freeze horizon and graph window choices using earlier development data, then evaluate on a new market and previously unobserved dates. Preserve negative and zero-weight outcomes. The historical qualification covered a derived panel ending in 2024. The raw Parquet metadata includes dates through July 2026. Check calendar coverage and the underlying universe before defining any later-date evaluation.
4. Use the best applicable validated non-graph control and faithful graph-volatility baselines. Architecture adaptations must retain their labels; the present modern baseline set is incomplete.
5. Claim a method contribution only if incremental performance survives capacity matching, null controls, multiple-testing treatment, independent data and a broader verified novelty review.

## Next comparison on the rebuilt panel

Freeze one candidate that uses equally lagged returns and a graph estimated on earlier sessions. Measure the energy of propagated shocks relative to permutations within bins of past node strength. The bins and random seeds must use only information available at each decision. Match the node-only, graph-density and rewired controls on inputs, samples, learner capacity and validation budget. Re-select the strongest competing model on validation under the new target definition. Compare paired MSE and day-block intervals on an evaluation window selected in advance. An informative result must show an improvement over the strongest forecast control and distinguish genuine graph alignment from the matched nulls.

The timing pilot's forward SPY variance target could not be constructed in its five-session slice. For the next development comparison, align nodes to the archived NTD decision clock and qualify the finite historical labels with exact one-hour horizons. The 11:31–14:31 New York cutoffs leave room for the 60-minute lookback and availability buffer. Exclude the 10:31 cutoff from every model in this matched protocol. Use the same intersection of valid feature and label rows for all controls. Re-estimate the baseline MSE on those rows before measuring any improvement.

A later-date holdout requires a documented forward-variance source and defined universe. Verify the calendar, as-of membership, arrival timing and coverage before selecting dates. Keep the 2025–2026 prices out of method selection.

## 中文结论
本轮结果不支持“NTD已超过最强对照”。下一阶段的重点应是补足因果时间对齐、节点强度条件对照和独立数据，而不是在已看过的年份不断调参争取一个更好数字。这是待执行的研究计划，不是已经完成的实验或CCF A贡献证明。
