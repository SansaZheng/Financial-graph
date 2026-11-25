# Verified state — 2026-11-25 Asia/Singapore

Primary archive: https://github.com/SansaZheng/Financial-graph
CQ compute mirror: https://github.com/SuuTTT/financial-graph-cq

## Completed evidence
- Raw 11GB multipart GitHub Release verified by sizes and SHA256; see maintenance/raw-release-verification.json. No Mac raw-data download required.
- Legacy CGI full comparison j-1125-dd9d4b: CGI MSE0.2386624 versus strong control0.2370911; no improvement.
- Modern adapted RG-ResMoE and matched MLP: seeds471/472/473 completed and independently recomputed. Matched MLP outperformed RG-ResMoE in each seed. See experiment-report.md for exact values and adaptation limitations.
- NTD implements past-only residual graph construction, exact permutation-null centering and cross-fitted residual correction with temporal and graph controls. Qualification passed10tests; Kaggle smoke j-1125-4850c7 completed. Smoke results did not trigger method changes.

## Remaining experiment
CQ job j-1125-a08289 runs the unchanged three-seed NTD batch on free Kaggle CPU, pinned to32a4480cd7a739a345abddf0691a5900ceddb9e8. At this update it is queued behind existing platform sessions. Its final predictive results have not been observed.

Lab environment qualification succeeded, but dependency import diagnosis timed out at90seconds and c225 smoke j-1125-194bed stalled before forecasts. That smoke is confirmed cancelled. Superseded unstarted full jobs are cancelled; no other projects or users affected. Diagnostic failure is preserved without an unsupported root-cause claim.

## Scope and limitations
Missing iCloud investigation is discontinued at the user's instruction. No original data deleted. No paid rental or paid compute enabled. All historical2022–2024 outcomes are development evidence, not untouched confirmation. No independent market panel or2025–2026 confirmation is complete. CCF A readiness, causal contagion and profitability are not established.

## 中文结论
研究已恢复推进，旧方法未超过强对照，三组现代对照和新方法的环境及小规模验证已完成。NTD正式三种子批次仍待免费资源，暂不能声称新方法优于最强对照，也不能声称达到CCF A录用水平。
