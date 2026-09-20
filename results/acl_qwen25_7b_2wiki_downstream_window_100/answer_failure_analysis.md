# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.420 | 0.505 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.350 | 0.320 | 0.392 | 57 | 0.000 |
| query_similarity_downstream_w2_k1 | 0.460 | 0.400 | 0.473 | 44 | 0.424 |
| query_similarity_downstream_w3_k1 | 0.580 | 0.370 | 0.442 | 36 | 0.569 |
| query_similarity_suffix_closure_k1 | 0.920 | 0.390 | 0.472 | 7 | 0.754 |
| random_downstream_w3_k1_seeded | 0.510 | 0.390 | 0.463 | 40 | 0.375 |
| random_suffix_closure_k1_seeded | 0.720 | 0.400 | 0.477 | 22 | 0.509 |
| risk_guided_doc_patch_k1 | 0.380 | 0.350 | 0.436 | 54 | 0.226 |
| risk_guided_downstream_w2_k1 | 0.450 | 0.390 | 0.475 | 45 | 0.419 |
| risk_guided_downstream_w3_k1 | 0.570 | 0.380 | 0.466 | 37 | 0.586 |
| risk_guided_downstream_w4_k1 | 0.790 | 0.390 | 0.483 | 18 | 0.729 |
| risk_guided_suffix_closure_k1 | 0.970 | 0.410 | 0.495 | 2 | 0.793 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.420 | 0 |
| prefix_conditioned_naive_global::external_2wiki | 0.350 | 0.320 | 57 |
| query_similarity_downstream_w2_k1::external_2wiki | 0.460 | 0.400 | 44 |
| query_similarity_downstream_w3_k1::external_2wiki | 0.580 | 0.370 | 36 |
| query_similarity_suffix_closure_k1::external_2wiki | 0.920 | 0.390 | 7 |
| random_downstream_w3_k1_seeded::external_2wiki | 0.510 | 0.390 | 40 |
| random_suffix_closure_k1_seeded::external_2wiki | 0.720 | 0.400 | 22 |
| risk_guided_doc_patch_k1::external_2wiki | 0.380 | 0.350 | 54 |
| risk_guided_downstream_w2_k1::external_2wiki | 0.450 | 0.390 | 45 |
| risk_guided_downstream_w3_k1::external_2wiki | 0.570 | 0.380 | 37 |
| risk_guided_downstream_w4_k1::external_2wiki | 0.790 | 0.390 | 18 |
| risk_guided_suffix_closure_k1::external_2wiki | 0.970 | 0.410 | 2 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 23.6307 | `ca. March 19, 1666` | `1666` | `March 19, 1666` |
| 2wiki_c99fc05e0bd911eba7f7acde48001122 | external_2wiki | 22.2847 | `15 March 1981` | `Unknown` | `15 March 1981` |
| 2wiki_5a4826b00bde11eba7f7acde48001122 | external_2wiki | 19.2929 | `1032` | `The document does not provide the date of death of Constance of Burgundy's` | `21 March 1076` |
| 2wiki_17904a03087611ebbd67ac1f6bf848b6 | external_2wiki | 18.9744 | `Roy William Neill` | `Publicity Madness` | `Eyes Of The Underworld` |
| 2wiki_c6ac8fcc0bdd11eba7f7acde48001122 | external_2wiki | 18.7393 | `Brisbane, Queensland` | `The document does not provide information about the birthplace of Michael Bryce's wife.` | `Brisbane` |
| 2wiki_61e86d5a0bdc11eba7f7acde48001122 | external_2wiki | 18.5825 | `Document 1 does not provide information about where Kearen Pang studied.` | `Paris Studio Magenia` | `Hong Kong Academy for Performing Arts` |
| 2wiki_5cad7ed608a111ebbd79ac1f6bf848b6 | external_2wiki | 17.3292 | `Terror-Creatures from the Grave` | `Westerplatte (Film)` | `Terror-Creatures From The Grave` |
| 2wiki_50d225540bde11eba7f7acde48001122 | external_2wiki | 16.8765 | `House of Ascania` | `Germany` | `Saxony` |
| 2wiki_0290cd840baf11ebab90acde48001122 | external_2wiki | 15.7279 | `Mary de Monthermer's husband, whose name is not provided in the documents` | `Ragnhild Butenschøn` | `Ralph de Monthermer` |
| 2wiki_e051bd000bdb11eba7f7acde48001122 | external_2wiki | 14.9688 | `British` | `Liverpool` | `British` |

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
