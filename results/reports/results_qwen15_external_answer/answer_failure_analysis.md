# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.620 | 0.340 | 0.425 | 33 | 0.415 |
| full_prefill | 1.000 | 0.410 | 0.499 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.640 | 0.350 | 0.449 | 31 | 0.416 |
| prefix_conditioned_naive_global | 0.440 | 0.270 | 0.362 | 48 | 0.000 |
| query_similarity_doc_patch_k2 | 0.620 | 0.340 | 0.423 | 32 | 0.447 |
| random_doc_patch_k2_seeded | 0.640 | 0.360 | 0.462 | 31 | 0.387 |
| safe_gate_t0.60 | 0.630 | 0.340 | 0.437 | 32 | 0.425 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::external_2wiki | 0.620 | 0.280 | 15 |
| entity_overlap_doc_patch_k2::external_hotpotqa | 0.620 | 0.400 | 18 |
| full_prefill::external_2wiki | 1.000 | 0.300 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.520 | 0 |
| oracle_evidence_doc_patch::external_2wiki | 0.640 | 0.300 | 14 |
| oracle_evidence_doc_patch::external_hotpotqa | 0.640 | 0.400 | 17 |
| prefix_conditioned_naive_global::external_2wiki | 0.480 | 0.200 | 22 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.400 | 0.340 | 26 |
| query_similarity_doc_patch_k2::external_2wiki | 0.580 | 0.240 | 17 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.660 | 0.440 | 15 |
| random_doc_patch_k2_seeded::external_2wiki | 0.640 | 0.320 | 14 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.640 | 0.400 | 17 |
| safe_gate_t0.60::external_2wiki | 0.620 | 0.280 | 15 |
| safe_gate_t0.60::external_hotpotqa | 0.640 | 0.400 | 17 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_0544 | external_hotpotqa | 12.2456 | `Phyllocnistis liquidambarisella` | `Liquidambar styraciflua` | `moth` |
| hotpotqa_7385 | external_hotpotqa | 10.1573 | `Christine MacIntyre` | `Joe Weider` | `Christine MacIntyre` |
| 2wiki_782f0c160bd911eba7f7acde48001122 | external_2wiki | 5.7468 | `Kodambakkam` | `October 22, 1970` | `Trivandrum` |
| hotpotqa_6827 | external_hotpotqa | 5.16592 | `Poughkeepsie–Newburgh–Middletown, NY Metropolitan` | `Rochester` | `Buffalo` |
| hotpotqa_7267 | external_hotpotqa | 5.15354 | `Kentucky Wildcats` | `Duke` | `The 1997–98 Kentucky Wildcats men's basketball team` |
| hotpotqa_4222 | external_hotpotqa | 5.04414 | `New York City` | `Fordham University` | `New York City` |
| 2wiki_21e70b7e0bde11eba7f7acde48001122 | external_2wiki | 4.9493 | `Russia` | `Prussia` | `Prussia` |
| 2wiki_34c3dd940bde11eba7f7acde48001122 | external_2wiki | 4.66675 | `Beaulieu-sur-Loire` | `Allada` | `Allada` |
| 2wiki_adf59bec0bdb11eba7f7acde48001122 | external_2wiki | 4.5356 | `Ian Hendry` | `Peter Michael Hamel` | `Leopoldo Torres Ríos` |
| hotpotqa_4537 | external_hotpotqa | 4.5186 | `Hakim Jamal` | `Malcolm X` | `Hakim Abdullah Jamal` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_7385 | external_hotpotqa | 0.00643037 | `Christine MacIntyre` | `Christine MacIntyre` | `Christine MacIntyre` |
| hotpotqa_4537 | external_hotpotqa | 0.0323716 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| hotpotqa_5645 | external_hotpotqa | 0.644215 | `Saturday Night Live` | `Saturday Night Live` | `"Saturday Night Live"` |
| 2wiki_dc3a36a00bdd11eba7f7acde48001122 | external_2wiki | 0.250143 | `France` | `France` | `Sweden` |
| hotpotqa_5226 | external_hotpotqa | 0.466907 | `Julian Assange` | `Julian Assange` | `Angelina Jolie` |
| hotpotqa_3263 | external_hotpotqa | 0.10424 | `Championship` | `Championship` | `second` |
| 2wiki_21832f3c0bde11eba7f7acde48001122 | external_2wiki | 1.4339 | `Italy` | `Italy` | `Italy` |
| hotpotqa_1564 | external_hotpotqa | 0.500667 | `American` | `American` | `a British composer` |
| hotpotqa_1483 | external_hotpotqa | 0.0746228 | `Jake Kasdan` | `Jake Kasdan` | `Brothers Quay` |
| 2wiki_27d8ec30091f11ebbdaeac1f6bf848b6 | external_2wiki | 0.487574 | `Guilty` | `Guilty` | `Guilty?` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_4537 | external_hotpotqa | 0.0323716 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| 2wiki_249f9f060bda11eba7f7acde48001122 | external_2wiki | 0.309904 | `Polish` | `Polish` | `Polish` |
| hotpotqa_0441 | external_hotpotqa | 0.0156915 | `The Bears and I` | `The Bears and I` | `The Bears and I` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_4537 | external_hotpotqa | 0.00403001 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| 2wiki_249f9f060bda11eba7f7acde48001122 | external_2wiki | 0.222462 | `Polish` | `Polish` | `Polish` |
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 0.271708 | `Archduke Maximilian Eugen of Austria` | `Archduke Maximilian Eugen of Austria` | `Charles I of Austria` |
| hotpotqa_4018 | external_hotpotqa | 0.0828372 | `Highland Heights` | `Highland Heights` | `Highland Heights` |
| 2wiki_c99c181e08b911ebbd88ac1f6bf848b6 | external_2wiki | 0.179703 | `Simon, the Magician` | `Simon, The Magician` | `Simon, The Magician` |
| hotpotqa_4389 | external_hotpotqa | 0.0233605 | `Northeast Regional` | `Northeast Regional` | `Acela Express` |
