# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::risk_guided_suffix_closure_k1 | 0.440 | 0.440 | 0.558 | 27 | 0.519 |
| full_prefill | 1.000 | 0.920 | 0.942 | 0 | 0.000 |
| risk_guided_suffix_closure_k1 | 0.640 | 0.600 | 0.661 | 18 | 0.519 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::risk_guided_suffix_closure_k1::boundary_sensitive | 0.600 | 0.600 | 4 |
| actual_recompute::risk_guided_suffix_closure_k1::conflict | 0.400 | 0.400 | 5 |
| actual_recompute::risk_guided_suffix_closure_k1::distractor_heavy | 0.700 | 0.700 | 3 |
| actual_recompute::risk_guided_suffix_closure_k1::multi_hop | 0.100 | 0.100 | 9 |
| actual_recompute::risk_guided_suffix_closure_k1::single_evidence | 0.400 | 0.400 | 6 |
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 0.800 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.800 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_suffix_closure_k1::boundary_sensitive | 0.900 | 0.900 | 1 |
| risk_guided_suffix_closure_k1::conflict | 0.300 | 0.100 | 7 |
| risk_guided_suffix_closure_k1::distractor_heavy | 0.900 | 0.900 | 1 |
| risk_guided_suffix_closure_k1::multi_hop | 0.300 | 0.300 | 7 |
| risk_guided_suffix_closure_k1::single_evidence | 0.800 | 0.800 | 2 |

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
