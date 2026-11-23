"""Predeclared rolling-origin development only: old holdout is consumed."""
import argparse,hashlib,json,os,platform,time
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.ensemble import HistGradientBoostingRegressor
from src.cgi import CGI,BASE,GRAPH,ridge

def load(path):
    f=pd.read_csv(path);f.index=pd.to_datetime(f.pop('time'),utc=True).dt.tz_convert('America/New_York')
    f['target_time']=pd.to_datetime(f.target_time,utc=True).dt.tz_convert('America/New_York')
    if not f.index.is_monotonic_increasing or f.index.has_duplicates:raise ValueError('index')
    if not ((f.target_time-f.index)==pd.Timedelta(hours=1)).all():raise ValueError('horizon')
    if not (f.target_time.dt.date==f.index.date).all():raise ValueError('overnight')
    if not np.isfinite(f[BASE+GRAPH+['target']].to_numpy()).all():raise ValueError('nonfinite')
    return f[f.index.year>=2018]

def interval(delta,dates,seed=471,draws=2000):
    v=pd.Series(np.asarray(delta),index=dates).groupby(level=0).mean().to_numpy();n=len(v);block=min(5,n)
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(draws):
        starts=rng.integers(0,n-block+1,size=int(np.ceil(n/block)));ix=np.concatenate([np.arange(s,s+block) for s in starts])[:n];vals.append(v[ix].mean())
    return {'mean_daily_gain':float(v.mean()),'ci95':np.quantile(vals,[.025,.975]).tolist(),'sessions':n}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--out',default=os.environ.get('CQ_OUTPUT_DIR'));ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    if not a.out:raise ValueError('out required')
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);start=time.time();f=load(a.data)
    years=[2022] if a.smoke else [2022,2023,2024];preds=[];choices={}
    def log(s):
        with (out/'progress.txt').open('a') as h:h.write(s+'\n')
        print(s,flush=True)
    for k,year in enumerate(years):
        train=f[f.index.year<year-1];valid=f[f.index.year==year-1];test=f[f.index.year==year]
        assert train.target_time.max()<valid.index.min() and valid.target_time.max()<test.index.min()
        models={};scores={}
        for alpha in [1.,10.,100.]:
            for name,cols in [('seasonal',BASE[:-2]),('density',BASE),('direct_graph',BASE+GRAPH)]:
                m=ridge(alpha).fit(train[cols],train.target);key=f'{name}_{alpha:g}';models[key]=(m,cols);scores[key]=float(mean_squared_error(valid.target,m.predict(valid[cols])))
        for name,cols in [('nonlinear_control',BASE),('nonlinear_graph',BASE+GRAPH)]:
            for leaves in [7,15]:
                m=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=leaves,l2_regularization=10,early_stopping=False,random_state=0).fit(train[cols],train.target)
                key=f'{name}_{leaves}';models[key]=(m,cols);scores[key]=float(mean_squared_error(valid.target,m.predict(valid[cols])))
        control=min([n for n in models if n.startswith(('seasonal_','density_','nonlinear_control_'))],key=scores.get)
        density=min([n for n in models if n.startswith('density_')],key=scores.get)
        direct=min([n for n in models if n.startswith(('direct_graph_','nonlinear_graph_'))],key=scores.get)
        candidates=[]
        for orth in [True,False]:
            for alpha in [1.,10.,100.]:
                model=CGI(alpha,orth).fit(train);b,c=model.predict_components(valid)
                for w in [0.,.25,.5,1.]:
                    p=b+w*c;ci=interval((valid.target.to_numpy()-b)**2-(valid.target.to_numpy()-p)**2,valid.index.date,draws=200)
                    candidates.append({'alpha':alpha,'orthogonal':orth,'weight':w,'mse':float(mean_squared_error(valid.target,p)),'gain_ci':ci})
        pick=min([r for r in candidates if r['orthogonal']],key=lambda r:r['mse']);abl=min([r for r in candidates if not r['orthogonal']],key=lambda r:r['mse'])
        gate=bool(pick['mse']<scores[control] and pick['gain_ci']['ci95'][0]>0)
        choices[str(year)]={'control':control,'density':density,'direct':direct,'cgi':pick,'ablation':abl,'gate':gate,'validation_scores':scores,'cgi_search':candidates}
        (out/'selection.json').write_text(json.dumps(choices,indent=2))
        fit=pd.concat([train,valid]);p=pd.DataFrame({'target':test.target})
        for label,key in [('strong_control',control),('density_control',density),('direct_graph',direct)]:
            m,cols=models[key];m.fit(fit[cols],fit.target);p[label]=m.predict(test[cols])
        for label,conf in [('cgi',pick),('no_orthogonalization',abl)]:
            model=CGI(conf['alpha'],conf['orthogonal']).fit(fit);p[label]=model.predict(test,conf['weight'])
            (out/f'fold_audit_{year}_{label}.json').write_text(json.dumps(model.fold_audit,indent=2))
        p['gated_cgi']=p.cgi if gate else p.strong_control
        preds.append(p);pd.concat(preds).to_csv(out/'predictions.csv');log(f'{k+1}/{len(years)} year={year}')
    p=pd.concat(preds);metrics={n:{'mse':float(mean_squared_error(p.target,p[n])),'r2':float(r2_score(p.target,p[n]))} for n in p if n!='target'}
    comparisons={}
    for m in ['cgi','gated_cgi','direct_graph','no_orthogonalization']:
        for c in ['strong_control','density_control']:comparisons[m+'_vs_'+c]=interval((p.target-p[c])**2-(p.target-p[m])**2,p.index.date)
    import resource
    report={'status':'complete','evidence_type':'development_only_previously_observed_2018_2024','metrics':metrics,'paired_intervals':comparisons,'rows':len(p),'years':years,'elapsed_seconds':time.time()-start,'peak_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'input_sha256':hashlib.sha256(Path(a.data).read_bytes()).hexdigest(),'python':platform.python_version(),'limitations':['Not untouched confirmation','Aggregate daily graph scores only','Intervals exploratory without multiplicity correction','Novelty and CCF A quality not established']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2));log(f'{len(years)}/{len(years)} complete')
if __name__=='__main__':main()
