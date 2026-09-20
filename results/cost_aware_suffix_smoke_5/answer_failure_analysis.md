# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.200 | 0.200 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.000 | 0.000 | 0.000 | 5 | 0.000 |
| query_similarity_cost_aware_suffix_a0_10 | 0.800 | 0.200 | 0.200 | 1 | 0.415 |
| query_similarity_suffix_closure_k1 | 1.000 | 0.200 | 0.200 | 0 | 0.694 |
| risk_guided_cost_aware_suffix_a0_10 | 1.000 | 0.200 | 0.200 | 0 | 0.694 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.200 | 0 |
| prefix_conditioned_naive_global::external_2wiki | 0.000 | 0.000 | 5 |
| query_similarity_cost_aware_suffix_a0_10::external_2wiki | 0.800 | 0.200 | 1 |
| query_similarity_suffix_closure_k1::external_2wiki | 1.000 | 0.200 | 0 |
| risk_guided_cost_aware_suffix_a0_10::external_2wiki | 1.000 | 0.200 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e051bd000bdb11eba7f7acde48001122 | external_2wiki | 14.9688 | `British` | `Liverpool` | `British` |
| 2wiki_782f0c160bd911eba7f7acde48001122 | external_2wiki | 7.0027 | `Jagathy Sreekumar` | `born in 1961` | `Trivandrum` |
| 2wiki_a1c37dc40bdd11eba7f7acde48001122 | external_2wiki | 5.54442 | `Sheena Shahabadi is an actress, but Michael Reagan's mother is Jane` | `actress` | `Warner Bros.` |
| 2wiki_21e70b7e0bde11eba7f7acde48001122 | external_2wiki | 2.31484 | `Russia` | `Germany` | `Prussia` |
| 2wiki_34c3dd940bde11eba7f7acde48001122 | external_2wiki | 0.819143 | `The documents do not provide the place of death of Tegbesu's father` | `The place of death of Tegbesu's father is not mentioned in the` | `Allada` |

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
