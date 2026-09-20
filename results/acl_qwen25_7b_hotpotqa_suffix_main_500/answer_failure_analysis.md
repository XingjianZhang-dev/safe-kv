# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.544 | 0.708 | 0 | 0.000 |
| hybrid_query_risk_union_suffix_k1 | 0.996 | 0.542 | 0.708 | 2 | 0.904 |
| prefix_conditioned_naive_global | 0.472 | 0.354 | 0.489 | 241 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.930 | 0.522 | 0.696 | 32 | 0.842 |
| query_similarity_suffix_closure_k2 | 0.958 | 0.534 | 0.704 | 18 | 0.883 |
| random_suffix_closure_k1_seeded | 0.780 | 0.478 | 0.636 | 99 | 0.614 |
| random_suffix_closure_k2_seeded | 0.918 | 0.528 | 0.696 | 35 | 0.814 |
| risk_guided_suffix_closure_k1 | 0.996 | 0.542 | 0.708 | 2 | 0.892 |
| risk_guided_suffix_closure_k2 | 0.998 | 0.544 | 0.709 | 1 | 0.948 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_hotpotqa | 1.000 | 0.544 | 0 |
| hybrid_query_risk_union_suffix_k1::external_hotpotqa | 0.996 | 0.542 | 2 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.472 | 0.354 | 241 |
| query_similarity_suffix_closure_k1::external_hotpotqa | 0.930 | 0.522 | 32 |
| query_similarity_suffix_closure_k2::external_hotpotqa | 0.958 | 0.534 | 18 |
| random_suffix_closure_k1_seeded::external_hotpotqa | 0.780 | 0.478 | 99 |
| random_suffix_closure_k2_seeded::external_hotpotqa | 0.918 | 0.528 | 35 |
| risk_guided_suffix_closure_k1::external_hotpotqa | 0.996 | 0.542 | 2 |
| risk_guided_suffix_closure_k2::external_hotpotqa | 0.998 | 0.544 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0832 | external_hotpotqa | 23.258 | `racehorse breeder and owner` | `The document does not provide information about Terry Owen's son's profession after retiring from` | `racehorse breeder and owner` |
| hotpotqa_0340 | external_hotpotqa | 22.2098 | `Matt Flynn` | `Jizmak Da Gusha` | `Matt Flynn` |
| hotpotqa_6533 | external_hotpotqa | 20.6366 | `Northwest Mall` | `Almeda Mall` | `Northwest Mall` |
| hotpotqa_1362 | external_hotpotqa | 20.569 | `High School was shot over five weeks in March and April 1968` | `March and April 1968` | `1968` |
| hotpotqa_7295 | external_hotpotqa | 19.7302 | `Richard` | `Basiková` | `Penniman` |
| hotpotqa_6622 | external_hotpotqa | 18.392 | `Zola` | `Blue Dragon` | `Blue Dragon` |
| hotpotqa_6895 | external_hotpotqa | 18.196 | `International Hotel` | `Las Vegas Hilton` | `the Las Vegas Hilton` |
| hotpotqa_7377 | external_hotpotqa | 17.2601 | `Chocolate-colored` | `The document does not provide the color of the dog Buddy that Socks had conflicts` | `chocolate-colored` |
| hotpotqa_3315 | external_hotpotqa | 17.0561 | `"Dr. Death" Steve Williams` | `Steven Williams` | `"Dr. Death" Steve Williams` |
| hotpotqa_0510 | external_hotpotqa | 16.7207 | `Backstage (magazine)` | `black readers` | `people working in film and the performing arts` |

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
