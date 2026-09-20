# Held-Out Method Calibration

| target budget | selection counts | test answer eq | 95% split interval | changed+wrong | patch ratio | KL |
|---:|---|---:|---:|---:|---:|---:|
| 0.82 | `{"hybrid_query_risk_union_suffix_k1": 6, "query_similarity_suffix_closure_k2": 6, "risk_guided_margin_adaptive_suffix_m0_05": 1, "risk_guided_suffix_closure_k1": 146, "risk_guided_suffix_closure_k2": 41}` | 0.9728 | [0.9628, 0.9886] | 0.0216 | 0.8416 | 0.0833 |
| 0.85 | `{"hybrid_query_risk_union_suffix_k1": 53, "risk_guided_margin_adaptive_suffix_m0_05": 22, "risk_guided_suffix_closure_k1": 125}` | 0.9705 | [0.9600, 0.9800] | 0.0239 | 0.8238 | 0.0867 |
| 0.89 | `{"hybrid_query_risk_union_suffix_k1": 44, "query_similarity_suffix_closure_k2": 57, "risk_guided_margin_adaptive_suffix_m0_05": 19, "risk_guided_suffix_closure_k1": 80}` | 0.9697 | [0.9600, 0.9772] | 0.0253 | 0.8423 | 0.1011 |
| 0.94 | `{"hybrid_query_risk_union_suffix_k1": 12, "query_similarity_suffix_closure_k2": 20, "risk_guided_margin_adaptive_suffix_m0_05": 4, "risk_guided_suffix_closure_k1": 16, "risk_guided_suffix_closure_k2": 148}` | 0.9792 | [0.9600, 0.9886] | 0.0164 | 0.9080 | 0.0499 |
