# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.920 | 0.800 | 0.829 | 6 | 0.548 |
| full_prefill | 1.000 | 0.830 | 0.859 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.890 | 0.770 | 0.805 | 10 | 0.423 |
| prefix_conditioned_naive_global | 0.740 | 0.760 | 0.797 | 20 | 0.000 |
| query_similarity_doc_patch_k2 | 0.920 | 0.810 | 0.834 | 6 | 0.550 |
| random_doc_patch_k2_seeded | 0.860 | 0.840 | 0.868 | 8 | 0.536 |
| safe_gate_t0.45 | 0.920 | 0.800 | 0.829 | 6 | 0.543 |
| safe_gate_t0.60 | 0.840 | 0.750 | 0.782 | 13 | 0.282 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::boundary_sensitive | 0.900 | 0.800 | 2 |
| entity_overlap_doc_patch_k2::conflict | 0.850 | 0.400 | 2 |
| entity_overlap_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| entity_overlap_doc_patch_k2::multi_hop | 0.850 | 0.800 | 2 |
| entity_overlap_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 0.850 | 0 |
| full_prefill::conflict | 1.000 | 0.450 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 0.850 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.750 | 0.700 | 5 |
| oracle_evidence_doc_patch::conflict | 0.850 | 0.400 | 2 |
| oracle_evidence_doc_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::multi_hop | 0.850 | 0.750 | 3 |
| oracle_evidence_doc_patch::single_evidence | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.750 | 0.800 | 3 |
| prefix_conditioned_naive_global::conflict | 0.350 | 0.400 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 1.000 | 1.000 | 0 |
| prefix_conditioned_naive_global::multi_hop | 0.650 | 0.650 | 6 |
| prefix_conditioned_naive_global::single_evidence | 0.950 | 0.950 | 1 |
| query_similarity_doc_patch_k2::boundary_sensitive | 0.900 | 0.800 | 2 |
| query_similarity_doc_patch_k2::conflict | 0.850 | 0.450 | 2 |
| query_similarity_doc_patch_k2::distractor_heavy | 1.000 | 1.000 | 0 |
| query_similarity_doc_patch_k2::multi_hop | 0.850 | 0.800 | 2 |
| query_similarity_doc_patch_k2::single_evidence | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::boundary_sensitive | 0.800 | 0.850 | 2 |
| random_doc_patch_k2_seeded::conflict | 0.650 | 0.550 | 4 |
| random_doc_patch_k2_seeded::distractor_heavy | 1.000 | 1.000 | 0 |
| random_doc_patch_k2_seeded::multi_hop | 0.850 | 0.800 | 2 |
| random_doc_patch_k2_seeded::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::boundary_sensitive | 0.900 | 0.850 | 1 |
| safe_gate_t0.45::conflict | 0.850 | 0.350 | 3 |
| safe_gate_t0.45::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.45::multi_hop | 0.850 | 0.800 | 2 |
| safe_gate_t0.45::single_evidence | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::boundary_sensitive | 0.750 | 0.800 | 3 |
| safe_gate_t0.60::conflict | 0.850 | 0.350 | 3 |
| safe_gate_t0.60::distractor_heavy | 1.000 | 1.000 | 0 |
| safe_gate_t0.60::multi_hop | 0.650 | 0.650 | 6 |
| safe_gate_t0.60::single_evidence | 0.950 | 0.950 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0008_noisy | multi_hop | 4.71503 | `Velora` | `Nimbar` | `Velora` |
| single_0000_noisy | single_evidence | 3.55488 | `Mira Solen` | `Valen` | `Mira Solen` |
| multihop_0003_noisy | multi_hop | 2.88178 | `Lydora` | `Fenric` | `Lydora` |
| multihop_0009_noisy | multi_hop | 2.73159 | `Project Valen was designed by Priya Holt, who was born in Mariton` | `The designer of Project Valen was born in Mariton.` | `Mariton` |
| boundary_0013_noisy | boundary_sensitive | 2.7126 | `1956` | `2003` | `2003` |
| conflict_0004_noisy | conflict | 2.32223 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `11 AM` | `8 AM` |
| multihop_0006_noisy | multi_hop | 2.20957 | `Rivenfall` | `Ilya Marr` | `Rivenfall` |
| conflict_0012_noisy | conflict | 1.84323 | `According to the official schedule, the Lydora observatory opens at 8` | `10 AM` | `8 AM` |
| multihop_0007_noisy | multi_hop | 1.75636 | `Vera Noll` | `Norwick` | `Norwick` |
| multihop_0018_noisy | multi_hop | 1.75557 | `Velora` | `The designer of Project Nimbar was born in Velora.` | `Velora` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0008_noisy | multi_hop | 6.34744e-07 | `Velora` | `Velora` | `Velora` |
| single_0000_noisy | single_evidence | 0.341621 | `Mira Solen` | `Mira Solen` | `Mira Solen` |
| multihop_0003_noisy | multi_hop | 1.62731e-05 | `Lydora` | `Lydora` | `Lydora` |
| multihop_0009_noisy | multi_hop | 4.84973e-05 | `Project Valen was designed by Priya Holt, who was born in Mariton` | `Project Valen was designed by Priya Holt, who was born in Mariton` | `Mariton` |
| conflict_0004_noisy | conflict | 0.00337666 | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `According to the official schedule, the Aster Port observatory opens at 8 AM` | `8 AM` |
| conflict_0012_noisy | conflict | 0.00844255 | `According to the official schedule, the Lydora observatory opens at 8` | `According to the official schedule, the Lydora observatory opens at 8` | `8 AM` |
| multihop_0018_noisy | multi_hop | 0.158226 | `Velora` | `Velora` | `Velora` |
| boundary_0017_noisy | boundary_sensitive | 8.01859e-05 | `2007` | `2007` | `2007` |
| multihop_0015_noisy | multi_hop | 0.100321 | `Aster Port` | `Aster Port` | `Aster Port` |
| boundary_0009_noisy | boundary_sensitive | 1.15924e-06 | `1999` | `1999` | `1999` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0006_noisy | multi_hop | 4.94667e-05 | `Rivenfall` | `Rivenfall` | `Rivenfall` |
| multihop_0007_noisy | multi_hop | 3.1466e-05 | `Vera Noll` | `Vera Noll` | `Norwick` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| conflict_0019_noisy | conflict | 4.22914e-05 | `11 AM` | `11 AM` | `11 AM` |
