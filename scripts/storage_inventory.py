"""Read-only scoped inventory. Never emits credential values."""
import argparse, importlib.util, json, os, shutil
from pathlib import Path

def inspect(roots):
    report={'roots':[], 'hf':{'client_installed':bool(importlib.util.find_spec('huggingface_hub'))}}
    for root in roots:
        p=Path(root).expanduser()
        item={'path':str(p),'exists':p.exists()}
        if p.exists():
            item.update(real_path=str(p.resolve()),free_bytes=shutil.disk_usage(p).free)
            files=[]; models=[]; total=0
            for base, dirs, names in os.walk(p):
                dirs[:]=[d for d in dirs if d not in ['env','.venv','.git','repo','__pycache__','node_modules','.cache','cache'] and not Path(base,d).is_symlink()]
                for name in names:
                    f=Path(base,name)
                    if f.is_symlink():continue
                    try:n=f.stat().st_size
                    except OSError:continue
                    total+=n
                    if f.suffix in ['.safetensors','.pt','.pth','.ckpt','.joblib','.pkl']:models.append({'path':str(f),'bytes':n})
                    if n>50000000:files.append({'path':str(f),'bytes':n})
            item.update(scoped_bytes=total,large_files=files,model_files=models)
        report['roots'].append(item)
    hfhome=Path(os.getenv('HF_HOME',str(Path.home()/'.cache/huggingface')))
    report['hf']['credential_present']=bool(os.getenv('HF_TOKEN') or os.getenv('HUGGING_FACE_HUB_TOKEN') or Path(os.getenv('HF_TOKEN_PATH',str(hfhome/'token'))).exists() or (Path.home()/'.huggingface/token').exists())
    if report['hf']['client_installed'] and report['hf']['credential_present']:
        from huggingface_hub import HfApi
        try:
            api=HfApi();u=api.whoami()
            report['hf'].update(account=u.get('name'),plan=u.get('type'),is_pro=u.get('isPro'),organizations=[{'name':o.get('name'),'role':o.get('roleInOrg')} for o in u.get('orgs',[])])
            report['hf']['datasets']=[{'id':x.id,'private':x.private,'sha':x.sha} for x in api.list_datasets(author=u['name'])]
            report['hf']['models']=[{'id':x.id,'private':x.private,'sha':x.sha} for x in api.list_models(author=u['name'])]
        except Exception as e:report['hf']['error_type']=type(e).__name__
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',action='append',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    Path(a.out).write_text(json.dumps(inspect(a.root),indent=2)+'\n')
