#!/usr/bin/env python3
"""Execute an unchanged scientific method against verified, pinned assets on a remote host."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from assets import load_manifest,choose,under,verify_file,remote_guard,digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',default=os.getenv('FG_DATA_ROOT'));p.add_argument('--output',required=True);p.add_argument('--method',choices=['ntd','modern'],default='ntd');p.add_argument('--seed',type=int,default=471);p.add_argument('--smoke',action='store_true');p.add_argument('--manifest',default=str(Path(__file__).resolve().parents[1]/'assets/manifest.json'));a=p.parse_args()
    remote_guard(False)
    if not a.data_root:raise ValueError('FG_DATA_ROOT or --data-root required')
    repo=Path(__file__).resolve().parents[1];out=Path(a.output).resolve()
    if out.is_relative_to(repo):raise ValueError('Run output must be outside the code checkout')
    m=load_manifest(a.manifest);asset,files=choose(m,'derived-inputs')
    for f in files:verify_file(under(Path(a.data_root)/asset['id'],f['local_path']),f)
    paths={f['path']:under(Path(a.data_root)/asset['id'],f['local_path']) for f in files}
    rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=repo,text=True).strip():raise ValueError('Commit tracked changes before execution')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'run-provenance.json').exists():raise ValueError('Use a fresh run output directory')
    command=[sys.executable,'-m','src.ntd_evaluate' if a.method=='ntd' else 'src.modern_baseline','--data',str(paths['derived/forecast_data.csv']),'--daily',str(paths['derived/daily_returns.csv']),'--out',str(out),'--seed',str(a.seed)]
    if a.smoke:command+=['--smoke']
    provenance={'status':'started','code_commit':rev,'dataset':{'repo_id':asset['repo_id'],'repo_type':asset['repo_type'],'revision':asset['revision']},'asset_manifest_sha256':digest(a.manifest),'random_seed':a.seed,'method':a.method,'smoke':a.smoke,'split_config':json.loads((repo/'configs/rolling-development.json').read_text()),'checkpoint_status':'This evaluator does not serialize trained weights; do not claim a saved model exists.'}
    receipt=out/'run-provenance.json';receipt.write_text(json.dumps(provenance,indent=2)+'\n')
    with (out/'environment.txt').open('w') as f:subprocess.run([sys.executable,'-m','pip','freeze'],stdout=f,check=True)
    r=subprocess.run(command,cwd=repo)
    provenance['status']='complete' if r.returncode==0 else 'failed';provenance['exit_code']=r.returncode
    if (out/'metrics.json').exists():provenance['metrics_sha256']=digest(out/'metrics.json')
    receipt.write_text(json.dumps(provenance,indent=2)+'\n');return r.returncode
if __name__=='__main__':sys.exit(main())
