# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.880 | 0.450 | 0.541 | 10 | 0.733 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.960 | 0.500 | 0.577 | 2 | 0.870 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.790 | 0.440 | 0.533 | 18 | 0.612 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.910 | 0.490 | 0.577 | 6 | 0.798 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_2wiki | 0.880 | 0.450 | 10 |
| actual_recompute::query_similarity_suffix_closure_k2::external_2wiki | 0.960 | 0.500 | 2 |
| actual_recompute::risk_guided_suffix_closure_k1::external_2wiki | 0.790 | 0.440 | 18 |
| actual_recompute::risk_guided_suffix_closure_k2::external_2wiki | 0.910 | 0.490 | 6 |

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
