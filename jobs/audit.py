"""Read-only inspection of specifically authorized legacy project inputs."""
import os,json,pathlib,hashlib,shutil,platform
out=pathlib.Path(os.environ['CQ_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True)
roots=[pathlib.Path('/data/zyy/FinancialAD/gae-instability-v2'),pathlib.Path('/date/zyy/FinancialAD/gae-instability')]
report={'host':platform.node(),'roots':[],'found_forecast':False}
for k,root in enumerate(roots):
    item={'path':str(root),'exists':root.is_dir(),'files':[]}
    if root.is_dir():
        for sub in ['results/forecast_data.csv','results/expanded_metrics.json','results/data_preparation.json','results/universe.csv','data/daily_returns.csv','data/hourly.csv']:
            p=root/sub
            if p.is_file():
                b=p.read_bytes();item['files'].append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
                dest=out/f'root{k}'/sub;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
                if sub.endswith('forecast_data.csv'):report['found_forecast']=True
        raw=root/'data/raw/stocks_bars_1m.parquet'
        item['raw']={'path':str(raw),'exists':raw.is_file(),'bytes':raw.stat().st_size if raw.is_file() else None}
        item['free_bytes']=shutil.disk_usage(root).free
    report['roots'].append(item)
    (out/'progress.txt').write_text(f'{k+1}/{len(roots)} roots inspected\n')
(out/'audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
