# Claim map

| ID | Bounded claim | Artifact | Status |
|---|---|---|---|
| C1 | Legacy CGI has worse pooled2022–24 development MSE than validation-selected strong control | reports/evaluations/j-1125-dd9d4b; prediction bytes listed in assets/manifest.json | supported |
| C2 | NTD graph features exclude the prediction session and fit graph before shock session | src/topology.py; tests/test_topology.py; source_day/graph_fit_end in outputs | supported: all three output timing audits passed |
| C3 | NTD outperforms the strongest tested control | reports/evaluations/j-1125-0c3a7c; original predictions listed in assets/manifest.json | not supported: all three seeds worse by0.404–0.507% |
| C4 | RG-ResMoE architecture adapted from author implementation | third_party/rg_resmoe; src/modern_baseline.py | three CQ runs verified; not exact paper reproduction |
| C5 | New method is novel and CCF A ready | independent data, modern baseline suite, causal-time audit and broader novelty review required | unsupported |
| C6 | All missing iCloud files recovered | none | false; user discontinued pursuit; no cleanup performed |
| C7 | Full11GB raw source persists on GitHub | maintenance/raw-release-verification.json | supported |
