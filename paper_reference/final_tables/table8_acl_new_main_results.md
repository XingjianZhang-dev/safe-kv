# Table 8: New ACL-Targeted Main Results

## External Multi-Hop, Qwen2.5-7B-Instruct

| dataset | method | answer equiv | gold EM | gold F1 | changed+wrong | patch ratio | avg KL |
|---|---|---:|---:|---:|---:|---:|---:|
| HotpotQA-500 | prefix naive | 0.472 | 0.354 | 0.489 | 241 | 0.000 | 3.053 |
| HotpotQA-500 | query suffix K1 | 0.930 | 0.522 | 0.696 | 32 | 0.842 | 0.196 |
| HotpotQA-500 | query suffix K2 | 0.958 | 0.534 | 0.704 | 18 | 0.883 | 0.106 |
| HotpotQA-500 | risk suffix K1 | 0.996 | 0.542 | 0.708 | 2 | 0.892 | 0.009 |
| HotpotQA-500 | risk suffix K2 | 0.998 | 0.544 | 0.709 | 1 | 0.948 | 0.00002 |
| HotpotQA-500 | random suffix K2 | 0.918 | 0.528 | 0.696 | 35 | 0.814 | 0.346 |
| 2Wiki-500 | prefix naive | 0.378 | 0.312 | 0.386 | 272 | 0.000 | 4.242 |
| 2Wiki-500 | query suffix K1 | 0.918 | 0.410 | 0.504 | 37 | 0.791 | 0.338 |
| 2Wiki-500 | query suffix K2 | 0.972 | 0.444 | 0.538 | 12 | 0.885 | 0.126 |
| 2Wiki-500 | risk suffix K1 | 0.970 | 0.442 | 0.536 | 12 | 0.813 | 0.098 |
| 2Wiki-500 | risk margin m=0.05 | 0.972 | 0.440 | 0.534 | 12 | 0.838 | 0.050 |
| 2Wiki-500 | hybrid query+risk K1 | 0.974 | 0.442 | 0.536 | 11 | 0.842 | 0.051 |
| 2Wiki-500 | risk suffix K2 | 0.984 | 0.452 | 0.546 | 6 | 0.929 | 0.028 |
| 2Wiki-500 | random suffix K2 | 0.834 | 0.434 | 0.517 | 66 | 0.711 | 0.671 |

## Position Sensitivity, Qwen2.5-7B-Instruct

| method | overall | first | early | middle | late | last | patch ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| prefix naive | 0.632 | 0.420 | 0.480 | 0.720 | 0.700 | 0.840 | 0.000 |
| oracle doc patch | 0.840 | 0.420 | 0.940 | 0.960 | 0.900 | 0.980 | 0.081 |
| oracle suffix closure | 0.980 | 1.000 | 1.000 | 0.980 | 0.940 | 0.980 | 0.527 |
| query suffix K1 | 0.980 | 1.000 | 1.000 | 0.980 | 0.940 | 0.980 | 0.527 |
| random suffix K1 | 0.964 | 0.960 | 0.940 | 0.960 | 0.980 | 0.980 | 0.506 |

## Cross-Model Sanity, Mistral-7B-Instruct-v0.3

| method | answer equiv | gold EM | gold F1 | changed+wrong | patch ratio | avg KL |
|---|---:|---:|---:|---:|---:|---:|
| prefix naive | 0.312 | 0.204 | 0.453 | 161 | 0.000 | 1.261 |
| oracle suffix closure | 0.992 | 0.396 | 0.614 | 1 | 0.783 | 0.0002 |
| query suffix K1 | 0.908 | 0.392 | 0.616 | 18 | 0.679 | 0.075 |
| query suffix K2 | 0.996 | 0.392 | 0.612 | 1 | 0.872 | 0.00004 |
| random suffix K1 | 0.872 | 0.388 | 0.610 | 27 | 0.668 | 0.047 |
| random suffix K2 | 1.000 | 0.392 | 0.612 | 0 | 0.850 | 0.00005 |
| risk suffix K1 | 0.852 | 0.376 | 0.607 | 31 | 0.668 | 0.080 |
| hybrid query+risk K1 | 0.928 | 0.388 | 0.613 | 14 | 0.790 | 0.072 |
| risk suffix K2 | 0.996 | 0.392 | 0.612 | 1 | 0.879 | 0.00011 |

## Local Recompute Ablation, 2Wiki-100, Qwen2.5-7B-Instruct

| method | answer equiv | gold EM | gold F1 | changed+wrong | patch ratio | avg KL |
|---|---:|---:|---:|---:|---:|---:|
| prefix naive | 0.350 | 0.320 | 0.392 | 57 | 0.000 | 4.974 |
| risk doc K1 | 0.380 | 0.350 | 0.436 | 54 | 0.226 | 4.336 |
| risk downstream w2 K1 | 0.450 | 0.390 | 0.475 | 45 | 0.419 | 3.604 |
| risk downstream w3 K1 | 0.570 | 0.380 | 0.466 | 37 | 0.586 | 2.659 |
| risk downstream w4 K1 | 0.790 | 0.390 | 0.483 | 18 | 0.729 | 1.082 |
| risk suffix K1 | 0.970 | 0.410 | 0.495 | 2 | 0.793 | 0.299 |

## External Full-Prefill-Correct Subsets, Qwen2.5-7B-Instruct

| dataset subset | method | n | answer equiv | gold EM | changed+wrong | repair rate | patch ratio |
|---|---|---:|---:|---:|---:|---:|---:|
| HotpotQA exact | prefix naive | 272 | 0.566 | 0.566 | 118 | 0.000 | 0.000 |
| HotpotQA exact | random suffix K2 | 272 | 0.949 | 0.949 | 14 | 0.890 | 0.811 |
| HotpotQA exact | risk suffix K1 | 272 | 0.996 | 0.996 | 1 | 0.992 | 0.894 |
| HotpotQA exact | risk suffix K2 | 272 | 1.000 | 1.000 | 0 | 1.000 | 0.949 |
| 2Wiki exact | prefix naive | 226 | 0.518 | 0.518 | 109 | 0.000 | 0.000 |
| 2Wiki exact | random suffix K2 | 226 | 0.885 | 0.885 | 26 | 0.862 | 0.709 |
| 2Wiki exact | risk suffix K1 | 226 | 0.965 | 0.965 | 8 | 0.954 | 0.807 |
| 2Wiki exact | hybrid query+risk K1 | 226 | 0.969 | 0.969 | 7 | 0.963 | 0.846 |
| 2Wiki exact | risk suffix K2 | 226 | 0.991 | 0.991 | 2 | 0.982 | 0.921 |
