"""Verify downloaded CQ outcomes and build bilingual evidence, without training."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from src.evaluate import interval
from src.ntd_evaluate import metrics


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='evidence/cq');ap.add_argument('--out',default='paper/workflow');a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    records=[];runs=[];families={}
    for metric_path in sorted(Path(a.root).rglob('metrics.json')):
        folder=metric_path.parent
        run_name=str(folder.relative_to(Path(a.root)))
        if not (folder/'metrics.json').exists() or not (folder/'predictions.csv').exists():continue
        m=json.loads((folder/'metrics.json').read_text())
        if m.get('status')!='complete' or m.get('years')!=[2022,2023,2024]:continue
        f=pd.read_csv(folder/'predictions.csv',index_col=0);f.index=pd.to_datetime(f.index,utc=True)
        if m.get('protocol')=='modern-adaptation-001':
            # Author Torch predicts float32; pandas CSV stores shortest float32 decimals.
            # Restore the producing dtype before demanding exact metric agreement.
            for c in m['metrics']:f[c]=f[c].astype(np.float32)
        assert not f.index.has_duplicates
        checked={}
        for model,values in m['metrics'].items():
            actual=metrics(f.target,f[model]);assert abs(actual['mse']-values['mse'])<1e-10
            if 'r2' in values:assert abs(actual['r2']-values['r2'])<1e-10
            records.append({'run':run_name,'protocol':m.get('protocol','cgi-001'),'seed':m.get('seed'),'model':model,**actual,'rows':len(f),'code_revision':(folder/'code-commit.txt').read_text().strip() if (folder/'code-commit.txt').exists() else 'unknown'})
            checked[model]=actual
        input_checks={}
        for path,expected in m.get('inputs',{}).items():
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
            input_checks[path]=True
        if 'input_sha256' in m:
            path=Path('evidence/cq/j-1123-b41d82/root0/results/forecast_data.csv')
            assert hashlib.sha256(path.read_bytes()).hexdigest()==m['input_sha256'];input_checks[str(path)]=True
        timing=None
        if (folder/'model_input.csv').exists():
            frame=pd.read_csv(folder/'model_input.csv',index_col=0)
            dates=pd.to_datetime(frame.index,utc=True).tz_convert('America/New_York').date
            assert (pd.to_datetime(frame.source_day).dt.date.to_numpy()<dates).all()
            assert (pd.to_datetime(frame.graph_fit_end)<pd.to_datetime(frame.source_day)).all()
            timing={'previous_session_only':True,'graph_fit_precedes_shock':True,'min_nodes':int(frame.graph_node_count.min())}
        source_checks={}
        if (folder/'source-hashes.json').exists():
            revision=(folder/'code-commit.txt').read_text().strip()
            import subprocess
            for path,expected in json.loads((folder/'source-hashes.json').read_text()).items():
                b=subprocess.check_output(['git','show',revision+':'+path]);assert hashlib.sha256(b).hexdigest()==expected;source_checks[path]=True
        manifest=[{'path':str(p.relative_to(folder)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.rglob('*')) if p.is_file() and p.name not in ['manifest.json','local-verification.json']]
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (folder/'local-verification.json').write_text(json.dumps({'status':'verified','metrics_recomputed':checked,'source_hashes_match_pinned_commit':source_checks,'source_verification':'runtime hashes and CQ pin' if source_checks else 'CQ pinned commit only; no runtime source hash output','input_hashes_checked':input_checks,'timing_audit':timing,'rows':len(f)},indent=2)+'\n')
        runs.append({'job':run_name,'protocol':m.get('protocol','cgi-001'),'seed':m.get('seed'),'seconds':m.get('elapsed_seconds'),'rows':len(f)})
        families.setdefault(m.get('protocol','cgi-001'),[]).append((run_name,m,f))
    pd.DataFrame(records).to_csv(out/'results.csv',index=False)
    lines=['# Research experiment report / 研究实验报告','', 'All numbers below are recomputed from CQ prediction files. Historical2018–2024 data is development-only. No CCF A readiness or untouched confirmation is claimed.','', '| CQ job | Protocol | Seed | Rows | Compute seconds |','|---|---|---:|---:|---:|']
    for r in runs:lines.append(f"| {r['job']} | {r['protocol']} | {r['seed']} | {r['rows']} | {r['seconds']:.2f} |")
    lines+=['','## Verified model results','', '| Protocol | Seed | Model | MSE↓ | R²↑ | QLIKE↓ |','|---|---:|---|---:|---:|---:|']
    for r in records:lines.append(f"| {r['protocol']} | {r['seed']} | {r['model']} | {r['mse']:.7f} | {r['r2']:.6f} | {r['qlike']:.6f} |")
    conclusions=[]
    if 'ntd-002' in families:
        ntd=families['ntd-002'];ref=ntd[0][2]
        for _,_,f in ntd:assert f.index.equals(ref.index);np.testing.assert_allclose(f.target,ref.target,rtol=0,atol=1e-10)
        for _,_,f in ntd:
            np.testing.assert_allclose(f.strong_control,ref.strong_control,rtol=0,atol=1e-10)
        lines+=['','## Primary per-seed comparison','', 'Positive gain favors NTD. These development-only intervals are exploratory, not multiplicity-adjusted confirmation.','', '| Seed | Hourly MSE improvement (%) | Mean daily gain | Daily block95% interval |','|---:|---:|---:|---|']
        for _,m,f in ntd:
            v=interval((f.target-f.strong_control)**2-(f.target-f.ntd)**2,f.index.tz_convert('America/New_York').date)
            g=100*(m['metrics']['strong_control']['mse']-m['metrics']['ntd']['mse'])/m['metrics']['strong_control']['mse']
            lines.append(f"| {m['seed']} | {g:.4f} | {v['mean_daily_gain']:.7f} | [{v['ci95'][0]:.7f}, {v['ci95'][1]:.7f}] |")
        # Three permutations are Monte Carlo sensitivity, never three independent markets.
        gain=[100*(m['metrics']['strong_control']['mse']-m['metrics']['ntd']['mse'])/m['metrics']['strong_control']['mse'] for _,m,_ in ntd]
        conclusions.append(f'NTD 相对各年度验证集选出的最强非图对照，{len(ntd)} 个排列种子的小时 MSE 改善范围为 {min(gain):.3f}% 至 {max(gain):.3f}%；负值表示更差。')
        aligned=pd.DataFrame({'target':ref.target,'ntd_mean':np.mean([f.ntd.to_numpy() for _,_,f in ntd],axis=0),'strong_control':ref.strong_control})
        for c in ['raw_diffusion','null_only','placebo','direct_ntd','ntd_no_orth']:
            aligned[c+'_mean']=np.mean([f[c].to_numpy() for _,_,f in ntd],axis=0)
        lines+=['','## Validation decisions','', '| Seed | Year | Base family | Strong control | NTD alpha | NTD weight | Gate |','|---:|---:|---|---|---:|---:|---|']
        for job,m,_ in ntd:
            selections=json.loads((Path(a.root)/job/'selection.json').read_text())
            for year,sel in selections.items():
                c=sel['branches']['ntd']['selected']
                lines.append(f"| {m['seed']} | {year} | {sel['base']} | {sel['strong_control']} | {c['alpha']} | {c['weight']} | {sel['gate']} |")
        modern=families.get('modern-adaptation-001',[])
        for _,_,f in modern:assert f.index.equals(ref.index);np.testing.assert_allclose(f.target,ref.target,rtol=0,atol=1e-10)
        for c in ['rg_resmoe_adapted','matched_mlp','small_mlp']:
            if modern:aligned[c+'_mean']=np.mean([f[c].to_numpy() for _,_,f in modern],axis=0)
        aligned.to_csv(out/'aligned-ensemble-predictions.csv')
        comps={c:interval((aligned.target-aligned[c])**2-(aligned.target-aligned.ntd_mean)**2,aligned.index.tz_convert('America/New_York').date) for c in aligned if c not in ['target','ntd_mean']}
        (out/'aligned-comparisons.json').write_text(json.dumps({'ntd_seeds':[m['seed'] for _,m,_ in ntd],'modern_seeds':[m['seed'] for _,m,_ in modern],'metrics':{c:metrics(aligned.target,aligned[c]) for c in aligned if c!='target'},'daily_intervals':comps,'status':'exploratory; seed-mean predictions are additional descriptive analysis, not primary preregistered endpoint'},indent=2)+'\n')
        lines+=['','## Aligned comparisons','', 'Seed-mean predictions are a descriptive sensitivity analysis. Seeds are not independent datasets. Intervals are five-session block bootstrap intervals on daily mean losses, unadjusted for multiplicity. Pooled hourly MSE and equally weighted daily gains differ in weighting.','', '| NTD seed mean vs | Mean daily gain | Exploratory95% interval |','|---|---:|---|']
        for c,v in comps.items():lines.append(f"| {c} | {v['mean_daily_gain']:.7f} | [{v['ci95'][0]:.7f}, {v['ci95'][1]:.7f}] |")
        if modern:conclusions.append('现代对照使用作者 RG-ResMoE 网络及近似参数量匹配 MLP，已按相同预测时刻对齐；任务与原作者论文不同，属于明确标注的适配实验。')
    lines+=['','## Evidence limits / 证据边界','', 'One US survivor-selected equity universe. No independent market confirmation, no full raw-minute reconstruction, no degree-conditioned null test, no faithful Sig-GSPHAR reproduction. The scalar permutation identity and residualization are established tools, not new theorems. Legacy CGI and NTD use different graph information timing and must not be treated as a matched before/after improvement. Negative, zero-weight and placebo outcomes remain in the archive. NTD portable runs use NumPy1.26.4/scikit-learn1.5.2/SciPy1.14.1; modern Kaggle runs use NumPy2.2.6/scikit-learn1.6.1/SciPy1.15.3. Within NTD every control shares the same environment; cross-family comparisons carry this additional software-version difference.','', '## 中文结论','']
    lines+=conclusions or ['尚无完整 NTD 结果；不能据此声称超过最强对照。']
    lines+=['当前完成的是可追溯的开发实验。只有稳定超过强对照、排除容量和随机图解释，并在独立数据及现代方法比较中复核后，才有理由进一步评价其顶会贡献；目前不能认定达到 CCF A 论文水平。']
    (out/'experiment-report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'verified_runs':runs,'result_rows':len(records)},indent=2))
if __name__=='__main__':main()
