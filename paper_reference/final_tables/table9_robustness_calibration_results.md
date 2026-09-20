# Table 9: Robustness and Calibration Experiments

## Bootstrap Answer-Equivalence CIs

| dataset | method | point | 95% CI |
|---|---|---:|---:|
| HotpotQA-500 | prefix naive | 0.472 | [0.428, 0.516] |
| HotpotQA-500 | random suffix K2 | 0.918 | [0.892, 0.942] |
| HotpotQA-500 | risk suffix K1 | 0.996 | [0.990, 1.000] |
| HotpotQA-500 | risk suffix K2 | 0.998 | [0.994, 1.000] |
| 2Wiki-500 | prefix naive | 0.378 | [0.336, 0.420] |
| 2Wiki-500 | random suffix K2 | 0.834 | [0.800, 0.866] |
| 2Wiki-500 | risk suffix K1 | 0.970 | [0.954, 0.984] |
| 2Wiki-500 | hybrid query+risk K1 | 0.974 | [0.958, 0.986] |
| 2Wiki-500 | risk suffix K2 | 0.984 | [0.972, 0.994] |

## Paired Delta CIs Against Random K2

| dataset | method - random K2 | answer-equiv delta | 95% CI | changed-wrong delta | 95% CI |
|---|---|---:|---:|---:|---:|
| HotpotQA-500 | risk K2 | +0.080 | [0.056, 0.104] | -0.068 | [-0.092, -0.046] |
| HotpotQA-500 | query K2 | +0.040 | [0.014, 0.068] | -0.034 | [-0.058, -0.010] |
| 2Wiki-500 | risk K1 | +0.136 | [0.104, 0.170] | -0.108 | [-0.140, -0.078] |
| 2Wiki-500 | hybrid K1 | +0.140 | [0.108, 0.174] | -0.110 | [-0.140, -0.080] |
| 2Wiki-500 | risk K2 | +0.150 | [0.118, 0.184] | -0.120 | [-0.150, -0.092] |

## Held-Out Method Calibration

| dataset | target budget | selected methods over 200 splits | test answer equiv | changed-wrong | test patch |
|---|---:|---|---:|---:|---:|
| 2Wiki-500 | 0.85 | risk K1 125; hybrid 53; margin 22 | 0.970 | 0.024 | 0.824 |
| 2Wiki-500 | 0.94 | risk K2 148; query K2 20; risk K1 16; hybrid 12; margin 4 | 0.979 | 0.016 | 0.908 |
| HotpotQA-500 | 0.82 | risk K1 153; risk K2 47 | 0.996 | 0.004 | 0.905 |
| HotpotQA-500 | 0.95 | risk K1 166; risk K2 34 | 0.996 | 0.004 | 0.901 |

## First-Token Latency Sanity

| dataset | method | avg wall | median | p95 | patch ratio | peak CUDA MB |
|---|---|---:|---:|---:|---:|---:|
| 2Wiki-50 | full prefill | 0.071s | 0.060s | 0.115s | 0.000 | 15204 |
| 2Wiki-50 | risk suffix K1 | 0.083s | 0.078s | 0.127s | 0.814 | 15198 |
| 2Wiki-50 | hybrid suffix K1 | 0.084s | 0.080s | 0.126s | 0.834 | 15202 |
| 2Wiki-50 | risk suffix K2 | 0.089s | 0.087s | 0.131s | 0.940 | 15223 |
| noise64-20 | full prefill | 0.215s | 0.192s | 0.224s | 0.000 | 16545 |
| noise64-20 | risk suffix K1 | 0.140s | 0.131s | 0.236s | 0.481 | 16345 |
| noise64-20 | hybrid suffix K1 | 0.163s | 0.167s | 0.235s | 0.600 | 16430 |
| noise64-20 | risk suffix K2 | 0.176s | 0.186s | 0.237s | 0.666 | 16474 |
