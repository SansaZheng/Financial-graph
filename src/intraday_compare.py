"""Compare conditional-null graph diffusion and matched controls on historical decisions."""

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.assets import digest
from src.intraday_panel import NY, SYMBOLS, TEMPORAL, legacy_labels

SEED = 471
WINDOW = 60
EVAL_YEARS = (2022, 2023, 2024)
NODE = ["return_mean", "return_energy", "return_dispersion", "return_downside"]
CONTEXT = NODE + ["graph_density", "graph_mean_weight"]
GRID = tuple(("ridge", alpha) for alpha in (1, 10, 100, 1000)) + tuple(
    ("histogram", leaves, rate) for leaves in (7, 15) for rate in (0.05, 0.1)
)
CONTROLS = {
    "temporal": TEMPORAL,
    "node": TEMPORAL + NODE,
    "density": TEMPORAL + CONTEXT,
    "raw_diffusion": TEMPORAL + CONTEXT + ["raw_energy"],
    "conditional_null": TEMPORAL + CONTEXT + ["null_energy"],
    "rewired": TEMPORAL + CONTEXT + ["rewired_energy"],
}
CANDIDATE = TEMPORAL + CONTEXT + ["excess_energy"]


def residual(values):
    return values - values.mean(axis=-1, keepdims=True)


def transition(weights):
    total = weights.sum(axis=1, keepdims=True)
    return np.divide(weights, total, out=np.zeros_like(weights), where=total > 0)


def diffusion_inputs(history, current):
    past = residual(history)
    center = past.mean(axis=0)
    scale = np.maximum(past.std(axis=0), 1e-8)
    centered = past - center
    norms = np.maximum(np.linalg.norm(centered, axis=0), 1e-8)
    correlation = np.abs((centered.T @ centered) / np.outer(norms, norms))
    np.fill_diagonal(correlation, 0)
    top = np.argsort(-correlation, axis=1, kind="stable")[:, :2]
    mask = np.zeros_like(correlation, dtype=bool)
    np.put_along_axis(mask, top, True, axis=1)
    weights = np.where(mask | mask.T, correlation, 0)

    shock = np.clip((residual(current) - center) / scale, -5, 5)
    return weights, shock


def graph_features(history, current, rng):
    weights, shock = diffusion_inputs(history, current)
    diff = transition(weights)
    raw = np.square(diff @ shock).mean()
    permutations = np.tile(np.arange(len(shock)), (128, 1))
    strength_order = np.argsort(weights.sum(axis=1), kind="stable")
    for group in np.array_split(strength_order, 3):
        permutations[:, group] = rng.permuted(permutations[:, group], axis=1)
    null = np.square(shock[permutations] @ diff.T).mean()
    rewired, swaps = rewire(weights, rng)
    return {
        "return_mean": current.mean(), "return_energy": np.square(current).mean(),
        "return_dispersion": current.std(), "return_downside": np.square(np.minimum(current, 0)).mean(),
        "graph_density": np.count_nonzero(weights) / (len(shock) * (len(shock) - 1)),
        "graph_mean_weight": weights.mean(), "raw_energy": raw, "null_energy": null,
        "excess_energy": raw - null, "rewired_energy": np.square(transition(rewired) @ shock).mean(),
        "rewire_swaps": swaps,
    }


def rewire(weights, rng):
    """Swap disjoint edges. Preserve binary node degrees and the edge-weight multiset."""
    matrix = weights.copy()
    edges = [tuple(edge) for edge in np.argwhere(np.triu(matrix, 1) > 0)]
    swaps = 0
    if len(edges) < 2:
        return matrix, swaps
    for _ in range(64):
        i, j = rng.choice(len(edges), 2, replace=False)
        a, b = edges[i]
        c, d = edges[j]
        if len({a, b, c, d}) != 4:
            continue
        if rng.integers(2):
            c, d = d, c
        if matrix[a, d] != 0 or matrix[b, c] != 0:
            continue
        first, second = matrix[a, b], matrix[c, d]
        matrix[a, b] = matrix[b, a] = matrix[c, d] = matrix[d, c] = 0
        matrix[a, d] = matrix[d, a] = first
        matrix[b, c] = matrix[c, b] = second
        edges[i], edges[j] = tuple(sorted((a, d))), tuple(sorted((b, c)))
        swaps += 1
        if swaps == 4:
            break
    return matrix, swaps


