import numpy as np
import pandas as pd
from src.topology import build_features, attach_features, graph_snapshot


def test_future_returns_cannot_change_past_features():
    rng=np.random.default_rng(71)
    daily=pd.DataFrame(rng.normal(size=(75,8)),index=pd.date_range('2020-01-01',periods=75))
    a=build_features(daily,window=20)
    daily.iloc[50:]*=100
    b=build_features(daily,window=20)
    pd.testing.assert_frame_equal(a.iloc[:30],b.iloc[:30])


def test_join_never_uses_current_close():
    f=pd.DataFrame(index=pd.date_range('2020-01-03',periods=2,tz='America/New_York')+pd.Timedelta(hours=11))
    x=pd.DataFrame({'source_day':['2020-01-02','2020-01-03','2020-01-04'],'marker':[2,3,4]})
    r=attach_features(f,x)
    assert r.marker.tolist()==[2,3]


def test_empty_network_has_zero_contrast():
    out=graph_snapshot(np.zeros((60,8)),np.zeros(8))
    assert all(np.isfinite(x) for x in out.values())
    assert all(v==0 for k,v in out.items() if k.startswith('ntd_'))


def test_exact_null_matches_exhaustive_permutations():
    from itertools import permutations
    from src.topology import permutation_mean
    rng=np.random.default_rng(1);m=rng.normal(size=(5,5));q=np.arange(5.)-2
    actual=np.mean([np.asarray(p)@m@np.asarray(p)/5 for p in permutations(q)])
    np.testing.assert_allclose(actual,permutation_mean(m,q),atol=1e-12)
