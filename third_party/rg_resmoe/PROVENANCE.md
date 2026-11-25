# RG-ResMoE author implementation

Source: https://github.com/JunyiYe/rg-resmoe
Commit: 5012deb5c6c376a85c31f55234df2ede4ac9ff3f
Retrieved: 2026-11-25 via GitHub connector.
Paper: https://arxiv.org/abs/2608.12251 ; https://doi.org/10.1145/3858063.3858798
License: MIT; LICENSE retained alongside source.

Files copied from src/train_rg_resmoe.py and src/walk_forward.py. The local adapter overrides runtime DEVICE to CPU and sets training constants explicitly; it calls the author's training and prediction functions without running their main pipeline. This is an architecture adaptation to next-hour market log variance, not replication of published cross-sectional five-day volatility results. No author data or reference metrics are relabeled as our results.

Import adds one trailing newline per upstream text file; executable contents are unchanged. Local byte hashes are in manifest.json. The upstream commit was independently checked via GitHub commits/main.
