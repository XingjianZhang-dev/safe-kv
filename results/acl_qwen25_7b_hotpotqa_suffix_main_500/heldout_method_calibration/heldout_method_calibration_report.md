# Held-Out Method Calibration

| target budget | selection counts | test answer eq | 95% split interval | changed+wrong | patch ratio | KL |
|---:|---|---:|---:|---:|---:|---:|
| 0.82 | `{"random_suffix_closure_k2_seeded": 146, "risk_guided_suffix_closure_k1": 36, "risk_guided_suffix_closure_k2": 18}` | 0.9402 | [0.9057, 0.9971] | 0.0515 | 0.8419 | 0.2470 |
| 0.89 | `{"query_similarity_suffix_closure_k2": 83, "random_suffix_closure_k2_seeded": 32, "risk_guided_suffix_closure_k1": 85}` | 0.9677 | [0.9057, 0.9971] | 0.0281 | 0.8765 | 0.1027 |
| 0.95 | `{"risk_guided_suffix_closure_k1": 166, "risk_guided_suffix_closure_k2": 34}` | 0.9958 | [0.9943, 1.0000] | 0.0042 | 0.9011 | 0.0096 |
