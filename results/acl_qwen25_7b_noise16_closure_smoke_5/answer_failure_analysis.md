# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| oracle_evidence_doc_adjacent_patch | 1.000 | 1.000 | 1.000 | 0 | 0.165 |
| oracle_evidence_doc_patch | 1.000 | 1.000 | 1.000 | 0 | 0.082 |
| oracle_evidence_doc_suffix_closure_patch | 1.000 | 1.000 | 1.000 | 0 | 0.496 |
| oracle_evidence_span_window_16 | 1.000 | 1.000 | 1.000 | 0 | 0.052 |
| oracle_support_and_conflict_suffix_patch | 1.000 | 1.000 | 1.000 | 0 | 0.041 |
| prefix_conditioned_naive_global | 0.600 | 0.600 | 0.714 | 2 | 0.000 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch | 0.800 | 0.800 | 0.800 | 1 | 0.041 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_adjacent_patch::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_span_window_16::single_evidence | 1.000 | 1.000 | 0 |
| oracle_support_and_conflict_suffix_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::single_evidence | 0.600 | 0.600 | 2 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::single_evidence | 0.800 | 0.800 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| single_0002_noise16 | single_evidence | 3.44856 | `Sera Mavin` | `The Zorvian device was calibrated by an unspecified individual, likely referring to` | `Sera Mavin` |
| single_0003_noise16 | single_evidence | 0.00854742 | `Tovan Reed` | `Tovan Reed calibrated the Ralvex device.` | `Tovan Reed` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| single_0002_noise16 | single_evidence | 9.73562e-05 | `Sera Mavin` | `Sera Mavin` | `Sera Mavin` |
| single_0003_noise16 | single_evidence | 0.000544243 | `Tovan Reed` | `Tovan Reed` | `Tovan Reed` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
