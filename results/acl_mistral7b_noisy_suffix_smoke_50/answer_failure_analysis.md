# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.440 | 0.766 | 0 | 0.000 |
| oracle_evidence_doc_suffix_closure_patch | 0.960 | 0.460 | 0.774 | 1 | 0.707 |
| prefix_conditioned_naive_global | 0.360 | 0.100 | 0.600 | 31 | 0.000 |
| random_suffix_closure_k1_seeded | 0.900 | 0.460 | 0.772 | 3 | 0.712 |
| risk_guided_suffix_closure_k1 | 0.900 | 0.440 | 0.767 | 4 | 0.706 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::single_evidence | 1.000 | 0.440 | 0 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 0.960 | 0.460 | 1 |
| prefix_conditioned_naive_global::single_evidence | 0.360 | 0.100 | 31 |
| random_suffix_closure_k1_seeded::single_evidence | 0.900 | 0.460 | 3 |
| risk_guided_suffix_closure_k1::single_evidence | 0.900 | 0.440 | 4 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| single_0039_noisy | single_evidence | 1.89348 | `Tovan Reed calibrated the Nimbar device.` | `The document does not provide information on who calibrated the Nimbar device` | `Tovan Reed` |
| single_0030_noisy | single_evidence | 0.210171 | `Nadia Voss` | `Nadia Voss calibrated the Valen device.` | `Nadia Voss` |
| single_0042_noisy | single_evidence | 0.138098 | `Nadia Voss` | `Nadia Voss calibrated the Zorvian device.` | `Nadia Voss` |
| single_0004_noisy | single_evidence | 0.00418196 | `Lina Kest` | `Lina Kest calibrated the Fenric device.` | `Lina Kest` |
| single_0033_noisy | single_evidence | 0.00336785 | `Vera Noll calibrated the Ralvex device. (From` | `Vera Noll calibrated the Ralvex device.` | `Vera Noll` |
| single_0038_noisy | single_evidence | 0.000761745 | `Sera Mavin in 1983. (From Document` | `Sera Mavin calibrated the Harrow device.` | `Sera Mavin` |
| single_0010_noisy | single_evidence | 0.000752655 | `Jalen Irix` | `Jalen Irix calibrated the Valen device.` | `Jalen Irix` |
| single_0032_noisy | single_evidence | 0.000588329 | `Ilya Marr (from Document 1)` | `Ilya Marr calibrated the Zorvian device.` | `Ilya Marr` |
| single_0016_noisy | single_evidence | 0.000472363 | `Lina Kest` | `Lina Kest calibrated the Caldrin device.` | `Lina Kest` |
| single_0006_noisy | single_evidence | 0.000465318 | `Nadia Voss` | `Nadia Voss calibrated the Caldrin device.` | `Nadia Voss` |

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
