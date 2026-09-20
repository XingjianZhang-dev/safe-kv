# SAFE-KV: Causal Suffix Repair for Behavior-Preserving Non-Prefix KV Cache Reuse in RAG

**Findings of AACL-IJCNLP 2026.** Xingjian Zhang, Carnegie Mellon University (xingjiaz@andrew.cmu.edu).

Retrieval-augmented generation reuses the same documents across requests, which makes non-prefix KV-cache reuse
attractive; but a cached document state depends on the prefix, position, and preceding documents it was computed under.
This repository is the artifact behind the paper: it studies non-prefix KV reuse as a behavior-preservation problem,
with full prefill on the exact prompt as the reference and normalized short-answer equivalence to it as the primary
metric. It contains the `safekv` package, every config, the processed datasets, every result directory the paper cites
(with per-example outputs, manifests and validator reports), and the scripts that regenerate every generated table and
every figure of the camera-ready from those raw result files. It is written for a reader who has the paper open and
wants to check a number.

## Read this first: two protocols, two orderings

Every table in the paper states which of these it uses; they are the easiest thing to get wrong.

| | What it means | Where it appears |
|---|---|---|
| **Donor-copy protocol** | The submitted evaluator: KV slices of the selected suffix are *copied* from a full-prefill cache into the composed cache. Measures the repair *unit*; not a deployable path. | Tables 1, 3, 5, 25, 26 and the appendix tables that cite `results/` (submitted runs) |
| **Actual forwarding** | The deployable path: the selected suffix is *re-run through the model* from the retained composed prefix (`actual_recompute::*` methods of `code/scripts/run_answer_eval.py`). | Tables 2, 6, 7, 13, 14, 18–20, 33 (`results_rebuttal/`); token-local variant in Tables 4 and 22 (`results_august/`) |
| **Gold-evidence-first construction** | The original HotpotQA-500 / 2Wiki-500 conversion: supporting paragraphs first, retrieval score 1.0 for them and at most 0.55 for distractors. The risk selector reads that score, so selector results on this construction are not evidence of selector generalization. | Tables 1, 2(a), 3, 14–16, 25, 26 |
| **Score-neutral shuffled order** | The same examples with every retrieval score set to 0 and documents shuffled with per-example seeds 101/202/303; the label-free evidence for the selectors. | Tables 2(b), 13, 19, 23; the shuffled/BM25 localized-baseline conversions in Tables 4 and 22 are also built without gold labels |

Synthetic diagnostics (position sweep, noise sweeps, the nested staleness benchmark) assign document ids before
shuffling and give evidence documents the smallest ids; the selectors break score ties by ascending id, so query-selector
rows on those files are effectively oracle-start results (paper Sections 4.2, 6.3 and Appendix N; `scripts/camera_ready/tie_break_audit.py`).

## Layout

```
code/                 safekv package, scripts and CPU tests, as they produced the submitted and response-period runs
configs/              YAML configs of every run (the `risk:` block is not consumed by the selector; see below)
data/                 processed JSONL datasets: HotpotQA-500, 2Wiki-500, synthetic diagnostics, noise/position sweeps, selector splits
results/              submitted runs (May 2026), unchanged
results_rebuttal/     response-period runs (July 2026): actual forwarding, score-neutral shuffled, staleness grid, L40S latency,
                      Noise64 quality gate, oracle diagnostic, CPU selector audit; results_rebuttal/README.md is the run-status ledger;
                      results_rebuttal/data/ holds the score-neutral / nested input variants
results_august/       query-attention localized-repair baseline (August 2026): three runs, their datasets, and the safekv_ipm code
paper_reference/      generated camera-ready tables, every figure PDF with its plotted-value CSV, review-time table sources and audits
scripts/              verifier, reproduction-command emitter, camera_ready/ (table/figure generators, tie-break audit), fetch_raw_outputs.sh
FULL_REPRODUCTION.md  environment, commands, and the paper-result map
ARTIFACT_MANIFEST.md  what each directory contains and what was deliberately left out
FILE_MANIFEST.tsv, SHA256SUMS, RESULT_FILE_LISTING.txt, TEST_LOG.txt   integrity files
LICENSE (MIT), NOTICE, requirements.txt (pinned)
```

