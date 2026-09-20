# Bootstrap Answer-Eval Confidence Intervals

## Method-Level 95% CIs

| method | metric | point | ci low | ci high | n |
|---|---|---:|---:|---:|---:|
| prefix_conditioned_naive_global | answer_equivalence | 0.4720 | 0.4280 | 0.5160 | 500 |
| prefix_conditioned_naive_global | gold_em | 0.3540 | 0.3120 | 0.3940 | 500 |
| prefix_conditioned_naive_global | gold_f1 | 0.4891 | 0.4495 | 0.5274 | 500 |
| prefix_conditioned_naive_global | changed_wrong_rate | 0.4820 | 0.4380 | 0.5240 | 500 |
| prefix_conditioned_naive_global | patch_ratio | 0.0000 | 0.0000 | 0.0000 | 500 |
| prefix_conditioned_naive_global | avg_kl | 3.0533 | 2.6783 | 3.4539 | 500 |
| query_similarity_suffix_closure_k2 | answer_equivalence | 0.9580 | 0.9400 | 0.9760 | 500 |
| query_similarity_suffix_closure_k2 | gold_em | 0.5340 | 0.4880 | 0.5780 | 500 |
| query_similarity_suffix_closure_k2 | gold_f1 | 0.7043 | 0.6696 | 0.7371 | 500 |
| query_similarity_suffix_closure_k2 | changed_wrong_rate | 0.0360 | 0.0200 | 0.0540 | 500 |
| query_similarity_suffix_closure_k2 | patch_ratio | 0.8826 | 0.8723 | 0.8925 | 500 |
| query_similarity_suffix_closure_k2 | avg_kl | 0.1056 | 0.0535 | 0.1639 | 500 |
| random_suffix_closure_k2_seeded | answer_equivalence | 0.9180 | 0.8920 | 0.9420 | 500 |
| random_suffix_closure_k2_seeded | gold_em | 0.5280 | 0.4840 | 0.5720 | 500 |
| random_suffix_closure_k2_seeded | gold_f1 | 0.6955 | 0.6602 | 0.7292 | 500 |
| random_suffix_closure_k2_seeded | changed_wrong_rate | 0.0700 | 0.0480 | 0.0940 | 500 |
| random_suffix_closure_k2_seeded | patch_ratio | 0.8139 | 0.7972 | 0.8291 | 500 |
| random_suffix_closure_k2_seeded | avg_kl | 0.3461 | 0.2020 | 0.5192 | 500 |
| risk_guided_suffix_closure_k1 | answer_equivalence | 0.9960 | 0.9900 | 1.0000 | 500 |
| risk_guided_suffix_closure_k1 | gold_em | 0.5420 | 0.4960 | 0.5860 | 500 |
| risk_guided_suffix_closure_k1 | gold_f1 | 0.7081 | 0.6736 | 0.7409 | 500 |
| risk_guided_suffix_closure_k1 | changed_wrong_rate | 0.0040 | 0.0000 | 0.0100 | 500 |
| risk_guided_suffix_closure_k1 | patch_ratio | 0.8916 | 0.8841 | 0.8993 | 500 |
| risk_guided_suffix_closure_k1 | avg_kl | 0.0088 | 0.0000 | 0.0262 | 500 |
| risk_guided_suffix_closure_k2 | answer_equivalence | 0.9980 | 0.9940 | 1.0000 | 500 |
| risk_guided_suffix_closure_k2 | gold_em | 0.5440 | 0.4980 | 0.5880 | 500 |
| risk_guided_suffix_closure_k2 | gold_f1 | 0.7094 | 0.6750 | 0.7424 | 500 |
| risk_guided_suffix_closure_k2 | changed_wrong_rate | 0.0020 | 0.0000 | 0.0060 | 500 |
| risk_guided_suffix_closure_k2 | patch_ratio | 0.9478 | 0.9429 | 0.9523 | 500 |
| risk_guided_suffix_closure_k2 | avg_kl | 0.0000 | 0.0000 | 0.0000 | 500 |

## Pairwise Delta CIs

| left - right | metric | delta | ci low | ci high | P(delta<=0) |
|---|---|---:|---:|---:|---:|
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | answer_equivalence | 0.0780 | 0.0540 | 0.1040 | 0.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | gold_em | 0.0140 | -0.0040 | 0.0320 | 0.0722 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | gold_f1 | 0.0125 | -0.0038 | 0.0305 | 0.0708 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.0660 | -0.0900 | -0.0440 | 1.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | patch_ratio | 0.0777 | 0.0612 | 0.0959 | 0.0000 |
| risk_guided_suffix_closure_k1 - random_suffix_closure_k2_seeded | avg_kl | -0.3373 | -0.5130 | -0.1921 | 1.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | answer_equivalence | 0.0800 | 0.0560 | 0.1040 | 0.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_em | 0.0160 | -0.0020 | 0.0340 | 0.0426 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_f1 | 0.0138 | -0.0021 | 0.0315 | 0.0464 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.0680 | -0.0920 | -0.0460 | 1.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | patch_ratio | 0.1339 | 0.1184 | 0.1510 | 0.0000 |
| risk_guided_suffix_closure_k2 - random_suffix_closure_k2_seeded | avg_kl | -0.3461 | -0.5192 | -0.2020 | 1.0000 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | answer_equivalence | 0.0400 | 0.0140 | 0.0680 | 0.0022 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_em | 0.0060 | -0.0140 | 0.0260 | 0.3122 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | gold_f1 | 0.0088 | -0.0093 | 0.0279 | 0.1786 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | changed_wrong_rate | -0.0340 | -0.0580 | -0.0100 | 0.9984 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | patch_ratio | 0.0687 | 0.0512 | 0.0867 | 0.0000 |
| query_similarity_suffix_closure_k2 - random_suffix_closure_k2_seeded | avg_kl | -0.2405 | -0.4171 | -0.0858 | 0.9994 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | answer_equivalence | 0.0020 | 0.0000 | 0.0060 | 0.3780 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | gold_em | 0.0020 | 0.0000 | 0.0060 | 0.3780 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | gold_f1 | 0.0013 | 0.0000 | 0.0040 | 0.3780 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | changed_wrong_rate | -0.0020 | -0.0060 | 0.0000 | 1.0000 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | patch_ratio | 0.0562 | 0.0489 | 0.0634 | 0.0000 |
| risk_guided_suffix_closure_k2 - risk_guided_suffix_closure_k1 | avg_kl | -0.0088 | -0.0262 | -0.0000 | 0.9992 |
