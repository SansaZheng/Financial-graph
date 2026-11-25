import numpy as np
import pandas as pd
from src.ntd_evaluate import X, transform, design, metrics
from src.cgi import ridge
from src.topology import NTD


def test_prediction_design_ignores_future_target():
    rng=np.random.default_rng(42)
    frame=pd.DataFrame(rng.normal(size=(50,len(X+NTD))),columns=X+NTD)
    frame['target']=rng.normal(size=50)
    model=ridge().fit(frame[X],frame[NTD]);a=transform(frame,model,NTD)
    frame.target=1e10;b=transform(frame,model,NTD)
    np.testing.assert_array_equal(design(a,NTD,np.zeros(2),np.ones(2)),design(b,NTD,np.zeros(2),np.ones(2)))


def test_qlike_perfect_forecast():
    m=metrics(np.array([-3.,-2.,-1.]),np.array([-3.,-2.,-1.]))
    assert m['qlike']==0 and m['mse']==0
