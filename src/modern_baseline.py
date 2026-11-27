"""Explicit task adaptation of author RG-ResMoE code; no paper reproduction claim."""
import argparse, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from src.evaluate import load
from src.topology import build_features, attach_features
from src.ntd_evaluate import X, metrics

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'third_party/rg_resmoe'))
import train_rg_resmoe as author
import walk_forward as wf


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--daily',default=os.getenv('FG_DAILY_PATH','evidence/cq/j-1123-b41d82/root0/data/daily_returns.csv'));ap.add_argument('--out',default=os.environ.get('CQ_OUTPUT_DIR'));ap.add_argument('--smoke',action='store_true');ap.add_argument('--seed',type=int,default=471);a=ap.parse_args()
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    author.DEVICE=torch.device('cpu');wf.DEVICE=torch.device('cpu')
    author.MAX_EPOCHS=2000;author.CHECK_EVERY=5;author.PATIENCE_CHECKS=10
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True);start=time.time()
    def log(s):
        print(s,flush=True)
        with (out/'progress.txt').open('a') as f:f.write(s+'\n')
    daily_path=a.daily
    daily=pd.read_csv(daily_path,index_col=0,parse_dates=True)
    if a.smoke:daily=daily[daily.index.year<=2022]
    features=build_features(daily,seed=471,progress=log)
    f=attach_features(load(a.data),features)
    # Same feature set in total as the NTD strongest control, with two state inputs gate-only.
    aux=['market_var','shock_energy'];own=[c for c in X if c not in aux]
    years=[2022] if a.smoke else [2022,2023,2024];predictions=[];selection={}
    for i,y in enumerate(years):
        tr=f[f.index.year<y-1];va=f[f.index.year==y-1];te=f[f.index.year==y]
        assert tr.target_time.max()<va.index.min() and va.target_time.max()<te.index.min()
        scaler=StandardScaler().fit(tr[own]);gs=StandardScaler().fit(tr[aux]);ys=StandardScaler().fit(tr[['target']])
        tx,vx,ex=[scaler.transform(z[own]) for z in [tr,va,te]]
        tg,vg,eg=[np.concatenate([v,gs.transform(z[aux])],axis=1) for v,z in zip([tx,vx,ex],[tr,va,te])]
        ty=ys.transform(tr[['target']]).ravel();vy=ys.transform(va[['target']]).ravel()
        base=author.train_global(tx,ty,vx,vy,len(own),seed=a.seed,hidden=16,lr=.03)
        base.eval()
        for p in base.parameters():p.requires_grad_(False)
        experts,gate,vm,ic=author.train_residual_datadriven(base,tx,ty,tg,vx,vy,vg,va.index.date,len(own),4,1.,seed=a.seed,residual_lr=.01,hidden=16)
        rp,_,_=author.predict_residual_datadriven(base,experts,gate,ex,eg)
        count=sum(p.numel() for m in [base,experts,gate] for p in m.parameters())
        # Closest two-layer MLP width to total base+experts+gate parameters.
        def nparams(h):return len(X)*h+h+h*h+h+h+1
        width=min(range(2,129),key=lambda h:abs(nparams(h)-count))
        mlp=author.train_global(tg,ty,vg,vy,len(X),seed=a.seed,hidden=width,lr=.03);mlp.eval()
        with torch.no_grad():mp=mlp(torch.tensor(eg,dtype=torch.float32)).numpy();bp=base(torch.tensor(ex,dtype=torch.float32)).numpy()
        inv=lambda v:ys.inverse_transform(np.asarray(v).reshape(-1,1)).ravel()
        p=pd.DataFrame({'target':te.target,'rg_resmoe_adapted':inv(rp),'matched_mlp':inv(mp),'small_mlp':inv(bp)})
        predictions.append(p);pd.concat(predictions).to_csv(out/'predictions.csv')
        selection[str(y)]={'rg_params':count,'mlp_width':width,'mlp_params':nparams(width),'parameter_relative_gap':abs(nparams(width)-count)/count,'seed':a.seed,'epochs_max':2000,'validation_mse_standardized':float(vm),'refit':'No train+validation refit: author early-stopped networks retain validation checkpoint; documented difference from ridge refit','train_end':str(tr.index.max()),'validation_end':str(va.index.max())}
        (out/'selection.json').write_text(json.dumps(selection,indent=2));log(f'{i+1}/{len(years)} modern year={y}')
    p=pd.concat(predictions)
    report={'status':'complete','protocol':'modern-adaptation-001','evidence_type':'development_only_previously_observed_2018_2024','metrics':{n:metrics(p.target,p[n]) for n in p if n!='target'},'rows':len(p),'seed':a.seed,'years':years,'elapsed_seconds':time.time()-start,'torch':torch.__version__,'author_commit':'5012deb5c6c376a85c31f55234df2ede4ac9ff3f','input_sha256':hashlib.sha256(Path(a.data).read_bytes()).hexdigest(),'limitations':['Architecture adaptation, not exact published result reproduction','Next-hour market target differs from five-day individual stock target','Author early stopping protocol does not refit with validation','No independently untouched confirmation']}
    (out/'metrics.json').write_text(json.dumps(report,indent=2));log(f'{len(years)}/{len(years)} complete')
if __name__=='__main__':main()
