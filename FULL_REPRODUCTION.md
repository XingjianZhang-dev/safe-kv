# Full Reproduction Guide

Commands assume the current working directory is the repository root. Nothing in the paper depends on files outside
this repository (plus, for the raw per-example dumps of four run families, the release tarball; see `RAW_OUTPUTS_IN_RELEASE.txt`
next to those runs and `scripts/fetch_raw_outputs.sh`). Section numbers below refer to the camera-ready PDF.

## 1. Environment

- Python 3.10 or newer; `requirements.txt` at the repository root pins the exact versions used for the CPU checks and
  the table/figure generators (torch 2.8.0, transformers 4.57.6, matplotlib 3.11.2, ...); `code/requirements.txt` and
  `code/pyproject.toml` are the range specifications the runs were made with.
- Submitted runs: NVIDIA L40S-class GPU, PyTorch 2.4.1+cu124, Transformers 4.57.6.
- Response-period runs (`results_rebuttal/`): one NVIDIA L40S (46 GB), PyTorch 2.8.0+cu128, Transformers 4.57.6,
  Python 3.12.3, `PYTHONHASHSEED=0`.
- Localized-baseline runs (`results_august/`): one NVIDIA RTX PRO 6000 Blackwell Server Edition, PyTorch
  2.8.0+cu128, Transformers 4.57.6, Python 3.11.15.
- The CPU test log in `TEST_LOG.txt` was produced from a fresh clone of this repository in a clean virtual environment
  built from `requirements.txt` (torch 2.8.0 CPU, transformers 4.57.6).

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip && python -m pip install -r requirements.txt
```

## 2. CPU checks (no model download)

```bash
CUDA_VISIBLE_DEVICES='' PYTHONHASHSEED=0 PYTHONPATH=code python -B -m pytest -q -p no:cacheprovider code/tests
python scripts/verify_packaged_results.py
python -B scripts/camera_ready/build_tables.py       # regenerates paper_reference/camera_ready_tables/*.tex
python -B scripts/camera_ready/tie_break_audit.py    # Appendix N tie-break table
python -B scripts/camera_ready/make_figures.py       # all five paper figures + plotted-value CSVs
bash scripts/fetch_raw_outputs.sh                    # optional: restore the raw per-example dumps kept in the release tarball
```

Expected: `135 passed, 1 skipped` (the skipped test is environment-dependent); the verifier prints
`Supplement verification passed`; the regenerated tables and figure CSVs are byte-identical to the shipped ones in
`paper_reference/camera_ready_tables/` and `paper_reference/final_figures/`.

## 3. Data

Submitted processed datasets are in `data/` (see `REPRODUCTION.md` for the synthetic generators). Response-period
variants are in `results_rebuttal/data/` and were built from `data/` with the shipped code:

```bash
# score-neutral shuffled variant (retrieval scores 0, per-example shuffle, order seed 101/202/303)
PYTHONPATH=code python code/scripts/build_rebuttal_variants.py \
  --input data/external_hotpotqa_500.jsonl --retrieval-mode zero --shuffle-seed 101 \
  --output results_rebuttal/data/rerun_hotpot_zero_shuffle101.jsonl
# nested single-evidence inputs for the staleness grid (N = 1,2,4,8,16)
PYTHONPATH=code python code/scripts/build_rebuttal_variants.py \
  --input data/noise_sweep_16_250.jsonl --retrieval-mode zero --shuffle-seed 101 \
  --nested-single-evidence --max-documents 16 --max-examples 50 \
  --output results_rebuttal/data/rerun_single_nested_n16_zero_layout101.jsonl
