# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::risk_guided_suffix_closure_k1 | 0.966 | 0.442 | 0.536 | 12 | 0.813 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.984 | 0.452 | 0.546 | 5 | 0.929 |
| risk_guided_suffix_closure_k1 | 0.978 | 0.444 | 0.537 | 8 | 0.813 |
| risk_guided_suffix_closure_k2 | 0.992 | 0.454 | 0.547 | 2 | 0.929 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::risk_guided_suffix_closure_k1::external_2wiki | 0.966 | 0.442 | 12 |
| actual_recompute::risk_guided_suffix_closure_k2::external_2wiki | 0.984 | 0.452 | 5 |
| risk_guided_suffix_closure_k1::external_2wiki | 0.978 | 0.444 | 8 |
| risk_guided_suffix_closure_k2::external_2wiki | 0.992 | 0.454 | 2 |

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
