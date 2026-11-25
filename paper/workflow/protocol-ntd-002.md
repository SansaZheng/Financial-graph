# NTD-002: frozen development protocol, 2026-11-25

Scope: a new node-level mechanism test using the available US equity panel. Original GAE reconstruction discrimination and next-hour volatility forecasting are different tasks. This experiment is not a numerical reproduction of the EPJ paper. All 2018–2024 observations are consumed development data; no untouched claim.

## Mechanism and falsifiable contribution hypothesis

NTD asks whether **where a shock occurs in a residual correlation network** predicts next-hour market volatility, beyond temporal persistence, shock magnitude and network density. It is a candidate contribution, not an established novelty claim. Unlike the old aggregate-GAE CGI, it operates on 100 individual stock returns.

For a prediction on session t, take shock returns from the latest completed session s<t. Regress each stock's return on an equal-weight market factor over the 60 sessions strictly preceding s. Build positive residual-correlation weights exceeding .25, with zero diagonal. Let P=D^(-1/2) W D^(-1/2). Standardize and clip the held-out shock with those past fit parameters. For signed and squared-downside shocks, center across nodes and compute q' P^h q/n for h=1,2,3.

Subtract the exact uniform node-permutation expectation:

E[q_perm' M q_perm/n] = mean(q²) [n tr(M) − sum(M)] / [n(n−1)], M=P^h.

Proof: centered q implies E[q_perm,i²]=mean(q²) and E[q_perm,i q_perm,j]=−mean(q²)/(n−1) for i≠j; expand the quadratic form. This is a standard finite-population identity, not a claimed new theorem. Scale by the sample standard deviation of 32 fixed-seed permutations (floor1e-6), clip to[-10,10]. The null preserves the entire network and the shock values, removing their node alignment. It does not condition on labeled degree/strength and is not edge rewiring. A degree-conditioned null and edge rewiring remain necessary follow-ups if there is useful signal.

## Controls and correction

Controls receive temporal lags1/7/6/30, shock, downside, slot plus8 prior-session context features: market return/variance, idiosyncratic energy/downside/dispersion, residual density, mean weight, strength coefficient of variation. No old GAE or density columns are used because their availability timestamps have not been recovered. Comparisons to legacy metrics are therefore descriptive, not matched-protocol improvements.

Base candidate families: standardized ridge alpha1/10/100/1000; HGB leaves7/15/31,150 rounds,l2=10; ExtraTrees100 trees,minleaf10/30. Also fit temporal-only candidates. Every correction has6 channels ×3 state interactions, ridge alpha10/100/1000, weight0/.25/.5/1. Branches: NTD, raw diffusion, null expectation only, permuted-shock placebo, temporal-only residual control, NTD without nuisance residualization. Direct fusion gets the same9 base candidates. No published neural architecture is claimed reproduced.

Forward annual cross fitting trains the base selector using only its prefix (last year of that prefix for hyperparameter selection); graph nuisance ridge alpha10 also sees only that prefix. Fit corrections to forward prediction errors and innovations. Final correction scale and normalization use only fit data. Outer validation selects alpha/weight and strongest control. Strong control includes the capacity-matched temporal correction. Report ungated NTD as primary; validation lower-bound gated fallback is secondary, not a no-harm guarantee.

## Splits and endpoints

Outer test years2022/2023/2024; preceding year is validation; train begins2018. Labels end strictly before next partition. Every daily source day must be strictly earlier than prediction day; graph fit ends before source day. Smoke uses2022 only. Smoke outcomes are not used to revise methodology before the full run. Full NTD runs use permutation seeds471/472/473; seeds quantify Monte Carlo sensitivity, not independent datasets. Retain all failures.

Primary endpoint: hourly squared log-variance error relative to the validation-selected strongest control. Secondary: R²,MAE,QLIKE of exponentiated log forecasts, per-year and high-volatility subset results. Stress threshold is training+validation target90th percentile; test outcomes define the retrospective subset only. QLIKE is diagnostic, with no smearing correction or QLIKE training.

Five-session moving block intervals (2000 draws) aggregate paired hourly losses per session. They are exploratory, not multiple-testing adjusted; daily intervals and pooled hourly MSE use different weights. Positive gains must survive capacity-matched and placebo comparisons and an untouched future multi-market evaluation before superiority claims. Final reports must show all models and negative results.

## Execution and archive

CQ free CPU only,2 CPUs/4GB per job, no rental. Environment/test -> smoke -> full; immutable Git SHA. All features, model input, predictions, validation predictions, selection grids, fold boundaries, metrics, input SHA256, runtime/RSS, package freeze and logs are archived on GitHub. Raw11GB source is already a verified multi-part Release. Existing iCloud placeholders are out of scope and preserved.

## 中文结论
创新假设是“网络中的冲击位置是否提供超越历史波动、密度和相同容量非图模型的信息”。残差学习或图融合本身不算创新。先通过真实 CQ 开发实验证伪或支持该机制，再决定是否值得扩大到独立市场、现代图模型和未观察样本；当前不能宣称超过最强对照或达到 CCF A 水平。

## Input correction before first predictive outcome

Smoke stopped before training because the archived daily input contains14 missing cells across8 tickers. Each graph now excludes nodes with a nonfinite return in its60-session fitting window or its shock session. Eligibility uses only already observed rows, never future availability. No market session or target is removed for performance reasons; require at least20 nodes and archive node count/excluded names per source session. The frozen graph mechanism and model grids are unchanged.

## Execution-only backend amendment

Kaggle CPU slot pressure delayed NTD. CQ built and verified an isolated c225 environment at /data3/sudingli/cq-home/financial-graph-ntd, with Python3.11.18, numpy2.2.6,pandas2.2.3,scipy1.15.3,scikit-learn1.6.1. Ten tests passed. Core numerical package versions match Kaggle; Python differs from3.13.18. Scientific source files are byte-identical between9f343af and8b3843c; only execution wrappers changed. The already-assigned Kaggle smoke is retained for a cross-backend consistency check. Three still-unstarted Kaggle full seeds were cancelled and replaced by c225 full runs after a c225 smoke. No full seed is intentionally duplicated. The alternative portable-existing-environment qualification finished too, but is not used for these experiments. No paid resources or other projects' jobs were changed.

## Final execution fallback

The c225 smoke stalled during pytest collection before generating forecasts. A separate90-second bounded import diagnostic exited124; import timing showed broad slow dependency imports (joblib cumulative about33.6 seconds). This does not establish a model defect or a specific host/storage cause. No system or other-user job was changed. Three unstarted lab full seeds were cancelled. The lab smoke received a CQ cancellation request; its final state is tracked separately.

The unchanged scientific code is now run as one sequential three-seed Kaggle CPU batch, j-1125-a08289, pinned32a4480 (full SHA in jobs/20261125-batch/batch.json). This reduces repeated provider startup. It depends on the successful original NTD smoke and environment qualification. No method, split, parameter grid or seed changed in response to prediction results. Each seed retains separate features, inputs, selections, predictions, metrics and version files under its own output subdirectory.