```

A clean CPU rebuild reproduces the shipped variant files byte-for-byte (their SHA-256 values are recorded in the
staleness manifest). The August HotpotQA conversions (`results_august/datasets/ipm_v1/hotpotqa_{natural,shuffle,bm25}_test.jsonl`)
were built by `results_august/code/scripts/build_ipm_realistic_inputs.py` from the public HotpotQA distractor
validation split (`hotpotqa_build_manifest.json` records source revision, seed 20260821, and per-condition statistics;
gold labels were not used for ranking).

## 4. Paper-result map

| Paper item | Protocol | Packaged sources |
|---|---|---|
| Table 1, Fig. (App. K left), App. H/I/J | donor copy | `results/acl_qwen25_7b_hotpotqa_suffix_main_500/`, `results/acl_qwen25_7b_2wiki_suffix_main_500/` (+ `bootstrap_ci/`, `heldout_method_calibration_safekv_only/`) |
| Table 2(a) actual forwarding, original inputs | actual forwarding | `results_rebuttal/actual_recompute_{hotpot,2wiki}_500/answer_eval_summary.json`; same-run reconciliation `results_rebuttal/actual_vs_copy_{hotpot,2wiki}_500_l40s_v2/donor_actual_reconciliation.json` (App. H) |
| Table 2(b) score-neutral shuffled | actual forwarding | `results_rebuttal/neutral_selector_actual_3seed_validation/neutral_selector_{across,by}_seed.csv`; per-run dirs `results_rebuttal/neutral_selector_actual_{hotpot,2wiki}_shuffle{101,202,303}_100/` |
| Table 3 local vs suffix | donor copy | `results/acl_qwen25_7b_2wiki_downstream_window_100/` |
| Table 4 and App. M query-attention baseline | token-local actual recompute | `results_august/run_registry/qwen25_query_attention_hotpotqa_{natural,shuffle,bm25}_test_n100_v1/query_attention_local_summary.csv` |
| Table 5 position sweep | donor copy | `results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv` |
| Table 6 and App. U staleness x document count | actual forwarding | `results_rebuttal/staleness_doccount_full_50_v3/staleness_doccount_summary.csv`, `staleness_paired_bootstrap_summary.csv`, `validation_report.json` |
| Table 7 and App. K latency | actual forwarding incl. planning | `results_rebuttal/latency_{hotpot_original,2wiki_original,2wiki_neutral_shuffle101,n16_neutral_layout101,noise64}_50_v1/latency_trace_summary.json`, `latency_paired_bootstrap_summary.csv`, `selector_latency.csv`, `validation_report.json` |
| Noise64 quality gate (App. K) | both | `results_rebuttal/quality_noise64_actual_riskk1_50_v1/` (`answer_eval_summary.json`, `donor_actual_reconciliation.json`, `bootstrap/`) |
| Selector CPU cost (App. K) | CPU | `selector_latency.csv` in the five latency runs; `results_rebuttal/cpu_selector_audit_l40s_host/latency.csv` |
| Oracle KV-drift diagnostic (App. M) | oracle donor copy | `results_rebuttal/oracle_kv_drift_2wiki_neutral_shuffle101_100_v3/` |
| Tie-break audit (App. N) | CPU | `scripts/camera_ready/tie_break_audit.py` on `data/` and `results_rebuttal/data/` |
| Submission-time prototype latency (App. K, relabelled) | donor copy, no planning | `results/acl_qwen25_7b_2wiki_latency_suffix_50_with_hybrid/`, `results/acl_qwen25_7b_noise64_latency_suffix_20_with_hybrid/` |
| Noise sweep / closure (App. M) | donor copy | `results/acl_qwen25_7b_noise_sweep_{0,8,16}_250/`, `results/acl_qwen25_7b_noise16_{k_sweep,closure,adaptive_suffix,linked_interval}_250/` |
| Selector diagnostics (App. N) | — | `results/selector_artifacts/selector_quality_{hotpotqa,2wiki}_500.csv` |
| Mistral operating points (App. N) | donor copy | `results/acl_mistral7b_noisy_suffix_250_balanced/` |
| Small-model development tables (App. E–G) | — | `results/paper_tables/results_paper/`, `results/metrics/` |

## 5. Regenerating the submitted runs

`python scripts/emit_reproduction_commands.py --kind answer` (or `--kind latency`) prints the exact commands
inferred from every packaged summary under `results/`; add `--execute` to run them into
`reproduction_runs/recomputed/`.

## 6. Regenerating the response-period runs

Set `export PYTHONPATH=code PYTHONHASHSEED=0` and use a new `--results-dir` each time.

```bash
# actual suffix forwarding on the original inputs (Table 2a)
python code/scripts/run_answer_eval.py --config configs/acl_qwen25_7b_hotpotqa_500.yaml \
  --data-path data/external_hotpotqa_500.jsonl --max-examples 500 \
  --methods actual_recompute::risk_guided_suffix_closure_k1,actual_recompute::risk_guided_suffix_closure_k2 \
  --results-dir reproduction_runs/actual_recompute_hotpot_500
# same-run donor vs actual reconciliation (App. H): add the donor methods to --methods and run
python code/scripts/validate_donor_actual_reconciliation.py --results-dir <dir>

# score-neutral shuffled runs (Table 2b): one per seed and dataset
python code/scripts/run_answer_eval.py --config configs/acl_qwen25_7b_hotpotqa_500.yaml \
  --data-path results_rebuttal/data/hotpot_zero_shuffle101.jsonl --max-examples 100 \
  --methods actual_recompute::risk_guided_suffix_closure_k1,actual_recompute::hybrid_query_risk_union_suffix_k1,actual_recompute::query_similarity_suffix_closure_k2,actual_recompute::risk_guided_suffix_closure_k2 \
  --results-dir reproduction_runs/neutral_selector_actual_hotpot_shuffle101_100

