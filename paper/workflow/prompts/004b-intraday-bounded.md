# 004b-intraday-bounded — local task specification

Configuration revision 1. Codex and CQ. Venue and research topic follow 004-intraday-audit.

While the full local scan waits for a CPU slot on c220, qualify a small panel on c225 from the pinned HF original. Fix the requested symbols to SPY, AAPL, AMZN, JNJ, JPM, MSFT, NVDA, PG, WMT and XOM only for this timing pilot. Use the same January 8–12, 2024 dates and hourly label definition as 004. Read three selected columns, at most 40 candidate row groups and 64 MiB of compressed projected columns. Report actual sample and timing coverage plus metadata bounds for later dates. Treat the range-read result as a timing pilot for a handpicked cohort. The full c220 audit separately verifies the raw-file checksum and unrestricted source coverage.
