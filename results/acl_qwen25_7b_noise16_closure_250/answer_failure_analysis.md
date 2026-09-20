# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| all_document_patch | 0.996 | 0.904 | 0.914 | 1 | 0.969 |
| full_prefill | 1.000 | 0.904 | 0.914 | 0 | 0.000 |
| oracle_evidence_doc_adjacent_patch | 0.676 | 0.696 | 0.728 | 74 | 0.257 |
| oracle_evidence_doc_patch | 0.544 | 0.552 | 0.583 | 111 | 0.122 |
| oracle_evidence_doc_suffix_closure_patch | 0.936 | 0.896 | 0.906 | 10 | 0.654 |
| oracle_evidence_span_window_16 | 0.536 | 0.548 | 0.581 | 113 | 0.063 |
| oracle_support_and_conflict_suffix_patch | 0.504 | 0.512 | 0.544 | 121 | 0.058 |
| prefix_conditioned_naive_global | 0.416 | 0.420 | 0.479 | 145 | 0.000 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch | 0.472 | 0.476 | 0.520 | 131 | 0.058 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| all_document_patch::boundary_sensitive | 0.980 | 0.820 | 1 |
| all_document_patch::conflict | 1.000 | 0.960 | 0 |
| all_document_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| all_document_patch::multi_hop | 1.000 | 0.760 | 0 |
| all_document_patch::single_evidence | 1.000 | 0.980 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 0.820 | 0 |
| full_prefill::conflict | 1.000 | 0.960 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.760 | 0 |
| full_prefill::single_evidence | 1.000 | 0.980 | 0 |
| oracle_evidence_doc_adjacent_patch::boundary_sensitive | 0.460 | 0.540 | 23 |
| oracle_evidence_doc_adjacent_patch::conflict | 0.560 | 0.580 | 21 |
| oracle_evidence_doc_adjacent_patch::distractor_heavy | 0.960 | 0.960 | 2 |
| oracle_evidence_doc_adjacent_patch::multi_hop | 0.500 | 0.480 | 24 |
| oracle_evidence_doc_adjacent_patch::single_evidence | 0.900 | 0.920 | 4 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.120 | 0.120 | 44 |
| oracle_evidence_doc_patch::conflict | 0.460 | 0.460 | 26 |
| oracle_evidence_doc_patch::distractor_heavy | 0.980 | 0.980 | 1 |
| oracle_evidence_doc_patch::multi_hop | 0.280 | 0.300 | 35 |
| oracle_evidence_doc_patch::single_evidence | 0.880 | 0.900 | 5 |
| oracle_evidence_doc_suffix_closure_patch::boundary_sensitive | 0.900 | 0.880 | 2 |
| oracle_evidence_doc_suffix_closure_patch::conflict | 0.940 | 0.900 | 3 |
| oracle_evidence_doc_suffix_closure_patch::distractor_heavy | 0.980 | 0.980 | 1 |
| oracle_evidence_doc_suffix_closure_patch::multi_hop | 0.880 | 0.720 | 4 |
| oracle_evidence_doc_suffix_closure_patch::single_evidence | 0.980 | 1.000 | 0 |
| oracle_evidence_span_window_16::boundary_sensitive | 0.040 | 0.040 | 48 |
| oracle_evidence_span_window_16::conflict | 0.500 | 0.520 | 24 |
| oracle_evidence_span_window_16::distractor_heavy | 0.980 | 0.980 | 1 |
| oracle_evidence_span_window_16::multi_hop | 0.280 | 0.300 | 35 |
| oracle_evidence_span_window_16::single_evidence | 0.880 | 0.900 | 5 |
| oracle_support_and_conflict_suffix_patch::boundary_sensitive | 0.000 | 0.000 | 50 |
| oracle_support_and_conflict_suffix_patch::conflict | 0.400 | 0.400 | 29 |
| oracle_support_and_conflict_suffix_patch::distractor_heavy | 0.980 | 0.980 | 1 |
| oracle_support_and_conflict_suffix_patch::multi_hop | 0.280 | 0.300 | 35 |
| oracle_support_and_conflict_suffix_patch::single_evidence | 0.860 | 0.880 | 6 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.000 | 0.000 | 50 |
| prefix_conditioned_naive_global::conflict | 0.520 | 0.540 | 23 |
| prefix_conditioned_naive_global::distractor_heavy | 0.900 | 0.900 | 5 |
| prefix_conditioned_naive_global::multi_hop | 0.100 | 0.100 | 45 |
| prefix_conditioned_naive_global::single_evidence | 0.560 | 0.560 | 22 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::boundary_sensitive | 0.020 | 0.020 | 49 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::conflict | 0.740 | 0.760 | 12 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::distractor_heavy | 0.880 | 0.880 | 6 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::multi_hop | 0.080 | 0.080 | 46 |
| random_patch_same_budget::oracle_support_and_conflict_suffix_patch::single_evidence | 0.640 | 0.640 | 18 |

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
| multihop_0028_noise16 | multi_hop | 0.0341198 | `Velora` | `Velora` | `Velora` |
| single_0014_noise16 | single_evidence | 0.000211905 | `Sera Mavin` | `Sera Mavin` | `Sera Mavin` |
| multihop_0013_noise16 | multi_hop | 0.579852 | `Lydora` | `Lydora` | `Lydora` |
| boundary_0037_noise16 | boundary_sensitive | 0.0821758 | `1999` | `1999` | `1999` |
| multihop_0008_noise16 | multi_hop | 0.00408827 | `Velora` | `Velora` | `Velora` |
| boundary_0026_noise16 | boundary_sensitive | 0.816802 | `2016` | `2016` | `2016` |
| boundary_0021_noise16 | boundary_sensitive | 0.0912261 | `2011` | `2011` | `2011` |
| boundary_0031_noise16 | boundary_sensitive | 0.0311626 | `1993` | `1993` | `1993` |
| multihop_0036_noise16 | multi_hop | 0.0114632 | `Rivenfall` | `Rivenfall` | `Rivenfall` |
| multihop_0033_noise16 | multi_hop | 2.34797 | `Lydora` | `Lydora` | `Lydora` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
