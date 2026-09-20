# Bootstrap Answer-Eval Confidence Intervals

## Method-Level 95% CIs

| method | metric | point | ci low | ci high | n |
|---|---|---:|---:|---:|---:|
| prefix_conditioned_naive_global | answer_equivalence | 0.3780 | 0.3360 | 0.4200 | 500 |
| prefix_conditioned_naive_global | gold_em | 0.3120 | 0.2720 | 0.3540 | 500 |
| prefix_conditioned_naive_global | gold_f1 | 0.3864 | 0.3470 | 0.4265 | 500 |
| prefix_conditioned_naive_global | changed_wrong_rate | 0.5440 | 0.5000 | 0.5880 | 500 |
| prefix_conditioned_naive_global | patch_ratio | 0.0000 | 0.0000 | 0.0000 | 500 |
| prefix_conditioned_naive_global | avg_kl | 4.2422 | 3.7851 | 4.7224 | 500 |
| query_similarity_suffix_closure_k2 | answer_equivalence | 0.9720 | 0.9560 | 0.9860 | 500 |
| query_similarity_suffix_closure_k2 | gold_em | 0.4440 | 0.4000 | 0.4880 | 500 |
| query_similarity_suffix_closure_k2 | gold_f1 | 0.5381 | 0.4975 | 0.5782 | 500 |
| query_similarity_suffix_closure_k2 | changed_wrong_rate | 0.0240 | 0.0120 | 0.0380 | 500 |
| query_similarity_suffix_closure_k2 | patch_ratio | 0.8845 | 0.8716 | 0.8966 | 500 |
| query_similarity_suffix_closure_k2 | avg_kl | 0.1256 | 0.0375 | 0.2427 | 500 |
| random_suffix_closure_k2_seeded | answer_equivalence | 0.8340 | 0.8000 | 0.8660 | 500 |
| random_suffix_closure_k2_seeded | gold_em | 0.4340 | 0.3900 | 0.4780 | 500 |
| random_suffix_closure_k2_seeded | gold_f1 | 0.5172 | 0.4754 | 0.5586 | 500 |
| random_suffix_closure_k2_seeded | changed_wrong_rate | 0.1320 | 0.1040 | 0.1620 | 500 |
| random_suffix_closure_k2_seeded | patch_ratio | 0.7106 | 0.6880 | 0.7334 | 500 |
| random_suffix_closure_k2_seeded | avg_kl | 0.6711 | 0.4888 | 0.8827 | 500 |
| risk_guided_suffix_closure_k1 | answer_equivalence | 0.9700 | 0.9540 | 0.9840 | 500 |
| risk_guided_suffix_closure_k1 | gold_em | 0.4420 | 0.3980 | 0.4860 | 500 |
| risk_guided_suffix_closure_k1 | gold_f1 | 0.5361 | 0.4946 | 0.5764 | 500 |
| risk_guided_suffix_closure_k1 | changed_wrong_rate | 0.0240 | 0.0120 | 0.0380 | 500 |
| risk_guided_suffix_closure_k1 | patch_ratio | 0.8134 | 0.7973 | 0.8293 | 500 |
| risk_guided_suffix_closure_k1 | avg_kl | 0.0976 | 0.0259 | 0.1949 | 500 |
| hybrid_query_risk_union_suffix_k1 | answer_equivalence | 0.9740 | 0.9580 | 0.9860 | 500 |
| hybrid_query_risk_union_suffix_k1 | gold_em | 0.4420 | 0.3980 | 0.4860 | 500 |
| hybrid_query_risk_union_suffix_k1 | gold_f1 | 0.5361 | 0.4953 | 0.5764 | 500 |
| hybrid_query_risk_union_suffix_k1 | changed_wrong_rate | 0.0220 | 0.0100 | 0.0360 | 500 |
| hybrid_query_risk_union_suffix_k1 | patch_ratio | 0.8425 | 0.8275 | 0.8573 | 500 |
| hybrid_query_risk_union_suffix_k1 | avg_kl | 0.0507 | 0.0175 | 0.0926 | 500 |
| risk_guided_suffix_closure_k2 | answer_equivalence | 0.9840 | 0.9720 | 0.9940 | 500 |
| risk_guided_suffix_closure_k2 | gold_em | 0.4520 | 0.4080 | 0.4940 | 500 |
| risk_guided_suffix_closure_k2 | gold_f1 | 0.5465 | 0.5054 | 0.5858 | 500 |
| risk_guided_suffix_closure_k2 | changed_wrong_rate | 0.0120 | 0.0040 | 0.0220 | 500 |
| risk_guided_suffix_closure_k2 | patch_ratio | 0.9287 | 0.9209 | 0.9360 | 500 |
| risk_guided_suffix_closure_k2 | avg_kl | 0.0277 | 0.0029 | 0.0638 | 500 |

