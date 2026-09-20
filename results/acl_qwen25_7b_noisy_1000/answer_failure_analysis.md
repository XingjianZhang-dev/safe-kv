# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.894 | 0.831 | 0.846 | 102 | 0.548 |
| full_prefill | 1.000 | 0.907 | 0.917 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.920 | 0.865 | 0.874 | 78 | 0.424 |
| prefix_conditioned_naive_global | 0.644 | 0.697 | 0.731 | 300 | 0.000 |
| query_similarity_doc_patch_k2 | 0.891 | 0.832 | 0.847 | 103 | 0.549 |
| random_doc_patch_k2_seeded | 0.881 | 0.865 | 0.878 | 93 | 0.535 |
| risk_guided_doc_patch_k2 | 0.880 | 0.816 | 0.831 | 116 | 0.555 |
| safe_gate_t0.45 | 0.877 | 0.819 | 0.833 | 116 | 0.541 |
| safe_gate_t0.60 | 0.752 | 0.789 | 0.795 | 199 | 0.287 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 0.760 | 0.505 | 45 |
| entity_overlap_doc_patch_k2::conflict | 1.000 | 0.975 | 0 |
| entity_overlap_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::multi_hop | 0.710 | 0.675 | 57 |
| entity_overlap_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 0.630 | 0 |
| full_prefill::conflict | 1.000 | 0.975 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.930 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.805 | 0.585 | 39 |
| oracle_evidence_doc_patch::conflict | 1.000 | 0.975 | 0 |
| oracle_evidence_doc_patch::distractor_heavy | 0.975 | 0.975 | 5 |
| oracle_evidence_doc_patch::multi_hop | 0.865 | 0.835 | 25 |
| oracle_evidence_doc_patch::single_evidence | 0.955 | 0.955 | 9 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.470 | 0.720 | 54 |
| prefix_conditioned_naive_global::conflict | 0.615 | 0.635 | 73 |
| prefix_conditioned_naive_global::distractor_heavy | 0.960 | 0.960 | 8 |
| prefix_conditioned_naive_global::multi_hop | 0.310 | 0.305 | 138 |
| prefix_conditioned_naive_global::single_evidence | 0.865 | 0.865 | 27 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.760 | 0.505 | 45 |
| query_similarity_doc_patch_k2::conflict | 0.985 | 0.980 | 1 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.710 | 0.675 | 57 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.720 | 0.665 | 35 |
| random_doc_patch_k2_seeded::conflict | 0.910 | 0.915 | 15 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.780 | 0.750 | 42 |
| random_doc_patch_k2_seeded::single_evidence | 0.995 | 0.995 | 1 |
| risk_guided_doc_patch_k2::boundary_sensitive | 0.740 | 0.480 | 49 |
| risk_guided_doc_patch_k2::conflict | 1.000 | 0.975 | 0 |
| risk_guided_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| risk_guided_doc_patch_k2::multi_hop | 0.685 | 0.650 | 62 |
| risk_guided_doc_patch_k2::single_evidence | 0.975 | 0.975 | 5 |
| safe_gate_t0.45::boundary_sensitive | 0.735 | 0.505 | 47 |
| safe_gate_t0.45::conflict | 1.000 | 0.975 | 0 |
| safe_gate_t0.45::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::multi_hop | 0.675 | 0.640 | 64 |
| safe_gate_t0.45::single_evidence | 0.975 | 0.975 | 5 |
| safe_gate_t0.60::boundary_sensitive | 0.490 | 0.710 | 53 |
| safe_gate_t0.60::conflict | 0.985 | 0.960 | 3 |
| safe_gate_t0.60::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::multi_hop | 0.365 | 0.355 | 127 |
| safe_gate_t0.60::single_evidence | 0.920 | 0.920 | 16 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| boundary_0078_noisy | boundary_sensitive | 36.5628 | `first year` | `2012` | `2012` |
| boundary_0036_noisy | boundary_sensitive | 33.0193 | `Dr. Orin Vale in 1998` | `1998` | `1998` |
| multihop_0018_noisy | multi_hop | 28.6482 | `Velora` | `Nimbar` | `Velora` |
| boundary_0030_noisy | boundary_sensitive | 27.7177 | `Dr. Priya Holt in 1992` | `1992` | `1992` |
| multihop_0147_noisy | multi_hop | 26.7622 | `Norwick` | `Harrow` | `Norwick` |
| multihop_0120_noisy | multi_hop | 25.1993 | `Halden` | `Meros` | `Halden` |
| multihop_0130_noisy | multi_hop | 24.7969 | `Halden` | `Meros` | `Halden` |
| multihop_0024_noisy | multi_hop | 24.3274 | `Kelminster` | `The document does not provide the birthplace of the Project Orison designer.` | `Kelminster` |
| boundary_0167_noisy | boundary_sensitive | 23.6774 | `Dr. Lina Kest in 2017` | `2017` | `2017` |
| multihop_0027_noisy | multi_hop | 22.596 | `Orin Vale was born in Norwick.` | `The documents do not provide information about the birthplace of the Project Harrow designer` | `Norwick` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| boundary_0078_noisy | boundary_sensitive | 3.10684e-05 | `first year` | `first year` | `2012` |
| boundary_0030_noisy | boundary_sensitive | 0.0532244 | `Dr. Priya Holt in 1992` | `Dr. Priya Holt in 1992` | `1992` |
| multihop_0147_noisy | multi_hop | 1.3655e-05 | `Norwick` | `Norwick` | `Norwick` |
| multihop_0024_noisy | multi_hop | 3.58086e-06 | `Kelminster` | `Kelminster` | `Kelminster` |
| boundary_0167_noisy | boundary_sensitive | 0.00857139 | `Dr. Lina Kest in 2017` | `Dr. Lina Kest in 2017` | `2017` |
| multihop_0094_noisy | multi_hop | 2.48286e-07 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0184_noisy | multi_hop | 0 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0064_noisy | multi_hop | 2.20374e-06 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0148_noisy | multi_hop | 0.000115966 | `Velora` | `Velora` | `Velora` |
| multihop_0168_noisy | multi_hop | 8.55341e-07 | `Velora` | `Velora` | `Velora` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0018_noisy | multi_hop | 0.0840984 | `Velora` | `Velora` | `Velora` |
| multihop_0120_noisy | multi_hop | 0.00185216 | `Halden` | `Halden` | `Halden` |
| multihop_0130_noisy | multi_hop | 0.00109548 | `Halden` | `Halden` | `Halden` |
| multihop_0174_noisy | multi_hop | 4.62273e-06 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0138_noisy | multi_hop | 1.1928e-07 | `Velora` | `Velora` | `Velora` |
| multihop_0104_noisy | multi_hop | 1.9896e-09 | `Kelminster` | `Kelminster` | `Kelminster` |
| boundary_0042_noisy | boundary_sensitive | 0.000432942 | `Dr. Priya Holt in` | `Dr. Priya Holt in` | `2004` |
| multihop_0164_noisy | multi_hop | 7.32979e-06 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0090_noisy | multi_hop | 0.000171343 | `Halden` | `Halden` | `Halden` |
| multihop_0067_noisy | multi_hop | 0.00100705 | `Norwick` | `Norwick` | `Norwick` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0120_noisy | multi_hop | 0.00185216 | `Halden` | `Halden` | `Halden` |
| multihop_0174_noisy | multi_hop | 4.62273e-06 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0138_noisy | multi_hop | 1.1928e-07 | `Velora` | `Velora` | `Velora` |
| multihop_0165_noisy | multi_hop | 3.80238e-10 | `Aster Port` | `Aster Port` | `Aster Port` |
| boundary_0042_noisy | boundary_sensitive | 0.000432942 | `Dr. Priya Holt in` | `Dr. Priya Holt in` | `2004` |
| multihop_0090_noisy | multi_hop | 0.000171343 | `Halden` | `Halden` | `Halden` |
| multihop_0067_noisy | multi_hop | 0 | `Norwick` | `Norwick` | `Norwick` |
| multihop_0079_noisy | multi_hop | 8.45354e-07 | `Mariton` | `Mariton` | `Mariton` |
| multihop_0012_noisy | multi_hop | 0 | `Brevic` | `Brevic` | `Brevic` |
| multihop_0126_noisy | multi_hop | 0 | `Rivenfall` | `Rivenfall` | `Rivenfall` |
