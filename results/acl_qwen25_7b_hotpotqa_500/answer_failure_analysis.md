# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.628 | 0.436 | 0.560 | 170 | 0.351 |
| full_prefill | 1.000 | 0.544 | 0.708 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.614 | 0.456 | 0.573 | 171 | 0.315 |
| prefix_conditioned_naive_global | 0.472 | 0.354 | 0.489 | 241 | 0.000 |
| query_similarity_doc_patch_k2 | 0.644 | 0.440 | 0.580 | 162 | 0.393 |
| random_doc_patch_k2_seeded | 0.640 | 0.454 | 0.592 | 159 | 0.384 |
| risk_guided_doc_patch_k2 | 0.626 | 0.452 | 0.573 | 167 | 0.343 |
| safe_gate_t0.45 | 0.624 | 0.450 | 0.571 | 168 | 0.339 |
| safe_gate_t0.60 | 0.618 | 0.448 | 0.566 | 171 | 0.331 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::external_hotpotqa | 0.628 | 0.436 | 170 |
| full_prefill::external_hotpotqa | 1.000 | 0.544 | 0 |
| oracle_evidence_doc_patch::external_hotpotqa | 0.614 | 0.456 | 171 |
| prefix_conditioned_naive_global::external_hotpotqa | 0.472 | 0.354 | 241 |
| query_similarity_doc_patch_k2::external_hotpotqa | 0.644 | 0.440 | 162 |
| random_doc_patch_k2_seeded::external_hotpotqa | 0.640 | 0.454 | 159 |
| risk_guided_doc_patch_k2::external_hotpotqa | 0.626 | 0.452 | 167 |
| safe_gate_t0.45::external_hotpotqa | 0.624 | 0.450 | 168 |
| safe_gate_t0.60::external_hotpotqa | 0.618 | 0.448 | 171 |

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
| hotpotqa_0832 | external_hotpotqa | 0.917052 | `racehorse breeder and owner` | `racehorse breeder and owner` | `racehorse breeder and owner` |
| hotpotqa_6533 | external_hotpotqa | 0.0373745 | `Northwest Mall` | `Northwest Mall` | `Northwest Mall` |
| hotpotqa_6622 | external_hotpotqa | 5.83448e-05 | `Zola` | `Zola` | `Blue Dragon` |
| hotpotqa_6895 | external_hotpotqa | 0.00513518 | `International Hotel` | `International Hotel` | `the Las Vegas Hilton` |
| hotpotqa_3315 | external_hotpotqa | 0.0403696 | `"Dr. Death" Steve Williams` | `"Dr. Death" Steve Williams` | `"Dr. Death" Steve Williams` |
| hotpotqa_6694 | external_hotpotqa | 0.091774 | `Rafael Márquez` | `Rafael Márquez` | `Rafael Márquez` |
| hotpotqa_1991 | external_hotpotqa | 0.00457916 | `24` | `24` | `24` |
| hotpotqa_1146 | external_hotpotqa | 2.15953 | `Hoffman Estates, Illinois, United States` | `Hoffman Estates, Illinois, United States` | `Hoffman Estates, Illinois` |
| hotpotqa_6269 | external_hotpotqa | 0.450632 | `Shameless` | `Shameless` | `Shameless` |
| hotpotqa_1904 | external_hotpotqa | 0.126814 | `January 16, 2013` | `January 16, 2013` | `January 16, 2013` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_6185 | external_hotpotqa | 0.0292139 | `Croatian` | `Croatian` | `Croatian` |
| hotpotqa_0257 | external_hotpotqa | 0.012149 | `Mountbatten family` | `Mountbatten family` | `Mountbatten family` |
| hotpotqa_6228 | external_hotpotqa | 0.110887 | `Colin Bryce` | `Colin Bryce` | `bobsledder` |
| hotpotqa_1935 | external_hotpotqa | 0.00147225 | `Hanford Nuclear Reservation` | `Hanford Nuclear Reservation` | `Hanford Site` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| hotpotqa_1210 | external_hotpotqa | 0.116491 | `Nicole Kidman` | `Nicole Kidman` | `Nicole Kidman` |
| hotpotqa_6297 | external_hotpotqa | 2.69147 | `Colorado River` | `The Colorado River` | `1450 mi` |
| hotpotqa_7094 | external_hotpotqa | 5.00498e-07 | `Wes Unseld` | `Wes Unseld` | `Westley Sissel Unseld` |
| hotpotqa_1312 | external_hotpotqa | 4.0838e-05 | `Matthew Vaughn` | `Matthew Vaughn` | `Matthew Vaughn` |
| hotpotqa_6453 | external_hotpotqa | 0.127717 | `Take That` | `Take That` | `Take That` |
| hotpotqa_0257 | external_hotpotqa | 0.0021824 | `Mountbatten family` | `Mountbatten family` | `Mountbatten family` |
| hotpotqa_5237 | external_hotpotqa | 0.298047 | `Boston University` | `Boston University` | `Harvard University` |
| hotpotqa_3024 | external_hotpotqa | 0.00567051 | `Phillips v. Martin Marietta Corp.` | `Phillips v. Martin Marietta Corp.` | `Roth v. United States` |
| hotpotqa_1916 | external_hotpotqa | 0.00828325 | `Kim Bauer` | `Kim Bauer` | `Kim Bauer` |
| hotpotqa_5464 | external_hotpotqa | 0.0153133 | `Sam Boyd Stadium` | `Sam Boyd Stadium` | `Sam Boyd Stadium` |
