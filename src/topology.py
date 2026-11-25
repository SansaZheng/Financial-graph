"""Previous-session factor-residual graph contrasts; no causal identification."""
import numpy as np
import pandas as pd

CONTEXT = ['market_return', 'market_var', 'shock_energy', 'shock_downside',
           'shock_dispersion', 'residual_density', 'mean_weight', 'strength_cv']
RAW = [f'raw_{kind}_{h}' for kind in ['signed', 'down'] for h in [1, 2, 3]]
NTD = [s.replace('raw_', 'ntd_') for s in RAW]
NULL = [s.replace('raw_', 'null_') for s in RAW]
PLACEBO = [s.replace('raw_', 'placebo_') for s in RAW]


def permutation_mean(operator, centered_signal):
    """Exact E[q_perm.T @ operator @ q_perm / n] under uniform permutation."""
    q=np.asarray(centered_signal); n=len(q)
    if abs(q.mean())>1e-8: raise ValueError('signal must be centered')
    return float(np.mean(q*q)*(n*np.trace(operator)-operator.sum())/(n*(n-1)))


def graph_snapshot(history, shock, seed=471, permutations=32):
    """Graph fit excludes shock day; null permutes shocks on the fixed graph.

    The null preserves the entire graph and shock distribution, but removes node
    alignment. It is NOT degree-conditioned or a degree-preserving edge rewire.
    """
    hist = np.asarray(history, float)
    market = hist.mean(axis=1)
    centered = hist - hist.mean(axis=0)
    m = market - market.mean()
    beta = (m @ centered) / max(m @ m, 1e-12)
    residual = centered - m[:, None] * beta
    scale = np.maximum(residual.std(axis=0), 1e-6)
    e = np.clip((shock - hist.mean(axis=0) - beta * (shock.mean()-market.mean())) / scale, -8, 8)
    standardized = residual / scale
    corr = standardized.T @ standardized / len(residual)
    w = np.maximum(corr, 0.); np.fill_diagonal(w, 0.)
    n = len(e)
    # Threshold fixed before outcomes; density is itself supplied to controls.
    w[w < .25] = 0.
    degree = w.sum(axis=1)
    inv = 1 / np.sqrt(np.maximum(degree, 1e-12))
    op = inv[:, None] * w * inv[None, :]
    powers=[op, op @ op]
    powers.append(powers[-1] @ op)
    rng = np.random.default_rng(seed)
    perm = np.array([rng.permutation(n) for _ in range(permutations)])
    out = dict(zip(CONTEXT, [shock.mean(), market.var(), np.mean(e**2),
                            np.mean(np.minimum(e, 0)**2), np.std(e),
                            np.count_nonzero(w)/(n*(n-1)), w.mean(),
                            degree.std()/max(degree.mean(), 1e-8)]))
    for kind, q in [('signed', e), ('down', np.minimum(e, 0)**2)]:
        q = q - q.mean()
        signals = np.column_stack([q, q[perm].T])
        propagated = signals.copy()
        for h in [1, 2, 3]:
            propagated = op @ propagated
            energies = np.mean(signals * propagated, axis=0)
            mu = permutation_mean(powers[h-1], q); sd = max(energies[1:].std(ddof=1), 1e-6)
            out[f'raw_{kind}_{h}'] = energies[0]
            out[f'null_{kind}_{h}'] = mu
            out[f'ntd_{kind}_{h}'] = np.clip((energies[0]-mu)/sd, -10, 10)
            placebo_mu = mu; placebo_sd = max(energies[2:].std(ddof=1), 1e-6)
            out[f'placebo_{kind}_{h}'] = np.clip((energies[1]-placebo_mu)/placebo_sd, -10, 10)
    return out


def build_features(daily, window=60, seed=471, progress=None):
    if daily.index.has_duplicates or not daily.index.is_monotonic_increasing:
        raise ValueError('daily index must be unique and increasing')
    rows = []
    for j in range(window, len(daily)):
        history=daily.iloc[j-window:j].to_numpy(); shock=daily.iloc[j].to_numpy()
        valid=np.isfinite(history).all(axis=0) & np.isfinite(shock)
        if valid.sum()<20: raise ValueError('fewer than 20 eligible past-window nodes')
        row = graph_snapshot(history[:,valid], shock[valid], seed=seed)
        row['graph_node_count']=int(valid.sum())
        row['graph_excluded_nodes']='|'.join(daily.columns[~valid].astype(str))
        row.update(source_day=str(daily.index[j].date()), graph_fit_end=str(daily.index[j-1].date()))
        rows.append(row)
        if progress and j % 100 == 0: progress(f'{j}/{len(daily)} graph features')
    return pd.DataFrame(rows)


def attach_features(frame, features):
    """Strict backward date join prevents using any same-session daily close."""
    left = pd.DataFrame({'forecast_day':pd.to_datetime(frame.index.date), 'row':np.arange(len(frame))})
    right = features.copy(); right['source_day'] = pd.to_datetime(right.source_day)
    merged = pd.merge_asof(left, right.sort_values('source_day'), left_on='forecast_day',
                           right_on='source_day', direction='backward', allow_exact_matches=False)
    good = merged.source_day.notna().to_numpy()
    out = frame.iloc[np.flatnonzero(good)].copy()
    for c in features.columns: out[c] = merged.loc[good,c].to_numpy()
    if not (pd.to_datetime(out.source_day).dt.date.to_numpy() < out.index.date).all():
        raise AssertionError('same-day graph leakage')
    return out
