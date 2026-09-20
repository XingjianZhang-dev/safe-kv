# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.910 | 0.510 | 0.665 | 6 | 0.721 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.970 | 0.500 | 0.660 | 3 | 0.869 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.850 | 0.490 | 0.646 | 12 | 0.564 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.920 | 0.490 | 0.650 | 7 | 0.751 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_hotpotqa | 0.910 | 0.510 | 6 |
| actual_recompute::query_similarity_suffix_closure_k2::external_hotpotqa | 0.970 | 0.500 | 3 |
| actual_recompute::risk_guided_suffix_closure_k1::external_hotpotqa | 0.850 | 0.490 | 12 |
| actual_recompute::risk_guided_suffix_closure_k2::external_hotpotqa | 0.920 | 0.490 | 7 |

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
