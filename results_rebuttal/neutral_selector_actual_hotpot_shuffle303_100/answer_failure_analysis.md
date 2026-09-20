# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.900 | 0.480 | 0.628 | 9 | 0.712 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.940 | 0.490 | 0.650 | 6 | 0.847 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.830 | 0.470 | 0.609 | 14 | 0.549 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.930 | 0.480 | 0.643 | 6 | 0.755 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_hotpotqa | 0.900 | 0.480 | 9 |
| actual_recompute::query_similarity_suffix_closure_k2::external_hotpotqa | 0.940 | 0.490 | 6 |
| actual_recompute::risk_guided_suffix_closure_k1::external_hotpotqa | 0.830 | 0.470 | 14 |
| actual_recompute::risk_guided_suffix_closure_k2::external_hotpotqa | 0.930 | 0.480 | 6 |

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
