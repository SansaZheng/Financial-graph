# Mac data migration — 2026-11-24

No original data deleted. The user requires **all** data migrated before deletion.

- Raw source release: 10,927,267,185 bytes in11 parts; remote digest/size checks match the manifest. See raw-release-verification.json. This raw file was on c220, not on the Mac.
- Readable local files:7 preserved in mac-data-20261124.tar.gz; archive manifest embedded. This is a **partial** archive.
- Unreadable local files:71 iCloud dataless placeholders. Earlier materialization reads timed out. See mac-data-manifest.json for exact paths. Do not unlink placeholders: that may delete cloud originals.
- c220 forecast table, daily returns, hourly data and prior metrics recovered through CQ and SHA256-checked in evidence/cq/j-1123-b41d82. These are extra backups, not proof that inaccessible Mac files are identical.
- Other projects and environments left untouched.

To finish: make the listed project files readable from iCloud, hash/archive them, upload and verify the remote archive, then delete only matching files with no remaining experiment dependencies. Do not download the entire mixed-project FinancialAD folder. Most target directories currently occupy0 allocated bytes, so deleting their placeholders would not materially free Mac storage.

## 中文结论
原始大数据及已读取文件已备份/校验，但71个 iCloud 占位文件仍无法读取，因此尚未满足“全部迁移后删除”的前提。本轮没有删除原始文件，实际释放空间为0；没有改动其他项目。

## Explicit recovery retry, 2026-11-24

Issued macOS NSFileManager download requests to the exact71 manifest paths; all71 accepted. Across12 polls10 seconds apart, zero files became resident. NSURL metadata says all71 downloading, not downloaded, with no reported error. A read-only NSFileCoordinator request also failed to return; only our waiting reader was terminated. No global iCloud service/settings changed. No source deleted. Recovery remains incomplete.

`request_icloud.m`, `icloud_status.m`, `recover_71.py` preserve the bounded workflow. `publish_recovered.py` refuses unless all71 files are recovered, checks local hashes, uploads a Release, redownloads it and checks every member. It does not delete sources. After successful remote verification, evict local downloads through macOS rather than unlink cloud originals.

中文结论：已再次主动请求恢复71个文件，但目前0个恢复成功；系统同步未返回内容，上传与删除条件仍未满足。

## Recovery retry, 2026-11-25

All 71 scoped macOS download requests were accepted again. Also requested Download in Finder for the project results/expanded folder only; Finder displayed downloading. Twelve polls at ten-second intervals and a final file-flag check found 0/71 resident files. Scoped bird/cloudd error diagnostics included network and timeout categories, but do not establish the cause. No account, network, global sync setting, other project, or original file was changed. The recovery archive remains incomplete and was not published.

中文结论：本轮继续尝试系统下载和 Finder 下载，71 个文件仍全部为 iCloud 占位文件，尚未恢复内容。已备份的文件仍保留在 GitHub；未满足全部上传并校验的前提，因此没有删除任何原始文件，也没有释放本地数据空间。后续清理仅在校验完成后移除本地下载，保留云端原件。
