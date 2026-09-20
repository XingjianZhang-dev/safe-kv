# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.896 | 0.902 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.932 | 0.884 | 0.892 | 16 | 0.456 |
| prefix_conditioned_naive_global | 0.672 | 0.760 | 0.801 | 60 | 0.000 |
| query_similarity_doc_patch_k2 | 0.932 | 0.884 | 0.892 | 16 | 0.542 |
| random_doc_patch_k2_seeded | 0.860 | 0.828 | 0.849 | 29 | 0.529 |
| risk_guided_doc_patch_k2 | 0.932 | 0.884 | 0.892 | 16 | 0.544 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::boundary_sensitive | 1.000 | 0.600 | 0 |
| full_prefill::conflict | 1.000 | 0.920 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.960 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.700 | 0.540 | 15 |
| oracle_evidence_doc_patch::conflict | 0.980 | 0.940 | 0 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.980 | 0.940 | 1 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.600 | 0.980 | 1 |
| prefix_conditioned_naive_global::conflict | 0.520 | 0.580 | 21 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.240 | 0.240 | 38 |
| prefix_conditioned_naive_global::single_evidence | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.700 | 0.540 | 15 |
| query_similarity_doc_patch_k2::conflict | 0.980 | 0.940 | 0 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.980 | 0.940 | 1 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.720 | 0.620 | 9 |
| random_doc_patch_k2_seeded::conflict | 0.820 | 0.780 | 8 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.760 | 0.740 | 12 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.700 | 0.540 | 15 |
| risk_guided_doc_patch_k2::conflict | 0.980 | 0.940 | 0 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 0.980 | 0.940 | 1 |
| risk_guided_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| boundary_0024_noise0 | boundary_sensitive | 23.639 | `The question cannot be directly answered from the given documents as the year of synthesis for` | `2014` | `2014` |
| boundary_0034_noise0 | boundary_sensitive | 22.5711 | `The question cannot be directly answered with the shortest exact answer phrase from the given documents` | `1996` | `1996` |
| boundary_0001_noise0 | boundary_sensitive | 22.4523 | `Dr. Nadia Voss in` | `1991` | `1991` |
| boundary_0033_noise0 | boundary_sensitive | 20.334 | `The compound Caldrin was first synthesized by Dr. Sera Mavin in` | `1995` | `1995` |
| multihop_0003_noise0 | multi_hop | 19.985 | `Lydora` | `The documents do not provide information about the birthplace of the designer of Project Fen` | `Lydora` |
| multihop_0037_noise0 | multi_hop | 19.6078 | `Norwick` | `The documents do not provide information about the birthplace of Tovan Reed. The` | `Norwick` |
| multihop_0024_noise0 | multi_hop | 18.4173 | `Kelminster` | `The documents do not provide information about the birthplace of the designer of Project Or` | `Kelminster` |
| multihop_0010_noise0 | multi_hop | 18.178 | `Halden` | `The information provided does not specify where the designer of Project Meros was born.` | `Halden` |
| multihop_0048_noise0 | multi_hop | 18.1243 | `Velora` | `The documents do not provide information about the birthplace of the designer of Project Nim` | `Velora` |
| boundary_0015_noise0 | boundary_sensitive | 17.9812 | `Document 2 does not provide the year Harrow was first synthesized. The exact` | `2005` | `2005` |

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
| multihop_0024_noise0 | multi_hop | 1.0614e-07 | `Kelminster` | `Kelminster` | `Kelminster` |
| boundary_0015_noise0 | boundary_sensitive | 3.25832e-05 | `Document 2 does not provide the year Harrow was first synthesized. The exact` | `Document 2 does not provide the year Harrow was first synthesized. The exact` | `2005` |
| boundary_0017_noise0 | boundary_sensitive | 3.82481e-05 | `The question cannot be directly answered with the shortest exact answer phrase from the documents provided` | `The question cannot be directly answered with the shortest exact answer phrase from the documents provided` | `2007` |
| boundary_0003_noise0 | boundary_sensitive | 1.09362e-05 | `The information provided does not include the year Caldrin was first synthesized.` | `The information provided does not include the year Caldrin was first synthesized.` | `1993` |
| conflict_0040_noise0 | conflict | 8.98714e-06 | `According to the official schedule, the Qorlan observatory opens at 8` | `According to the official schedule, the Qorlan observatory opens at 8` | `8 AM` |
| boundary_0000_noise0 | boundary_sensitive | 2.38967e-05 | `The question cannot be answered exactly from the given documents. Document 3 mentions that` | `The question cannot be answered exactly from the given documents. Document 3 mentions that` | `1990` |
| boundary_0020_noise0 | boundary_sensitive | 1.68895e-05 | `The question asks for the year Ralvex was first synthesized, but the` | `The question asks for the year Ralvex was first synthesized, but the` | `2010` |
| boundary_0029_noise0 | boundary_sensitive | 7.44765e-06 | `The document does not provide the year Zorvian was first synthesized. It` | `The document does not provide the year Zorvian was first synthesized. It` | `1991` |
