# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.970 | 0.990 | 0.990 | 1 | 0.543 |
| full_prefill | 1.000 | 0.980 | 0.984 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.970 | 0.990 | 0.990 | 1 | 0.457 |
| prefix_conditioned_naive_global | 0.850 | 0.850 | 0.884 | 14 | 0.000 |
| query_similarity_doc_patch_k2 | 0.970 | 0.990 | 0.990 | 1 | 0.544 |
| random_doc_patch_k2_seeded | 0.960 | 0.960 | 0.960 | 3 | 0.528 |
| risk_guided_doc_patch_k2 | 0.970 | 0.990 | 0.990 | 1 | 0.546 |
| safe_gate_t0.45 | 0.980 | 0.980 | 0.984 | 1 | 0.358 |
| safe_gate_t0.60 | 0.920 | 0.920 | 0.924 | 7 | 0.110 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::conflict | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::distractor_heavy | 0.950 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::multi_hop | 0.900 | 0.950 | 1 |
| entity_overlap_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 1.000 | 0 |
| full_prefill::conflict | 1.000 | 1.000 | 0 |
| full_prefill::distractor_heavy | 1.000 | 0.950 | 0 |
| full_prefill::multi_hop | 1.000 | 0.950 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::conflict | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::distractor_heavy | 0.950 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.900 | 0.950 | 1 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.950 | 0.950 | 1 |
| prefix_conditioned_naive_global::conflict | 0.550 | 0.550 | 9 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 0.950 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.750 | 0.800 | 4 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::conflict | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::distractor_heavy | 0.950 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.900 | 0.950 | 1 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.950 | 0.950 | 1 |
| random_doc_patch_k2_seeded::conflict | 0.950 | 0.950 | 1 |
| random_doc_patch_k2_seeded::distractor_heavy | 0.950 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.950 | 0.900 | 1 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::conflict | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::distractor_heavy | 0.950 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 0.900 | 0.950 | 1 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::boundary_sensitive | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::conflict | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::distractor_heavy | 1.000 | 0.950 | 0 |
| safe_gate_t0.45::multi_hop | 0.900 | 0.950 | 1 |
| safe_gate_t0.45::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::boundary_sensitive | 0.950 | 0.950 | 1 |
| safe_gate_t0.60::conflict | 0.900 | 0.900 | 2 |
| safe_gate_t0.60::distractor_heavy | 1.000 | 0.950 | 0 |
| safe_gate_t0.60::multi_hop | 0.750 | 0.800 | 4 |
| safe_gate_t0.60::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| boundary_0010 | boundary_sensitive | 1.34259 | `2000` | `1970` | `2000` |
| multihop_0015 | multi_hop | 1.19262 | `Document 2` | `Aster Port` | `Aster Port` |
| conflict_0001 | conflict | 1.02447 | `9 AM` | `11 AM` | `9 AM` |
| conflict_0006 | conflict | 0.616073 | `10 AM` | `1 PM` | `10 AM` |
| conflict_0016 | conflict | 0.613134 | `8 AM` | `11 AM` | `8 AM` |
| conflict_0013 | conflict | 0.591903 | `9 AM` | `11 AM` | `9 AM` |
| multihop_0018 | multi_hop | 0.508391 | `Velora` | `Ilya Marr` | `Velora` |
| multihop_0011 | multi_hop | 0.423142 | `Qorlan` | `Aria Lorne` | `Qorlan` |
| conflict_0017 | conflict | 0.316911 | `9 AM` | `12 AM` | `9 AM` |
| conflict_0018 | conflict | 0.287366 | `10 AM` | `1 PM` | `10 AM` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| boundary_0010 | boundary_sensitive | 0.00395677 | `2000` | `2000` | `2000` |
| conflict_0001 | conflict | 0.165254 | `9 AM` | `9 AM` | `9 AM` |
| conflict_0006 | conflict | 0.178274 | `10 AM` | `10 AM` | `10 AM` |
| conflict_0016 | conflict | 0.0577907 | `8 AM` | `8 AM` | `8 AM` |
| conflict_0013 | conflict | 0.0587866 | `9 AM` | `9 AM` | `9 AM` |
| multihop_0011 | multi_hop | 0.019625 | `Qorlan` | `Qorlan` | `Qorlan` |
| conflict_0017 | conflict | 0.0567816 | `9 AM` | `9 AM` | `9 AM` |
| conflict_0018 | conflict | 0.0722241 | `10 AM` | `10 AM` | `10 AM` |
| multihop_0002 | multi_hop | 0.012923 | `Brevic` | `Brevic` | `Brevic` |
| conflict_0010 | conflict | 0.03471 | `10 AM` | `10 AM` | `10 AM` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0015 | multi_hop | 0.000770899 | `Document 2` | `Document 2` | `Aster Port` |
