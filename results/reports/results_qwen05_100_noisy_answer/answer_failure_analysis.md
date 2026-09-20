# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.900 | 0.820 | 0.855 | 7 | 0.548 |
| full_prefill | 1.000 | 0.830 | 0.865 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.900 | 0.830 | 0.863 | 6 | 0.423 |
| prefix_conditioned_naive_global | 0.690 | 0.740 | 0.784 | 23 | 0.000 |
| query_similarity_doc_patch_k2 | 0.890 | 0.820 | 0.849 | 7 | 0.550 |
| random_doc_patch_k2_seeded | 0.830 | 0.830 | 0.864 | 11 | 0.536 |
| risk_guided_doc_patch_k2 | 0.860 | 0.780 | 0.812 | 11 | 0.554 |
| safe_gate_t0.45 | 0.860 | 0.790 | 0.822 | 10 | 0.543 |
| safe_gate_t0.60 | 0.810 | 0.760 | 0.792 | 14 | 0.282 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 0.800 | 0.700 | 3 |
| entity_overlap_doc_patch_k2::conflict | 0.850 | 0.600 | 1 |
| entity_overlap_doc_patch_k2::distractor_heavy | 0.950 | 0.950 | 1 |
| entity_overlap_doc_patch_k2::multi_hop | 0.900 | 0.850 | 2 |
| entity_overlap_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 0.800 | 0 |
| full_prefill::conflict | 1.000 | 0.500 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.850 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.800 | 0.700 | 3 |
| oracle_evidence_doc_patch::conflict | 0.850 | 0.600 | 1 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.850 | 0.850 | 2 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.550 | 0.550 | 7 |
| prefix_conditioned_naive_global::conflict | 0.250 | 0.450 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 0.950 | 0.950 | 1 |
| prefix_conditioned_naive_global::multi_hop | 0.700 | 0.750 | 5 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.800 | 0.700 | 3 |
| query_similarity_doc_patch_k2::conflict | 0.750 | 0.550 | 2 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.900 | 0.850 | 2 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.800 | 0.750 | 3 |
| random_doc_patch_k2_seeded::conflict | 0.650 | 0.650 | 3 |
| random_doc_patch_k2_seeded::distractor_heavy | 0.950 | 0.950 | 1 |
| random_doc_patch_k2_seeded::multi_hop | 0.750 | 0.800 | 4 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.750 | 0.700 | 4 |
| risk_guided_doc_patch_k2::conflict | 0.800 | 0.500 | 2 |
| risk_guided_doc_patch_k2::distractor_heavy | 0.950 | 0.950 | 1 |
| risk_guided_doc_patch_k2::multi_hop | 0.800 | 0.750 | 4 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::boundary_sensitive | 0.750 | 0.750 | 3 |
| safe_gate_t0.45::conflict | 0.800 | 0.500 | 2 |
| safe_gate_t0.45::distractor_heavy | 0.950 | 0.950 | 1 |
| safe_gate_t0.45::multi_hop | 0.800 | 0.750 | 4 |
| safe_gate_t0.45::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::boundary_sensitive | 0.600 | 0.600 | 6 |
| safe_gate_t0.60::conflict | 0.800 | 0.500 | 2 |
| safe_gate_t0.60::distractor_heavy | 0.950 | 0.950 | 1 |
| safe_gate_t0.60::multi_hop | 0.700 | 0.750 | 5 |
| safe_gate_t0.60::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| conflict_0000_noisy | conflict | 4.01709 | `According to the official schedule, the Qorlan observatory opens at 8` | `8 AM` | `8 AM` |
| conflict_0018_noisy | conflict | 3.43592 | `According to the official schedule, the Mariton observatory opens at 10` | `1 PM` | `10 AM` |
| multihop_0015_noisy | multi_hop | 2.9812 | `Aster Port` | `The garden survey tracked rainfall near the western greenhouse.` | `Aster Port` |
| conflict_0003_noisy | conflict | 2.87821 | `According to the official schedule, the Kelminster observatory opens at 11` | `11 AM` | `11 AM` |
| conflict_0011_noisy | conflict | 2.74329 | `The Brevic observatory opens at 11 AM.` | `11 AM` | `11 AM` |
| multihop_0018_noisy | multi_hop | 2.70412 | `Ilya Marr` | `The designer of Project Nimbar was born in the northern records room.` | `Velora` |
| conflict_0017_noisy | conflict | 2.6876 | `The official schedule states: "The Velora observatory opens at 9 AM` | `12 AM` | `9 AM` |
| multihop_0009_noisy | multi_hop | 2.25959 | `Mariton` | `Northern records room` | `Mariton` |
| conflict_0009_noisy | conflict | 2.0267 | `According to the official schedule, the Halden observatory opens at 9` | `10 AM` | `9 AM` |
| multihop_0001_noisy | multi_hop | 1.6142 | `Qorlan` | `Tovan Reed` | `Qorlan` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| conflict_0000_noisy | conflict | 7.77608e-05 | `According to the official schedule, the Qorlan observatory opens at 8` | `According to the official schedule, the Qorlan observatory opens at 8` | `8 AM` |
| conflict_0018_noisy | conflict | 3.65182e-05 | `According to the official schedule, the Mariton observatory opens at 10` | `According to the official schedule, the Mariton observatory opens at 10` | `10 AM` |
| multihop_0015_noisy | multi_hop | 0.48306 | `Aster Port` | `Aster Port` | `Aster Port` |
| conflict_0003_noisy | conflict | 2.77305e-05 | `According to the official schedule, the Kelminster observatory opens at 11` | `According to the official schedule, the Kelminster observatory opens at 11` | `11 AM` |
| conflict_0011_noisy | conflict | 0.160881 | `The Brevic observatory opens at 11 AM.` | `The Brevic observatory opens at 11 AM.` | `11 AM` |
| conflict_0017_noisy | conflict | 3.87256e-05 | `The official schedule states: "The Velora observatory opens at 9 AM` | `The official schedule states: "The Velora observatory opens at 9 AM` | `9 AM` |
| multihop_0009_noisy | multi_hop | 4.15084e-06 | `Mariton` | `Mariton` | `Mariton` |
| multihop_0001_noisy | multi_hop | 5.08585e-05 | `Qorlan` | `Qorlan` | `Qorlan` |
| conflict_0001_noisy | conflict | 0.0529927 | `The official schedule states the Brevic observatory opens at 9 AM.` | `The official schedule states the Brevic observatory opens at 9 AM.` | `9 AM` |
| boundary_0017_noisy | boundary_sensitive | 1.88137e-05 | `2007` | `2007` | `2007` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0006_noisy | multi_hop | 4.1531e-05 | `Ilya Marr` | `Ilya Marr` | `Rivenfall` |
| boundary_0015_noisy | boundary_sensitive | 1.76812e-07 | `2005` | `2005` | `2005` |
| boundary_0016_noisy | boundary_sensitive | 3.36836e-06 | `2006` | `2006` | `2006` |
| boundary_0000_noisy | boundary_sensitive | 3.64002e-06 | `1990` | `1990` | `1990` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| conflict_0012_noisy | conflict | 0.000323566 | `10 AM` | `10 AM` | `8 AM` |
| boundary_0015_noisy | boundary_sensitive | 0.00112774 | `2005` | `2005` | `2005` |
| boundary_0016_noisy | boundary_sensitive | 3.36836e-06 | `2006` | `2006` | `2006` |
