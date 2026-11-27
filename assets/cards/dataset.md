---
pretty_name: FinancialGraph research assets
language:
- en
- zh
---
# FinancialGraph research assets

Private project dataset and experimental evidence; not an investment product.

Raw source is reused, not duplicated: CryptoSpartan/stocks_bars_1m at
0c6f25f287918b1421c2572d2c9e2b75bd8959a9. Its upstream card declares MIT;
this card does not change the licensing of upstream or derived assets.
No new redistribution license is granted for project-derived artifacts here.

`derived/` contains the preserved historical forecast table, daily returns and
hourly aggregates. `splits/` specifies rolling development partitions.
`experiments/` contains selected completed runs' predictions, validation choices,
metrics and source/environment provenance. Individual files are small logical
shards by method/run/seed; original CSV bytes are retained so audit hashes remain
valid. No environments, caches, credentials or intermediate checkpoint directories
are uploaded. The upstream raw Parquet supports range reads; it is not silently
converted or re-uploaded.

2018–2024 is development data, not untouched confirmation. The 100-stock universe
has survivorship/curation limitations. The minute-level preprocessing has not been
fully reconstructed; preserving legacy inputs is not proof of raw reproducibility.
NTD did not beat the strongest tested control. RG-ResMoE is a task adaptation.

Code and manifests: https://github.com/SansaZheng/Financial-graph
