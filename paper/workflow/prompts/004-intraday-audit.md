# 004-intraday-audit — local task specification

Configuration revision 1. Topic: incremental topology information for market volatility forecasting. This study follows NTD-002. Conference remains unspecified and CCF A is the quality goal. Codex prepares and audits the implementation. CQ executes it on c220.

Verify that the c220 raw Parquet matches the pinned HF manifest by full size and SHA-256. Audit timestamp coverage with row-group metadata and summarize later years without decoding their prices. On January 8–12, 2024 only, scan timestamp, symbol and close over the regular US session. Use the vendor's left-edge minute timestamps and an extra minute of feature latency. Check duplicate, invalid and missing bars. Test whether lagged node returns and the forward one-hour market realized variance can be assembled without crossing session boundaries or using future observations for feature membership.

Save a compact audit with source revision, package versions, timestamp and row counts, and feature/label coverage. Keep raw data on the data disk. Use one CPU, no GPU or paid rental. The audit qualifies inputs. A separate protocol will freeze the graph representation, temporally matched controls and later-date evaluation before inspecting later-date prices or model scores.
