"""Qualify a bounded development sample from the pinned raw minute bars."""

import argparse
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from scripts.assets import MANIFEST, choose, configure_tls, load_manifest, verify_file

NY = ZoneInfo("America/New_York")
DAYS = tuple(date(2024, 1, day) for day in range(8, 13))
MINUTE = timedelta(minutes=1)
COLUMNS = ["ticker", "timestamp", "close"]
PILOT_SYMBOLS = ("SPY", "AAPL", "AMZN", "JNJ", "JPM", "MSFT", "NVDA", "PG", "WMT", "XOM")


def data_disk(path):
    resolved = path.resolve(strict=True)
    if not re.match(r"^/(data|date)\d*/", str(resolved)):
        raise ValueError(f"Expected a project path on a data disk: {resolved}")
    return resolved


def coverage_metadata(parquet):
    names = parquet.schema_arrow.names
    time_column = names.index("timestamp")
    ticker_column = names.index("ticker")
    starts, ends, spy_starts, spy_ends = [], [], [], []
    later = {}
    for year in (2025, 2026):
        later[year] = {"row_groups_overlapping_year": 0, "spy_only_groups_overlapping_year": 0}
    for i in range(parquet.num_row_groups):
        group = parquet.metadata.row_group(i)
        ts = group.column(time_column).statistics
        symbols = group.column(ticker_column).statistics
        if ts is None or not ts.has_min_max:
            continue
        lo, hi = ts.min, ts.max
        starts.append(lo)
        ends.append(hi)
        spy_only = symbols is not None and symbols.has_min_max and symbols.min == symbols.max == "SPY"
        if spy_only:
            spy_starts.append(lo)
            spy_ends.append(hi)
        for year, counts in later.items():
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            if hi >= start and lo < end:
                counts["row_groups_overlapping_year"] += 1
                counts["spy_only_groups_overlapping_year"] += int(spy_only)
    return {
        "rows": parquet.metadata.num_rows,
        "row_groups": parquet.num_row_groups,
        "groups_with_time_bounds": len(starts),
        "first_utc": min(starts).isoformat(),
        "last_utc": max(ends).isoformat(),
        "spy_only_group_first_utc": min(spy_starts).isoformat() if spy_starts else None,
        "spy_only_group_last_utc": max(spy_ends).isoformat() if spy_ends else None,
        "later_year_metadata": later,
    }


def sample_bounds():
    start = datetime.combine(DAYS[0], time(9, 30), NY).astimezone(timezone.utc)
    end = datetime.combine(DAYS[-1], time(16), NY).astimezone(timezone.utc)
    return start, end


def sample_bars(source):
    start, end = sample_bounds()
    stamp = ds.field("timestamp")
    table = ds.dataset(source, format="parquet").to_table(
        columns=COLUMNS,
        filter=(stamp >= start) & (stamp < end),
        use_threads=False,
    )
    return clean_sample(table)


def clean_sample(table):
    bars = table.to_pandas()
    eastern = bars["timestamp"].dt.tz_convert(NY)
    minute_of_day = eastern.dt.hour * 60 + eastern.dt.minute
    bars = bars.loc[eastern.dt.date.isin(DAYS) & (minute_of_day >= 570) & (minute_of_day < 960)].copy()
    if not bars["timestamp"].eq(bars["timestamp"].dt.floor("min")).all():
        raise ValueError("Off-minute timestamp in development sample")
    bad = bars["ticker"].isna() | ~np.isfinite(bars["close"]) | (bars["close"] <= 0)
    duplicates = bars.duplicated(["timestamp", "ticker"], keep=False)
    clean = bars.loc[~(bad | duplicates)]
    prices = clean.pivot(index="timestamp", columns="ticker", values="close").sort_index()
    return prices, {
        "regular_session_rows": len(bars),
        "invalid_rows": int(bad.sum()),
        "rows_with_duplicate_keys": int(duplicates.sum()),
        "retained_rows": len(clean),
        "observed_symbols": len(prices.columns),
    }


