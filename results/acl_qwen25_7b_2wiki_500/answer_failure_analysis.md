# Answer Failure Analysis

Rows compare deterministic generated answers against full-prefill generation.

## Method Summary

| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |
|---|---:|---:|---:|---:|---:|
| entity_overlap_doc_patch_k2 | 0.504 | 0.364 | 0.442 | 216 | 0.449 |
| full_prefill | 1.000 | 0.452 | 0.546 | 0 | 0.000 |
| oracle_evidence_doc_patch | 0.546 | 0.414 | 0.490 | 194 | 0.536 |
| prefix_conditioned_naive_global | 0.378 | 0.312 | 0.386 | 272 | 0.000 |
| query_similarity_doc_patch_k2 | 0.494 | 0.356 | 0.437 | 222 | 0.462 |
| random_doc_patch_k2_seeded | 0.492 | 0.352 | 0.436 | 220 | 0.355 |
| risk_guided_doc_patch_k2 | 0.530 | 0.400 | 0.477 | 200 | 0.484 |
| safe_gate_t0.45 | 0.526 | 0.400 | 0.477 | 202 | 0.468 |
| safe_gate_t0.60 | 0.526 | 0.400 | 0.477 | 202 | 0.466 |

## Category Breakdown

| method::category | answer equiv | gold EM | changed+wrong |
|---|---:|---:|---:|
| entity_overlap_doc_patch_k2::external_2wiki | 0.504 | 0.364 | 216 |
| full_prefill::external_2wiki | 1.000 | 0.452 | 0 |
| oracle_evidence_doc_patch::external_2wiki | 0.546 | 0.414 | 194 |
| prefix_conditioned_naive_global::external_2wiki | 0.378 | 0.312 | 272 |
| query_similarity_doc_patch_k2::external_2wiki | 0.494 | 0.356 | 222 |
| random_doc_patch_k2_seeded::external_2wiki | 0.492 | 0.352 | 220 |
| risk_guided_doc_patch_k2::external_2wiki | 0.530 | 0.400 | 200 |
| safe_gate_t0.45::external_2wiki | 0.526 | 0.400 | 202 |
| safe_gate_t0.60::external_2wiki | 0.526 | 0.400 | 202 |

## Top 10 Base Answer Changes

| example | category | KL | full answer | base answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e5d416220bdd11eba7f7acde48001122 | external_2wiki | 25.4328 | `5 October 1852` | `Information not provided in the given document.` | `5 October 1852` |
| 2wiki_281793980bdd11eba7f7acde48001122 | external_2wiki | 23.8154 | `in battle with the pro-Persian Georgian ruler Rostom of Kartli` | `Information not provided in the given document.` | `Astarabad` |
| 2wiki_0fc59fa00bde11eba7f7acde48001122 | external_2wiki | 23.6764 | `8 June 1746` | `Information not provided in the given document.` | `8 June 1746` |
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 23.6307 | `ca. March 19, 1666` | `1666` | `March 19, 1666` |
| 2wiki_35e09904086b11ebbd5fac1f6bf848b6 | external_2wiki | 23.4202 | `Axel von Ambesser` | `Sengottai Singam` | `I Learned It From Father` |
| 2wiki_424d56700bde11eba7f7acde48001122 | external_2wiki | 23.0127 | `Ostrogoths` | `English` | `Ostrogothic Kingdom` |
| 2wiki_c99fc05e0bd911eba7f7acde48001122 | external_2wiki | 22.2847 | `15 March 1981` | `Unknown` | `15 March 1981` |
| 2wiki_f9ac302a0bd911eba7f7acde48001122 | external_2wiki | 21.4467 | `Kiev` | `The document does not provide information about the birthplace of Vladimir Feldman's wife` | `Kiev` |
| 2wiki_5ff291a80bda11eba7f7acde48001122 | external_2wiki | 20.5672 | `The documents do not provide Chuck Berry's birthplace, only his birth year and` | `St. Louis, Missouri` | `St. Louis, Missouri` |
| 2wiki_accfdb580bd911eba7f7acde48001122 | external_2wiki | 20.3043 | `1964` | `Date of death unknown` | `10 October 1964` |

## Repaired By Safe Gates

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_e5d416220bdd11eba7f7acde48001122 | external_2wiki | 1.26207e-07 | `5 October 1852` | `5 October 1852` | `5 October 1852` |
| 2wiki_281793980bdd11eba7f7acde48001122 | external_2wiki | 0.312414 | `in battle with the pro-Persian Georgian ruler Rostom of Kartli` | `in battle with the pro-Persian Georgian ruler Rostom of Kartli` | `Astarabad` |
| 2wiki_0fc59fa00bde11eba7f7acde48001122 | external_2wiki | 0 | `8 June 1746` | `8 June 1746` | `8 June 1746` |
| 2wiki_400bf8800bde11eba7f7acde48001122 | external_2wiki | 0.906563 | `ca. March 19, 1666` | `ca. March 19, 1666` | `March 19, 1666` |
| 2wiki_2b9500fe0bde11eba7f7acde48001122 | external_2wiki | 0 | `22 June 1893` | `22 June 1893` | `22 June 1893` |
| 2wiki_5cad7ed608a111ebbd79ac1f6bf848b6 | external_2wiki | 0.618393 | `Terror-Creatures from the Grave` | `Terror-Creatures From The Grave` | `Terror-Creatures From The Grave` |
| 2wiki_6f0a6a5e0bde11eba7f7acde48001122 | external_2wiki | 0.227687 | `Auckland` | `Auckland` | `Flanders` |
| 2wiki_b1bb441b08e411ebbda4ac1f6bf848b6 | external_2wiki | 1.32222e-05 | `The Tuttles of Tahiti` | `The Tuttles Of Tahiti` | `The Tuttles Of Tahiti` |
| 2wiki_abf4c578090811ebbdadac1f6bf848b6 | external_2wiki | 0.0467177 | `The Supporter` | `The Supporter` | `Vetri Vizha` |
| 2wiki_eb18f7ac0baf11ebab90acde48001122 | external_2wiki | 0.00724023 | `Alfonso II of Aragon` | `Alfonso II of Aragon` | `Ramon Berenguer IV` |