## Pairwise Delta CIs

| left - right | metric | delta | ci low | ci high | P(delta<=0) |
|---|---|---:|---:|---:|---:|
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | answer_equivalence | 0.1360 | 0.1040 | 0.1700 | 0.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | gold_em | 0.0080 | -0.0180 | 0.0340 | 0.3064 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | gold_f1 | 0.0190 | -0.0050 | 0.0432 | 0.0626 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.1080 | -0.1400 | -0.0780 | 1.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | patch_ratio | 0.1029 | 0.0767 | 0.1296 | 0.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | avg_kl | -0.5735 | -0.7952 | -0.3743 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | answer_equivalence | 0.1400 | 0.1080 | 0.1740 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | gold_em | 0.0080 | -0.0180 | 0.0340 | 0.3046 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | gold_f1 | 0.0190 | -0.0058 | 0.0431 | 0.0622 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.1100 | -0.1400 | -0.0800 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | patch_ratio | 0.1319 | 0.1063 | 0.1582 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - random_suffix_closure_k2_seeded | avg_kl | -0.6204 | -0.8334 | -0.4345 | 1.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | answer_equivalence | 0.1500 | 0.1180 | 0.1840 | 0.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_em | 0.0180 | -0.0080 | 0.0440 | 0.0948 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_f1 | 0.0293 | 0.0053 | 0.0529 | 0.0072 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.1200 | -0.1500 | -0.0920 | 1.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | patch_ratio | 0.2182 | 0.1943 | 0.2423 | 0.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | avg_kl | -0.6435 | -0.8567 | -0.4594 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | answer_equivalence | 0.0040 | 0.0000 | 0.0100 | 0.1396 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | gold_em | 0.0000 | -0.0060 | 0.0060 | 0.6580 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | gold_f1 | 0.0000 | -0.0060 | 0.0060 | 0.6580 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | changed_wrong_rate | -0.0020 | -0.0060 | 0.0000 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | patch_ratio | 0.0290 | 0.0208 | 0.0378 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | avg_kl | -0.0469 | -0.1329 | -0.0004 | 0.9996 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | answer_equivalence | 0.0100 | -0.0020 | 0.0220 | 0.0648 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | gold_em | 0.0100 | 0.0000 | 0.0200 | 0.0374 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | gold_f1 | 0.0104 | 0.0004 | 0.0207 | 0.0228 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | changed_wrong_rate | -0.0100 | -0.0200 | 0.0000 | 0.9878 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | patch_ratio | 0.0863 | 0.0725 | 0.1002 | 0.0000 |
| risk_guided_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | avg_kl | -0.0230 | -0.0647 | 0.0129 | 0.8892 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | answer_equivalence | 0.1380 | 0.1040 | 0.1740 | 0.0000 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_em | 0.0100 | -0.0160 | 0.0360 | 0.2524 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_f1 | 0.0210 | -0.0032 | 0.0449 | 0.0436 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.1080 | -0.1400 | -0.0780 | 1.0000 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | patch_ratio | 0.1739 | 0.1484 | 0.1991 | 0.0000 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | avg_kl | -0.5455 | -0.7749 | -0.3353 | 1.0000 |
