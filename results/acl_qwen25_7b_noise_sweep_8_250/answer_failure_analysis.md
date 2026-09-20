# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.896 | 0.919 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.724 | 0.772 | 0.797 | 56 | 0.193 |
| prefix_conditioned_naive_global | 0.564 | 0.592 | 0.621 | 102 | 0.000 |
| query_similarity_doc_patch_k2 | 0.632 | 0.668 | 0.683 | 83 | 0.172 |
| random_doc_patch_k2_seeded | 0.644 | 0.676 | 0.708 | 81 | 0.164 |
| risk_guided_doc_patch_k2 | 0.596 | 0.632 | 0.657 | 91 | 0.195 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.760 | 0 |
| full_prefill::conflict | 1.000 | 1.000 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.820 | 0 |
| full_prefill::single_evidence | 1.000 | 0.900 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.540 | 0.620 | 18 |
| oracle_evidence_doc_patch::conflict | 0.600 | 0.600 | 20 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.600 | 0.660 | 17 |
| oracle_evidence_doc_patch::single_evidence | 0.880 | 0.980 | 1 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.020 | 0.040 | 48 |
| prefix_conditioned_naive_global::conflict | 0.720 | 0.720 | 14 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.220 | 0.240 | 38 |
| prefix_conditioned_naive_global::single_evidence | 0.860 | 0.960 | 2 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.180 | 0.240 | 38 |
| query_similarity_doc_patch_k2::conflict | 0.840 | 0.840 | 8 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.260 | 0.280 | 36 |
| query_similarity_doc_patch_k2::single_evidence | 0.880 | 0.980 | 1 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.320 | 0.380 | 31 |
| random_doc_patch_k2_seeded::conflict | 0.700 | 0.700 | 15 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.300 | 0.300 | 35 |
| random_doc_patch_k2_seeded::single_evidence | 0.900 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.240 | 0.300 | 34 |
| risk_guided_doc_patch_k2::conflict | 0.600 | 0.600 | 20 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 0.240 | 0.260 | 37 |
| risk_guided_doc_patch_k2::single_evidence | 0.900 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0034_noise8 | multi_hop | 23.2063 | `Kelminster` | `The documents do not provide any information about where the designer of Project Orison was` | `Kelminster` |
| multihop_0038_noise8 | multi_hop | 20.2242 | `Velora` | `Based on the information provided in the document, there is no specific answer to the` | `Velora` |
| multihop_0011_noise8 | multi_hop | 17.5911 | `Qorlan` | `The document does not provide an answer to the question "Where was the designer of` | `Qorlan` |
| multihop_0048_noise8 | multi_hop | 17.3571 | `Velora` | `Based on the information provided in the document, there is no answer to the question` | `Velora` |
| boundary_0018_noise8 | boundary_sensitive | 17.1859 | `2008` | `The documents do not provide a specific year for when Meros was first synthesized.` | `2008` |
| boundary_0045_noise8 | boundary_sensitive | 17.0639 | `2007` | `The documents do not provide a specific year for when Harrow was first synthesized.` | `2007` |
| multihop_0039_noise8 | multi_hop | 16.748 | `Mariton` | `The document does not provide information about where the designer of Project Valen was born` | `Mariton` |
| boundary_0008_noise8 | boundary_sensitive | 16.6755 | `1998` | `The document does not provide a specific year for when Meros was first synthesized.` | `1998` |
| boundary_0011_noise8 | boundary_sensitive | 16.5918 | `2001` | `The documents do not provide a specific year for when Fenric was first synthesized.` | `2001` |
| multihop_0029_noise8 | multi_hop | 16.5661 | `Mariton` | `The document does not provide any information about where the designer of Project Valen was` | `Mariton` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0034_noise8 | multi_hop | 0.102383 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0039_noise8 | multi_hop | 1.74334 | `Mariton` | `Mariton` | `Mariton` |
| multihop_0003_noise8 | multi_hop | 0.266198 | `Lydora` | `Lydora` | `Lydora` |
| multihop_0008_noise8 | multi_hop | 0.0152171 | `Velora` | `Velora` | `Velora` |
| multihop_0017_noise8 | multi_hop | 0.00875748 | `Norwick` | `Norwick` | `Norwick` |
| boundary_0006_noise8 | boundary_sensitive | 0.134992 | `1996` | `1996` | `1996` |
| multihop_0026_noise8 | multi_hop | 0.00113962 | `Rivenfall` | `Rivenfall` | `Rivenfall` |
| boundary_0004_noise8 | boundary_sensitive | 0.000258408 | `1994` | `1994` | `1994` |
| multihop_0024_noise8 | multi_hop | 0.19294 | `Kelminster` | `Kelminster` | `Kelminster` |
| boundary_0035_noise8 | boundary_sensitive | 0.000886881 | `1997` | `1997` | `1997` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| boundary_0045_noise8 | boundary_sensitive | 0.725305 | `2007` | `2007` | `2007` |
| multihop_0039_noise8 | multi_hop | 2.05157 | `Mariton` | `Mariton` | `Mariton` |
| boundary_0011_noise8 | boundary_sensitive | 0.987292 | `2001` | `2001` | `2001` |
| multihop_0026_noise8 | multi_hop | 0.0243305 | `Rivenfall` | `Rivenfall` | `Rivenfall` |
| boundary_0004_noise8 | boundary_sensitive | 0.0277608 | `1994` | `1994` | `1994` |
| boundary_0035_noise8 | boundary_sensitive | 0.000886881 | `1997` | `1997` | `1997` |
| boundary_0021_noise8 | boundary_sensitive | 0.175786 | `2011` | `2011` | `2011` |
| boundary_0009_noise8 | boundary_sensitive | 0.0104578 | `1999` | `1999` | `1999` |
| boundary_0032_noise8 | boundary_sensitive | 0.456513 | `1994` | `1994` | `1994` |
| boundary_0010_noise8 | boundary_sensitive | 0.49846 | `2000` | `2000` | `2000` |
