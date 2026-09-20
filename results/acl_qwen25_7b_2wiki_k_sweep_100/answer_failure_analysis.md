# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.420 | 0.505 | 0 | 0.000 |
| prefix_conditioned_naive_global | 0.350 | 0.320 | 0.392 | 57 | 0.000 |
| query_similarity_doc_patch_k1 | 0.400 | 0.370 | 0.454 | 52 | 0.229 |
| query_similarity_doc_patch_k2 | 0.450 | 0.380 | 0.467 | 46 | 0.472 |
| query_similarity_doc_patch_k4 | 0.670 | 0.380 | 0.475 | 27 | 0.780 |
| query_similarity_suffix_closure_k1 | 0.920 | 0.390 | 0.472 | 7 | 0.754 |
| query_similarity_suffix_closure_k2 | 0.970 | 0.420 | 0.505 | 2 | 0.868 |
| query_similarity_suffix_closure_k4 | 0.980 | 0.410 | 0.497 | 2 | 0.917 |
| random_doc_patch_k1_seeded | 0.390 | 0.360 | 0.432 | 53 | 0.165 |
| random_doc_patch_k2_seeded | 0.490 | 0.450 | 0.521 | 38 | 0.374 |
| random_doc_patch_k4_seeded | 0.680 | 0.390 | 0.481 | 24 | 0.739 |
| random_suffix_closure_k1_seeded | 0.720 | 0.400 | 0.477 | 22 | 0.509 |
| random_suffix_closure_k2_seeded | 0.870 | 0.420 | 0.506 | 10 | 0.716 |
| random_suffix_closure_k4_seeded | 0.990 | 0.420 | 0.507 | 1 | 0.897 |
| risk_guided_doc_patch_k1 | 0.380 | 0.350 | 0.436 | 54 | 0.226 |
| risk_guided_doc_patch_k2 | 0.470 | 0.420 | 0.507 | 43 | 0.496 |
| risk_guided_doc_patch_k4 | 0.660 | 0.390 | 0.486 | 29 | 0.814 |
| risk_guided_suffix_closure_k1 | 0.970 | 0.410 | 0.495 | 2 | 0.793 |
| risk_guided_suffix_closure_k2 | 0.980 | 0.410 | 0.497 | 2 | 0.924 |
| risk_guided_suffix_closure_k4 | 0.990 | 0.420 | 0.507 | 1 | 0.953 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.420 | 0 |
| prefix_conditioned_naive_global::external_2wiki | 0.350 | 0.320 | 57 |
| query_similarity_doc_patch_k1::external_2wiki | 0.400 | 0.370 | 52 |
| query_similarity_doc_patch_k2::external_2wiki | 0.450 | 0.380 | 46 |
| query_similarity_doc_patch_k4::external_2wiki | 0.670 | 0.380 | 27 |
| query_similarity_suffix_closure_k1::external_2wiki | 0.920 | 0.390 | 7 |
| query_similarity_suffix_closure_k2::external_2wiki | 0.970 | 0.420 | 2 |
| query_similarity_suffix_closure_k4::external_2wiki | 0.980 | 0.410 | 2 |
| random_doc_patch_k1_seeded::external_2wiki | 0.390 | 0.360 | 53 |
| random_doc_patch_k2_seeded::external_2wiki | 0.490 | 0.450 | 38 |
| random_doc_patch_k4_seeded::external_2wiki | 0.680 | 0.390 | 24 |
| random_suffix_closure_k1_seeded::external_2wiki | 0.720 | 0.400 | 22 |
| random_suffix_closure_k2_seeded::external_2wiki | 0.870 | 0.420 | 10 |
| random_suffix_closure_k4_seeded::external_2wiki | 0.990 | 0.420 | 1 |
| risk_guided_doc_patch_k1::external_2wiki | 0.380 | 0.350 | 54 |
| risk_guided_doc_patch_k2::external_2wiki | 0.470 | 0.420 | 43 |
| risk_guided_doc_patch_k4::external_2wiki | 0.660 | 0.390 | 29 |
| risk_guided_suffix_closure_k1::external_2wiki | 0.970 | 0.410 | 2 |
| risk_guided_suffix_closure_k2::external_2wiki | 0.980 | 0.410 | 2 |
| risk_guided_suffix_closure_k4::external_2wiki | 0.990 | 0.420 | 1 |

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
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 0.387695 | `Archduke Maximilian Eugen of Austria` | `Archduke Maximilian Eugen of Austria` | `Charles I of Austria` |
| 2wiki_c370b4540bd911eba7f7acde48001122 | external_2wiki | 0.204313 | `Rasual Butler` | `Rasual Butler` | `Rasual Butler` |
| 2wiki_566c1e2c08a811ebbd7fac1f6bf848b6 | external_2wiki | 0.103057 | `Riders of the Santa Fe` | `Riders of the Santa Fe` | `Riders Of The Santa Fe` |
| 2wiki_5ead23420baf11ebab90acde48001122 | external_2wiki | 0.539395 | `Lord William Powlett` | `Lord William Powlett` | `Charles Paulet, 1st Duke of Bolton` |
| 2wiki_016e72260bdc11eba7f7acde48001122 | external_2wiki | 0.185272 | `Selena` | `Selena` | `Chris Pérez` |
| 2wiki_61644425091011ebbdadac1f6bf848b6 | external_2wiki | 0.245836 | `Swaroopa` | `Swaroopa` | `Swaroopa` |
| 2wiki_3e0cebde0bd911eba7f7acde48001122 | external_2wiki | 0.0037948 | `China` | `China` | `Chinese` |
