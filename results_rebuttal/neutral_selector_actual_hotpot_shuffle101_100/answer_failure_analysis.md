# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.920 | 0.550 | 0.688 | 7 | 0.739 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.970 | 0.560 | 0.701 | 3 | 0.880 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.810 | 0.470 | 0.625 | 18 | 0.579 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.900 | 0.510 | 0.660 | 10 | 0.780 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_hotpotqa | 0.920 | 0.550 | 7 |
| actual_recompute::query_similarity_suffix_closure_k2::external_hotpotqa | 0.970 | 0.560 | 3 |
| actual_recompute::risk_guided_suffix_closure_k1::external_hotpotqa | 0.810 | 0.470 | 18 |
| actual_recompute::risk_guided_suffix_closure_k2::external_hotpotqa | 0.900 | 0.510 | 10 |

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
