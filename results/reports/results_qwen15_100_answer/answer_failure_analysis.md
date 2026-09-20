# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.960 | 0.890 | 0.912 | 3 | 0.543 |
| full_prefill | 1.000 | 0.910 | 0.930 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.960 | 0.890 | 0.912 | 3 | 0.457 |
| prefix_conditioned_naive_global | 0.880 | 0.860 | 0.882 | 11 | 0.000 |
| query_similarity_doc_patch_k2 | 0.960 | 0.890 | 0.912 | 3 | 0.544 |
| random_doc_patch_k2_seeded | 0.930 | 0.880 | 0.907 | 6 | 0.528 |
| safe_gate_t0.45 | 0.960 | 0.890 | 0.912 | 3 | 0.358 |
| safe_gate_t0.60 | 0.920 | 0.880 | 0.900 | 6 | 0.110 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::conflict | 0.800 | 0.500 | 3 |
| entity_overlap_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::multi_hop | 1.000 | 0.950 | 0 |
| entity_overlap_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 0.600 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.950 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::conflict | 0.800 | 0.500 | 3 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 1.000 | 0.950 | 0 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::conflict | 0.500 | 0.350 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.900 | 0.950 | 1 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::conflict | 0.800 | 0.500 | 3 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 1.000 | 0.950 | 0 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::conflict | 0.650 | 0.450 | 6 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 1.000 | 0.950 | 0 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::conflict | 0.800 | 0.500 | 3 |
| safe_gate_t0.45::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::multi_hop | 1.000 | 0.950 | 0 |
| safe_gate_t0.45::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::conflict | 0.700 | 0.450 | 5 |
| safe_gate_t0.60::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::multi_hop | 0.900 | 0.950 | 1 |
| safe_gate_t0.60::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| conflict_0004 | conflict | 3.30391 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `11 AM` | `8 AM` |
| multihop_0009 | multi_hop | 2.73932 | `Mariton` | `Priya Holt` | `Mariton` |
| conflict_0013 | conflict | 2.26899 | `According to the official schedule, the Kelminster observatory opens at 9 AM` | `According to the official schedule, the Kelminster observatory opens at 11` | `9 AM` |
| conflict_0012 | conflict | 2.02657 | `According to the official schedule, the Lydora observatory opens at 8` | `10 AM` | `8 AM` |
| conflict_0001 | conflict | 1.63146 | `9 AM` | `According to the official schedule, the Brevic observatory opens at 1` | `9 AM` |
| conflict_0016 | conflict | 1.06975 | `According to the official schedule, the Norwick observatory opens at 8 AM` | `According to the official schedule, the Norwick observatory opens at 11` | `8 AM` |
| conflict_0006 | conflict | 0.302249 | `According to the official schedule, the Norwick observatory opens at 10` | `1 PM` | `10 AM` |
| conflict_0018 | conflict | 0.219297 | `10 AM` | `1 PM` | `10 AM` |
| conflict_0015 | conflict | 0.123849 | `11 AM` | `10 AM` | `11 AM` |
| multihop_0019 | multi_hop | 0.0614844 | `Vera Noll` | `Mariton` | `Mariton` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| conflict_0004 | conflict | 0.0119985 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `8 AM` |
| multihop_0009 | multi_hop | 0.235067 | `Mariton` | `Mariton` | `Mariton` |
| conflict_0013 | conflict | 0.0662746 | `According to the official schedule, the Kelminster observatory opens at 9 AM` | `According to the official schedule, the Kelminster observatory opens at 9 AM` | `9 AM` |
| conflict_0012 | conflict | 0.0344055 | `According to the official schedule, the Lydora observatory opens at 8` | `According to the official schedule, the Lydora observatory opens at 8` | `8 AM` |
| conflict_0016 | conflict | 0.0175479 | `According to the official schedule, the Norwick observatory opens at 8 AM` | `According to the official schedule, the Norwick observatory opens at 8 AM` | `8 AM` |
| conflict_0006 | conflict | 0.0157131 | `According to the official schedule, the Norwick observatory opens at 10` | `According to the official schedule, the Norwick observatory opens at 10` | `10 AM` |
| conflict_0018 | conflict | 0.0253297 | `10 AM` | `10 AM` | `10 AM` |
| conflict_0015 | conflict | 0.0128638 | `11 AM` | `11 AM` | `11 AM` |
| multihop_0019 | multi_hop | 0.0143525 | `Vera Noll` | `Vera Noll` | `Mariton` |
| conflict_0007 | conflict | 0.0118227 | `11 AM` | `11 AM` | `11 AM` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
