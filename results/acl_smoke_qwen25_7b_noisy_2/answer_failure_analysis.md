# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 1.000 | 1.000 | 0 | 0.000 |
| oracle_evidence_doc_patch | 1.000 | 1.000 | 1.000 | 0 | 0.250 |
| prefix_conditioned_naive_global | 0.500 | 0.500 | 0.500 | 1 | 0.000 |
| random_doc_patch_k2_seeded | 1.000 | 1.000 | 1.000 | 0 | 0.608 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::single_evidence | 0.500 | 0.500 | 1 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| single_0000_noisy | single_evidence | 4.23624 | `Mira Solen` | `The document does not provide a clear answer to who calibrated the Valen device.` | `Mira Solen` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| single_0000_noisy | single_evidence | 0 | `Mira Solen` | `Mira Solen` | `Mira Solen` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| single_0000_noisy | single_evidence | 0 | `Mira Solen` | `Mira Solen` | `Mira Solen` |
