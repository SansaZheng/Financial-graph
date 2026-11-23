# Research execution — 2026-11-23 Asia/Singapore

## Publication
Primary archive: https://github.com/SansaZheng/Financial-graph
CQ-only private mirror: https://github.com/SuuTTT/financial-graph-cq
Both published code commit b832d7b (full SHA in immutable job specs). CQ rejects repositories outside SuuTTT; mirror preserves exact commit identity. No original local file deleted. Recovery checkout: /Users/zyy/.local/share/financial-graph; original Documents checkout blocked by iCloud and nearly full Mac disk.

## Actual CQ jobs
- j-1123-b41d82: read-only input recovery on c220; queued, CPU capacity unavailable at last inspection.
- j-1123-373d6c: read-only backup-input audit on c225; submitted.
- j-1123-fca05c: isolated conda environment + three structural tests on c225; submitted, not yet passed.

No smoke or forecasting batch submitted yet: verify real input first. No paid compute, GPU allocation, manual remote SSH or interference with other jobs.

## Research
Implemented CGI and chronological development evaluator. Old 2022–2024 results are consumed development data. No new empirical outcome yet. Fresh confirmation cohort, topology-level extension, modern comparable methods, multiple independent datasets and raw data archive remain unfinished. CCF A is an aspiration, not an achieved claim.

## Storage
Small source now published. Legacy derived results and 10.9 GB raw parquet still NOT uploaded to the target repository. Audit recovers bounded derived files with hashes and checks raw size without copying the full archive. All new compute output uses CQ local project storage; c225 project home resolves to its large /data2 disk. c220 reports ~4TB free on its project-home disk. Old shared /date has 92% usage and is not a training output destination.

## 中文结论
GitHub 权限已生效，关键新代码与协议已经发布，并提交了真实 CQ 输入核验和环境任务。尚未运行新的预测对比，也没有超过最强对照的结论。待数据和环境核验完成后，继续冒烟测试与完整开发实验，所有结果包括失败均应归档。
