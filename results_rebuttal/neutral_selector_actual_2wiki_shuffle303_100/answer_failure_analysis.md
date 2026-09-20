# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.840 | 0.400 | 0.506 | 16 | 0.698 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.970 | 0.480 | 0.577 | 2 | 0.867 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.810 | 0.390 | 0.494 | 19 | 0.632 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.930 | 0.450 | 0.547 | 7 | 0.803 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_2wiki | 0.840 | 0.400 | 16 |
| actual_recompute::query_similarity_suffix_closure_k2::external_2wiki | 0.970 | 0.480 | 2 |
| actual_recompute::risk_guided_suffix_closure_k1::external_2wiki | 0.810 | 0.390 | 19 |
| actual_recompute::risk_guided_suffix_closure_k2::external_2wiki | 0.930 | 0.450 | 7 |

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