Raw per-example dumps of four run families (232 MB) are kept out of git and shipped as a release asset; see
[Raw outputs in the release tarball](#raw-outputs-in-the-release-tarball). Every summary file the paper uses is in git.

## Install and run the CPU checks

Python 3.10 or newer (tested on 3.13). No GPU and no model download are needed for anything on this page except
re-running the model experiments themselves.

```bash
git clone https://github.com/XingjianZhang-dev/safe-kv.git && cd safe-kv
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip && python -m pip install -r requirements.txt

CUDA_VISIBLE_DEVICES='' PYTHONHASHSEED=0 PYTHONPATH=code python -B -m pytest -q -p no:cacheprovider code/tests
#   expected: 135 passed, 1 skipped (TEST_LOG.txt)
python scripts/verify_packaged_results.py            # expected files, data row counts, headline metrics: "Supplement verification passed"
shasum -a 256 -c SHA256SUMS | grep -v ': OK$' || echo "all checksums OK"
```

## Regenerate every table and figure

```bash
python -B scripts/camera_ready/build_tables.py       # 11 generated tables -> paper_reference/camera_ready_tables/*.tex
python -B scripts/camera_ready/tie_break_audit.py    # Table 24 (selector tie-break audit) -> paper_reference/camera_ready_tables/appendix_tie_break.tex
python -B scripts/camera_ready/make_figures.py       # Figures 1-5 -> paper_reference/final_figures/*.pdf (+ .data.csv for each data figure)
```

The tables and the figure CSVs are byte-identical to the shipped files in `paper_reference/camera_ready_tables/` and
`paper_reference/final_figures/`; the figure PDFs carry no timestamp and are byte-identical too when regenerated with the
pinned matplotlib and the same fonts (Arial/Helvetica, DejaVu Sans fallback), so `git status` stays clean after running
them. Tables that were reproduced unchanged from the submission are not regenerated by a script; the map below names the
result file each one is read from, and `scripts/rebuild_headline_tables.py` rebuilds the headline external/Mistral/latency
audit tables from the same summaries.

## Where every number comes from

Table and figure numbers are those of the camera-ready PDF. "Generated" rows are written by the commands above from the
listed files; "read from" rows are the submission's tables whose cells are the listed summaries.

| Paper item | Protocol / ordering | Command or source |
|---|---|---|
| **Table 1** main 7B external results | donor copy; gold-first | read from `results/acl_qwen25_7b_{hotpotqa,2wiki}_suffix_main_500/answer_eval_summary.json` (`scripts/rebuild_headline_tables.py`) |
| **Table 2(a)** actual forwarding, original inputs | actual forwarding; gold-first | `build_tables.py` from `results_rebuttal/actual_recompute_{hotpot,2wiki}_500/answer_eval_summary.json` and `results_rebuttal/actual_vs_copy_{hotpot,2wiki}_500_l40s_v2/donor_actual_reconciliation.json` (token exactness) |
| **Table 2(b)** score-neutral shuffled | actual forwarding; shuffled 101/202/303 | `build_tables.py` from `results_rebuttal/neutral_selector_actual_3seed_validation/neutral_selector_across_seed.csv` (per-run dirs `results_rebuttal/neutral_selector_actual_{hotpot,2wiki}_shuffle{101,202,303}_100/`) |
| **Table 3** local vs suffix repair, 2Wiki-100 | donor copy; gold-first | read from `results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json` |
| **Table 4** operational token-local baseline | token-local actual recompute; natural / shuffled / BM25 (no gold labels) | `build_tables.py` from `results_august/run_registry/qwen25_query_attention_hotpotqa_{natural,shuffle,bm25}_test_n100_v1/query_attention_local_summary.csv` |
| **Table 5** position sensitivity | donor copy; synthetic (Noise16, 19 documents) | read from `results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv` and `answer_eval_summary.json` |
| **Table 6** staleness x document count (compact) | actual forwarding; nested synthetic, scores zero, layout seed 101 | `build_tables.py` from `results_rebuttal/staleness_doccount_full_50_v3/staleness_doccount_summary.csv` |
| **Table 7** time to first logit, five L40S workloads | actual forwarding incl. selector planning; orderings as in the rows | `build_tables.py` from `results_rebuttal/latency_{hotpot_original,2wiki_original,2wiki_neutral_shuffle101,n16_neutral_layout101,noise64}_50_v1/latency_trace_summary.json` and `latency_paired_bootstrap_summary.csv`; Noise64 gate from `results_rebuttal/quality_noise64_actual_riskk1_50_v1/` |
| **Table 8** full early composition ablation (Qwen2.5-0.5B) | development; synthetic | read from `results/paper_tables/results_paper/table1_composition_ablation.csv` |
| **Table 9** full early repair-granularity diagnostic (Qwen2.5-0.5B) | development; synthetic | read from `results/paper_tables/results_paper/table2_repair_granularity.csv` |
| **Table 10** full synthetic answer-level table (small models) | development; synthetic | read from `results/paper_tables/results_paper/table3_answer_level_synthetic.csv` (`results/metrics/results_*_answer/`) |
| **Table 11** external and cross-model summary | donor copy; gold-first / Mistral noisy | read from the Table 1 summaries, `results/paper_tables/results_paper/table5_external_full_prefill_correct_subset.csv`, and `results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json` |
| **Table 12** full Qwen2.5-7B external answer-level results | donor copy; gold-first | read from `results/acl_qwen25_7b_{hotpotqa,2wiki}_suffix_main_500/answer_eval_summary.json` (all methods) |
| **Table 13** per-seed values behind Table 2(b) | actual forwarding; shuffled | `build_tables.py` from `results_rebuttal/neutral_selector_actual_3seed_validation/neutral_selector_by_seed.csv` |
| **Table 14** same-run donor-copy vs actual-forwarding reconciliation | both; gold-first | `build_tables.py` from `results_rebuttal/actual_vs_copy_{hotpot,2wiki}_500_l40s_v2/donor_actual_reconciliation.json` |
| **Table 15** robustness and calibration checks | donor copy; gold-first | read from `results/acl_qwen25_7b_{hotpotqa,2wiki}_suffix_main_500/bootstrap_ci/bootstrap_pairwise_delta_ci.csv`, the held-out summaries of Table 16, and the Table 17 latency summaries |
| **Table 16** held-out calibration | donor copy; gold-first | read from `results/acl_qwen25_7b_{hotpotqa,2wiki}_suffix_main_500/heldout_method_calibration_safekv_only/heldout_method_calibration_summary.csv` |
| **Table 17** submission-time prototype latency | donor copy, no selector planning | read from `results/acl_qwen25_7b_2wiki_latency_suffix_50_with_hybrid/latency_summary.json` and `results/acl_qwen25_7b_noise64_latency_suffix_20_with_hybrid/latency_summary.json` |
| **Table 18** all timed methods, five workloads | actual forwarding incl. planning | `build_tables.py` from the five `results_rebuttal/latency_*_50_v1/latency_trace_summary.json` and `latency_paired_bootstrap_summary.csv` |
| **Table 19** selector CPU cost | CPU, inside the timed path / separate audit | `build_tables.py` from `selector_latency.csv` in the five latency runs and `results_rebuttal/cpu_selector_audit_l40s_host/latency.csv` |
| **Table 20** Noise64 quality gate | both | `build_tables.py` from `results_rebuttal/quality_noise64_actual_riskk1_50_v1/answer_eval_summary.json`, `donor_actual_reconciliation.json`, `bootstrap/bootstrap_{method,pairwise_delta}_ci.csv` |
| **Table 21** noise-sweep and closure diagnostics | donor copy; synthetic | read from `results/acl_qwen25_7b_noise_sweep_{0,8,16}_250/`, `results/acl_qwen25_7b_noise16_{k_sweep,closure}_250/answer_eval_summary.json` |
| **Table 22** token-local baseline, full budget curves | token-local actual recompute; natural / shuffled / BM25 | `build_tables.py` from the three `query_attention_local_summary.csv` of Table 4 |
| **Table 23** oracle KV-drift token-local diagnostic | oracle donor copy; shuffled 101 | `build_tables.py` from `results_rebuttal/oracle_kv_drift_2wiki_neutral_shuffle101_100_v3/oracle_kv_drift_summary.json` and `oracle_paired_bootstrap_summary.json` |
| **Table 24** tie-break audit | CPU selectors on the shipped inputs | `tie_break_audit.py` on `data/`, `results_rebuttal/data/` with `code/safekv/doc_selector.py` |
| **Table 25** selector and budget operating points | donor copy; gold-first / Mistral noisy | read from `results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json` and `results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json` |
| **Table 26** selector evidence-recall diagnostics | selector only; gold-first | read from `results/selector_artifacts/selector_quality_{hotpotqa,2wiki}_500.csv` |
| **Table 27** design ledger | donor copy; mixed | narrative of the runs above (`results/acl_qwen25_7b_noise16_*`, `results/acl_qwen25_7b_2wiki_adaptive_interval_200`, learned selector in `results/selector_artifacts/`) |
| **Table 28** result inventory | — | `RESULT_FILE_LISTING.txt` (counts in the header) |
| **Tables 29–31** compact development tables (Qwen2.5-0.5B/1.5B) | development; synthetic | read from the Table 8–10 CSVs and `results/metrics/results_{qwen05,qwen15}_100{,_noisy}_answer/` |
| **Table 32** related-work positioning | — | no data |
| **Table 33** full staleness grid (26,250 rows) | actual forwarding; nested synthetic | `build_tables.py` from `results_rebuttal/staleness_doccount_full_50_v3/staleness_doccount_summary.csv` (clustered intervals; `validation_report.json` = PASS) |
| **Figure 1** setup schematic | — | `make_figures.py` (conceptual; no data) |
| **Figure 2** local vs suffix repair curve (Section 6.2) | donor copy; gold-first | `make_figures.py` from `results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json` → `paper_reference/final_figures/figure_local_vs_suffix.data.csv` |
| **Figure 3** robustness checks (Appendix H) | donor copy | `make_figures.py` from `results/acl_qwen25_7b_{hotpotqa,2wiki}_suffix_main_500/answer_eval_metrics.csv` (full-prefill-correct subsets, recomputed per example) and the Mistral summary → `figure5_external_sanity.data.csv` |
| **Figure 4** quality–budget points and L40S latency (Appendix K) | donor copy (left) / actual forwarding (right) | `make_figures.py` from the Table 1 2Wiki summary and the five `latency_trace_summary.json` → `figure4_budget_gate_pareto.data.csv` |
| **Figure 5** position sweep (Appendix M) | donor copy; synthetic | `make_figures.py` from `results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv` → `figure_position_sweep.data.csv` |

Every processed input the runs used is in `data/` (submitted), `results_rebuttal/data/` (score-neutral and nested
variants, rebuilt byte-for-byte by `code/scripts/build_rebuttal_variants.py`), and `results_august/datasets/`
(localized-baseline conversions with their build manifest). `FULL_REPRODUCTION.md` gives the exact GPU command for every
run family; each shipped run also records its own invocation in its manifest.

## Raw outputs in the release tarball

To keep the repository around 190 MB with no file above 25 MB, the raw per-example dumps of four run families
(232 MB) are not in git. They are the release asset `safe-kv-raw-outputs-v1.0.0.tar.gz` of release tag `v1.0.0`:

| File(s) | Size | What it is | Summary kept in git |
|---|---|---|---|
| `results_rebuttal/staleness_doccount_full_50_v3/staleness_doccount_outputs.jsonl` | 35 MB | 26,250 per-example rows of the staleness grid | `staleness_doccount_summary.{csv,json}`, `staleness_paired_bootstrap_summary.{csv,json}`, `validation_report.json` |
| `results_august/run_registry/*/query_attention_local_outputs.jsonl` (3 runs) | 59 MB | per-example outputs of the token-local baseline | `query_attention_local_summary.{csv,json}`, `run_manifest.json`, logs |
| `results/paper_tables/results_paper/heldout_gate_calibration_outputs.jsonl` | 98 MB | per-example rows of the small-model budget-gate calibration | `heldout_gate_calibration_{summary.json,metrics.csv,report.md}` |
| `results/metrics/results_budget_gate/*/budget_gate_metrics.csv` (6 files) | 40 MB | per-example metrics of the small-model budget-gate development runs | `results/summaries/results_budget_gate/*/` and `budget_gate_pareto.csv` next to each |

`bash scripts/fetch_raw_outputs.sh` downloads the asset, verifies its SHA-256 and every extracted file, and restores the
files in place; each affected directory carries a `RAW_OUTPUTS_IN_RELEASE.txt` with the names, sizes and hashes. None
of the paper's tables or figures need these files.

## Known configuration caveat

The `risk:` block in `configs/*.yaml` (`similarity_backend: tfidf` and six weights) is not read by the selector.
`code/safekv/doc_selector.py::risk_guided_doc_scores` hard-codes the executed formula
`0.25*retrieval + 0.30*query + 0.20*entity + 0.15*conflict + 0.10*shared_entity` with lexical (not TF-IDF) query
recall; `query_similarity_doc_scores` is plain question-term recall. Every reported run used the hard-coded formula;
ties are broken by ascending document id (paper Appendix N).

The configs and manifests under `results_august/code/configs/` and in the run manifests record the paths of the
original GPU hosts (`/workspace/...`, `/root/autodl-tmp/...`); replace them with your own model and data locations
when re-running (`FULL_REPRODUCTION.md`, Sections 6–7).

## Licensing

The code, configs, and derived result files are released under the MIT License (`LICENSE`). Model weights are not
redistributed; the public benchmark data are not redistributed beyond the processed examples used in the experiments,
which stay under the original datasets' terms (HotpotQA: CC BY-SA 4.0); third-party dependencies are under their own
licenses. See `NOTICE`.

## Citation

```bibtex
@inproceedings{zhang2026safekv,
  title     = {{SAFE-KV}: Causal Suffix Repair for Behavior-Preserving Non-Prefix {KV} Cache Reuse in {RAG}},
  author    = {Zhang, Xingjian},
  booktitle = {Findings of the Association for Computational Linguistics: AACL-IJCNLP 2026},
  year      = {2026}
}
```
