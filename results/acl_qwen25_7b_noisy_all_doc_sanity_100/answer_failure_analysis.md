# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| all_document_patch | 1.000 | 0.900 | 0.907 | 0 | 0.899 |
| full_prefill | 1.000 | 0.900 | 0.907 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.860 | 0.830 | 0.836 | 14 | 0.425 |
| prefix_conditioned_naive_global | 0.560 | 0.630 | 0.670 | 37 | 0.000 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| all_document_patch::boundary_sensitive | 1.000 | 0.500 | 0 |
| all_document_patch::conflict | 1.000 | 1.000 | 0 |
| all_document_patch::distractor_heavy | 1.000 | 1.000 | 0 |
| all_document_patch::multi_hop | 1.000 | 1.000 | 0 |
| all_document_patch::single_evidence | 1.000 | 1.000 | 0 |
| full_prefill::boundary_sensitive | 1.000 | 0.500 | 0 |
| full_prefill::conflict | 1.000 | 1.000 | 0 |
| full_prefill::distractor_heavy | 1.000 | 1.000 | 0 |
| full_prefill::multi_hop | 1.000 | 1.000 | 0 |
| full_prefill::single_evidence | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::boundary_sensitive | 0.500 | 0.350 | 10 |
| oracle_evidence_doc_patch::conflict | 1.000 | 1.000 | 0 |
| oracle_evidence_doc_patch::distractor_heavy | 0.950 | 0.950 | 1 |
| oracle_evidence_doc_patch::multi_hop | 0.900 | 0.900 | 2 |
| oracle_evidence_doc_patch::single_evidence | 0.950 | 0.950 | 1 |
| prefix_conditioned_naive_global::boundary_sensitive | 0.300 | 0.650 | 7 |
| prefix_conditioned_naive_global::conflict | 0.500 | 0.500 | 10 |
| prefix_conditioned_naive_global::distractor_heavy | 0.950 | 0.950 | 1 |
| prefix_conditioned_naive_global::multi_hop | 0.200 | 0.200 | 16 |
| prefix_conditioned_naive_global::single_evidence | 0.850 | 0.850 | 3 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| multihop_0018_noisy | multi_hop | 28.6482 | `Velora` | `Nimbar` | `Velora` |
| multihop_0000_noisy | multi_hop | 19.8266 | `Halden` | `The document provided does not contain information about where the designer of Project Meros was` | `Halden` |
| boundary_0007_noisy | boundary_sensitive | 19.7005 | `1997` | `The question appears to be based on a misunderstanding, as the document does not mention` | `1997` |
| multihop_0004_noisy | multi_hop | 18.7592 | `Kelminster` | `The documents do not provide the birthplace of Nadia Voss, who designed` | `Kelminster` |
| multihop_0012_noisy | multi_hop | 18.0671 | `Brevic` | `The documents do not provide information about the birthplace of the designer of Project R` | `Brevic` |
| multihop_0003_noisy | multi_hop | 18.023 | `Lydora` | `Fenric` | `Lydora` |
| boundary_0015_noisy | boundary_sensitive | 17.9812 | `Document 2 does not provide the year Harrow was first synthesized. The exact` | `2005` | `2005` |
| boundary_0008_noisy | boundary_sensitive | 17.9756 | `The question asks for the year Meros was first synthesized. The relevant information is` | `1998` | `1998` |
| multihop_0010_noisy | multi_hop | 17.8015 | `Halden` | `Information not provided in the given documents.` | `Halden` |
| boundary_0012_noisy | boundary_sensitive | 17.499 | `Dr. Orin Vale in 2002` | `2002` | `2002` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| multihop_0018_noisy | multi_hop | 0.0840984 | `Velora` | `Velora` | `Velora` |
| multihop_0000_noisy | multi_hop | 0.0158218 | `Halden` | `Halden` | `Halden` |
| multihop_0004_noisy | multi_hop | 0.176082 | `Kelminster` | `Kelminster` | `Kelminster` |
| multihop_0012_noisy | multi_hop | 0 | `Brevic` | `Brevic` | `Brevic` |
| multihop_0003_noisy | multi_hop | 0.00041238 | `Lydora` | `Lydora` | `Lydora` |
| boundary_0008_noisy | boundary_sensitive | 3.95475e-05 | `The question asks for the year Meros was first synthesized. The relevant information is` | `The question asks for the year Meros was first synthesized. The relevant information is` | `1998` |
| multihop_0010_noisy | multi_hop | 0 | `Halden` | `Halden` | `Halden` |
| boundary_0012_noisy | boundary_sensitive | 0.508127 | `Dr. Orin Vale in 2002` | `Dr. Orin Vale in 2002` | `2002` |
| conflict_0001_noisy | conflict | 0.0021286 | `9 AM` | `9 AM` | `9 AM` |
| conflict_0000_noisy | conflict | 0.0179702 | `8 AM` | `8 AM` | `8 AM` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |
