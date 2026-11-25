"""NTD-002: frozen rolling development evaluation, never untouched confirmation."""
import argparse, hashlib, json, os, platform, time, resource
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_squared_error, r2_score
from src.cgi import ridge, BASE
from src.evaluate import load, interval
from src.topology import build_features, attach_features, CONTEXT, RAW, NTD, NULL, PLACEBO

X = BASE[:-2] + CONTEXT
TEMP = ['lag1','lag7','lag30','shock','downside','slot']
FAMILIES = {'ntd':NTD,'raw_diffusion':RAW,'null_only':NULL,'placebo':PLACEBO,
            'temporal_residual':TEMP,'ntd_no_orth':NTD}
SPECS = [('ridge',a) for a in [1,10,100,1000]] + [('hgb',n) for n in [7,15,31]] + [('extra',n) for n in [10,30]]


def estimator(spec):
    kind, arg=spec
    if kind=='ridge': return ridge(arg)
    if kind=='hgb': return HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=arg,l2_regularization=10,early_stopping=False,random_state=471)
    return ExtraTreesRegressor(n_estimators=100,min_samples_leaf=arg,max_features=1.,n_jobs=2,random_state=471)


def search(train, valid, cols=X):
    scores={}; models={}
    for kind,arg in SPECS:
        key=f'{kind}_{arg}';m=estimator((kind,arg)).fit(train[cols],train.target)
        scores[key]=float(mean_squared_error(valid.target,m.predict(valid[cols])));models[key]=m
    key=min(scores,key=scores.get)
    return key, models, scores


def parsed(key):
    kind,arg=key.rsplit('_',1);return kind,int(arg)


def nested_base(f):
    years=sorted(set(f.index.year))
    if len(years)<2: key='ridge_10'
    else:
        tr=f[f.index.year<years[-1]];va=f[f.index.year==years[-1]]
        key,_,_=search(tr,va)
    return estimator(parsed(key)).fit(f[X],f.target),key


def oof(f):
    pieces=[];audit=[]
    cols=list(dict.fromkeys(RAW+NTD+NULL+PLACEBO))
    for year in sorted(set(f.index.year))[1:]:
        tr=f[f.index.year<year];va=f[f.index.year==year]
        if len(tr)<100 or len(va)<30:continue
        assert tr.target_time.max()<va.index.min()
        base,key=nested_base(tr);nuisance=ridge(10).fit(tr[X],tr[cols])
        z=va.copy();z['error']=va.target-base.predict(va[X])
        z.loc[:,cols]=va[cols].to_numpy()-nuisance.predict(va[X])
        for c in cols:z['unorth_'+c]=va[c]
        pieces.append(z)
        audit.append({'year':int(year),'train_end':str(tr.index.max()),'label_end':str(tr.target_time.max()),'base':key,'selection':'last year within training prefix only'})
    if not pieces:raise ValueError('not enough forward folds')
    nuisance=ridge(10).fit(f[X],f[cols])
    return pd.concat(pieces),nuisance,cols,audit


def design(f, cols, mean, scale, orth=True):
    c=cols if orth else ['unorth_'+s for s in cols]
    u=f[c].to_numpy()
    state=np.clip((f[['lag1','shock']].to_numpy()-mean)/scale,-3,3)
    return np.concatenate([u,u*state[:,:1],u*state[:,1:]],axis=1)


def transform(f,nuisance,cols):
    z=f.copy()
    for c in cols:z['unorth_'+c]=f[c]
    z.loc[:,cols]=f[cols].to_numpy()-nuisance.predict(f[X])
    return z