## Repaired By Oracle But Not Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_85f17aea08c911ebbd92ac1f6bf848b6 | external_2wiki | 0.0213542 | `Georges Lampin` | `Georges Lampin` | `La Tour, Prends Garde !` |
| 2wiki_e95acdbc085f11ebbd5dac1f6bf848b6 | external_2wiki | 0.282194 | `Deuce High` | `Deuce High` | `The King Is The Best Mayor` |
| 2wiki_998af60a088b11ebbd6fac1f6bf848b6 | external_2wiki | 2.06637 | `The Crime Doctor's Courage` | `Crime Doctor's Courage` | `The Crime Doctor'S Courage` |
| 2wiki_566c1e2c08a811ebbd7fac1f6bf848b6 | external_2wiki | 0.19934 | `Riders of the Santa Fe` | `Riders of the Santa Fe` | `Riders Of The Santa Fe` |
| 2wiki_7257a60608cb11ebbd92ac1f6bf848b6 | external_2wiki | 0.103158 | `Yeh Dil` | `Yeh Dil` | `Yeh Dil` |
| 2wiki_9fc45d75089811ebbd77ac1f6bf848b6 | external_2wiki | 0.00828026 | `Sir Walter Boyd, 1st Baronet` | `Sir Walter Boyd, 1st Baronet` | `Sir Walter Boyd, 1St Baronet` |
| 2wiki_ea755618087311ebbd67ac1f6bf848b6 | external_2wiki | 0.251432 | `Amici miei – Atto III` | `Amici Miei – Atto III` | `Amici Miei – Atto Iii` |
| 2wiki_4d982dc308c111ebbd8bac1f6bf848b6 | external_2wiki | 0.225376 | `Condemned Women` | `Condemned Women` | `Condemned Women` |
| 2wiki_49baa9120bde11eba7f7acde48001122 | external_2wiki | 0.00839689 | `Valencia, Carabobo` | `Valencia, Carabobo` | `Valencia` |
| 2wiki_1cf4dbe80baf11ebab90acde48001122 | external_2wiki | 0.0502951 | `King Stanisław Leszczyński` | `King Stanisław Leszczyński` | `Stanisław Leszczyński` |

## Random K2 Beats Semantic K2

| example | category | KL | full answer | method answer | gold |
|---|---|---:|---|---|---|
| 2wiki_424d56700bde11eba7f7acde48001122 | external_2wiki | 0.0207929 | `Ostrogoths` | `Ostrogoths` | `Ostrogothic Kingdom` |
| 2wiki_fab2aa100bdb11eba7f7acde48001122 | external_2wiki | 8.331e-07 | `1 June 1220` | `1 June 1220` | `1 June 1220` |
| 2wiki_76b617e40bde11eba7f7acde48001122 | external_2wiki | 1.58937 | `Portuguese` | `Portuguese` | `Kingdom of Portugal` |
| 2wiki_4c1772720bb011ebab90acde48001122 | external_2wiki | 0.0487198 | `Archduke Maximilian Eugen of Austria` | `Archduke Maximilian Eugen of Austria` | `Charles I of Austria` |
| 2wiki_9724141c0bda11eba7f7acde48001122 | external_2wiki | 0.136461 | `Le Fleix in Dordogne` | `Le Fleix in Dordogne` | `Le Fleix` |
| 2wiki_c370b4540bd911eba7f7acde48001122 | external_2wiki | 9.49296e-06 | `Rasual Butler` | `Rasual Butler` | `Rasual Butler` |
| 2wiki_7f8db33a0bda11eba7f7acde48001122 | external_2wiki | 0.581411 | `Basu Bhattacharya` | `Basu Bhattacharya` | `Rinki Bhattacharya` |
| 2wiki_b583abd20baf11ebab90acde48001122 | external_2wiki | 1.2689 | `Rukn al-Dawla` | `Rukn al-Dawla` | `'Adud al-Dawla` |
| 2wiki_5ead23420baf11ebab90acde48001122 | external_2wiki | 0.0216241 | `Lord William Powlett` | `Lord William Powlett` | `Charles Paulet, 1st Duke of Bolton` |
| 2wiki_75612cee0bde11eba7f7acde48001122 | external_2wiki | 1.11852 | `The documents do not provide Muhammad I of Khwarazm's father's nationality` | `The documents do not provide Muhammad I of Khwarazm's father's nationality` | `Turkic` |
