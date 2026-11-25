# Research experiment report / 研究实验报告

All numbers below are recomputed from CQ prediction files. Historical2018–2024 data is development-only. No CCF A readiness or untouched confirmation is claimed.

| CQ job | Protocol | Seed | Rows | Compute seconds |
|---|---|---:|---:|---:|
| j-1125-0c3a7c/seed471 | ntd-002 | 471 | 3644 | 54.91 |
| j-1125-0c3a7c/seed472 | ntd-002 | 472 | 3644 | 44.80 |
| j-1125-0c3a7c/seed473 | ntd-002 | 473 | 3644 | 42.09 |
| j-1125-4cabb4 | modern-adaptation-001 | 471 | 3644 | 22.60 |
| j-1125-50ac72 | modern-adaptation-001 | 473 | 3644 | 20.98 |
| j-1125-6121b4 | modern-adaptation-001 | 472 | 3644 | 24.77 |
| j-1125-dd9d4b | cgi-001 | None | 3644 | 10.07 |

## Verified model results

| Protocol | Seed | Model | MSE↓ | R²↑ | QLIKE↓ |
|---|---:|---|---:|---:|---:|
| ntd-002 | 471 | base_control | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 471 | density_ridge | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 471 | nonlinear_control | 0.2431740 | 0.755864 | 0.184205 |
| ntd-002 | 471 | temporal_only | 0.2369636 | 0.762099 | 0.178743 |
| ntd-002 | 471 | ntd | 0.2377171 | 0.761342 | 0.183437 |
| ntd-002 | 471 | raw_diffusion | 0.2377211 | 0.761338 | 0.183107 |
| ntd-002 | 471 | null_only | 0.2376108 | 0.761449 | 0.182693 |
| ntd-002 | 471 | placebo | 0.2379717 | 0.761087 | 0.183096 |
| ntd-002 | 471 | temporal_residual | 0.2372304 | 0.761831 | 0.183178 |
| ntd-002 | 471 | ntd_no_orth | 0.2380866 | 0.760971 | 0.183675 |
| ntd-002 | 471 | direct_ntd | 0.2382676 | 0.760790 | 0.178207 |
| ntd-002 | 471 | strong_control | 0.2366833 | 0.762380 | 0.184786 |
| ntd-002 | 471 | gated_ntd | 0.2366833 | 0.762380 | 0.184786 |
| ntd-002 | 472 | base_control | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 472 | density_ridge | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 472 | nonlinear_control | 0.2431740 | 0.755864 | 0.184205 |
| ntd-002 | 472 | temporal_only | 0.2369636 | 0.762099 | 0.178743 |
| ntd-002 | 472 | ntd | 0.2378833 | 0.761175 | 0.183572 |
| ntd-002 | 472 | raw_diffusion | 0.2377211 | 0.761338 | 0.183107 |
| ntd-002 | 472 | null_only | 0.2376108 | 0.761449 | 0.182693 |
| ntd-002 | 472 | placebo | 0.2379168 | 0.761142 | 0.183049 |
| ntd-002 | 472 | temporal_residual | 0.2372304 | 0.761831 | 0.183178 |
| ntd-002 | 472 | ntd_no_orth | 0.2388526 | 0.760202 | 0.183178 |
| ntd-002 | 472 | direct_ntd | 0.2385251 | 0.760531 | 0.178816 |
| ntd-002 | 472 | strong_control | 0.2366833 | 0.762380 | 0.184786 |
| ntd-002 | 472 | gated_ntd | 0.2366833 | 0.762380 | 0.184786 |
| ntd-002 | 473 | base_control | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 473 | density_ridge | 0.2375920 | 0.761468 | 0.177132 |
| ntd-002 | 473 | nonlinear_control | 0.2431740 | 0.755864 | 0.184205 |
| ntd-002 | 473 | temporal_only | 0.2369636 | 0.762099 | 0.178743 |
| ntd-002 | 473 | ntd | 0.2376406 | 0.761419 | 0.183576 |
| ntd-002 | 473 | raw_diffusion | 0.2377211 | 0.761338 | 0.183107 |
| ntd-002 | 473 | null_only | 0.2376108 | 0.761449 | 0.182693 |
| ntd-002 | 473 | placebo | 0.2380380 | 0.761020 | 0.183405 |
| ntd-002 | 473 | temporal_residual | 0.2372304 | 0.761831 | 0.183178 |
| ntd-002 | 473 | ntd_no_orth | 0.2379549 | 0.761103 | 0.183633 |
| ntd-002 | 473 | direct_ntd | 0.2382793 | 0.760778 | 0.178383 |
| ntd-002 | 473 | strong_control | 0.2366833 | 0.762380 | 0.184786 |
| ntd-002 | 473 | gated_ntd | 0.2366833 | 0.762380 | 0.184786 |
| modern-adaptation-001 | 471 | rg_resmoe_adapted | 0.2444567 | 0.754576 | 0.185820 |
| modern-adaptation-001 | 471 | matched_mlp | 0.2429164 | 0.756122 | 0.188918 |
| modern-adaptation-001 | 471 | small_mlp | 0.2457424 | 0.753285 | 0.185195 |
| modern-adaptation-001 | 473 | rg_resmoe_adapted | 0.2451769 | 0.753853 | 0.183992 |
| modern-adaptation-001 | 473 | matched_mlp | 0.2417617 | 0.757282 | 0.176722 |
| modern-adaptation-001 | 473 | small_mlp | 0.2461317 | 0.752894 | 0.181959 |
| modern-adaptation-001 | 472 | rg_resmoe_adapted | 0.2446049 | 0.754427 | 0.184276 |
| modern-adaptation-001 | 472 | matched_mlp | 0.2405113 | 0.758537 | 0.178812 |
| modern-adaptation-001 | 472 | small_mlp | 0.2435408 | 0.755496 | 0.183178 |
| cgi-001 | None | strong_control | 0.2370911 | 0.761971 | 0.180252 |
| cgi-001 | None | density_control | 0.2370575 | 0.762004 | 0.180462 |
| cgi-001 | None | direct_graph | 0.2378618 | 0.761197 | 0.180787 |
| cgi-001 | None | cgi | 0.2386624 | 0.760393 | 0.187650 |
| cgi-001 | None | no_orthogonalization | 0.2390045 | 0.760050 | 0.187793 |
| cgi-001 | None | gated_cgi | 0.2392281 | 0.759825 | 0.186959 |