# staleness probability x document count (Table 6, App. U)
python code/scripts/run_staleness_doccount_sweep.py --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-spec N1=results_rebuttal/data/single_nested_n1_zero_layout101.jsonl \
  --data-spec N2=results_rebuttal/data/single_nested_n2_zero_layout101.jsonl \
  --data-spec N4=results_rebuttal/data/single_nested_n4_zero_layout101.jsonl \
  --data-spec N8=results_rebuttal/data/single_nested_n8_zero_layout101.jsonl \
  --data-spec N16=results_rebuttal/data/single_nested_n16_zero_layout101.jsonl \
  --max-examples 50 --probabilities 0,0.25,0.5,0.75,1 --mask-seeds 13,29,47 \
  --strict-invariants --require-paired-examples --results-dir reproduction_runs/staleness_doccount_full_50

# latency (Table 7, App. K): one run per workload; inputs as listed in Section 4 of this guide
python code/scripts/run_rebuttal_latency_trace.py --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-path results_rebuttal/data/2wiki_zero_shuffle101.jsonl --max-examples 50 --repeats 5 \
  --warmup-examples 3 --results-dir reproduction_runs/latency_2wiki_neutral_shuffle101_50
python code/scripts/validate_rebuttal_latency_results.py --results-dir reproduction_runs/latency_2wiki_neutral_shuffle101_50
python code/scripts/summarize_latency_paired_bootstrap.py --results-dir reproduction_runs/latency_2wiki_neutral_shuffle101_50

# Noise64 quality gate (App. K): same 50 examples as the Noise64 latency run
python code/scripts/run_answer_eval.py --config configs/acl_qwen25_7b_diagnostic_1000_noisy.yaml \
  --data-path data/noise_sweep_64_50.jsonl --max-examples 50 \
  --methods full_prefill,risk_guided_suffix_closure_k1,actual_recompute::risk_guided_suffix_closure_k1 \
  --results-dir reproduction_runs/quality_noise64_actual_riskk1_50

# oracle KV-drift token-local diagnostic (App. M; nondeployable)
python code/scripts/run_oracle_kv_drift_local_baseline.py --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-path results_rebuttal/data/2wiki_zero_shuffle101.jsonl --max-examples 100 \
  --budgets 0.20,0.30,0.45,0.60 --results-dir reproduction_runs/oracle_kv_drift_2wiki_100

# selector-only CPU audit (App. K/N)
python code/scripts/run_rebuttal_cpu_selector_audit.py --out-dir reproduction_runs/cpu_selector_audit \
  --latency-repeats 20 --latency-max-examples 500 --shuffle-seeds 101,202,303 \
  --random-seeds 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
```

The exact invocation of every shipped response-period run is also recorded in its `answer_eval_manifest.json`,
`staleness_doccount_manifest.json`, or `latency_trace_summary.json` where present; the HotpotQA
`actual_recompute_hotpot_500` directory predates the manifest writer (its raw rows and summary are complete).

## 7. Regenerating the localized-baseline runs (August code)

```bash
cd results_august/code && export PYTHONPATH=. PYTHONHASHSEED=0
python scripts/run_query_attention_local_baseline.py --config configs/ipm_qwen25_7b_main.yaml \
  --data-path ../datasets/ipm_v1/hotpotqa_natural_test.jsonl --max-examples 100 \
  --budgets 0.05,0.10,0.16,0.20,0.30,0.45,0.60 --random-seeds 13,29,47 \
  --results-dir ../run_registry/rerun_qwen25_query_attention_hotpotqa_natural_test_n100
```

(`run_manifest.json` in each shipped run records the original command, duration, and code hash.) The
`ipm_qwen25_7b_main.yaml` config points at a local ModelScope snapshot of Qwen2.5-7B-Instruct; replace
`model_name` with `Qwen/Qwen2.5-7B-Instruct` to download from the Hub.

## 8. Determinism and expected variation

Answer-level runs use greedy decoding, fixed seeds, and the packaged processed examples. Answer metrics match the
packaged summaries when run with the same model revision and compatible PyTorch/Transformers versions; across
PyTorch versions FP16/SDPA near-ties can flip a few outputs (the 2Wiki donor-copy rerun under PyTorch 2.8.0 differs
from the submitted 2.4.1 run on 7 and 5 of 500 outputs for K1 and K2; Appendix H). Latency values vary with GPU
model, driver, and load; the paper's conclusions about latency are qualitative and are stated as read off these
measurements.

## 9. Model and data access

The repository does not redistribute model weights (NOTICE). GPU reproduction downloads Qwen2.5-7B-Instruct and
Mistral-7B-Instruct-v0.3 from the Hugging Face Hub; accept any model terms locally.
