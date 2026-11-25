# CGI development experiment / 条件图创新开发实验

Evidence type: **development_only_previously_observed_2018_2024**. Previously observed data; no independent confirmation.

| Model | MSE ↓ | R² ↑ |
|---|---:|---:|
| strong_control | 0.237091 | 0.761971 |
| density_control | 0.237057 | 0.762004 |
| direct_graph | 0.237862 | 0.761197 |
| cgi | 0.238662 | 0.760393 |
| no_orthogonalization | 0.239005 | 0.760050 |
| gated_cgi | 0.239228 | 0.759825 |

## Paired daily loss comparisons

| Comparison | Mean gain | Exploratory 95% interval |
|---|---:|---|
| cgi_vs_strong_control | -0.001485 | [-0.003224, 0.000249] |
| cgi_vs_density_control | -0.001522 | [-0.003277, 0.000215] |
| gated_cgi_vs_strong_control | -0.002083 | [-0.003764, -0.000361] |
| gated_cgi_vs_density_control | -0.002120 | [-0.003827, -0.000390] |
| direct_graph_vs_strong_control | -0.000776 | [-0.001534, -0.000039] |
| direct_graph_vs_density_control | -0.000813 | [-0.001560, -0.000080] |
| no_orthogonalization_vs_strong_control | -0.001835 | [-0.003751, 0.000014] |
| no_orthogonalization_vs_density_control | -0.001872 | [-0.003796, -0.000029] |

Positive gain favors the method. Intervals are exploratory and unadjusted for multiple comparisons. Daily-loss intervals and aggregate hourly MSE use different weights. Validation selects controls and correction weights; outer-year outcomes never select models in this script. All years are still development evidence because they were inspected previously.

## 中文结论

条件图创新原型相对验证集选出的强对照，小时 MSE 改善为 -0.663%；正值表示误差降低，负值表示更差。按交易日配对得到的探索性区间为 [-0.003224, 0.000249]。无论本次结果如何，旧数据上的开发实验均不能替代未观察数据上的独立确认，也不能据此认定达到 CCF A 水平。
