# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 0.980 | 0.340 | 0.427 | 1 | 0.834 |
| actual_recompute::query_similarity_suffix_closure_k1 | 0.860 | 0.360 | 0.440 | 5 | 0.732 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.940 | 0.360 | 0.447 | 2 | 0.874 |
| actual_recompute::risk_guided_suffix_closure_k1 | 0.980 | 0.340 | 0.427 | 1 | 0.814 |
| actual_recompute::risk_guided_suffix_closure_k2 | 0.980 | 0.340 | 0.427 | 1 | 0.940 |
| full_prefill | 1.000 | 0.360 | 0.447 | 0 | 0.000 |
| hybrid_query_risk_union_suffix_k1 | 0.980 | 0.340 | 0.427 | 1 | 0.834 |
| prefix_conditioned_naive_global | 0.320 | 0.320 | 0.410 | 28 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.880 | 0.340 | 0.420 | 5 | 0.732 |
| query_similarity_suffix_closure_k2 | 0.940 | 0.360 | 0.447 | 2 | 0.874 |
| risk_guided_suffix_closure_k1 | 0.980 | 0.340 | 0.427 | 1 | 0.814 |
| risk_guided_suffix_closure_k2 | 0.980 | 0.340 | 0.427 | 1 | 0.940 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_2wiki | 0.980 | 0.340 | 1 |
| actual_recompute::query_similarity_suffix_closure_k1::external_2wiki | 0.860 | 0.360 | 5 |
| actual_recompute::query_similarity_suffix_closure_k2::external_2wiki | 0.940 | 0.360 | 2 |
| actual_recompute::risk_guided_suffix_closure_k1::external_2wiki | 0.980 | 0.340 | 1 |
| actual_recompute::risk_guided_suffix_closure_k2::external_2wiki | 0.980 | 0.340 | 1 |
| full_prefill::external_2wiki | 1.000 | 0.360 | 0 |
| hybrid_query_risk_union_suffix_k1::external_2wiki | 0.980 | 0.340 | 1 |
| prefix_conditioned_naive_global::external_2wiki | 0.320 | 0.320 | 28 |
| query_similarity_suffix_closure_k1::external_2wiki | 0.880 | 0.340 | 5 |
| query_similarity_suffix_closure_k2::external_2wiki | 0.940 | 0.360 | 2 |
| risk_guided_suffix_closure_k1::external_2wiki | 0.980 | 0.340 | 1 |
| risk_guided_suffix_closure_k2::external_2wiki | 0.980 | 0.340 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 23.5841 | `ca. March 19, 1666` | `1666` | `March 19, 1666` |
| 2wiki_c99fc05e0bd911eba7f7acde48001122 | external_2wiki | 22.2624 | `15 March 1981` | `Unknown` | `15 March 1981` |
| 2wiki_e051bd000bdb11eba7f7acde48001122 | external_2wiki | 14.9318 | `British` | `Liverpool` | `British` |
| 2wiki_62ce8c8e0bde11eba7f7acde48001122 | external_2wiki | 12.7826 | `Emperor Zhang of Han` | `The document does not provide information about the place of birth of Consort Liang's` | `Chinese` |
| 2wiki_3cddcc46086511ebbd5eac1f6bf848b6 | external_2wiki | 11.9062 | `Peter Haslop` | `Barbara Nawratowicz` | `Barbara Nawratowicz` |
| 2wiki_003285a80bde11eba7f7acde48001122 | external_2wiki | 11.7896 | `Tamil` | `Kazakh` | `chola kingdom` |
| 2wiki_e6a4ff4c0bda11eba7f7acde48001122 | external_2wiki | 11.5541 | `The information provided does not include the death date of the director of "The General` | `11 February 1948` | `11 February 1948` |
| 2wiki_041879d0093a11ebbdaeac1f6bf848b6 | external_2wiki | 10.5806 | `End of Watch` | `Burnt by the Sun` | `Burnt By The Sun` |
| 2wiki_27d8ec30091f11ebbdaeac1f6bf848b6 | external_2wiki | 10.4837 | `The Clink of Ice` | `Guilty?` | `Guilty?` |
| 2wiki_8d3d54ec0bdd11eba7f7acde48001122 | external_2wiki | 9.6699 | `Castle of Bredevoort` | `The document does not provide the place of death for Engelbert I's father,` | `Altenberg` |

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
