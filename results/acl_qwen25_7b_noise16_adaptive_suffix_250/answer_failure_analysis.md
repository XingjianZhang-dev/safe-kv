# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.904 | 0.914 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.416 | 0.420 | 0.479 | 145 | 0.000 |
| query_similarity_adaptive_suffix_t0_65_k2 | 0.856 | 0.852 | 0.859 | 28 | 0.570 |
| query_similarity_doc_patch_k2 | 0.536 | 0.544 | 0.561 | 114 | 0.110 |
| query_similarity_suffix_closure_k2 | 0.868 | 0.864 | 0.871 | 25 | 0.680 |
| random_adaptive_suffix_t0_65_k2_seeded | 0.764 | 0.760 | 0.805 | 53 | 0.532 |
| random_doc_patch_k2_seeded | 0.520 | 0.524 | 0.566 | 119 | 0.099 |
| random_suffix_closure_k2_seeded | 0.852 | 0.828 | 0.853 | 32 | 0.670 |
| risk_guided_adaptive_suffix_t0_65_k2 | 0.868 | 0.844 | 0.858 | 28 | 0.579 |
| risk_guided_doc_patch_k2 | 0.488 | 0.492 | 0.520 | 126 | 0.124 |
| risk_guided_suffix_closure_k2 | 0.888 | 0.856 | 0.870 | 24 | 0.699 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.820 | 0 |
| full_prefill::conflict | 1.000 | 0.960 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.760 | 0 |
| full_prefill::single_evidence | 1.000 | 0.980 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.000 | 0.000 | 50 |
| prefix_conditioned_naive_global::conflict | 0.520 | 0.540 | 23 |
| prefix_conditioned_naive_global::distractor_heavy | 0.900 | 0.900 | 5 |
| prefix_conditioned_naive_global::multi_hop | 0.100 | 0.100 | 45 |
| prefix_conditioned_naive_global::single_evidence | 0.560 | 0.560 | 22 |
| query_similarity_adaptive_suffix_t0_65_k2::boundary_sensitive | 0.700 | 0.780 | 10 |
| query_similarity_adaptive_suffix_t0_65_k2::conflict | 0.980 | 0.940 | 1 |
| query_similarity_adaptive_suffix_t0_65_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_adaptive_suffix_t0_65_k2::multi_hop | 0.680 | 0.600 | 14 |
| query_similarity_adaptive_suffix_t0_65_k2::single_evidence | 0.920 | 0.940 | 3 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.000 | 0.000 | 50 |
| query_similarity_doc_patch_k2::conflict | 0.640 | 0.660 | 17 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.120 | 0.120 | 44 |
| query_similarity_doc_patch_k2::single_evidence | 0.920 | 0.940 | 3 |
| query_similarity_suffix_closure_k2::boundary_sensitive | 0.700 | 0.780 | 10 |
| query_similarity_suffix_closure_k2::conflict | 0.980 | 0.940 | 1 |
| query_similarity_suffix_closure_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_suffix_closure_k2::multi_hop | 0.680 | 0.600 | 14 |
| query_similarity_suffix_closure_k2::single_evidence | 0.980 | 1.000 | 0 |
| random_adaptive_suffix_t0_65_k2_seeded::boundary_sensitive | 0.720 | 0.780 | 10 |
| random_adaptive_suffix_t0_65_k2_seeded::conflict | 0.800 | 0.780 | 10 |
| random_adaptive_suffix_t0_65_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_adaptive_suffix_t0_65_k2_seeded::multi_hop | 0.580 | 0.500 | 20 |
| random_adaptive_suffix_t0_65_k2_seeded::single_evidence | 0.720 | 0.740 | 13 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.000 | 0.000 | 50 |
| random_doc_patch_k2_seeded::conflict | 0.680 | 0.700 | 15 |
| random_doc_patch_k2_seeded::distractor_heavy | 0.960 | 0.960 | 2 |
| random_doc_patch_k2_seeded::multi_hop | 0.120 | 0.120 | 44 |
| random_doc_patch_k2_seeded::single_evidence | 0.840 | 0.840 | 8 |
| random_suffix_closure_k2_seeded::boundary_sensitive | 0.720 | 0.780 | 10 |
| random_suffix_closure_k2_seeded::conflict | 0.840 | 0.820 | 8 |
| random_suffix_closure_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_suffix_closure_k2_seeded::multi_hop | 0.700 | 0.560 | 14 |
| random_suffix_closure_k2_seeded::single_evidence | 1.000 | 0.980 | 0 |
| risk_guided_adaptive_suffix_t0_65_k2::boundary_sensitive | 0.820 | 0.860 | 6 |
| risk_guided_adaptive_suffix_t0_65_k2::conflict | 0.940 | 0.900 | 3 |
| risk_guided_adaptive_suffix_t0_65_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_adaptive_suffix_t0_65_k2::multi_hop | 0.680 | 0.540 | 15 |
| risk_guided_adaptive_suffix_t0_65_k2::single_evidence | 0.900 | 0.920 | 4 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.000 | 0.000 | 50 |
| risk_guided_doc_patch_k2::conflict | 0.460 | 0.460 | 26 |
| risk_guided_doc_patch_k2::distractor_heavy | 0.980 | 0.980 | 1 |
| risk_guided_doc_patch_k2::multi_hop | 0.100 | 0.100 | 45 |
| risk_guided_doc_patch_k2::single_evidence | 0.900 | 0.920 | 4 |
| risk_guided_suffix_closure_k2::boundary_sensitive | 0.820 | 0.860 | 6 |
| risk_guided_suffix_closure_k2::conflict | 0.940 | 0.900 | 3 |
| risk_guided_suffix_closure_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_suffix_closure_k2::multi_hop | 0.680 | 0.540 | 15 |
| risk_guided_suffix_closure_k2::single_evidence | 1.000 | 0.980 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0024_noise16 | multi_hop | 24.382 | `Kelminster` | `Based on the information provided in the document, there is no answer to the question` | `Kelminster` |
| multihop_0004_noise16 | multi_hop | 24.2667 | `Kelminster` | `Based on the information provided in the document, there is no clear answer to the` | `Kelminster` |
| multihop_0034_noise16 | multi_hop | 24.1718 | `Kelminster` | `Based on the information provided in the document, there is no answer to the question` | `Kelminster` |
| multihop_0027_noise16 | multi_hop | 22.169 | `Orin Vale` | `The document does not provide any information about where the designer of Project Harrow was` | `Norwick` |
| multihop_0009_noise16 | multi_hop | 20.8662 | `Mariton` | `Based on the information provided in the document, there is no specific answer to the` | `Mariton` |
| multihop_0007_noise16 | multi_hop | 20.802 | `Norwick` | `Based on the information provided in the document, there is no specific answer to the` | `Norwick` |
| multihop_0037_noise16 | multi_hop | 19.969 | `Norwick` | `Based on the information provided in the document, there is no direct answer to the` | `Norwick` |
| multihop_0018_noise16 | multi_hop | 19.9442 | `Velora` | `Based on the information provided in the document, there is no clear answer to the` | `Velora` |
| multihop_0047_noise16 | multi_hop | 19.7418 | `Norwick` | `Based on the information provided in the document, there is no direct answer to the` | `Norwick` |
| multihop_0032_noise16 | multi_hop | 19.5773 | `Jalen Irix` | `Based on the information provided in the document, there is no answer to the question` | `Brevic` |

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
| multihop_0043_noise16 | multi_hop | 3.3871 | `Lydora` | `Lydora` | `Lydora` |
| single_0024_noise16 | single_evidence | 0.263863 | `Mira Solen` | `Mira Solen` | `Mira Solen` |
| single_0033_noise16 | single_evidence | 0.194299 | `Vera Noll` | `Vera Noll` | `Vera Noll` |
| conflict_0032_noise16 | conflict | 0.327963 | `8 AM` | `8 AM` | `8 AM` |
| conflict_0035_noise16 | conflict | 0.0881264 | `11 AM` | `11 AM` | `11 AM` |
