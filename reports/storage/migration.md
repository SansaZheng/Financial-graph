# Storage migration — 2026-11-27 (Asia/Singapore)

## Scope and completed reversible changes

Active checkout: `/Users/zyy/.local/share/financial-graph`. It was clean at the start. The larger Documents/FinancialAD workspace contains other projects and was not reorganized. Missing iCloud originals are not being recovered or deleted.

GitHub source is public and the connected account has push permission (no admin permission). Both existing remotes are reused; no new GitHub repository was created. Working branch: `codex/asset-storage`. New private HF destinations are not created without authenticated account inspection and verified included quota.

Data/generated outputs have been removed from the Git index, but their Mac bytes remain intact and ignored. Compact full-run metrics, validation choices, source revisions and environment records moved to `reports/evaluations/`. Original raw-source metadata moved from `data/source.json` to `assets/upstream-source.json`. The former GitHub raw-upload workflow now performs only a read-only storage-policy check when manually invoked. The existing11GB Release remains a backup.

The version manifest has exact paths, byte sizes and SHA256 for raw assets, derived data and selected full-run evidence. Upload/download/verify/account/stream scripts use official huggingface_hub0.36.0, refuse floating published revisions, enforce private destinations, avoid duplicate content, and preserve interrupted large-upload task metadata. Model selection requires best/final/recovery roles and provenance. No weights were observed in the local checkout or c225 project outputs; no empty model repo was created.

## Assets and remaining access

| Asset | Location / revision | State |
|---|---|---|
| Raw minute Parquet,10,927,267,185bytes | `CryptoSpartan/stocks_bars_1m`, dataset, `0c6f25f287918b1421c2572d2c9e2b75bd8959a9` | Existing HF source reused; LFS SHA and previous independent Release digests match |
| Upstream card,1,272bytes | Same repo/revision, `README.md` | Downloaded small metadata and SHA256 checked |
| Derived inputs + split/provenance/card | Planned existing-or-private project Dataset repo | Pending login, namespace and included storage headroom |
| Selected full-run evidence | Same project Dataset repo, grouped by run/seed | Pending authenticated upload and pinned readback |
| Models | None selected | No serialized weights identified; training code does not save them |

Project curated upload: approximately44.2MB,69explicit files, no environments/caches. The account's existing private HF repositories, write scopes and real storage balance cannot be inspected without credentials. There is no usable HF login on the Mac or observed c225 context. A c220-labelled first inventory was scheduled by CQ to c227; its report is correctly labeled c227, not evidence about c220. A strict c220 inventory was submitted separately.

## Verification

- Eleven local unit tests passed: immutable revisions, selective downloads, SHA corruption, safe paths, default Mac guard, quota gates, public-destination refusal, duplicate avoidance and failure-safe manifest updates.
- Git index policy passes after untracking assets; source originals remain on disk.
- Upstream HF metadata and card verified. No full raw download to Mac.
- Clean remote GitHub/HF streaming/dependency qualification: pending CQ receipt; this section will be updated after execution.
- Authenticated private upload/readback and full scientific reconstruction from HF: **not yet verified**. Unit mocks and public metadata do not count as real private upload success.

## History and cleanup plan — approval required before destructive actions

About55.8MB of unique blob payload remains in existing Git history (compressed local `.git` was about16.6MB at audit). The largest blob is8.35MB, so this is avoidable clone overhead, not a100MB GitHub file-limit emergency. Keep history unchanged now. Fresh shallow checkouts avoid historical payloads. A future history rewrite requires separate explicit approval, collaborator coordination, full repository backup and verified HF replacement mappings; never force-push as part of this task.

About55.5MB of active-checkout data/generated files were untracked but not deleted. These are potential future reclaimable bytes, not already freed. Only the curated subset is scheduled for HF migration; excluded smoke/install/intermediate artifacts must be reviewed separately before deleting their only copies. Current cleanup eligibility is **zero original files**, because the private HF uploads and independent readbacks have not completed. The prior raw Release is an independent backup and is not removed; replacing/deleting it requires another verified backup and explicit approval.

Remote runtime caches/environments are isolated under the CQ project's data-disk output directory. They are not fetched to the Mac and not tracked. The Mac temporarily has a small HF tooling environment and1,272-byte source-card cache under `/tmp`; these are newly created verification tools, not original research assets. No unrelated project or shared cache is cleaned. Remaining Documents/iCloud data is out of this reorganization's scope.

## Required decisions

1. Supply the intended HF namespace and establish a secure write-capable login on the chosen remote server; do not send tokens in chat.
2. Confirm remaining included/free private storage through HF account settings. No subscription or overage is authorized.
3. Only after upload, pinned download, checksum verification and independent backup: approve exact local original/cache cleanup paths if desired.
4. Shared history rewriting and deletion of the old raw Release remain separate optional decisions; neither is needed for a clean current checkout.

## 中文结论
代码与资产已经在仓库结构上分离，固定版本和校验工具已实现并进行本地测试；现有原始数据HF版本直接复用。私有派生数据上传仍受账号登录与额度信息缺失阻塞，因此尚不能宣称整个迁移完成，也不能删除本地原件。科研结果保持不变：NTD未超过最强对照。
