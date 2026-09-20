# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.940 | 0.640 | 0.764 | 5 | 0.549 |
| full_prefill | 1.000 | 0.640 | 0.765 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.890 | 0.650 | 0.759 | 7 | 0.425 |
| prefix_conditioned_naive_global | 0.680 | 0.660 | 0.720 | 24 | 0.000 |
| query_similarity_doc_patch_k2 | 0.920 | 0.640 | 0.767 | 7 | 0.551 |
| random_doc_patch_k2_seeded | 0.840 | 0.650 | 0.756 | 12 | 0.540 |
| safe_gate_t0.60 | 0.810 | 0.610 | 0.711 | 15 | 0.283 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::conflict | 0.850 | 0.050 | 3 |
| entity_overlap_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::multi_hop | 0.900 | 0.300 | 2 |
| entity_overlap_doc_patch_k2::single_evidence | 0.950 | 0.850 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 0.100 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.300 | 0 |
| full_prefill::single_evidence | 1.000 | 0.800 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::conflict | 0.850 | 0.050 | 3 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.800 | 0.200 | 4 |
| oracle_evidence_doc_patch::single_evidence | 0.800 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::conflict | 0.250 | 0.250 | 12 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.400 | 0.100 | 11 |
| prefix_conditioned_naive_global::single_evidence | 0.750 | 0.950 | 1 |
| query_similarity_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::conflict | 0.750 | 0.050 | 5 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.900 | 0.300 | 2 |
| query_similarity_doc_patch_k2::single_evidence | 0.950 | 0.850 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::conflict | 0.650 | 0.100 | 6 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.650 | 0.250 | 6 |
| random_doc_patch_k2_seeded::single_evidence | 0.900 | 0.900 | 0 |
| safe_gate_t0.60::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::conflict | 0.800 | 0.050 | 4 |
| safe_gate_t0.60::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::multi_hop | 0.450 | 0.100 | 10 |
| safe_gate_t0.60::single_evidence | 0.800 | 0.900 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0003_noisy | multi_hop | 1.6834 | `Lydora` | `Fenric was designed by Orin Vale.` | `Lydora` |
| multihop_0004_noisy | multi_hop | 0.914194 | `Kelminster` | `Nadia Voss` | `Kelminster` |
| multihop_0015_noisy | multi_hop | 0.73527 | `Aster Port` | `The designer of Project Caldrin was born in Aster Port.` | `Aster Port` |
| conflict_0011_noisy | conflict | 0.552486 | `According to the official schedule, the Brevic observatory opens at 11 AM` | `12 AM` | `11 AM` |
| single_0017_noisy | single_evidence | 0.433944 | `The Veyra device was calibrated by Orin Vale in 19` | `Orin Vale` | `Orin Vale` |
| multihop_0006_noisy | multi_hop | 0.404462 | `Ilya Marr was born in Rivenfall` | `Ilya Marr` | `Rivenfall` |
| conflict_0004_noisy | conflict | 0.36932 | `The official schedule states that the Aster Port observatory opens at 8 AM.` | `The Aster Port observatory opens at 11 AM.` | `8 AM` |
| multihop_0000_noisy | multi_hop | 0.36213 | `Sera Mavin was born in Halden.` | `Sera Mavin` | `Halden` |
| multihop_0002_noisy | multi_hop | 0.362029 | `Brevic` | `The designer of Project Ralvex was born in Brevic.` | `Brevic` |
| multihop_0008_noisy | multi_hop | 0.325648 | `Velora` | `Jalen Irix` | `Velora` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| conflict_0011_noisy | conflict | 0.0185028 | `According to the official schedule, the Brevic observatory opens at 11 AM` | `According to the official schedule, the Brevic observatory opens at 11 AM` | `11 AM` |
| conflict_0004_noisy | conflict | 0.0311141 | `The official schedule states that the Aster Port observatory opens at 8 AM.` | `The official schedule states that the Aster Port observatory opens at 8 AM.` | `8 AM` |
| conflict_0018_noisy | conflict | 0.000112716 | `According to the official schedule, the Mariton observatory opens at 10 AM` | `According to the official schedule, the Mariton observatory opens at 10 AM` | `10 AM` |
| conflict_0003_noisy | conflict | 3.38834e-05 | `According to the official schedule, the Kelminster observatory opens at 11 AM` | `According to the official schedule, the Kelminster observatory opens at 11 AM` | `11 AM` |
| conflict_0001_noisy | conflict | 0.013589 | `The Brevic observatory opens at 9 AM.` | `The Brevic observatory opens at 9 AM.` | `9 AM` |
| conflict_0016_noisy | conflict | 2.5745e-05 | `The official schedule says the Norwick observatory opens at 8 AM.` | `The official schedule says the Norwick observatory opens at 8 AM.` | `8 AM` |
| conflict_0002_noisy | conflict | 0.00284424 | `The Lydora observatory opens at 10 AM.` | `The Lydora observatory opens at 10 AM.` | `10 AM` |
| conflict_0013_noisy | conflict | 0.0285464 | `The Kelminster observatory opens at 9 AM.` | `The Kelminster observatory opens at 9 AM.` | `9 AM` |
| conflict_0015_noisy | conflict | 0.0280865 | `The Rivenfall observatory opens at 11 AM.` | `The Rivenfall observatory opens at 11 AM.` | `11 AM` |
| conflict_0005_noisy | conflict | 4.38018e-06 | `According to the official schedule, the Rivenfall observatory opens at 9 AM` | `According to the official schedule, the Rivenfall observatory opens at 9 AM` | `9 AM` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0006_noisy | multi_hop | 9.59295e-06 | `Ilya Marr was born in Rivenfall` | `Ilya Marr was born in Rivenfall` | `Rivenfall` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| single_0017_noisy | single_evidence | 0.297732 | `The Veyra device was calibrated by Orin Vale in 19` | `The Veyra device was calibrated by Orin Vale in 19` | `Orin Vale` |
| conflict_0012_noisy | conflict | 3.29126e-05 | `According to the official schedule, the Lydora observatory opens at 8 AM` | `According to the official schedule, the Lydora observatory opens at 8 AM` | `8 AM` |
