# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.550 | 0.220 | 0.325 | 42 | 0.416 |
| full_prefill | 1.000 | 0.250 | 0.350 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.570 | 0.250 | 0.342 | 40 | 0.416 |
| prefix_conditioned_naive_global | 0.520 | 0.230 | 0.306 | 44 | 0.000 |
| query_similarity_doc_patch_k2 | 0.580 | 0.230 | 0.333 | 39 | 0.447 |
| random_doc_patch_k2_seeded | 0.600 | 0.280 | 0.383 | 34 | 0.387 |
| safe_gate_t0.60 | 0.560 | 0.220 | 0.324 | 42 | 0.424 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::external_2wiki | 0.460 | 0.160 | 24 |
| entity_overlap_doc_patch_k2::external_hotpotqa | 0.640 | 0.280 | 18 |
| full_prefill::external_2wiki | 1.000 | 0.180 | 0 |
| full_prefill::external_hotpotqa | 1.000 | 0.320 | 0 |
| oracle_evidence_doc_patch::external_2wiki | 0.500 | 0.180 | 23 |
| oracle_evidence_doc_patch::external_hotpotqa | 0.640 | 0.320 | 17 |
| prefix_conditioned_naive_global::external_2wiki | 0.440 | 0.180 | 25 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.600 | 0.280 | 19 |
| query_similarity_doc_patch_k2::external_2wiki | 0.500 | 0.160 | 23 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.660 | 0.300 | 16 |
| random_doc_patch_k2_seeded::external_2wiki | 0.540 | 0.220 | 20 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.660 | 0.340 | 14 |
| safe_gate_t0.60::external_2wiki | 0.500 | 0.140 | 24 |
| safe_gate_t0.60::external_hotpotqa | 0.620 | 0.300 | 18 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_d60529440baf11ebab90acde48001122 | external_2wiki | 1.37761 | `Nawrahta of Kanni's uncle is Thihathu.` | `Jon Flanagan` | `Yazathingyan` |
| 2wiki_350ec8b80bde11eba7f7acde48001122 | external_2wiki | 1.36356 | `Liverpool` | `Atlantic City, New Jersey` | `Atlantic City, New Jersey` |
| hotpotqa_4529 | external_hotpotqa | 1.04329 | `Filmmaker` | `English director` | `filmmaker.` |
| 2wiki_62ce8c8e0bde11eba7f7acde48001122 | external_2wiki | 0.994784 | `Consort Liang's husband was born in 62-83.` | `Liu Shen-liang` | `Chinese` |
| 2wiki_9b8278a20bdd11eba7f7acde48001122 | external_2wiki | 0.854444 | `Fredrikstad` | `Hastings, Minnesota` | `Hastings, Minnesota` |
| hotpotqa_2244 | external_hotpotqa | 0.824855 | `The Centers for Medicare & Medicaid Services (CMS) works with AHCCCS` | `The Health Insurance Portability and Accountability Act (HIPAA)` | `Centers for Medicare and Medicaid Services` |
| 2wiki_322178260bde11eba7f7acde48001122 | external_2wiki | 0.76499 | `John I, Burgrave of Nuremberg's father died in 129` | `Frederick I of Nuremberg` | `Cadolzburg` |
| hotpotqa_4537 | external_hotpotqa | 0.730592 | `Hakim Jamal` | `Maulana Karenga` | `Hakim Abdullah Jamal` |
| hotpotqa_3622 | external_hotpotqa | 0.685457 | `The artist behind "Shit" was born and raised in Atlanta, Georgia.` | `Boise, Idaho` | `Atlanta, Georgia` |
| 2wiki_be851b660bdd11eba7f7acde48001122 | external_2wiki | 0.682792 | `Percy Faraday Frankland CBE FRS` | `University College, Dundee` | `Birmingham University` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_350ec8b80bde11eba7f7acde48001122 | external_2wiki | 0.584242 | `Liverpool` | `Liverpool` | `Atlantic City, New Jersey` |
| hotpotqa_4537 | external_hotpotqa | 0.494368 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 0.314884 | `1666` | `1666` | `March 19, 1666` |
| 2wiki_dc3a36a00bdd11eba7f7acde48001122 | external_2wiki | 0.0999138 | `France` | `France` | `Sweden` |
| 2wiki_6d1fa90e086711ebbd5eac1f6bf848b6 | external_2wiki | 0.0310522 | `Lyubomira Kazanova was born first.` | `Lyubomira Kazanova was born first.` | `Nadia Min Dern Heng` |
| hotpotqa_3647 | external_hotpotqa | 0.0444833 | `Greenwood, Tulsa` | `Greenwood, Tulsa` | `Greenwood neighborhood in their hometown of Tulsa, Oklahoma` |
| hotpotqa_0374 | external_hotpotqa | 0.0183841 | `2017` | `2017` | `2017` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_4537 | external_hotpotqa | 0.494368 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| 2wiki_fac0692508c111ebbd8bac1f6bf848b6 | external_2wiki | 0.642868 | `Varuthapadatha Valibar Sangam` | `Varuthapadatha Valibar Sangam` | `Varuthapadatha Valibar Sangam` |
| hotpotqa_0441 | external_hotpotqa | 0.217564 | `The Bears and I` | `The Bears and I` | `The Bears and I` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_350ec8b80bde11eba7f7acde48001122 | external_2wiki | 0.584242 | `Liverpool` | `Liverpool` | `Atlantic City, New Jersey` |
| hotpotqa_4537 | external_hotpotqa | 0.148211 | `Hakim Jamal` | `Hakim Jamal` | `Hakim Abdullah Jamal` |
| 2wiki_fac0692508c111ebbd8bac1f6bf848b6 | external_2wiki | 0.283009 | `Varuthapadatha Valibar Sangam` | `Varuthapadatha Valibar Sangam` | `Varuthapadatha Valibar Sangam` |
| 2wiki_003285a80bde11eba7f7acde48001122 | external_2wiki | 0.169385 | `Kerala` | `Kerala` | `chola kingdom` |
| hotpotqa_0878 | external_hotpotqa | 0.382065 | `Shakespeareana` | `Shakespeareana` | `Shakespeare performances` |
| hotpotqa_3263 | external_hotpotqa | 0.0174849 | `Championship` | `Championship` | `second` |
| hotpotqa_4018 | external_hotpotqa | 0.0347701 | `Northern Kentucky University` | `Northern Kentucky University` | `Highland Heights` |
| 2wiki_0254eea408b911ebbd88ac1f6bf848b6 | external_2wiki | 0.109856 | `Arthur 2: On the Rocks` | `Arthur 2: On the Rocks` | `Arthur 2: On The Rocks` |
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 0.0565655 | `Princess Leopodine of Löwenstein-Wertheim-R` | `Princess Leopodine of Löwenstein-Wertheim-R` | `Charles I of Austria` |