def make_features(panel, feature_function=graph_features):
    labels = panel.index.tz_convert(NY)
    slots = labels.hour * 60 + labels.minute
    features = []
    for _, rows in panel.groupby(slots):
        rows = rows.loc[np.isfinite(rows).all(axis=1)]
        values = rows.to_numpy()
        for i in range(WINDOW, len(rows)):
            decision = rows.index[i]
            epoch_minute = int(decision.timestamp() // 60)
            rng = np.random.default_rng(np.random.SeedSequence([SEED, epoch_minute]))
            record = feature_function(values[i - WINDOW:i], values[i], rng)
            record.update(decision=decision, graph_history_end=rows.index[i - 1])
            features.append(record)
    if not features:
        raise ValueError("Too few complete prior same-clock observations")
    return pd.DataFrame(features).set_index("decision").sort_index()


def learner(config):
    if config[0] == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=config[1]))
    return HistGradientBoostingRegressor(
        max_iter=100, max_leaf_nodes=config[1], learning_rate=config[2],
        l2_regularization=10, early_stopping=False, random_state=SEED,
    )


def mse(target, prediction):
    return float(np.mean(np.square(np.asarray(target) - np.asarray(prediction))))


def fit_comparison(frame, progress):
    families = {**CONTROLS, "graph": CANDIDATE}
    predictions, selected = [], {}
    for year in EVAL_YEARS:
        train = frame.loc[frame.index.year < year - 1]
        valid = frame.loc[frame.index.year == year - 1]
        test = frame.loc[frame.index.year == year]
        if min(len(train), len(valid), len(test)) < 100:
            raise ValueError(f"Too few common rows for the {year} split")
        if not (train.target_time.max() < valid.index.min() and valid.target_time.max() < test.index.min()):
            raise ValueError(f"Label overlap in {year}")
        train_valid = pd.concat([train, valid])
        result = test[["target"]].copy()
        choices = {}
        for model, cols in families.items():
            trials = []
            for config in GRID:
                trained = learner(config).fit(train[cols], train.target)
                trials.append((mse(valid.target, trained.predict(valid[cols])), config))
            loss, config = min(trials, key=lambda v: v[0])
            choices[model] = {"validation_mse": loss, "config": config}
            refit = learner(config).fit(train_valid[cols], train_valid.target)
            result[model] = refit.predict(test[cols])
        strongest = min(CONTROLS, key=lambda name: choices[name]["validation_mse"])
        result["strong_control"] = result[strongest]
        result["strong_control_name"] = strongest
        selected[str(year)] = {
            "train_rows": len(train), "validation_rows": len(valid), "test_rows": len(test),
            "strongest": strongest, "models": choices,
        }
        predictions.append(result)
        progress(f"Completed matched split {year}: {len(test)} test rows, control {strongest}")
    return pd.concat(predictions), selected


