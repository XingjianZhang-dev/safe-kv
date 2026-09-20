# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.500 | 0.230 | 0.310 | 43 | 0.415 |
| full_prefill | 1.000 | 0.250 | 0.357 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.470 | 0.220 | 0.307 | 47 | 0.416 |
| prefix_conditioned_naive_global | 0.410 | 0.230 | 0.331 | 49 | 0.000 |
| query_similarity_doc_patch_k2 | 0.500 | 0.220 | 0.316 | 43 | 0.447 |
| random_doc_patch_k2_seeded | 0.550 | 0.240 | 0.342 | 39 | 0.387 |
| safe_gate_t0.60 | 0.480 | 0.220 | 0.314 | 45 | 0.425 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::external_2wiki | 0.480 | 0.260 | 20 |
| entity_overlap_doc_patch_k2::external_hotpotqa | 0.520 | 0.200 | 23 |
| full_prefill::external_2wiki | 1.000 | 0.200 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.300 | 0 |
| oracle_evidence_doc_patch::external_2wiki | 0.480 | 0.180 | 23 |
| oracle_evidence_doc_patch::external_hotpotqa | 0.460 | 0.260 | 24 |
| prefix_conditioned_naive_global::external_2wiki | 0.400 | 0.260 | 23 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.420 | 0.200 | 26 |
| query_similarity_doc_patch_k2::external_2wiki | 0.480 | 0.200 | 22 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.520 | 0.240 | 21 |
| random_doc_patch_k2_seeded::external_2wiki | 0.500 | 0.260 | 19 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.600 | 0.220 | 20 |
| safe_gate_t0.60::external_2wiki | 0.480 | 0.220 | 21 |
| safe_gate_t0.60::external_hotpotqa | 0.480 | 0.220 | 24 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 5.31846 | `Maximilian Eugen` | `Princess Leopodine of Löwenstein- Wertheim- Roch` | `Charles I of Austria` |
| hotpotqa_4835 | external_hotpotqa | 4.42292 | `Wren` | `Thalassery` | `East Knoyle` |
| 2wiki_350ec8b80bde11eba7f7acde48001122 | external_2wiki | 4.21525 | `Harold R. Atteridge` | `Atlantic City, New Jersey` | `Atlantic City, New Jersey` |
| 2wiki_34c3dd940bde11eba7f7acde48001122 | external_2wiki | 3.77263 | `Loiret department, north-central France` | `Allada` | `Allada` |
| 2wiki_21832f3c0bde11eba7f7acde48001122 | external_2wiki | 3.70964 | `Italy` | `Burgundian castle` | `Italy` |
| hotpotqa_2482 | external_hotpotqa | 3.64245 | `Chuck Long played for the Detroit Lions and the Los Angeles Rams professionally.` | `The 2007 San Diego State Aztecs played for the San` | `Detroit Lions and the Los Angeles Rams` |
| 2wiki_9b8278a20bdd11eba7f7acde48001122 | external_2wiki | 2.89492 | `Hastings, Minnesota` | `Fredrikstad` | `Hastings, Minnesota` |
| 2wiki_d60529440baf11ebab90acde48001122 | external_2wiki | 2.66488 | `Andrzej Gawroński` | `The uncle of Nawrahta of Kanni is the late actor.` | `Yazathingyan` |
| hotpotqa_0638 | external_hotpotqa | 2.50483 | `GSN Live` | `National Geographic Channel` | `SBS` |
| hotpotqa_1991 | external_hotpotqa | 2.4865 | `24` | `Four` | `24` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_21e70b7e0bde11eba7f7acde48001122 | external_2wiki | 1.17624 | `Duke of Schleswig-Holstein-Sonderburg-Beck` | `Duke of Schleswig- Holstein- Sonderburg- Beck` | `Prussia` |
| hotpotqa_4537 | external_hotpotqa | 0.49599 | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` |
| hotpotqa_7385 | external_hotpotqa | 0.412095 | `Weider Publications` | `Weider Publications` | `Christine MacIntyre` |
| 2wiki_322178260bde11eba7f7acde48001122 | external_2wiki | 0.344782 | `1309` | `1309` | `Cadolzburg` |
| 2wiki_6d1fa90e086711ebbd5eac1f6bf848b6 | external_2wiki | 0.0480749 | `Lyubomira Kazanova` | `Lyubomira Kazanova` | `Nadia Min Dern Heng` |
| hotpotqa_4389 | external_hotpotqa | 0.0747274 | `Acela Express` | `Acela Express` | `Acela Express` |
| hotpotqa_1481 | external_hotpotqa | 0.113692 | `Dana Fox` | `Dana Fox` | `Dana Fox` |
| hotpotqa_1679 | external_hotpotqa | 0.357621 | `24 March` | `24 March` | `4 April 1963` |
| hotpotqa_4222 | external_hotpotqa | 0.0657968 | `New Jersey City` | `New Jersey City` | `New York City` |
| 2wiki_dbca21a20bd911eba7f7acde48001122 | external_2wiki | 0.0107377 | `Algiers, Alger, France` | `Algiers, Alger, France` | `Algiers` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0878 | external_hotpotqa | 0.129612 | `Shakespeare performances` | `Shakespeare performances` | `Shakespeare performances` |
| hotpotqa_4537 | external_hotpotqa | 0.49599 | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0638 | external_hotpotqa | 0.858687 | `GSN Live` | `GSN Live` | `SBS` |
| hotpotqa_2569 | external_hotpotqa | 0.276762 | `KXII` | `KXII` | `KXII` |
| hotpotqa_4537 | external_hotpotqa | 0.241579 | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` | `Hakim Abdullah Jamal` |
| hotpotqa_1564 | external_hotpotqa | 0.430643 | `United States` | `United States` | `a British composer` |
| 2wiki_003285a80bde11eba7f7acde48001122 | external_2wiki | 0.0708613 | `Kerala` | `Kerala` | `chola kingdom` |
| hotpotqa_6754 | external_hotpotqa | 0.000284117 | `1942` | `1942` | `1927` |
