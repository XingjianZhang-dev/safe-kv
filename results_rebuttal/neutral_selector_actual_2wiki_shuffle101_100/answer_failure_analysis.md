# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.810 | 0.390 | 0.497 | 16 | 0.710 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.930 | 0.410 | 0.514 | 6 | 0.854 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.720 | 0.430 | 0.531 | 20 | 0.622 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.890 | 0.400 | 0.507 | 9 | 0.801 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_2wiki | 0.810 | 0.390 | 16 |
| actual_recompute::query_similarity_suffix_closure_k2::external_2wiki | 0.930 | 0.410 | 6 |
| actual_recompute::risk_guided_suffix_closure_k1::external_2wiki | 0.720 | 0.430 | 20 |
| actual_recompute::risk_guided_suffix_closure_k2::external_2wiki | 0.890 | 0.400 | 9 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