def paired_interval(loss_gain, block, draws=10000):
    """Resample complete trading-day blocks within each year, retaining hourly weighting."""
    daily = loss_gain.groupby(loss_gain.index.tz_convert(NY).normalize()).agg(["sum", "count"])
    rng = np.random.default_rng(SEED)
    numer = np.zeros(draws)
    denom = np.zeros(draws)
    for _, days in daily.groupby(daily.index.year):
        size = len(days)
        width = min(block, size)
        start = rng.integers(0, size - width + 1, size=(draws, (size + width - 1) // width))
        take = (start[:, :, None] + np.arange(width)[None, None, :]).reshape(draws, -1)[:, :size]
        numer += days["sum"].to_numpy()[take].sum(axis=1)
        denom += days["count"].to_numpy()[take].sum(axis=1)
    estimate = float(loss_gain.mean())
    resampled = numer / denom
    return {
        "block_trading_days": block, "draws": draws, "days": len(daily), "mse_gain": estimate,
        "ci95": np.quantile(resampled, (0.025, 0.975)).tolist(),
        "centered_bootstrap_p_two_sided": float(
            (1 + np.count_nonzero(np.abs(resampled - estimate) >= abs(estimate))) / (draws + 1)
        ),
    }


def summarize(predictions):
    def losses(table):
        return {name: mse(table.target, table[name]) for name in (*CONTROLS, "graph", "strong_control")}

    aggregate = losses(predictions)
    delta = (predictions.target - predictions.strong_control) ** 2 - (predictions.target - predictions.graph) ** 2
    inference = [paired_interval(delta, block) for block in (5, 10, 20)]
    return {
        "pooled_mse": aggregate, "per_year_mse": {str(k): losses(t) for k, t in predictions.groupby(predictions.index.year)},
        "graph_mse_reduction_pct": 100 * (1 - aggregate["graph"] / aggregate["strong_control"]),
        "paired_graph_vs_strong": inference[0], "block_length_sensitivity": inference[1:],
        "significant_mse_reduction_at_95pct": inference[0]["ci95"][0] > 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    options = parser.parse_args()
    options.out.mkdir(parents=True, exist_ok=True)

    def progress(message):
        print(message, flush=True)
        with (options.out / "progress.txt").open("a") as f:
            f.write(message + "\n")

    labels, label_source = legacy_labels(options.labels)
    audit = json.loads((options.panel_dir / "panel-audit.json").read_text())
    panel_path = options.panel_dir / "node-returns.parquet"
    if audit["status"] != "built" or digest(panel_path) != audit["panel_sha256"] or label_source != audit["labels"]:
        raise ValueError("Panel/label receipt does not match")
    panel = pd.read_parquet(panel_path)
    if list(panel.columns) != list(SYMBOLS) or not panel.index.equals(labels.index):
        raise ValueError("Panel does not match the frozen universe and decision clock")
    features = make_features(panel)
    if not (features.graph_history_end < features.index).all():
        raise ValueError("Graph fitting used a non-past row")
    frame = labels.join(features, how="inner", validate="one_to_one")
    if not np.isfinite(frame[CANDIDATE + ["rewired_energy", "target"]]).all().all():
        raise ValueError("Non-finite common-sample features")
    predictions, selections = fit_comparison(frame, progress)
    pred_path = options.out / "predictions.csv"
    predictions.to_csv(pred_path, float_format="%.17g")
    (options.out / "selection.json").write_text(json.dumps(selections, indent=2) + "\n")
    report = {
        "status": "complete", "protocol": "005-intraday-matched", "seed": SEED,
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "panel_sha256": audit["panel_sha256"], "label_source": label_source, "raw_source": audit["raw"],
        "rows": len(predictions), "rows_with_graph_features": len(frame),
        "rows_with_no_successful_rewire": int(frame.rewire_swaps.eq(0).sum()),
        "predictions_sha256": digest(pred_path),
        "versions": {"numpy": np.__version__, "pandas": pd.__version__, "sklearn": sklearn.__version__},
        **summarize(predictions),
        "limitations": [
            "2022–2024 are previously used development years, with three overlapping training prefixes.",
            "Nine fixed pilot equities do not constitute a point-in-time representation of the full market.",
            "The archived target and temporal covariates are pinned, but their original construction is not fully reconstructed.",
            "Block intervals condition on the validation decisions and cannot establish out-of-archive superiority.",
        ],
    }
    (options.out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    progress("Matched graph comparison and paired intervals complete")


if __name__ == "__main__":
    main()
