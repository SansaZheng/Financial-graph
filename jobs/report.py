"""Build a bilingual report from actual CQ development artifacts only."""
import argparse,json,hashlib
from pathlib import Path

def main():
    a=argparse.ArgumentParser();a.add_argument('run');args=a.parse_args();p=Path(args.run)
    m=json.loads((p/'metrics.json').read_text());sel=json.loads((p/'selection.json').read_text())
    if m['status']!='complete':raise ValueError('incomplete output')
    lines=['# CGI development experiment / 条件图创新开发实验','',f"Evidence type: **{m['evidence_type']}**. Previously observed data; no independent confirmation.",'', '| Model | MSE ↓ | R² ↑ |','|---|---:|---:|']
    for n,v in m['metrics'].items():lines.append(f"| {n} | {v['mse']:.6f} | {v['r2']:.6f} |")
    lines+=['','## Paired daily loss comparisons','', '| Comparison | Mean gain | Exploratory 95% interval |','|---|---:|---|']
    for n,v in m['paired_intervals'].items():lines.append(f"| {n} | {v['mean_daily_gain']:.6f} | [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}] |")
    lines+=['','Positive gain favors the method. Intervals are exploratory and unadjusted for multiple comparisons. Daily-loss intervals and aggregate hourly MSE use different weights. Validation selects controls and correction weights; outer-year outcomes never select models in this script. All years are still development evidence because they were inspected previously.','', '## 中文结论','']
    c=m['metrics']['strong_control']['mse'];x=m['metrics']['cgi']['mse'];gain=100*(c-x)/c
    ci=m['paired_intervals']['cgi_vs_strong_control']['ci95']
    lines.append(f'条件图创新原型相对验证集选出的强对照，小时 MSE 改善为 {gain:.3f}%；正值表示误差降低，负值表示更差。按交易日配对得到的探索性区间为 [{ci[0]:.6f}, {ci[1]:.6f}]。无论本次结果如何，旧数据上的开发实验均不能替代未观察数据上的独立确认，也不能据此认定达到 CCF A 水平。')
    (p/'report.md').write_text('\n'.join(lines)+'\n')
    manifest=[{'path':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(p.iterdir()) if f.is_file() and f.name!='manifest.json']
    (p/'manifest.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
