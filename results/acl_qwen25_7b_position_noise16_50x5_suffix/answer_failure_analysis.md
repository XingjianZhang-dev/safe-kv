# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.968 | 0.989 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.840 | 0.872 | 0.899 | 32 | 0.081 |
| oracle_evidence_doc_suffix_closure_patch | 0.980 | 0.980 | 0.993 | 1 | 0.527 |
| prefix_conditioned_naive_global | 0.632 | 0.648 | 0.743 | 88 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.980 | 0.980 | 0.993 | 1 | 0.527 |
| random_suffix_closure_k1_seeded | 0.964 | 0.972 | 0.985 | 4 | 0.506 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::single_evidence | 1.000 | 0.968 | 0 |
| oracle_evidence_doc_patch::single_evidence | 0.840 | 0.872 | 32 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 0.980 | 0.980 | 1 |
| prefix_conditioned_naive_global::single_evidence | 0.632 | 0.648 | 88 |
| query_similarity_suffix_closure_k1::single_evidence | 0.980 | 0.980 | 1 |
| random_suffix_closure_k1_seeded::single_evidence | 0.964 | 0.972 | 4 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| single_0041_noisy_noise16_pos_first | single_evidence | 21.8791 | `Orin Vale` | `The documents do not provide a specific person who calibrated the Meros device. The` | `Orin Vale` |
| single_0047_noisy_noise16_pos_early | single_evidence | 13.8731 | `Priya Holt` | `The document does not provide a clear answer to who calibrated the Veyra device` | `Priya Holt` |
| single_0027_noisy_noise16_pos_first | single_evidence | 11.7977 | `Tovan Reed` | `The document does not provide a clear answer to who calibrated the Veyra device` | `Tovan Reed` |
| single_0041_noisy_noise16_pos_early | single_evidence | 9.20236 | `Orin Vale` | `The documents do not provide a clear answer to who calibrated the Meros device.` | `Orin Vale` |
| single_0011_noisy_noise16_pos_first | single_evidence | 8.68245 | `Priya Holt` | `Based on the information provided in the document, the answer to "Who calibrated the` | `Priya Holt` |
| single_0036_noisy_noise16_pos_early | single_evidence | 8.56623 | `Mira Solen` | `The documents do not provide a clear answer to who calibrated the Caldrin device` | `Mira Solen` |
| single_0023_noisy_noise16_pos_early | single_evidence | 8.45204 | `Priya Holt` | `The document does not provide any information about who calibrated the Ralvex device` | `Priya Holt` |
| single_0024_noisy_noise16_pos_first | single_evidence | 7.27889 | `Mira Solen` | `The documents do not provide a clear answer to who calibrated the Fenric device.` | `Mira Solen` |
| single_0030_noisy_noise16_pos_early | single_evidence | 7.11251 | `Nadia Voss` | `The documents do not provide a clear answer to who calibrated the Valen device.` | `Nadia Voss` |
| single_0048_noisy_noise16_pos_first | single_evidence | 6.55265 | `Mira Solen` | `The document does not provide any information about who calibrated the Harrow device. The` | `Mira Solen` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| single_0047_noisy_noise16_pos_early | single_evidence | 0.0043627 | `Priya Holt` | `Priya Holt` | `Priya Holt` |
| single_0041_noisy_noise16_pos_early | single_evidence | 0.00171915 | `Orin Vale` | `Orin Vale` | `Orin Vale` |
| single_0036_noisy_noise16_pos_early | single_evidence | 0.0026138 | `Mira Solen` | `Mira Solen` | `Mira Solen` |
| single_0023_noisy_noise16_pos_early | single_evidence | 0.00136385 | `Priya Holt` | `Priya Holt` | `Priya Holt` |
| single_0030_noisy_noise16_pos_early | single_evidence | 0.000822279 | `Nadia Voss` | `Nadia Voss` | `Nadia Voss` |
| single_0011_noisy_noise16_pos_middle | single_evidence | 0.174492 | `Priya Holt` | `Priya Holt` | `Priya Holt` |
| single_0011_noisy_noise16_pos_early | single_evidence | 0.0027749 | `Priya Holt` | `Priya Holt` | `Priya Holt` |
| single_0020_noisy_noise16_pos_early | single_evidence | 0.000472754 | `Ilya Marr` | `Ilya Marr` | `Ilya Marr` |
| single_0008_noisy_noise16_pos_early | single_evidence | 0.0223741 | `Ilya Marr` | `Ilya Marr` | `Ilya Marr` |
| single_0023_noisy_noise16_pos_middle | single_evidence | 0.00128585 | `Priya Holt` | `Priya Holt` | `Priya Holt` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
