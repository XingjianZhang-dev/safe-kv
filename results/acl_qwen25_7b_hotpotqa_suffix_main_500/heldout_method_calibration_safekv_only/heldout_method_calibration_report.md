# Held-Out Method Calibration

| target budget | selection counts | test answer eq | 95% split interval | changed+wrong | patch ratio | KL |
|---:|---|---:|---:|---:|---:|---:|
| 0.82 | `{"risk_guided_suffix_closure_k1": 153, "risk_guided_suffix_closure_k2": 47}` | 0.9958 | [0.9943, 1.0000] | 0.0042 | 0.9048 | 0.0096 |
| 0.89 | `{"query_similarity_suffix_closure_k2": 86, "risk_guided_suffix_closure_k1": 107, "risk_guided_suffix_closure_k2": 7}` | 0.9799 | [0.9514, 1.0000] | 0.0178 | 0.8906 | 0.0488 |
| 0.95 | `{"risk_guided_suffix_closure_k1": 166, "risk_guided_suffix_closure_k2": 34}` | 0.9958 | [0.9943, 1.0000] | 0.0042 | 0.9011 | 0.0096 |
