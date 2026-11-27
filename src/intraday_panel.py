"""Materialize the exact minute endpoints needed by the matched development experiment."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from pathlib import Path
import json

import numpy as np
import pandas as pd

from scripts.assets import MANIFEST, choose, configure_tls, digest, load_manifest, verify_file

SYMBOLS = ("AAPL", "AMZN", "JNJ", "JPM", "MSFT", "NVDA", "PG", "WMT", "XOM")
CLOCK = (11 * 60 + 31, 12 * 60 + 31, 13 * 60 + 31, 14 * 60 + 31)
NY = "America/New_York"
MINUTE = pd.Timedelta(minutes=1)
TEMPORAL = ["logrv", "downside", "slot", "lag1", "lag7", "lag6", "lag30", "shock"]


def legacy_labels(path):
    asset, _ = choose(load_manifest(MANIFEST), "derived-inputs")
    file = next(f for f in asset["files"] if f["path"] == "derived/forecast_data.csv")
    verify_file(path, file)
    frame = pd.read_csv(path)
    decisions = pd.to_datetime(frame.pop("time"), utc=True)
    frame.index = pd.DatetimeIndex(decisions, name="decision")
    frame["target_time"] = pd.to_datetime(frame["target_time"], utc=True)
    local = frame.index.tz_convert(NY)
    frame = frame.loc[
        np.isin(local.year, range(2018, 2025)) & np.isin(local.hour * 60 + local.minute, CLOCK)
        & (local.second == 0) & (local.microsecond == 0)
    ].copy()
    if frame.empty or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("Invalid matched decision index")
    if not ((frame["target_time"] - frame.index) == 60 * MINUTE).all():
        raise ValueError("Historical market label horizon is not exactly one hour")
    if not np.isfinite(frame[TEMPORAL + ["target"]].to_numpy()).all():
        raise ValueError("Non-finite historical baseline or target")
    return frame[TEMPORAL + ["target", "target_time"]], {
        "repo_id": asset["repo_id"], "revision": asset["revision"], "sha256": file["sha256"],
    }


def endpoints(decisions):
    return (decisions - 62 * MINUTE).union(decisions - 2 * MINUTE)


def select_groups(metadata, names, wanted):
    columns = ["timestamp", "ticker", "close"]
    indexes = {name: names.index(name) for name in columns}
    lo = wanted[0].to_pydatetime()
    hi = wanted[-1].to_pydatetime()
    selected = []
    projected_bytes = 0
    for i in range(metadata.num_row_groups):
        group = metadata.row_group(i)
        ts = group.column(indexes["timestamp"]).statistics
        symbols = group.column(indexes["ticker"]).statistics
        if ts is None or not ts.has_min_max or symbols is None or not symbols.has_min_max:
            raise ValueError(f"Required timestamp or ticker statistics absent in row group {i}")
        if ts.max >= lo and ts.min <= hi and any(symbols.min <= s <= symbols.max for s in SYMBOLS):
            selected.append(i)
            projected_bytes += sum(group.column(j).total_compressed_size for j in indexes.values())
    if not selected or projected_bytes > 256 * 1024**2:
        raise ValueError(f"Selected data outside the 256 MiB projection budget: {projected_bytes}")
    return selected, projected_bytes


def read_prices(wanted, raw, workers, progress):
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    asset, files = choose(load_manifest(MANIFEST), "raw-minute-bars")
    file = files[0]
    if raw is not None:
        verify_file(raw, file)
        open_source = lambda: nullcontext(raw)
    else:
        configure_tls()
        uri = f"datasets/{asset['repo_id']}@{asset['revision']}/{file['path']}"
        fs = HfFileSystem()
        open_source = lambda: fs.open(uri, "rb", block_size=1024**2, cache_type="none")
    with open_source() as source:
        parquet = pq.ParquetFile(source)
        metadata = parquet.metadata
        schema = parquet.schema_arrow
    if str(schema.field("timestamp").type) != "timestamp[ms, tz=UTC]":
        raise ValueError("Unexpected minute timestamp schema")
    selected, budget = select_groups(metadata, schema.names, wanted)
    progress(f"Selected {len(selected)} row groups, {budget:,} projected compressed bytes")
    times = pa.array(wanted, type=schema.field("timestamp").type)
    symbols = pa.array(SYMBOLS, type=schema.field("ticker").type)
    chunks = [selected[i::workers] for i in range(workers)]

    def scan(group_ids):
        kept = []
        with open_source() as source:
            parquet = pq.ParquetFile(source, metadata=metadata)
            for i in group_ids:
                table = parquet.read_row_group(i, columns=["timestamp", "ticker", "close"], use_threads=False)
                match = pc.and_(pc.is_in(table["timestamp"], value_set=times),
                                pc.is_in(table["ticker"], value_set=symbols))
                subset = table.filter(match)
                if subset.num_rows:
                    kept.append(subset)
        progress(f"Finished {len(group_ids)} selected row groups")
        return kept

    with ThreadPoolExecutor(max_workers=workers) as pool:
        tables = [table for chunk in pool.map(scan, chunks) for table in chunk]
    if not tables:
        raise ValueError("No requested rows found in the pinned raw archive")
    kept = pa.concat_tables(tables).to_pandas()
    dups = kept.duplicated(["timestamp", "ticker"], keep=False)
    invalid = ~np.isfinite(kept["close"]) | (kept["close"] <= 0)
    prices = kept.loc[~(dups | invalid)].pivot(index="timestamp", columns="ticker", values="close")
    prices = prices.reindex(columns=SYMBOLS)
    return prices, {
        "repo_id": asset["repo_id"], "revision": asset["revision"], "raw_expected_sha256": file["sha256"],
        "whole_file_sha256_verified": raw is not None,
        "projected_compressed_bytes": budget, "row_groups": len(selected), "endpoint_price_rows": len(kept),
        "duplicate_endpoint_rows": int(dups.sum()), "invalid_endpoint_rows": int(invalid.sum()),
    }


def node_returns(prices, decisions):
    end = prices.reindex(decisions - 2 * MINUTE).to_numpy()
    start = prices.reindex(decisions - 62 * MINUTE).to_numpy()
    return pd.DataFrame(np.log(end) - np.log(start), index=decisions, columns=SYMBOLS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--raw", type=Path)
    parser.add_argument("--workers", type=int, choices=range(1, 7), default=4)
    options = parser.parse_args()
    options.out.mkdir(parents=True, exist_ok=True)
    progress_file = options.out / "progress.txt"

    def progress(message):
        print(message, flush=True)
        with progress_file.open("a") as log:
            log.write(message + "\n")

    labels, label_source = legacy_labels(options.labels)
    prices, raw_source = read_prices(endpoints(labels.index), options.raw, options.workers, progress)
    returns = node_returns(prices, labels.index)
    complete = returns.notna().all(axis=1)
    counts = {str(year): {"candidates": int((returns.index.year == year).sum()),
                          "complete": int((complete & (returns.index.year == year)).sum())}
              for year in range(2018, 2025)}
    panel = options.out / "node-returns.parquet"
    returns.to_parquet(panel, engine="pyarrow")
    result = {
        "status": "built", "labels": label_source, "raw": raw_source,
        "counts_utc_year": counts, "symbols": SYMBOLS, "endpoint_utc_range": [str(prices.index.min()), str(prices.index.max())],
        "panel_sha256": digest(panel),
    }
    (options.out / "panel-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    progress("Done with the matched intraday panel")


if __name__ == "__main__":
    main()
