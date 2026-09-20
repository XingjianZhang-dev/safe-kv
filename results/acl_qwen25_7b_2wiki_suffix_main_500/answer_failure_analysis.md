# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.452 | 0.546 | 0 | 0.000 |
| hybrid_query_risk_union_suffix_k1 | 0.974 | 0.442 | 0.536 | 11 | 0.842 |
| prefix_conditioned_naive_global | 0.378 | 0.312 | 0.386 | 272 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.918 | 0.410 | 0.504 | 37 | 0.791 |
| query_similarity_suffix_closure_k2 | 0.972 | 0.444 | 0.538 | 12 | 0.885 |
| random_suffix_closure_k1_seeded | 0.650 | 0.400 | 0.476 | 144 | 0.490 |
| random_suffix_closure_k2_seeded | 0.834 | 0.434 | 0.517 | 66 | 0.711 |
| risk_guided_margin_adaptive_suffix_m0_05 | 0.972 | 0.440 | 0.534 | 12 | 0.838 |
| risk_guided_suffix_closure_k1 | 0.970 | 0.442 | 0.536 | 12 | 0.813 |
| risk_guided_suffix_closure_k2 | 0.984 | 0.452 | 0.546 | 6 | 0.929 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.452 | 0 |
| hybrid_query_risk_union_suffix_k1::external_2wiki | 0.974 | 0.442 | 11 |
| prefix_conditioned_naive_global::external_2wiki | 0.378 | 0.312 | 272 |
| query_similarity_suffix_closure_k1::external_2wiki | 0.918 | 0.410 | 37 |
| query_similarity_suffix_closure_k2::external_2wiki | 0.972 | 0.444 | 12 |
| random_suffix_closure_k1_seeded::external_2wiki | 0.650 | 0.400 | 144 |
| random_suffix_closure_k2_seeded::external_2wiki | 0.834 | 0.434 | 66 |
| risk_guided_margin_adaptive_suffix_m0_05::external_2wiki | 0.972 | 0.440 | 12 |
| risk_guided_suffix_closure_k1::external_2wiki | 0.970 | 0.442 | 12 |
| risk_guided_suffix_closure_k2::external_2wiki | 0.984 | 0.452 | 6 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e5d416220bdd11eba7f7acde48001122 | external_2wiki | 25.4328 | `5 October 1852` | `Information not provided in the given document.` | `5 October 1852` |
| 2wiki_281793980bdd11eba7f7acde48001122 | external_2wiki | 23.8154 | `in battle with the pro-Persian Georgian ruler Rostom of Kartli` | `Information not provided in the given document.` | `Astarabad` |
| 2wiki_0fc59fa00bde11eba7f7acde48001122 | external_2wiki | 23.6764 | `8 June 1746` | `Information not provided in the given document.` | `8 June 1746` |
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 23.6307 | `ca. March 19, 1666` | `1666` | `March 19, 1666` |
| 2wiki_35e09904086b11ebbd5fac1f6bf848b6 | external_2wiki | 23.4202 | `Axel von Ambesser` | `Sengottai Singam` | `I Learned It From Father` |
| 2wiki_424d56700bde11eba7f7acde48001122 | external_2wiki | 23.0127 | `Ostrogoths` | `English` | `Ostrogothic Kingdom` |
| 2wiki_c99fc05e0bd911eba7f7acde48001122 | external_2wiki | 22.2847 | `15 March 1981` | `Unknown` | `15 March 1981` |
| 2wiki_f9ac302a0bd911eba7f7acde48001122 | external_2wiki | 21.4467 | `Kiev` | `The document does not provide information about the birthplace of Vladimir Feldman's wife` | `Kiev` |
| 2wiki_5ff291a80bda11eba7f7acde48001122 | external_2wiki | 20.5672 | `The documents do not provide Chuck Berry's birthplace, only his birth year and` | `St. Louis, Missouri` | `St. Louis, Missouri` |
| 2wiki_accfdb580bd911eba7f7acde48001122 | external_2wiki | 20.3043 | `1964` | `Date of death unknown` | `10 October 1964` |

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
