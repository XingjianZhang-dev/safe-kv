# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| learned_suffix_closure_k2 | 0.800 | 0.800 | 0.914 | 1 | 0.616 |
| oracle_evidence_doc_suffix_closure_patch | 1.000 | 1.000 | 1.000 | 0 | 0.496 |
| prefix_conditioned_naive_global | 0.600 | 0.600 | 0.714 | 2 | 0.000 |
| query_similarity_suffix_closure_k2 | 1.000 | 1.000 | 1.000 | 0 | 0.627 |
| random_suffix_closure_k2_seeded | 1.000 | 1.000 | 1.000 | 0 | 0.749 |
| risk_guided_suffix_closure_k2 | 1.000 | 1.000 | 1.000 | 0 | 0.797 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| learned_suffix_closure_k2::single_evidence | 0.800 | 0.800 | 1 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::single_evidence | 0.600 | 0.600 | 2 |
| query_similarity_suffix_closure_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_suffix_closure_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_suffix_closure_k2::single_evidence | 1.000 | 1.000 | 0 |

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
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
