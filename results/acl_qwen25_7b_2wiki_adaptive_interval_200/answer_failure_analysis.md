# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| full_prefill | 1.000 | 0.425 | 0.530 | 0 | 0.000 |
| oracle_evidence_doc_linked_interval_patch | 0.880 | 0.405 | 0.517 | 19 | 0.913 |
| oracle_evidence_doc_patch | 0.560 | 0.435 | 0.519 | 73 | 0.537 |
| oracle_evidence_doc_suffix_closure_patch | 0.995 | 0.425 | 0.531 | 1 | 0.958 |
| prefix_conditioned_naive_global | 0.425 | 0.325 | 0.414 | 102 | 0.000 |
| query_similarity_adaptive_suffix_t0_65_k2 | 0.945 | 0.410 | 0.511 | 10 | 0.854 |
| query_similarity_doc_patch_k2 | 0.505 | 0.380 | 0.471 | 86 | 0.479 |
| query_similarity_linked_interval_k2 | 0.855 | 0.390 | 0.504 | 24 | 0.826 |
| query_similarity_suffix_closure_k2 | 0.975 | 0.420 | 0.525 | 4 | 0.878 |
| random_adaptive_suffix_t0_65_k2_seeded | 0.875 | 0.395 | 0.504 | 24 | 0.676 |
| random_doc_patch_k2_seeded | 0.550 | 0.425 | 0.510 | 72 | 0.365 |
| random_linked_interval_k2_seeded | 0.795 | 0.390 | 0.489 | 34 | 0.696 |
| random_suffix_closure_k2_seeded | 0.885 | 0.445 | 0.542 | 16 | 0.717 |
| risk_guided_adaptive_suffix_t0_65_k2 | 0.960 | 0.410 | 0.512 | 8 | 0.897 |
| risk_guided_doc_patch_k2 | 0.540 | 0.420 | 0.506 | 76 | 0.493 |
| risk_guided_linked_interval_k2 | 0.865 | 0.390 | 0.502 | 22 | 0.871 |
| risk_guided_suffix_closure_k2 | 0.990 | 0.420 | 0.526 | 2 | 0.922 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| full_prefill::external_2wiki | 1.000 | 0.425 | 0 |
| oracle_evidence_doc_linked_interval_patch::external_2wiki | 0.880 | 0.405 | 19 |
| oracle_evidence_doc_patch::external_2wiki | 0.560 | 0.435 | 73 |
| oracle_evidence_doc_suffix_closure_patch::external_2wiki | 0.995 | 0.425 | 1 |
| prefix_conditioned_naive_global::external_2wiki | 0.425 | 0.325 | 102 |
| query_similarity_adaptive_suffix_t0_65_k2::external_2wiki | 0.945 | 0.410 | 10 |
| query_similarity_doc_patch_k2::external_2wiki | 0.505 | 0.380 | 86 |
| query_similarity_linked_interval_k2::external_2wiki | 0.855 | 0.390 | 24 |
| query_similarity_suffix_closure_k2::external_2wiki | 0.975 | 0.420 | 4 |
| random_adaptive_suffix_t0_65_k2_seeded::external_2wiki | 0.875 | 0.395 | 24 |
| random_doc_patch_k2_seeded::external_2wiki | 0.550 | 0.425 | 72 |
| random_linked_interval_k2_seeded::external_2wiki | 0.795 | 0.390 | 34 |
| random_suffix_closure_k2_seeded::external_2wiki | 0.885 | 0.445 | 16 |
| risk_guided_adaptive_suffix_t0_65_k2::external_2wiki | 0.960 | 0.410 | 8 |
| risk_guided_doc_patch_k2::external_2wiki | 0.540 | 0.420 | 76 |
| risk_guided_linked_interval_k2::external_2wiki | 0.865 | 0.390 | 22 |
| risk_guided_suffix_closure_k2::external_2wiki | 0.990 | 0.420 | 2 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e5d416220bdd11eba7f7acde48001122 | external_2wiki | 25.4328 | `5 October 1852` | `Information not provided in the given document.` | `5 October 1852` |
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 23.6307 | `ca. March 19, 1666` | `1666` | `March 19, 1666` |
| 2wiki_35e09904086b11ebbd5fac1f6bf848b6 | external_2wiki | 23.4202 | `Axel von Ambesser` | `Sengottai Singam` | `I Learned It From Father` |
| 2wiki_c99fc05e0bd911eba7f7acde48001122 | external_2wiki | 22.2847 | `15 March 1981` | `Unknown` | `15 March 1981` |
| 2wiki_accfdb580bd911eba7f7acde48001122 | external_2wiki | 20.3043 | `1964` | `Date of death unknown` | `10 October 1964` |
| 2wiki_5a4826b00bde11eba7f7acde48001122 | external_2wiki | 19.2929 | `1032` | `The document does not provide the date of death of Constance of Burgundy's` | `21 March 1076` |
| 2wiki_17904a03087611ebbd67ac1f6bf848b6 | external_2wiki | 18.9744 | `Roy William Neill` | `Publicity Madness` | `Eyes Of The Underworld` |
| 2wiki_c6ac8fcc0bdd11eba7f7acde48001122 | external_2wiki | 18.7393 | `Brisbane, Queensland` | `The document does not provide information about the birthplace of Michael Bryce's wife.` | `Brisbane` |
| 2wiki_61e86d5a0bdc11eba7f7acde48001122 | external_2wiki | 18.5825 | `Document 1 does not provide information about where Kearen Pang studied.` | `Paris Studio Magenia` | `Hong Kong Academy for Performing Arts` |
| 2wiki_2b9500fe0bde11eba7f7acde48001122 | external_2wiki | 17.3951 | `22 June 1893` | `The document does not provide the date of death of George Tryon's father.` | `22 June 1893` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| none | - | 0 | - | - | - |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e95acdbc085f11ebbd5dac1f6bf848b6 | external_2wiki | 0.282194 | `Deuce High` | `Deuce High` | `The King Is The Best Mayor` |
| 2wiki_566c1e2c08a811ebbd7fac1f6bf848b6 | external_2wiki | 0.19934 | `Riders of the Santa Fe` | `Riders of the Santa Fe` | `Riders Of The Santa Fe` |
| 2wiki_61644425091011ebbdadac1f6bf848b6 | external_2wiki | 0.020778 | `Swaroopa` | `Swaroopa` | `Swaroopa` |
| 2wiki_a346f150089811ebbd77ac1f6bf848b6 | external_2wiki | 0.000887322 | `The Incredibly Strange Creatures Who Stopped Living and Became Mixed-Up Zombies` | `The Incredibly Strange Creatures Who Stopped Living and Became Mixed- Up Zombies` | `The Incredibly Strange Creatures Who Stopped Living And Became Mixed-Up Zombies` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_6dd2e77a0bb011ebab90acde48001122 | external_2wiki | 0.461766 | `Denise Robins` | `Denise Robins` | `Patricia Robins` |
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 0.387695 | `Archduke Maximilian Eugen of Austria` | `Archduke Maximilian Eugen of Austria` | `Charles I of Austria` |
| 2wiki_c370b4540bd911eba7f7acde48001122 | external_2wiki | 0.204313 | `Rasual Butler` | `Rasual Butler` | `Rasual Butler` |
| 2wiki_1865e1e40bdc11eba7f7acde48001122 | external_2wiki | 0.129998 | `Naples, Florida` | `Naples, Florida` | `Naples` |
| 2wiki_566c1e2c08a811ebbd7fac1f6bf848b6 | external_2wiki | 0.103057 | `Riders of the Santa Fe` | `Riders of the Santa Fe` | `Riders Of The Santa Fe` |
| 2wiki_5ead23420baf11ebab90acde48001122 | external_2wiki | 0.539395 | `Lord William Powlett` | `Lord William Powlett` | `Charles Paulet, 1st Duke of Bolton` |
| 2wiki_016e72260bdc11eba7f7acde48001122 | external_2wiki | 0.185272 | `Selena` | `Selena` | `Chris Pérez` |
| 2wiki_61644425091011ebbdadac1f6bf848b6 | external_2wiki | 0.245836 | `Swaroopa` | `Swaroopa` | `Swaroopa` |
| 2wiki_3e0cebde0bd911eba7f7acde48001122 | external_2wiki | 0.0037948 | `China` | `China` | `Chinese` |
| 2wiki_a346f150089811ebbd77ac1f6bf848b6 | external_2wiki | 0.0623044 | `The Incredibly Strange Creatures Who Stopped Living and Became Mixed-Up Zombies` | `The Incredibly Strange Creatures Who Stopped Living And Became Mixed-Up Zombies` | `The Incredibly Strange Creatures Who Stopped Living And Became Mixed-Up Zombies` |
