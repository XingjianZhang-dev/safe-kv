# Held-Out Gate Calibration

| model | dataset | target | test budget | answer eq | random mean | percentile | changed+wrong |
|---|---|---:|---:|---:|---:|---:|---:|
| qwen05 | diagnostic_100_noisy | 0.10 | 0.192 | 0.786 | 0.840 | 0.030 | 0.171 |
| qwen05 | diagnostic_100_noisy | 0.25 | 0.234 | 0.843 | 0.851 | 0.540 | 0.114 |
| qwen05 | diagnostic_100_noisy | 0.40 | 0.398 | 0.900 | 0.892 | 0.740 | 0.071 |
| qwen15 | diagnostic_100_noisy | 0.10 | 0.192 | 0.829 | 0.850 | 0.350 | 0.129 |
| qwen15 | diagnostic_100_noisy | 0.25 | 0.234 | 0.886 | 0.865 | 0.810 | 0.100 |
| qwen15 | diagnostic_100_noisy | 0.40 | 0.398 | 0.957 | 0.920 | 0.960 | 0.029 |
| qwen05 | external_multihop_100 | 0.10 | 0.080 | 0.429 | 0.448 | 0.270 | 0.500 |
| qwen05 | external_multihop_100 | 0.25 | 0.215 | 0.471 | 0.482 | 0.490 | 0.457 |
| qwen05 | external_multihop_100 | 0.40 | 0.417 | 0.529 | 0.526 | 0.960 | 0.429 |
| qwen15 | external_multihop_100 | 0.10 | 0.080 | 0.400 | 0.415 | 0.370 | 0.514 |
| qwen15 | external_multihop_100 | 0.25 | 0.215 | 0.471 | 0.469 | 0.680 | 0.443 |
| qwen15 | external_multihop_100 | 0.40 | 0.417 | 0.529 | 0.553 | 0.040 | 0.414 |

Calibration uses 30% of example ids to derive a risk cutoff from the predeclared budget.
Final quality metrics are computed only on the held-out 70% test examples.
Matched random gates select on the same held-out examples to match the safe gate's actual test budget.
