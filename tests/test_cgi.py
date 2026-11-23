import numpy as np,pandas as pd
from src.cgi import CGI,BASE,GRAPH

def sample():
    r=np.random.default_rng(1);i=pd.date_range('2018-01-01',periods=1100,freq='D',tz='UTC')
    f=pd.DataFrame(r.normal(size=(len(i),len(BASE+GRAPH))),index=i,columns=BASE+GRAPH)
    f['target']=f.lag1+.1*r.normal(size=len(i));f['target_time']=i+pd.Timedelta(hours=1);return f

def test_zero_weight():
    f=sample();m=CGI().fit(f.iloc[:900]);t=f.iloc[900:]
    np.testing.assert_array_equal(m.predict(t,0),m.base.predict(t[BASE].to_numpy()))

def test_future_labels():
    f=sample();m=CGI().fit(f.iloc[:900]);t=f.iloc[900:].copy();p=m.predict(t);t.target=1e9
    np.testing.assert_array_equal(p,m.predict(t))
    assert all(pd.Timestamp(x['label_max']).year<x['validation_year'] for x in m.fold_audit)

def test_empty_graph():
    f=sample();f[GRAPH]=0.;m=CGI().fit(f.iloc[:900]);assert np.isfinite(m.predict(f.iloc[900:])).all()
