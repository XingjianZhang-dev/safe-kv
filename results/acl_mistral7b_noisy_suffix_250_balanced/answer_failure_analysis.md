# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.392 | 0.612 | 0 | 0.000 |
| hybrid_query_risk_union_suffix_k1 | 0.928 | 0.388 | 0.613 | 14 | 0.790 |
| oracle_evidence_doc_suffix_closure_patch | 0.992 | 0.396 | 0.614 | 1 | 0.783 |
| prefix_conditioned_naive_global | 0.312 | 0.204 | 0.453 | 161 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.908 | 0.392 | 0.616 | 18 | 0.679 |
| query_similarity_suffix_closure_k2 | 0.996 | 0.392 | 0.612 | 1 | 0.872 |
| random_suffix_closure_k1_seeded | 0.872 | 0.388 | 0.610 | 27 | 0.668 |
| random_suffix_closure_k2_seeded | 1.000 | 0.392 | 0.612 | 0 | 0.850 |
| risk_guided_suffix_closure_k1 | 0.852 | 0.376 | 0.607 | 31 | 0.668 |
| risk_guided_suffix_closure_k2 | 0.996 | 0.392 | 0.612 | 1 | 0.879 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.180 | 0 |
| full_prefill::conflict | 1.000 | 0.280 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.060 | 0 |
| full_prefill::single_evidence | 1.000 | 0.440 | 0 |
| hybrid_query_risk_union_suffix_k1::boundary_sensitive | 0.720 | 0.100 | 13 |
| hybrid_query_risk_union_suffix_k1::conflict | 0.960 | 0.320 | 0 |
| hybrid_query_risk_union_suffix_k1::distractor_heavy | 1.000 | 1.000 | 0 |
| hybrid_query_risk_union_suffix_k1::multi_hop | 0.960 | 0.080 | 1 |
| hybrid_query_risk_union_suffix_k1::single_evidence | 1.000 | 0.440 | 0 |
| oracle_evidence_doc_suffix_closure_patch::boundary_sensitive | 1.000 | 0.180 | 0 |
| oracle_evidence_doc_suffix_closure_patch::conflict | 1.000 | 0.280 | 0 |
| oracle_evidence_doc_suffix_closure_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_suffix_closure_patch::multi_hop | 1.000 | 0.060 | 0 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 0.960 | 0.460 | 1 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.040 | 0.100 | 44 |
| prefix_conditioned_naive_global::conflict | 0.020 | 0.000 | 49 |
| prefix_conditioned_naive_global::distractor_heavy | 0.700 | 0.700 | 15 |
| prefix_conditioned_naive_global::multi_hop | 0.440 | 0.120 | 22 |
| prefix_conditioned_naive_global::single_evidence | 0.360 | 0.100 | 31 |
| query_similarity_suffix_closure_k1::boundary_sensitive | 0.700 | 0.100 | 14 |
| query_similarity_suffix_closure_k1::conflict | 0.920 | 0.320 | 2 |
| query_similarity_suffix_closure_k1::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_suffix_closure_k1::multi_hop | 0.960 | 0.080 | 1 |
| query_similarity_suffix_closure_k1::single_evidence | 0.960 | 0.460 | 1 |
| query_similarity_suffix_closure_k2::boundary_sensitive | 0.980 | 0.180 | 1 |
| query_similarity_suffix_closure_k2::conflict | 1.000 | 0.280 | 0 |
| query_similarity_suffix_closure_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_suffix_closure_k2::multi_hop | 1.000 | 0.060 | 0 |
| query_similarity_suffix_closure_k2::single_evidence | 1.000 | 0.440 | 0 |
| random_suffix_closure_k1_seeded::boundary_sensitive | 0.740 | 0.160 | 11 |
| random_suffix_closure_k1_seeded::conflict | 0.800 | 0.240 | 10 |
| random_suffix_closure_k1_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_suffix_closure_k1_seeded::multi_hop | 0.920 | 0.080 | 3 |
| random_suffix_closure_k1_seeded::single_evidence | 0.900 | 0.460 | 3 |
| random_suffix_closure_k2_seeded::boundary_sensitive | 1.000 | 0.180 | 0 |
| random_suffix_closure_k2_seeded::conflict | 1.000 | 0.280 | 0 |
| random_suffix_closure_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_suffix_closure_k2_seeded::multi_hop | 1.000 | 0.060 | 0 |
| random_suffix_closure_k2_seeded::single_evidence | 1.000 | 0.440 | 0 |
| risk_guided_suffix_closure_k1::boundary_sensitive | 0.720 | 0.100 | 13 |
| risk_guided_suffix_closure_k1::conflict | 0.700 | 0.280 | 12 |
| risk_guided_suffix_closure_k1::distractor_heavy | 0.980 | 0.980 | 1 |
| risk_guided_suffix_closure_k1::multi_hop | 0.960 | 0.080 | 1 |
| risk_guided_suffix_closure_k1::single_evidence | 0.900 | 0.440 | 4 |
| risk_guided_suffix_closure_k2::boundary_sensitive | 0.980 | 0.180 | 1 |
| risk_guided_suffix_closure_k2::conflict | 1.000 | 0.280 | 0 |
| risk_guided_suffix_closure_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_suffix_closure_k2::multi_hop | 1.000 | 0.060 | 0 |
| risk_guided_suffix_closure_k2::single_evidence | 1.000 | 0.440 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0024_noisy | multi_hop | 17.9839 | `Kelminster (from Document 1)` | `The document does not provide information about the birthplace of the Project Orison designer` | `Kelminster` |
| multihop_0033_noisy | multi_hop | 15.5475 | `Lydora (from Document 1)` | `The document does not provide information about the birthplace of the Project Fenric designer` | `Lydora` |
| multihop_0012_noisy | multi_hop | 15.2373 | `Brevic (Document 3)` | `The document does not provide information about the birthplace of Sera Mavin` | `Brevic` |
| multihop_0000_noisy | multi_hop | 12.203 | `Sera Mavin was born in Halden.` | `The document does not provide information about the birthplace of the designer of Project Mer` | `Halden` |
| multihop_0027_noisy | multi_hop | 10.8836 | `Orin Vale was born in Norwick.` | `The document does not provide information about the birthplace of the Project Harrow designer` | `Norwick` |
| multihop_0039_noisy | multi_hop | 10.7672 | `Mariton (from Document 1)` | `The document does not provide information about where Project designer Valen was born. The` | `Mariton` |
| multihop_0048_noisy | multi_hop | 9.00857 | `Sera Mavin was born in Velora.` | `The document does not provide information about the birthplace of the Project Nimbar` | `Velora` |
| boundary_0001_noisy | boundary_sensitive | 8.06268 | `Dr. Nadia Voss first synthesized Fenric in an unspec` | `The year Fenric was first synthesized is not explicitly stated in the provided` | `1991` |
| multihop_0021_noisy | multi_hop | 7.33456 | `Qorlan` | `The document does not provide information about the birthplace of Priya Holt,` | `Qorlan` |
| boundary_0036_noisy | boundary_sensitive | 7.14444 | `Dr. Orin Vale first synthesized Nimbar in an un` | `1998` | `1998` |

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
