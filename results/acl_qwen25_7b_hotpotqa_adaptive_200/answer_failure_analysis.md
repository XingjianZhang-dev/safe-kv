# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.555 | 0.691 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.650 | 0.475 | 0.581 | 62 | 0.320 |
| oracle_evidence_doc_suffix_closure_patch | 0.995 | 0.555 | 0.694 | 1 | 0.965 |
| prefix_conditioned_naive_global | 0.530 | 0.400 | 0.505 | 86 | 0.000 |
| query_similarity_adaptive_suffix_t0_65_k2 | 0.955 | 0.555 | 0.697 | 7 | 0.867 |
| query_similarity_doc_patch_k2 | 0.660 | 0.480 | 0.580 | 61 | 0.396 |
| query_similarity_suffix_closure_k2 | 0.965 | 0.560 | 0.702 | 5 | 0.885 |
| random_adaptive_suffix_t0_65_k2_seeded | 0.910 | 0.520 | 0.671 | 18 | 0.780 |
| random_doc_patch_k2_seeded | 0.660 | 0.495 | 0.602 | 58 | 0.385 |
| random_suffix_closure_k2_seeded | 0.925 | 0.555 | 0.692 | 13 | 0.811 |
| risk_guided_adaptive_suffix_t0_65_k2 | 0.980 | 0.545 | 0.684 | 4 | 0.929 |
| risk_guided_doc_patch_k2 | 0.645 | 0.470 | 0.569 | 65 | 0.340 |
| risk_guided_suffix_closure_k2 | 0.995 | 0.555 | 0.694 | 1 | 0.950 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_hotpotqa | 1.000 | 0.555 | 0 |
| oracle_evidence_doc_patch::external_hotpotqa | 0.650 | 0.475 | 62 |
| oracle_evidence_doc_suffix_closure_patch::external_hotpotqa | 0.995 | 0.555 | 1 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.530 | 0.400 | 86 |
| query_similarity_adaptive_suffix_t0_65_k2::external_hotpotqa | 0.955 | 0.555 | 7 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.660 | 0.480 | 61 |
| query_similarity_suffix_closure_k2::external_hotpotqa | 0.965 | 0.560 | 5 |
| random_adaptive_suffix_t0_65_k2_seeded::external_hotpotqa | 0.910 | 0.520 | 18 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.660 | 0.495 | 58 |
| random_suffix_closure_k2_seeded::external_hotpotqa | 0.925 | 0.555 | 13 |
| risk_guided_adaptive_suffix_t0_65_k2::external_hotpotqa | 0.980 | 0.545 | 4 |
| risk_guided_doc_patch_k2::external_hotpotqa | 0.645 | 0.470 | 65 |
| risk_guided_suffix_closure_k2::external_hotpotqa | 0.995 | 0.555 | 1 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0340 | external_hotpotqa | 22.2098 | `Matt Flynn` | `Jizmak Da Gusha` | `Matt Flynn` |
| hotpotqa_6622 | external_hotpotqa | 18.392 | `Zola` | `Blue Dragon` | `Blue Dragon` |
| hotpotqa_6895 | external_hotpotqa | 18.196 | `International Hotel` | `Las Vegas Hilton` | `the Las Vegas Hilton` |
| hotpotqa_2830 | external_hotpotqa | 15.7999 | `Park Drive` | `Agawam River` | `Potomac River` |
| hotpotqa_1284 | external_hotpotqa | 14.8028 | `eight girls and nine boys` | `nine girls and 10 boys` | `nine girls and 10 boys` |
| hotpotqa_0267 | external_hotpotqa | 12.9428 | `Lady Antebellum` | `Scott Whitehead` | `Charles Kelley` |
| hotpotqa_0763 | external_hotpotqa | 12.5391 | `Traverse City` | `14,674` | `143,372` |
| hotpotqa_1991 | external_hotpotqa | 12.4678 | `24` | `Fourteen main novels plus two additional bonus novels.` | `24` |
| hotpotqa_1904 | external_hotpotqa | 11.3761 | `January 16, 2013` | `The document does not provide the first air date for the CGI animated series that preceded` | `January 16, 2013` |
| hotpotqa_1108 | external_hotpotqa | 11.1963 | `flowering plants` | `There is no information in the provided document about any species in the Lithocarp` | `trees` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0257 | external_hotpotqa | 0.012149 | `Mountbatten family` | `Mountbatten family` | `Mountbatten family` |
| hotpotqa_0717 | external_hotpotqa | 0.0292976 | `Coca-Cola FEMSA` | `Coca-Cola FEMSA` | `Fomento Económico Mexicano` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_7354 | external_hotpotqa | 0.854496 | `Gulfport–Biloxi Metropolitan Statistical Area` | `Gulfport–Biloxi Metropolitan Statistical Area` | `Gulfport, Biloxi` |
| hotpotqa_0878 | external_hotpotqa | 0.0106527 | `Shakespeare performances` | `Shakespeare performances` | `Shakespeare performances` |
| hotpotqa_0257 | external_hotpotqa | 0.0015989 | `Mountbatten family` | `Mountbatten family` | `Mountbatten family` |
| hotpotqa_1916 | external_hotpotqa | 0.289317 | `Kim Bauer` | `Kim Bauer` | `Kim Bauer` |
| hotpotqa_1481 | external_hotpotqa | 0.519199 | `Dana Fox` | `Dana Fox` | `Dana Fox` |
| hotpotqa_6410 | external_hotpotqa | 0.507813 | `acting career` | `acting career` | `an acting career` |
| hotpotqa_5630 | external_hotpotqa | 0.00663421 | `Minnesota State University, Mankato` | `Minnesota State University, Mankato` | `Minnesota State Mavericks` |
| hotpotqa_0717 | external_hotpotqa | 3.37239e-05 | `Coca-Cola FEMSA` | `Coca-Cola FEMSA` | `Fomento Económico Mexicano` |
| hotpotqa_4487 | external_hotpotqa | 0.426939 | `Cincinnati Bengals` | `Cincinnati Bengals` | `Cincinnati Bengals` |
