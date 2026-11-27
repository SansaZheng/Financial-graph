"""Diagnose graph covariates and test an anchored residual correction on frozen rows."""

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.assets import digest
from src.intraday_compare import CONTEXT, CANDIDATE, CONTROLS, EVAL_YEARS, learner, mse
from src.intraday_compare import diffusion_inputs, graph_features, make_features, paired_interval, transition
from src.intraday_panel import SYMBOLS, TEMPORAL, legacy_labels

BASE = CONTROLS["node"]
WEIGHTS = (0., .25, .5, 1.)
REFERENCE = Path(__file__).resolve().parents[1] / "reports/intraday-matched"


def exact_null_energy(weights, shock):
    """Average diffusion energy over independent uniform permutations within strength bins."""
    mean = np.zeros(len(shock))
    variance = np.zeros(len(shock))
    transport = transition(weights)
    strength_order = np.argsort(weights.sum(axis=1), kind="stable")
    for group in np.array_split(strength_order, 3):
        values = shock[group]
        shares = transport[:, group]
        mean += shares.sum(axis=1) * values.mean()
        if len(group) > 1:
            centered = shares - shares.mean(axis=1, keepdims=True)
            variance += values.var() * len(group) / (len(group) - 1) * np.square(centered).sum(axis=1)
    return float(np.mean(np.square(mean) + variance))


def diagnostic_features(history, current, rng):
    record = graph_features(history, current, rng)
    weights, shock = diffusion_inputs(history, current)
    record["exact_energy"] = record["raw_energy"] - exact_null_energy(weights, shock)
    return record


def load_frozen_inputs(panel_dir, reference_predictions):
    labels, source = legacy_labels(panel_dir / "forecast_data.csv")
    audit = json.loads((REFERENCE / "panel-audit.json").read_text())
    selection = json.loads((REFERENCE / "selection.json").read_text())
    official = json.loads((REFERENCE / "verification.json").read_text())
    receipts = {f["path"]: f["sha256"] for f in official["output_receipts"]}
    panel_file = panel_dir / "node-returns.parquet"
    if source != audit["labels"] or digest(panel_file) != audit["panel_sha256"]:
        raise ValueError("Panel and label must match the archived study")
    if digest(reference_predictions) != receipts["predictions.csv"] or digest(REFERENCE / "selection.json") != receipts["selection.json"]:
        raise ValueError("Original predictions or model selection changed")
    panel = pd.read_parquet(panel_file)
    if list(panel.columns) != list(SYMBOLS) or not panel.index.equals(labels.index):
        raise ValueError("Unexpected node panel or time index")
    archived = pd.read_csv(reference_predictions, float_precision="round_trip")
    archived.index = pd.DatetimeIndex(pd.to_datetime(archived.pop("decision"), utc=True), name="decision")
    frame = labels.join(make_features(panel, diagnostic_features), how="inner", validate="one_to_one")
    test = frame.loc[frame.index.year.isin(EVAL_YEARS)]
    if not test.index.equals(archived.index) or len(test) != 2912 or not np.array_equal(test.target, archived.target):
        raise ValueError("Matched row or target mismatch")
    if not (frame.graph_history_end < frame.index).all():
        raise ValueError("Graph history must end before forecast")
    return frame, archived, selection, audit, receipts["predictions.csv"]


def year_splits(frame, archived, selections, year):
    train = frame.loc[frame.index.year < year - 1]
    valid = frame.loc[frame.index.year == year - 1]
    test = frame.loc[frame.index.year == year]
    ref = archived.loc[test.index]
    old = selections[str(year)]
    if old["strongest"] != "node" or not ref.strong_control_name.eq("node").all():
        raise ValueError("Expected the frozen node-only control")
    if not np.array_equal(ref.strong_control, ref.node):
        raise ValueError("Previous strongest prediction differs from node prediction")
    if [len(train), len(valid), len(test)] != [old[key] for key in ("train_rows", "validation_rows", "test_rows")]:
        raise ValueError(f"Archived fold counts changed for {year}")
    if not (train.target_time.max() < valid.index.min() and valid.target_time.max() < test.index.min()):
        raise ValueError(f"Outcome overlap in {year}")
    return train, valid, test, ref, old["models"]["node"]["config"]


def feature_mse(train, test, columns, config):
    model = learner(config).fit(train[columns], train.target)
    return mse(test.target, model.predict(test[columns]))


def excess_covariate_model(train):
    return make_pipeline(StandardScaler(), LinearRegression()).fit(train[BASE], train.exact_energy)