def bounded_hf_sample(asset, file):
    from huggingface_hub import HfFileSystem

    configure_tls()
    start, end = sample_bounds()
    uri = f"datasets/{asset['repo_id']}@{asset['revision']}/{file['path']}"
    fs = HfFileSystem()
    with fs.open(uri, "rb", block_size=1024**2, cache_type="none") as handle:
        pq_file = pq.ParquetFile(handle)
        if str(pq_file.schema_arrow.field("timestamp").type) != "timestamp[ms, tz=UTC]":
            raise ValueError("Unexpected timestamp schema")
        coverage = coverage_metadata(pq_file)
        names = pq_file.schema_arrow.names
        indexes = {name: names.index(name) for name in COLUMNS}
        selected, compressed = [], 0
        for i in range(pq_file.num_row_groups):
            group = pq_file.metadata.row_group(i)
            ts = group.column(indexes["timestamp"]).statistics
            sym = group.column(indexes["ticker"]).statistics
            if not ts or not ts.has_min_max or not sym or not sym.has_min_max:
                continue
            if ts.max < start or ts.min >= end:
                continue
            if any(sym.min <= ticker <= sym.max for ticker in PILOT_SYMBOLS):
                selected.append(i)
                compressed += sum(group.column(j).total_compressed_size for j in indexes.values())
        if not selected or len(selected) > 40 or compressed > 64 * 1024**2:
            raise ValueError("Pilot row group request outside the declared read budget")
        tables = []
        for i in selected:
            table = pq_file.read_row_group(i, columns=COLUMNS, use_threads=False)
            allowed = pyarrow.array(PILOT_SYMBOLS, type=table.schema.field("ticker").type)
            stamps = table["timestamp"]
            keep = pc.and_(
                pc.is_in(table["ticker"], value_set=allowed),
                pc.and_(pc.greater_equal(stamps, start), pc.less(stamps, end)),
            )
            tables.append(table.filter(keep))
    prices, sample = clean_sample(pyarrow.concat_tables(tables))
    sample.update({
        "requested_symbols": list(PILOT_SYMBOLS),
        "selected_row_groups": len(selected),
        "projected_column_compressed_bytes": compressed,
    })
    return coverage, prices, sample


def hourly_rows(prices):
    rows = []
    for day in DAYS:
        for hour in range(11, 16):
            cutoff = datetime.combine(day, time(hour), NY).astimezone(timezone.utc)
            feature_start, feature_end = cutoff - 62 * MINUTE, cutoff - 2 * MINUTE
            label_minutes = pd.date_range(cutoff - MINUTE, periods=61, freq="min")
            endpoint = prices.reindex([feature_start, feature_end]).drop(columns=["SPY"], errors="ignore")
            node_returns = np.log(endpoint.iloc[-1]) - np.log(endpoint.iloc[0])
            spy = prices.get("SPY", pd.Series(dtype=float, index=prices.index))
            label_path = spy.reindex(label_minutes)
            missing = int(label_path.isna().sum())
            variance = None if missing else float(np.square(np.diff(np.log(label_path.to_numpy()))).sum())
            rows.append({
                "decision_utc": cutoff.isoformat(),
                "feature_price_bar_start_utc": feature_start.isoformat(),
                "feature_price_bar_end_utc": feature_end.isoformat(),
                "last_feature_bar_closed_utc": (feature_end + MINUTE).isoformat(),
                "target_end_utc": (cutoff + 60 * MINUTE).isoformat(),
                "eligible_nodes": int(node_returns.notna().sum()),
                "missing_spy_bars": missing,
                "target_available": variance is not None and bool(np.isfinite(variance)),
            })
    return rows


def main():
    args = argparse.ArgumentParser(description=__doc__)
    source_args = args.add_mutually_exclusive_group(required=True)
    source_args.add_argument("--raw", type=Path)
    source_args.add_argument("--bounded-hf", action="store_true")
    args.add_argument("--out", required=True, type=Path)
    options = args.parse_args()
    out = data_disk(options.out)
    progress = out / "progress.txt"
    manifest = load_manifest(MANIFEST)
    asset, files = choose(manifest, "raw-minute-bars")
    if len(files) != 1:
        raise ValueError("Expected one pinned raw minute-bar file")
    if options.bounded_hf:
        progress.write_text("Reading the pinned HF pilot slice\n")
        coverage, prices, sample = bounded_hf_sample(asset, files[0])
        whole_file_verified = False
    else:
        source = data_disk(options.raw)
        progress.write_text("Verifying the pinned raw file\n")
        verify_file(source, files[0])
        parquet = pq.ParquetFile(source)
        if str(parquet.schema_arrow.field("timestamp").type) != "timestamp[ms, tz=UTC]":
            raise ValueError("Unexpected timestamp schema")
        coverage = coverage_metadata(parquet)
        with progress.open("a") as log:
            log.write("Scanning the five 2024 development sessions\n")
        prices, sample = sample_bars(source)
        whole_file_verified = True
    rows = hourly_rows(prices)
    valid = sum(r["target_available"] and r["eligible_nodes"] > 0 for r in rows)
    report = {
        "status": "qualified-development-input" if valid == len(rows) else "coverage-issues",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source": {
            "repo_id": asset["repo_id"], "revision": asset["revision"], "path": files[0]["path"],
            "bytes": files[0]["bytes"], "sha256": files[0]["sha256"], "whole_file_verified": whole_file_verified,
        },
        "versions": {"pyarrow": pyarrow.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        "coverage": coverage,
        "sample": {
            **sample, "sessions": [day.isoformat() for day in DAYS], "timezone": str(NY),
            "candidate_forecasts": len(rows), "valid_forecasts": valid, "hourly_checks": rows,
        },
        "limits": [
            "Archived bars do not record the arrival time of late trade corrections.",
            "Causal membership within this archive does not establish an unbiased source universe.",
            "Later-year row-group bounds do not establish exact coverage or a valid held-out panel.",
        ],
    }
    (out / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
    with progress.open("a") as log:
        log.write(f"Audit finished: {valid}/{len(rows)} usable pilot decisions\n")


if __name__ == "__main__":
    main()
