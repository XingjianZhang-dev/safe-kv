# Bootstrap Answer-Eval Confidence Intervals

## Method-Level 95% CIs

| method | metric | point | ci low | ci high | n |
|---|---|---:|---:|---:|---:|
| prefix_conditioned_naive_global | answer_equivalence | 0.3120 | 0.2560 | 0.3680 | 250 |
| prefix_conditioned_naive_global | gold_em | 0.2040 | 0.1560 | 0.2560 | 250 |
| prefix_conditioned_naive_global | gold_f1 | 0.4528 | 0.4105 | 0.4947 | 250 |
| prefix_conditioned_naive_global | changed_wrong_rate | 0.6440 | 0.5840 | 0.7000 | 250 |
| prefix_conditioned_naive_global | patch_ratio | 0.0000 | 0.0000 | 0.0000 | 250 |
| prefix_conditioned_naive_global | avg_kl | 1.2614 | 0.9545 | 1.5902 | 250 |
| query_similarity_suffix_closure_k1 | answer_equivalence | 0.9080 | 0.8720 | 0.9440 | 250 |
| query_similarity_suffix_closure_k1 | gold_em | 0.3920 | 0.3320 | 0.4520 | 250 |
| query_similarity_suffix_closure_k1 | gold_f1 | 0.6161 | 0.5729 | 0.6565 | 250 |
| query_similarity_suffix_closure_k1 | changed_wrong_rate | 0.0720 | 0.0400 | 0.1040 | 250 |
| query_similarity_suffix_closure_k1 | patch_ratio | 0.6794 | 0.6446 | 0.7147 | 250 |
| query_similarity_suffix_closure_k1 | avg_kl | 0.0749 | 0.0209 | 0.1503 | 250 |
| risk_guided_suffix_closure_k1 | answer_equivalence | 0.8520 | 0.8080 | 0.8920 | 250 |
| risk_guided_suffix_closure_k1 | gold_em | 0.3760 | 0.3160 | 0.4360 | 250 |
| risk_guided_suffix_closure_k1 | gold_f1 | 0.6065 | 0.5633 | 0.6468 | 250 |
| risk_guided_suffix_closure_k1 | changed_wrong_rate | 0.1240 | 0.0840 | 0.1680 | 250 |
| risk_guided_suffix_closure_k1 | patch_ratio | 0.6683 | 0.6352 | 0.7015 | 250 |
| risk_guided_suffix_closure_k1 | avg_kl | 0.0801 | 0.0256 | 0.1554 | 250 |
| hybrid_query_risk_union_suffix_k1 | answer_equivalence | 0.9280 | 0.8960 | 0.9560 | 250 |
| hybrid_query_risk_union_suffix_k1 | gold_em | 0.3880 | 0.3280 | 0.4480 | 250 |
| hybrid_query_risk_union_suffix_k1 | gold_f1 | 0.6127 | 0.5693 | 0.6535 | 250 |
| hybrid_query_risk_union_suffix_k1 | changed_wrong_rate | 0.0560 | 0.0280 | 0.0880 | 250 |
| hybrid_query_risk_union_suffix_k1 | patch_ratio | 0.7903 | 0.7599 | 0.8200 | 250 |
| hybrid_query_risk_union_suffix_k1 | avg_kl | 0.0718 | 0.0176 | 0.1471 | 250 |
| query_similarity_suffix_closure_k2 | answer_equivalence | 0.9960 | 0.9880 | 1.0000 | 250 |
| query_similarity_suffix_closure_k2 | gold_em | 0.3920 | 0.3320 | 0.4520 | 250 |
| query_similarity_suffix_closure_k2 | gold_f1 | 0.6122 | 0.5685 | 0.6539 | 250 |
| query_similarity_suffix_closure_k2 | changed_wrong_rate | 0.0040 | 0.0000 | 0.0120 | 250 |
| query_similarity_suffix_closure_k2 | patch_ratio | 0.8720 | 0.8500 | 0.8934 | 250 |
| query_similarity_suffix_closure_k2 | avg_kl | 0.0000 | 0.0000 | 0.0001 | 250 |
| random_suffix_closure_k2_seeded | answer_equivalence | 1.0000 | 1.0000 | 1.0000 | 250 |
| random_suffix_closure_k2_seeded | gold_em | 0.3920 | 0.3320 | 0.4520 | 250 |
| random_suffix_closure_k2_seeded | gold_f1 | 0.6122 | 0.5685 | 0.6539 | 250 |
| random_suffix_closure_k2_seeded | changed_wrong_rate | 0.0000 | 0.0000 | 0.0000 | 250 |
| random_suffix_closure_k2_seeded | patch_ratio | 0.8499 | 0.8277 | 0.8722 | 250 |
| random_suffix_closure_k2_seeded | avg_kl | 0.0000 | 0.0000 | 0.0001 | 250 |
| risk_guided_suffix_closure_k2 | answer_equivalence | 0.9960 | 0.9880 | 1.0000 | 250 |
| risk_guided_suffix_closure_k2 | gold_em | 0.3920 | 0.3320 | 0.4520 | 250 |
| risk_guided_suffix_closure_k2 | gold_f1 | 0.6122 | 0.5685 | 0.6539 | 250 |
| risk_guided_suffix_closure_k2 | changed_wrong_rate | 0.0040 | 0.0000 | 0.0120 | 250 |
| risk_guided_suffix_closure_k2 | patch_ratio | 0.8792 | 0.8582 | 0.8995 | 250 |
| risk_guided_suffix_closure_k2 | avg_kl | 0.0001 | 0.0000 | 0.0003 | 250 |

