# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.540 | 0.714 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.520 | 0.370 | 0.505 | 44 | 0.000 |
| query_similarity_doc_patch_k1 | 0.560 | 0.410 | 0.553 | 40 | 0.188 |
| query_similarity_doc_patch_k2 | 0.640 | 0.450 | 0.601 | 32 | 0.401 |
| query_similarity_doc_patch_k4 | 0.890 | 0.520 | 0.684 | 9 | 0.794 |
| query_similarity_suffix_closure_k1 | 0.950 | 0.540 | 0.719 | 4 | 0.848 |
| query_similarity_suffix_closure_k2 | 0.960 | 0.540 | 0.719 | 3 | 0.882 |
| query_similarity_suffix_closure_k4 | 1.000 | 0.540 | 0.714 | 0 | 0.933 |
| random_doc_patch_k1_seeded | 0.580 | 0.400 | 0.554 | 38 | 0.200 |
| random_doc_patch_k2_seeded | 0.660 | 0.480 | 0.611 | 29 | 0.395 |
| random_doc_patch_k4_seeded | 0.840 | 0.540 | 0.700 | 14 | 0.769 |
| random_suffix_closure_k1_seeded | 0.850 | 0.540 | 0.688 | 13 | 0.631 |
| random_suffix_closure_k2_seeded | 0.940 | 0.530 | 0.707 | 5 | 0.824 |
| random_suffix_closure_k4_seeded | 1.000 | 0.540 | 0.714 | 0 | 0.929 |
| risk_guided_doc_patch_k1 | 0.550 | 0.390 | 0.534 | 41 | 0.162 |
| risk_guided_doc_patch_k2 | 0.640 | 0.460 | 0.593 | 32 | 0.335 |
| risk_guided_doc_patch_k4 | 0.850 | 0.520 | 0.679 | 14 | 0.774 |
| risk_guided_suffix_closure_k1 | 1.000 | 0.540 | 0.714 | 0 | 0.895 |
| risk_guided_suffix_closure_k2 | 1.000 | 0.540 | 0.714 | 0 | 0.954 |
| risk_guided_suffix_closure_k4 | 1.000 | 0.540 | 0.714 | 0 | 0.961 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_hotpotqa | 1.000 | 0.540 | 0 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.520 | 0.370 | 44 |
| query_similarity_doc_patch_k1::external_hotpotqa | 0.560 | 0.410 | 40 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.640 | 0.450 | 32 |
| query_similarity_doc_patch_k4::external_hotpotqa | 0.890 | 0.520 | 9 |
| query_similarity_suffix_closure_k1::external_hotpotqa | 0.950 | 0.540 | 4 |
| query_similarity_suffix_closure_k2::external_hotpotqa | 0.960 | 0.540 | 3 |
| query_similarity_suffix_closure_k4::external_hotpotqa | 1.000 | 0.540 | 0 |
| random_doc_patch_k1_seeded::external_hotpotqa | 0.580 | 0.400 | 38 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.660 | 0.480 | 29 |
| random_doc_patch_k4_seeded::external_hotpotqa | 0.840 | 0.540 | 14 |
| random_suffix_closure_k1_seeded::external_hotpotqa | 0.850 | 0.540 | 13 |
| random_suffix_closure_k2_seeded::external_hotpotqa | 0.940 | 0.530 | 5 |
| random_suffix_closure_k4_seeded::external_hotpotqa | 1.000 | 0.540 | 0 |
| risk_guided_doc_patch_k1::external_hotpotqa | 0.550 | 0.390 | 41 |
| risk_guided_doc_patch_k2::external_hotpotqa | 0.640 | 0.460 | 32 |
| risk_guided_doc_patch_k4::external_hotpotqa | 0.850 | 0.520 | 14 |
| risk_guided_suffix_closure_k1::external_hotpotqa | 1.000 | 0.540 | 0 |
| risk_guided_suffix_closure_k2::external_hotpotqa | 1.000 | 0.540 | 0 |
| risk_guided_suffix_closure_k4::external_hotpotqa | 1.000 | 0.540 | 0 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0340 | external_hotpotqa | 22.2098 | `Matt Flynn` | `Jizmak Da Gusha` | `Matt Flynn` |
| hotpotqa_2830 | external_hotpotqa | 15.7999 | `Park Drive` | `Agawam River` | `Potomac River` |
| hotpotqa_1284 | external_hotpotqa | 14.8028 | `eight girls and nine boys` | `nine girls and 10 boys` | `nine girls and 10 boys` |
| hotpotqa_1991 | external_hotpotqa | 12.4678 | `24` | `Fourteen main novels plus two additional bonus novels.` | `24` |
| hotpotqa_1904 | external_hotpotqa | 11.3761 | `January 16, 2013` | `The document does not provide the first air date for the CGI animated series that preceded` | `January 16, 2013` |
| hotpotqa_1108 | external_hotpotqa | 11.1963 | `flowering plants` | `There is no information in the provided document about any species in the Lithocarp` | `trees` |
| hotpotqa_0638 | external_hotpotqa | 10.0016 | `SBS` | `National Geographic Channel` | `SBS` |
| hotpotqa_7267 | external_hotpotqa | 9.36744 | `Kentucky Wildcats` | `Duke` | `The 1997–98 Kentucky Wildcats men's basketball team` |
| hotpotqa_3700 | external_hotpotqa | 8.61549 | `Zack Snyder's version` | `the remake by George A. Romero` | `Zack Snyder` |
| hotpotqa_6334 | external_hotpotqa | 8.40662 | `Kevin Richardson was inducted into the Kentucky Music Hall of Fame.` | `Kentucky Music Hall of Fame` | `Kentucky Music Hall of Fame` |

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
| hotpotqa_0878 | external_hotpotqa | 0.0106527 | `Shakespeare performances` | `Shakespeare performances` | `Shakespeare performances` |
| hotpotqa_1916 | external_hotpotqa | 0.289317 | `Kim Bauer` | `Kim Bauer` | `Kim Bauer` |
| hotpotqa_1481 | external_hotpotqa | 0.519199 | `Dana Fox` | `Dana Fox` | `Dana Fox` |
| hotpotqa_0717 | external_hotpotqa | 3.37239e-05 | `Coca-Cola FEMSA` | `Coca-Cola FEMSA` | `Fomento Económico Mexicano` |
| hotpotqa_4487 | external_hotpotqa | 0.426939 | `Cincinnati Bengals` | `Cincinnati Bengals` | `Cincinnati Bengals` |