def diagnosis(frame, archived, selections, audit, pred_sha):
    def decomposition(rows):
        node, density, graph = (mse(rows.target, rows[name]) for name in ("node", "density", "graph"))
        return {
            "node_mse": node, "density_mse": density, "graph_mse": graph,
            "density_minus_node": density - node, "graph_minus_density": graph - density,
            "graph_minus_node": graph - node,
        }

    yearly = {}
    for year in EVAL_YEARS:
        train, valid, test, ref, config = year_splits(frame, archived, selections, year)
        fit = pd.concat([train, valid])
        fixed = {name: feature_mse(fit, test, cols, config) for name, cols in (
            ("node", BASE), ("density", TEMPORAL + CONTEXT), ("graph", CANDIDATE),
            ("node_plus_graph_without_density", BASE + ["excess_energy"]),
        )}
        np.testing.assert_allclose(fixed["node"], mse(ref.target, ref.node), rtol=0, atol=1e-11)
        residual = valid.target - learner(config).fit(train[BASE], train.target).predict(valid[BASE])
        exact = valid.exact_energy
        orthogonal = exact - excess_covariate_model(train).predict(valid[BASE])
        coefficient = np.corrcoef(residual, orthogonal)[0, 1]
        yearly[str(year)] = {
            "archived": decomposition(ref), "fixed_node_config": config, "fixed_penalty_mse": fixed,
            "fixed_penalty_density_minus_node": fixed["density"] - fixed["node"],
            "fixed_penalty_graph_minus_density": fixed["graph"] - fixed["density"],
            "test_mc_null_error_rmse": float(np.sqrt(mse(test.excess_energy, test.exact_energy))),
            "test_exact_surplus_sd": float(test.exact_energy.std()),
            "validation_year": year - 1,
            "validation_residual_correlation": float(coefficient) if np.isfinite(coefficient) else None,
        }
    overall = decomposition(archived)
    overall["density_share_of_archived_gap"] = overall["density_minus_node"] / overall["graph_minus_node"]
    return {
        "status": "complete", "rows": len(archived), "panel_sha256": audit["panel_sha256"],
        "reference_predictions_sha256": pred_sha, "archived_pooled": overall, "per_year": yearly,
        "interpretation": "Controlled feature-set test with a fixed ridge penalty, not causal identification of market mechanisms.",
    }


class GraphCorrection:
    def __init__(self, train, config):
        self.base = learner(config).fit(train[BASE], train.target)
        self.nuisance = excess_covariate_model(train)
        scores = train.exact_energy - self.nuisance.predict(train[BASE])
        self.scale = max(float(scores.std(ddof=0)), 1e-12)
        z = scores.to_numpy() / self.scale
        errors = train.target.to_numpy() - self.baseline(train)
        self.slope = float((z @ errors) / (z @ z + 0.25 * len(z)))

    def baseline(self, data):
        return self.base.predict(data[BASE])

    def correction(self, data):
        unexplained = data.exact_energy.to_numpy() - self.nuisance.predict(data[BASE])
        return (self.slope / self.scale) * unexplained


def corrected_predictions(frame, archived, selections):
    predictions, choices = [], {}
    for year in EVAL_YEARS:
        train, valid, test, ref, config = year_splits(frame, archived, selections, year)
        train_model = GraphCorrection(train, config)
        baseline = train_model.baseline(valid)
        validation_correction = train_model.correction(valid)
        scores = {weight: mse(valid.target, baseline + weight * validation_correction) for weight in WEIGHTS}
        expected = selections[str(year)]["models"]["node"]["validation_mse"]
        np.testing.assert_allclose(scores[0.], expected, rtol=0, atol=1e-11)
        weight = min(WEIGHTS, key=scores.get)
        fit_model = GraphCorrection(pd.concat([train, valid]), config)
        np.testing.assert_allclose(fit_model.baseline(test), ref.strong_control, rtol=0, atol=1e-9)
        part = ref[["target", "strong_control", "graph"]].rename(columns={"graph": "old_graph"}).copy()
        part["full_correction"] = part.strong_control + fit_model.correction(test)
        part["corrected_graph"] = part.strong_control + weight * fit_model.correction(test)
        choices[str(year)] = {
            "validation_year": year - 1, "baseline_config": config, "weight": weight,
            "validation_mse_by_weight": scores, "refit_slope": fit_model.slope, "test_rows": len(test),
        }
        predictions.append(part)
    return pd.concat(predictions), choices


def comparisons(predictions):
    def losses(table):
        return {k: mse(table.target, table[k]) for k in table.columns if k != "target"}

    scores = losses(predictions)
    baseline = np.square(predictions.target - predictions.strong_control)
    delta = baseline - np.square(predictions.target - predictions.corrected_graph)
    intervals = [paired_interval(delta, length) for length in (5, 10, 20)]
    return {
        "pooled_mse": scores,
        "per_year_mse": {str(k): losses(rows) for k, rows in predictions.groupby(predictions.index.year)},
        "mse_reduction_pct": 100 * (1 - scores["corrected_graph"] / scores["strong_control"]),
        "paired_vs_strong": intervals[0], "block_length_sensitivity": intervals[1:],
        "significant_mse_reduction_at_95pct": intervals[0]["ci95"][0] > 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--reference-predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    frame, archived, selections, audit, pred_sha = load_frozen_inputs(args.panel_dir, args.reference_predictions)
    reason = diagnosis(frame, archived, selections, audit, pred_sha)
    (args.out / "diagnosis.json").write_text(json.dumps(reason, indent=2) + "\n")
    print("Fixed-penalty and archived diagnoses written", flush=True)
    predictions, weights = corrected_predictions(frame, archived, selections)
    if not predictions.index.equals(archived.index) or not np.isfinite(predictions.to_numpy()).all():
        raise ValueError("Corrected graph changed the matched comparison sample")
    output = args.out / "predictions.csv"
    predictions.to_csv(output, float_format="%.17g")
    (args.out / "selection.json").write_text(json.dumps(weights, indent=2) + "\n")
    summary = {
        "status": "complete", "protocol": "006-intraday-residual", "rows": len(predictions),
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "panel_sha256": audit["panel_sha256"], "reference_predictions_sha256": pred_sha,
        "predictions_sha256": digest(output), **comparisons(predictions),
        "evidence_scope": "Historical development comparison designed after observing study 005",
    }
    (args.out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Frozen-control paired comparison complete", flush=True)


if __name__ == "__main__":
    main()
