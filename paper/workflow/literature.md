# Initial literature audit — verified 2026-11-23

- https://arxiv.org/abs/2605.19278 — submitted May19,2026, revised May20. Graph volatility forecasts, ranking and portfolio outcomes differ; forecasting gains alone do not establish economic value.
- https://doi.org/10.1007/s10489-026-07445-1 — published September8,2026. Sig-GSPHAR combines temporal signatures and directed graph spectral HAR across29 markets. Temporal-graph fusion is already studied. Our candidate contribution is conditional incremental graph information, still unverified.
- https://doi.org/10.1140/epjds/s13688-025-00523-3 — original GAE paper. Our previous public-data implementation is not an exact numerical reproduction.

These are primary-source starting points, not an exhaustive novelty review or reproduced modern baseline suite. Proposed CGI combines established residual learning/cross fitting; CCF A readiness requires substantially stronger independent evidence and contribution analysis.

## Focused refresh — 2026-11-25

Primary pages were opened and publication/submission dates checked. These are relevant findings, not evidence that our method is novel or that these authors' results reproduce on our data.

| Work and verified source | Date | Relevance and limit |
|---|---|---|
| [RG-ResMoE](https://arxiv.org/abs/2608.12251) | Submitted 2026-08-12 | Regime variables route residual experts; capacity-matched US and Japanese forecasting study. Residual gating is already studied, so CGI gating alone is insufficient novelty. Different target/horizon requires a faithful adaptation rather than quoting its scores as ours. |
| [Signal Simplification Is Not Predictive Simplification](https://arxiv.org/abs/2610.03019) | Submitted 2026-10-02 | Reports that reduced HAR residual variance need not improve residual-LSTM prediction. Motivates explicit no-benefit outcomes and capacity controls, not an assumption that residual learning will win. |
| [Sig-GSPHAR](https://doi.org/10.1007/s10489-026-07445-1) | Published 2026-09-08 | Directed graph spectral HAR plus path signatures for29 markets. Spectral temporal fusion is not new; multi-market topology baselines are pending, not reproduced here. |
| [Do Better Volatility Forecasts Lead to Better Portfolios?](https://arxiv.org/abs/2605.19278) | Submitted 2026-05-19, revised05-20 | Forecast, ranking and portfolio objectives differ. We restrict claims to forecast loss, not trading value. |

Our inference: testing topology-shock alignment after removal of common factors and comparison with permutation expectations may offer a more discriminating research question than adding another graph encoder. This is a candidate direction. The permutation identity and cross fitting are established tools; no first-of-kind claim is supported by this focused search. Need broader graph-signal/null-model literature audit and faithful modern implementations if the mechanism survives development. Two2026 methods identified as candidate baselines (RG-ResMoE, Sig-GSPHAR), zero faithfully reproduced yet.
