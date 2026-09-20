# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1 | 1.000 | 0.600 | 0.754 | 0 | 0.924 |
| actual_recompute::query_similarity_suffix_closure_k1 | 0.940 | 0.600 | 0.750 | 2 | 0.852 |
| actual_recompute::query_similarity_suffix_closure_k2 | 0.940 | 0.600 | 0.750 | 2 | 0.886 |
| actual_recompute::risk_guided_suffix_closure_k1 | 1.000 | 0.600 | 0.754 | 0 | 0.917 |
| actual_recompute::risk_guided_suffix_closure_k2 | 1.000 | 0.600 | 0.754 | 0 | 0.952 |
| full_prefill | 1.000 | 0.600 | 0.754 | 0 | 0.000 |
| hybrid_query_risk_union_suffix_k1 | 1.000 | 0.600 | 0.754 | 0 | 0.924 |
| prefix_conditioned_naive_global | 0.520 | 0.360 | 0.469 | 23 | 0.000 |
| query_similarity_suffix_closure_k1 | 0.920 | 0.600 | 0.764 | 3 | 0.852 |
| query_similarity_suffix_closure_k2 | 0.920 | 0.600 | 0.764 | 3 | 0.886 |
| risk_guided_suffix_closure_k1 | 1.000 | 0.600 | 0.754 | 0 | 0.917 |
| risk_guided_suffix_closure_k2 | 1.000 | 0.600 | 0.754 | 0 | 0.952 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| actual_recompute::hybrid_query_risk_union_suffix_k1::external_hotpotqa | 1.000 | 0.600 | 0 |
| actual_recompute::query_similarity_suffix_closure_k1::external_hotpotqa | 0.940 | 0.600 | 2 |
| actual_recompute::query_similarity_suffix_closure_k2::external_hotpotqa | 0.940 | 0.600 | 2 |
| actual_recompute::risk_guided_suffix_closure_k1::external_hotpotqa | 1.000 | 0.600 | 0 |
| actual_recompute::risk_guided_suffix_closure_k2::external_hotpotqa | 1.000 | 0.600 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.600 | 0 |
| hybrid_query_risk_union_suffix_k1::external_hotpotqa | 1.000 | 0.600 | 0 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.520 | 0.360 | 23 |
| query_similarity_suffix_closure_k1::external_hotpotqa | 0.920 | 0.600 | 3 |
| query_similarity_suffix_closure_k2::external_hotpotqa | 0.920 | 0.600 | 3 |
| risk_guided_suffix_closure_k1::external_hotpotqa | 1.000 | 0.600 | 0 |
| risk_guided_suffix_closure_k2::external_hotpotqa | 1.000 | 0.600 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_1991 | external_hotpotqa | 12.5282 | `24` | `Fourteen main novels plus two additional bonus novels.` | `24` |
| hotpotqa_0638 | external_hotpotqa | 10.0016 | `SBS` | `National Geographic Channel` | `SBS` |
| hotpotqa_7267 | external_hotpotqa | 9.29212 | `Kentucky Wildcats` | `Duke` | `The 1997–98 Kentucky Wildcats men's basketball team` |
| hotpotqa_0327 | external_hotpotqa | 7.7611 | `"Power" (from My Beautiful Dark Twisted Fantasy)` | `The College Dropout` | `My Beautiful Dark Twisted Fantasy` |
| hotpotqa_0878 | external_hotpotqa | 7.09261 | `Shakespeare performances` | `actors who toured India and Asia with their theatre group, Shakespeareana, performing Shakespeare` | `Shakespeare performances` |
| hotpotqa_2952 | external_hotpotqa | 7.07883 | `Johnny McDaid` | `Paul van Dyk` | `Johnny McDaid` |
| hotpotqa_1564 | external_hotpotqa | 6.47237 | `British` | `Canada` | `a British composer` |
| hotpotqa_3263 | external_hotpotqa | 6.06551 | `Championship` | `Second division` | `second` |
| hotpotqa_5645 | external_hotpotqa | 5.90633 | `"Saturday Night Live"` | `The document does not provide information about Andrew "Andy" Spade's brother's` | `"Saturday Night Live"` |
| hotpotqa_4203 | external_hotpotqa | 4.96089 | `Prussia` | `House of Hohenzollern` | `Prussia` |

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
