# Storage migration — 2026-11-28 (Asia/Singapore)

## Scope and completed reversible changes

Active checkout: `/Users/zyy/.local/share/financial-graph`. It was clean at the start. The larger Documents/FinancialAD workspace contains other projects and was not reorganized. Missing iCloud originals are not being recovered or deleted.

GitHub source is public and the connected account has push permission (no admin permission). Both existing remotes are reused; no new GitHub repository was created. The private project Dataset repository is `Sansa005/financial-graph-assets`. The personal HF Billing page showed 801 MB used out of 100 GB before upload. The existing `FinancialAD-target` repositories serve a separate project.

Data/generated outputs have been removed from the Git index, but their Mac bytes remain intact and ignored. Compact full-run metrics, validation choices, source revisions and environment records moved to `reports/evaluations/`. Original raw-source metadata moved from `data/source.json` to `assets/upstream-source.json`. The former GitHub raw-upload workflow now performs only a read-only storage-policy check when manually invoked. The existing 11 GB Release remains a backup.

The version manifest has exact paths, byte sizes and SHA256 for raw assets, derived data and selected full-run evidence. Upload/download/verify/account/stream scripts use official huggingface_hub 0.36.0, refuse floating published revisions, enforce private destinations, avoid duplicate content, and preserve interrupted large-upload task metadata. Model selection requires best/final/recovery roles and provenance. No weights were observed in the local checkout or c225 project outputs; no empty model repo was created.

## Assets and remaining access

| Asset | Location / revision | State |
|---|---|---|
| Raw minute Parquet,10,927,267,185bytes | `CryptoSpartan/stocks_bars_1m`, dataset, `0c6f25f287918b1421c2572d2c9e2b75bd8959a9` | Existing HF source reused; LFS SHA and previous independent Release digests match |
| Upstream card,1,272bytes | Same repo/revision, `README.md` | Downloaded small metadata and SHA256 checked |
| Derived inputs + split/provenance/card | `Sansa005/financial-graph-assets`, `00015899c8ac9511332d05949bf41d9cc0fe5c49` | 6 files read back and SHA-256 verified |
| Selected full-run evidence | Same private Dataset repo, `dcefc2163ef4c583085be39d239356ef6f024972` | 63 files read back and SHA-256 verified |
| Models | None selected | No serialized weights identified; training code does not save them |

CQ `j-1128-9e92e8` uploaded and read back all 69 selected files (44,218,695 bytes) on c225 with the official Hub client. See [upload receipt](private-upload-receipt.json). The strict c220 inventory `j-1127-f8f1aa` completed and found the 10,927,267,185-byte raw Parquet file in the legacy project. Scoped inventories of the Mac checkout, c225 and c220 found no saved model weights. See [c220 inventory](c220-inventory.json).

## Verification

- Thirteen local asset unit tests passed: immutable revisions, selective downloads, SHA corruption, safe paths, default Mac guard, quota gates, public-destination refusal, duplicate avoidance and failure-safe manifest updates.
- Git index policy passes after untracking assets; source originals remain on disk.
- Upstream HF metadata and card verified. No full raw download to Mac.
- Clean remote qualification passed on c225, CQ `j-1128-647b69`, code `921a5d38fc2bd152a2fc5ac6e793a0c10ccfb1f1`: clean shallow GitHub checkout, exact dependencies, 23 tests passed, pinned card full SHA256 verification, and five rows/three columns streamed from Parquet. Streaming does not verify the whole 11GB file hash. See `remote-validation.json` and `remote-tests.txt`.
- Authenticated private upload and full pinned readback succeeded. CQ replay `j-1128-cb02e7` fetched the pinned GitHub checkout into a fresh directory, downloaded and verified six private inputs and one historical metrics file, then ran 2022 NTD with seed 471. All 13 MSE values matched the corresponding historical 2022 results exactly across 1,238 predictions. See the [replay receipt](private-replay-receipt.json).

CQ `j-1127-647b22` staged all 69 selected files (44,218,695 bytes) on c225 at `/data3/sudingli/cq-home/financial-graph/results/asset-staging-20261127/source`; every file passed SHA256 verification. See `remote-staging-receipt.json` for the source copies used by the upload.

The server's HF HEAD response incorrectly reported zero bytes while API metadata reported 1,272. An official `HfFileSystem` pinned range read returned the correct content/hash. The downloader now supports a resumable range fallback for this specific zero-byte case, retaining strict final size/hash checks. No TLS or integrity checks were disabled. Failure diagnostics remain in this report directory.

## History and cleanup plan — approval required before destructive actions

About 55.8 MB of unique blob payload remains in existing Git history (compressed local `.git` was about 16.6 MB at audit). The largest blob is 8.35 MB, so this is avoidable clone overhead, not a 100 MB GitHub file-limit emergency. Keep history unchanged now. Fresh shallow checkouts avoid historical payloads. A future history rewrite requires separate explicit approval, collaborator coordination, full repository backup and verified HF replacement mappings; never force-push as part of this task.

The Mac retains 197 untracked files totaling 55,478,858 bytes. Of those, 65 files totaling 44,214,959 bytes match the verified HF manifest and the independent GitHub backup at `616f99b77efb84537ddbf3229c25661854d4827e` by SHA-256. Select cleanup candidates by intersecting the manifest's `source_path` entries with [the local inventory](untracked-assets.json) and checking the hashes again at deletion time. The other 132 files (11,263,899 bytes) need separate review. The original GitHub raw-data Release remains an independent backup.

Remote runtime caches/environments are isolated under the CQ project's data-disk output directory. They are not fetched to the Mac and not tracked. The Mac temporarily has a small HF tooling environment and a 1,272-byte source-card cache under `/tmp`; these are newly created verification tools, not original research assets. No unrelated project or shared cache is cleaned. Remaining Documents/iCloud data is out of this reorganization's scope.

## Local cleanup decision

Deletion of original Mac files requires explicit approval for the reviewed file set. The 65 verified paths above account for about 44.2 MB of potential reclamation. The existing Git history and raw Release are outside that file set.

## 中文结论

已将 69 个派生数据与实验文件迁入私有 HF 仓库，全部按固定提交回读并校验了 SHA-256。GitHub 保存代码、轻量结果与版本清单，Mac 保留原件以便审阅清理范围。既有科研结果中 NTD 未超过最强对照。
