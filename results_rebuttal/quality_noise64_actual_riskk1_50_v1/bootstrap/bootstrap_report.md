# Bootstrap Answer-Eval Confidence Intervals

## Method-Level 95% CIs

| method | metric | point | ci low | ci high | n |
|---|---|---:|---:|---:|---:|
| risk_guided_suffix_closure_k1 | answer_equivalence | 0.6400 | 0.5000 | 0.7600 | 50 |
| risk_guided_suffix_closure_k1 | gold_em | 0.6000 | 0.4600 | 0.7200 | 50 |
| risk_guided_suffix_closure_k1 | gold_f1 | 0.6613 | 0.5427 | 0.7737 | 50 |
| risk_guided_suffix_closure_k1 | changed_wrong_rate | 0.3600 | 0.2400 | 0.5000 | 50 |
| risk_guided_suffix_closure_k1 | patch_ratio | 0.5192 | 0.4422 | 0.5997 | 50 |
| risk_guided_suffix_closure_k1 | avg_kl | 2.2311 | 0.9938 | 3.6534 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | answer_equivalence | 0.4400 | 0.3000 | 0.5800 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | gold_em | 0.4400 | 0.3000 | 0.5800 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | gold_f1 | 0.5577 | 0.4441 | 0.6761 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | changed_wrong_rate | 0.5400 | 0.4000 | 0.6800 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | patch_ratio | 0.5192 | 0.4422 | 0.5997 | 50 |
| actual_recompute::risk_guided_suffix_closure_k1 | avg_kl | 3.5103 | 1.9168 | 5.2347 | 50 |

## Pairwise Delta CIs

| left - right | metric | delta | ci low | ci high | P(delta<=0) |
|---|---|---:|---:|---:|---:|
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | answer_equivalence | 0.2000 | 0.0600 | 0.3400 | 0.0022 |
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | gold_em | 0.1600 | 0.0200 | 0.3000 | 0.0170 |
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | gold_f1 | 0.1036 | -0.0021 | 0.2117 | 0.0270 |
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | changed_wrong_rate | -0.1800 | -0.3200 | -0.0600 | 0.9980 |
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | patch_ratio | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| risk_guided_suffix_closure_k1 - actual_recompute::risk_guided_suffix_closure_k1 | avg_kl | -1.2791 | -2.2361 | -0.4234 | 0.9986 |