## Pairwise Delta CIs

| left - right | metric | delta | ci low | ci high | P(delta<=0) |
|---|---|---:|---:|---:|---:|
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | answer_equivalence | 0.0200 | 0.0040 | 0.0400 | 0.0062 |
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | gold_em | -0.0040 | -0.0120 | 0.0000 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | gold_f1 | -0.0034 | -0.0073 | -0.0004 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | changed_wrong_rate | -0.0160 | -0.0320 | -0.0040 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | patch_ratio | 0.1108 | 0.0856 | 0.1382 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - query_similarity_suffix_closure_k1 | avg_kl | -0.0031 | -0.0073 | -0.0007 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | answer_equivalence | 0.0760 | 0.0480 | 0.1080 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | gold_em | 0.0120 | -0.0080 | 0.0320 | 0.1674 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | gold_f1 | 0.0061 | -0.0057 | 0.0198 | 0.1814 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | changed_wrong_rate | -0.0680 | -0.1000 | -0.0400 | 1.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | patch_ratio | 0.1220 | 0.0959 | 0.1494 | 0.0000 |
| hybrid_query_risk_union_suffix_k1 - risk_guided_suffix_closure_k1 | avg_kl | -0.0082 | -0.0187 | -0.0018 | 1.0000 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | answer_equivalence | 0.0680 | 0.0400 | 0.1000 | 0.0000 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | gold_em | 0.0040 | -0.0200 | 0.0280 | 0.4346 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | gold_f1 | -0.0005 | -0.0183 | 0.0169 | 0.5280 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | changed_wrong_rate | -0.0520 | -0.0800 | -0.0280 | 1.0000 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | patch_ratio | 0.0817 | 0.0544 | 0.1103 | 0.0000 |
| query_similarity_suffix_closure_k2 - hybrid_query_risk_union_suffix_k1 | avg_kl | -0.0718 | -0.1471 | -0.0175 | 1.0000 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | answer_equivalence | 0.0720 | 0.0440 | 0.1040 | 0.0000 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | gold_em | 0.0040 | -0.0200 | 0.0280 | 0.4346 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | gold_f1 | -0.0005 | -0.0183 | 0.0169 | 0.5280 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | changed_wrong_rate | -0.0560 | -0.0880 | -0.0280 | 1.0000 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | patch_ratio | 0.0596 | 0.0221 | 0.0979 | 0.0006 |
| random_suffix_closure_k2_seeded - hybrid_query_risk_union_suffix_k1 | avg_kl | -0.0718 | -0.1471 | -0.0175 | 1.0000 |