## Primary per-seed comparison

Positive gain favors NTD. These development-only intervals are exploratory, not multiplicity-adjusted confirmation.

| Seed | Hourly MSE improvement (%) | Mean daily gain | Daily block95% interval |
|---:|---:|---:|---|
| 471 | -0.4368 | -0.0010061 | [-0.0023473, 0.0001731] |
| 472 | -0.5070 | -0.0012257 | [-0.0025553, -0.0000562] |
| 473 | -0.4045 | -0.0009095 | [-0.0022604, 0.0003250] |

## Validation decisions

| Seed | Year | Base family | Strong control | NTD alpha | NTD weight | Gate |
|---:|---:|---|---|---:|---:|---|
| 471 | 2022 | ridge_10 | temporal_residual | 1000.0 | 0.5 | False |
| 471 | 2023 | ridge_10 | temporal_only | 10.0 | 0.0 | False |
| 471 | 2024 | ridge_1000 | temporal_residual | 100.0 | 0.5 | False |
| 472 | 2022 | ridge_10 | temporal_residual | 1000.0 | 0.5 | False |
| 472 | 2023 | ridge_10 | temporal_only | 10.0 | 0.0 | False |
| 472 | 2024 | ridge_1000 | temporal_residual | 1000.0 | 0.5 | False |
| 473 | 2022 | ridge_10 | temporal_residual | 1000.0 | 0.5 | False |
| 473 | 2023 | ridge_10 | temporal_only | 10.0 | 0.0 | False |
| 473 | 2024 | ridge_1000 | temporal_residual | 10.0 | 0.5 | False |

## Aligned comparisons

Seed-mean predictions are a descriptive sensitivity analysis. Seeds are not independent datasets. Intervals are five-session block bootstrap intervals on daily mean losses, unadjusted for multiplicity. Pooled hourly MSE and equally weighted daily gains differ in weighting.

| NTD seed mean vs | Mean daily gain | Exploratory95% interval |
|---|---:|---|
| strong_control | -0.0010233 | [-0.0023507, 0.0001502] |
| raw_diffusion_mean | 0.0000755 | [-0.0002453, 0.0003637] |
| null_only_mean | -0.0000368 | [-0.0003472, 0.0002690] |
| placebo_mean | 0.0002618 | [-0.0000927, 0.0006118] |
| direct_ntd_mean | 0.0007467 | [-0.0008241, 0.0022701] |
| ntd_no_orth_mean | 0.0005567 | [0.0001547, 0.0009840] |
| rg_resmoe_adapted_mean | 0.0052287 | [0.0019268, 0.0085973] |
| matched_mlp_mean | 0.0010115 | [-0.0019426, 0.0041449] |
| small_mlp_mean | 0.0054193 | [0.0025576, 0.0082388] |

## Evidence limits / 证据边界

One US survivor-selected equity universe. No independent market confirmation, no full raw-minute reconstruction, no degree-conditioned null test, no faithful Sig-GSPHAR reproduction. The scalar permutation identity and residualization are established tools, not new theorems. Legacy CGI and NTD use different graph information timing and must not be treated as a matched before/after improvement. Negative, zero-weight and placebo outcomes remain in the archive. NTD portable runs use NumPy1.26.4/scikit-learn1.5.2/SciPy1.14.1; modern Kaggle runs use NumPy2.2.6/scikit-learn1.6.1/SciPy1.15.3. Within NTD every control shares the same environment; cross-family comparisons carry this additional software-version difference.

## 中文结论

NTD 相对各年度验证集选出的最强对照，3 个排列种子的小时 MSE 改善范围为 -0.507% 至 -0.404%；负值表示更差。
三组均未超过最强对照，主要实验目标未达成。门控回退不构成性能提升；原始扩散、仅零模型和置换安慰剂的比较也不足以证明拓扑特异性增益。
现代对照使用作者 RG-ResMoE 网络及近似参数量匹配 MLP，已按相同预测时刻对齐；任务与原作者论文不同，属于明确标注的适配实验。
当前完成的是可追溯的开发实验。只有稳定超过强对照、排除容量和随机图解释，并在独立数据及现代方法比较中复核后，才有理由进一步评价其顶会贡献；目前不能认定达到 CCF A 论文水平。