def metrics(y,p):
    d=np.asarray(y)-np.asarray(p)
    return {'mse':float(np.mean(d*d)),'mae':float(np.mean(np.abs(d))),
            'r2':float(r2_score(y,p)), 'qlike':float(np.mean(np.exp(np.clip(d,-50,50))-d-1)),
            'qlike_clip_count':int((np.abs(d)>50).sum())}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--daily',default='evidence/cq/j-1123-b41d82/root0/data/daily_returns.csv');ap.add_argument('--out',default=os.environ.get('CQ_OUTPUT_DIR'));ap.add_argument('--smoke',action='store_true');ap.add_argument('--seed',type=int,default=471);a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);started=time.time()
    def log(s):
        print(s,flush=True)
        with (out/'progress.txt').open('a') as h:h.write(s+'\n')
    daily=pd.read_csv(a.daily,index_col=0,parse_dates=True)
    if a.smoke:daily=daily[daily.index.year<=2022]
    feats=build_features(daily,seed=a.seed,progress=log);feats.to_csv(out/'daily_graph_features.csv',index=False)
    f=attach_features(load(a.data),feats)
    # Do not use legacy density or GAE scores: their source-time provenance is unresolved.
    f=f[f.index.year>=2018]; f.to_csv(out/'model_input.csv')
    selections={};allpred=[];allvalid=[]
    years=[2022] if a.smoke else [2022,2023,2024]
    for ii,year in enumerate(years):
        tr=f[f.index.year<year-1];va=f[f.index.year==year-1];te=f[f.index.year==year];fit=pd.concat([tr,va])
        assert tr.target_time.max()<va.index.min() and va.target_time.max()<te.index.min()
        key,models,scores=search(tr,va)
        vp=pd.DataFrame({'target':va.target,'base_control':models[key].predict(va[X])})
        p=pd.DataFrame({'target':te.target,'base_control':estimator(parsed(key)).fit(fit[X],fit.target).predict(te[X])})
        # Save independently tuned temporal-only ridge, context ridge, nonlinear control.
        for label,keys in [('density_ridge',[k for k in scores if k.startswith('ridge')]),('nonlinear_control',[k for k in scores if not k.startswith('ridge')])]:
            ck=min(keys,key=scores.get);vp[label]=models[ck].predict(va[X]);p[label]=estimator(parsed(ck)).fit(fit[X],fit.target).predict(te[X])
        sk,sm,ss=search(tr,va,BASE[:-2]);vp['temporal_only']=sm[sk].predict(va[BASE[:-2]]);p['temporal_only']=estimator(parsed(sk)).fit(fit[BASE[:-2]],fit.target).predict(te[BASE[:-2]])
        z,n,cols,audit=oof(tr);zt,nt,_,auditt=oof(fit);v=transform(va,n,cols);t=transform(te,nt,cols)
        conf={'base':key,'control_search':scores,'folds_train':audit,'folds_refit':auditt,'branches':{}}
        for name,features in FAMILIES.items():
            orth=name not in ['ntd_no_orth','temporal_residual']
            # Temporal control has the same 6 x 3 correction design and tuning budget.
            if name=='temporal_residual':
                for frame in [z,zt,v,t]:
                    for c in features:frame['unorth_'+c]=frame[c]
            mean=z[['lag1','shock']].mean().to_numpy();scale=np.maximum(z[['lag1','shock']].std().to_numpy(),1e-8)
            trials=[]
            for alpha in [10.,100.,1000.]:
                m=ridge(alpha).fit(design(z,features,mean,scale,orth),z.error)
                correction=m.predict(design(v,features,mean,scale,orth))
                for weight in [0.,.25,.5,1.]:
                    pred=vp.base_control.to_numpy()+weight*correction
                    trials.append({'alpha':alpha,'weight':weight,'mse':float(mean_squared_error(va.target,pred))})
            best=min(trials,key=lambda c:c['mse']);conf['branches'][name]={'selected':best,'trials':trials}
            m=ridge(best['alpha']).fit(design(z,features,mean,scale,orth),z.error)
            vp[name]=vp.base_control+best['weight']*m.predict(design(v,features,mean,scale,orth))
            mean=zt[['lag1','shock']].mean().to_numpy();scale=np.maximum(zt[['lag1','shock']].std().to_numpy(),1e-8)
            m=ridge(best['alpha']).fit(design(zt,features,mean,scale,orth),zt.error)
            p[name]=p.base_control+best['weight']*m.predict(design(t,features,mean,scale,orth))
            log(f'{ii}/{len(years)} year={year} branch={name}')
        # Direct fusion ablation receives the same base-family grid.
        dk,dm,ds=search(tr,va,X+NTD);vp['direct_ntd']=dm[dk].predict(va[X+NTD]);p['direct_ntd']=estimator(parsed(dk)).fit(fit[X+NTD],fit.target).predict(te[X+NTD]);conf['direct_search']=ds
        controls=['base_control','temporal_only','density_ridge','nonlinear_control','temporal_residual']
        strongest=min(controls,key=lambda c:mean_squared_error(vp.target,vp[c]))
        vp['strong_control']=vp[strongest];p['strong_control']=p[strongest];conf['strong_control']=strongest
        gain=interval((vp.target-vp.strong_control)**2-(vp.target-vp.ntd)**2,vp.index.date)
        gate=gain['ci95'][0]>0;conf['gate']=bool(gate);conf['validation_gain']=gain
        p['gated_ntd']=p.ntd if gate else p.strong_control
        conf['stress_threshold']=float(fit.target.quantile(.9));p['stress']=te.target>conf['stress_threshold']
        selections[str(year)]=conf;allpred.append(p);allvalid.append(vp)
        pd.concat(allpred).to_csv(out/'predictions.csv');pd.concat(allvalid).to_csv(out/'validation_predictions.csv')
        (out/'selection.json').write_text(json.dumps(selections,indent=2));log(f'{ii+1}/{len(years)} year complete')
    p=pd.concat(allpred);names=[c for c in p if c not in ['target','stress']]
    scores={c:metrics(p.target,p[c]) for c in names}
    comparisons={c:interval((p.target-p.strong_control)**2-(p.target-p[c])**2,p.index.date) for c in ['ntd','gated_ntd','raw_diffusion','placebo','null_only','direct_ntd','ntd_no_orth']}
    peryear={str(y):{c:metrics(g.target,g[c]) for c in names} for y,g in p.groupby(p.index.year)}
    stress={str(s):{c:metrics(g.target,g[c]) for c in names} for s,g in p.groupby('stress')}
    report={'status':'complete','protocol':'ntd-002','evidence_type':'development_only_previously_observed_2018_2024','metrics':scores,'paired_intervals_vs_strong_control':comparisons,'per_year':peryear,'stress':stress,'rows':len(p),'years':years,'seed':a.seed,'elapsed_seconds':time.time()-started,'peak_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'python':platform.python_version(),'inputs':{str(x):hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in [a.data,a.daily]},'limitations':['Single US survivor-selected equity universe; development only','No exact reproduction of original GAE paper or published graph-HAR models','Permutation null is not degree-conditioned','No causal claim; no CCF A readiness claim','Block intervals exploratory and not multiple-testing adjusted','QLIKE uses exponentiated log forecasts without smearing; not a QLIKE-trained model']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2));log(f'{len(years)}/{len(years)} complete')
if __name__=='__main__':main()
