# SAFE-KV rebuttal experiment ledger

Last audited: **2026-07-10 17:13 UTC**. This directory is separate from the immutable submission artifact under `../safekv_acl_supplement 2/results/`.

`../EXPERIMENT_STATUS.md` is the final claim-level source of truth. This file retains the operational and historical directory ledger. A directory containing a JSONL file is **not** automatically a completed experiment: cite a result only when a final validator permits it and its summary, completeness checks, provenance, and invariants are present.

## Status labels

- `VALIDATED_PRIMARY`: complete enough to quote, subject to the caveat in its row.
- `VALIDATED_DIAGNOSTIC`: technically checked, but only supports a narrow diagnostic claim.
- `VALIDATED_INPUT`: deterministic input artifact, not an experimental result.
- `RUNNING`: append-only partial output; do not compute or quote intermediate metrics.
- `DEBUG_ONLY`: implementation smoke or superseded small sample; do not quote as evidence.
- `INVALID_DO_NOT_CITE`: known methodological or measurement defect.
- `PENDING_NOT_RUN`: script/template exists, but no valid result is present.

## Environment and code state

- GPU: NVIDIA L40S, 46,068 MiB; driver 570.195.03.
- Python 3.12.3; PyTorch 2.8.0+cu128; Transformers 4.57.6.
- Model used by GPU rebuttal runs: `Qwen/Qwen2.5-7B-Instruct`, float16, deterministic decoding.
- Current CPU suite: **135 passed, 1 skipped** with `CUDA_VISIBLE_DEVICES=''`.
- The current tree contains post-submission fixes. Do not treat its checksums as the checksums of `safekv_acl_supplement_full.zip`.

## Final completion override

The later validated artifacts below supersede any older `RUNNING` or
`PENDING_NOT_RUN` descriptions retained in historical subsections:

- `staleness_doccount_full_50_v3/`: PASS, 26,250 rows and zero invariant failures.
- `oracle_kv_drift_2wiki_neutral_shuffle101_100_v3/`: PASS, 1,300 rows; oracle-only, nondeployable, and not Cache-Craft.
- `actual_vs_copy_{hotpot,2wiki}_500_l40s_v2/`: PASS, same-run donor/actual reconciliation.
- `neutral_selector_actual_{hotpot,2wiki}_shuffle{101,202,303}_100/`: PASS, six actual-forward neutral runs.
- `smoke_answer_resume_contract_2wiki_v5/` and `smoke_latency_v5/`: final implementation gates, not scientific sample-size evidence.
- `latency_hotpot_original_50_v1/`, `latency_2wiki_original_50_v1/`, `latency_2wiki_neutral_shuffle101_50_v1/`, `latency_n16_neutral_layout101_50_v1/`, and `latency_noise64_50_v1/`: all PASS with validator and paired bootstrap.
- `quality_noise64_actual_riskk1_50_v1/`: PASS. Actual Risk-K1 preservation is 44% at 51.9% cost; this invalidates the apparent Noise64 median speed crossover as a useful quality-latency point.

No faithful Cache-Craft or vLLM/continuous-batching production result exists.

## Results that may be cited now

### True suffix forward on the original 500-example datasets — `VALIDATED_PRIMARY`

These runs perform a real forward pass from the selected suffix start and then run the query; they do not merely copy the corresponding slice from a full-prefill donor cache.

| Dataset | Method | N | Answer equivalence to full prefill | Mean patched-token ratio | Output directory |
|---|---|---:|---:|---:|---|
| HotpotQA | Actual Risk suffix K1 | 500 | 0.998 | 0.8916 | `actual_recompute_hotpot_500/` |
| HotpotQA | Actual Risk suffix K2 | 500 | 1.000 | 0.9478 | `actual_recompute_hotpot_500/` |
| 2Wiki | Actual Risk suffix K1 | 500 | 0.966 | 0.8134 | `actual_recompute_2wiki_500/` |
| 2Wiki | Actual Risk suffix K2 | 500 | 0.984 | 0.9287 | `actual_recompute_2wiki_500/` |

Independent raw-output checks found 1,000 rows, 500 distinct examples per method pair, no duplicate `(example_id, method)` keys, and zero recorded failures in each run. The Hotpot directory predates the new run-manifest writer and therefore lacks a manifest; its raw rows and summary are complete. The 2Wiki directory includes `answer_eval_manifest.json`.

**Scope caveat:** these two runs validate recomputation semantics on the submitted inputs, not selector generalization. In the original external builder, evidence documents are first in every example and have perfectly separated retrieval scores in 100% of HotpotQA and 99.6% of 2Wiki examples.

### Retrieval-neutral and order-shuffled frontier stress — `VALIDATED_PRIMARY`

All retrieval scores are zero. The `shuffle101` variants also deterministically randomize document order. Each run evaluates 100 examples with executable suffix forwards. Values below are SQuAD-style normalized answer equivalence; patch ratio is the context-token fraction recomputed.

| Dataset variant | Method | Equivalence | Mean patch ratio |
|---|---|---:|---:|
| Hotpot zero, original order | Query K1 | 0.96 | 0.848 |
| Hotpot zero, original order | Query K2 | 0.97 | 0.882 |
| Hotpot zero, original order | Risk K1 | 0.91 | 0.718 |
| Hotpot zero, original order | Risk K2 | 0.95 | 0.837 |
| Hotpot zero, original order | Hybrid K1 | 0.97 | 0.863 |
| Hotpot zero, shuffle 101 | Query K1 | 0.91 | 0.688 |
| Hotpot zero, shuffle 101 | Query K2 | 0.97 | 0.880 |
| Hotpot zero, shuffle 101 | Risk K1 | 0.81 | 0.579 |
| Hotpot zero, shuffle 101 | Risk K2 | 0.90 | 0.780 |
| Hotpot zero, shuffle 101 | Hybrid K1 | 0.92 | 0.739 |
| 2Wiki zero, original order | Query K1 | 0.89 | 0.754 |
| 2Wiki zero, original order | Query K2 | 0.95 | 0.868 |
| 2Wiki zero, original order | Risk K1 | 0.87 | 0.727 |
| 2Wiki zero, original order | Risk K2 | 0.95 | 0.860 |
| 2Wiki zero, original order | Hybrid K1 | 0.94 | 0.792 |
| 2Wiki zero, shuffle 101 | Query K1 | 0.81 | 0.698 |
| 2Wiki zero, shuffle 101 | Query K2 | 0.93 | 0.854 |
| 2Wiki zero, shuffle 101 | Risk K1 | 0.72 | 0.622 |
| 2Wiki zero, shuffle 101 | Risk K2 | 0.89 | 0.801 |
| 2Wiki zero, shuffle 101 | Hybrid K1 | 0.81 | 0.710 |

Output directories:

- `frontier_hotpot_zero_100/`
- `frontier_hotpot_zero_shuffle101_100/`
- `frontier_2wiki_zero_100/`
- `frontier_2wiki_zero_shuffle101_100/`

The observed minimum normalized-answer-equivalent patch ratios are 0.275, 0.233, 0.351, and 0.317 respectively. They are **observed answer-level minima over enumerated starts**, not a proof of a unique monotone causal frontier: normalized-answer monotonicity violations occur in 6%, 22%, 18%, and 26% of examples. Generated-token-sequence exactness is unavailable in these saved frontier rows; use only the normalized-answer or raw-trimmed-string columns in schema-v2 summaries.

These results require narrowing the selector claim: the submitted Risk selector is not reliably generalizable after removal of gold-derived score/order signals.

### Selector-only CPU audit — `VALIDATED_DIAGNOSTIC`

Directory: `cpu_selector_audit_l40s_host/`.

- Risk K2 selector p95: 1.800 ms on HotpotQA, 2.125 ms on 2Wiki, and 3.631 ms on the 67-document synthetic workload.
- Query K2 selector p95: 0.182 ms, 0.199 ms, and 0.614 ms on those workloads.
- On retrieval-neutral shuffled inputs, Risk K2 evidence recall is 0.467 on HotpotQA and 0.620 on 2Wiki; exact-set rates are 0.163 and 0.321.

This supports only a selector-cost/selector-quality statement. It is not end-to-end latency, production throughput, or language-model answer quality.

### Direct donor-copy versus actual-forward check — `VALIDATED_DIAGNOSTIC`

Directories: `actual_vs_copy_hotpot_50/` and `actual_vs_copy_2wiki_50/`.

On 50 examples, donor-copy and actual forward produce identical normalized answers for Risk K1, Risk K2, and Hybrid K1 on both datasets. Query K1/K2 agreement is 98% on HotpotQA; on 2Wiki it is 98% for Query K1 and 100% for Query K2. These runs are superseded by the two 500-example actual-Risk runs for headline use.

### Staleness implementation reference — `VALIDATED_DIAGNOSTIC`

Directory: `smoke_staleness_reference_v3/`.

This is a two-example N1/N4 implementation check, not a scientific result. It has zero invariant failures; its all-fresh chunk-matched reference agrees with one-shot full prefill on all four example/setting cases at both normalized-answer and generated-token levels, with mean first-token KL `1.64e-13`. Operational Query/Risk selectors rank all structurally eligible positions `>=2` and do not observe the sampled stale mask.

## Input variants — `VALIDATED_INPUT`

All files live in `data/`; each JSONL has a sidecar `.summary.json`.

- `hotpot_zero.jsonl`, `2wiki_zero.jsonl`: original order, all retrieval scores zero.
- `hotpot_zero_shuffle{101,202,303}.jsonl`, `2wiki_zero_shuffle{101,202,303}.jsonl`: score-neutral and deterministically shuffled.
- `hotpot_k{2,3,4,5}_zero_shuffle101.jsonl`: controlled document-count variants. K3/K4/K5 contain 499/498/497 examples because inputs with too few documents are excluded; do not assume N=500.
- `single_nested_n{1,2,4,8,16}_zero_layout101.jsonl`: paired 50-example, single-evidence factorial inputs for the staleness-by-document-count sweep. Retrieval scores are zero and evidence layout is label-independent.

A clean CPU regeneration with the current builder reproduced the saved bytes exactly for Hotpot/2Wiki `zero_shuffle101` and all five nested N variants; their SHA-256 values therefore match the hashes recorded by the active staleness manifest.

## Running, pending, debug-only, and invalid outputs

The six directories marked `DEBUG_ONLY` or `INVALID_DO_NOT_CITE` below are listed for the record only; they are not
included in the repository. The raw `staleness_doccount_outputs.jsonl` of `staleness_doccount_full_50_v3/` is in the
release tarball (see `RAW_OUTPUTS_IN_RELEASE.txt` in that directory).

| Directory / experiment | Status | What to do |
|---|---|---|
| `staleness_doccount_full_50_v3/` | `VALIDATED_PRIMARY` | PASS; use the final summary/bootstrap with the provenance-mismatch scope caveat. |
| Five corrected warm repeated latency traces | `VALIDATED_PRIMARY` | PASS; quality-gated conclusion is negative and non-production. |
| Full oracle KV-drift local diagnostic | `VALIDATED_DIAGNOSTIC` | PASS; optimistic, donor-copied, nondeployable, and explicitly not Cache-Craft. |
| Cache-Craft comparison | `PENDING_NOT_RUN` | No faithful implementation is present. Never relabel the oracle KV-drift diagnostic as Cache-Craft. |
| vLLM/continuous-batching production benchmark | `PENDING_NOT_RUN` | No result exists. |
| `smoke_actual_hotpot_1/` | `DEBUG_ONLY` | Superseded by `actual_recompute_hotpot_500/`. |
| `smoke_frontier_hotpot_zero_shuffle101_1/` | `DEBUG_ONLY` | Superseded by the 100-example frontier run. |
| `smoke_oracle_kv_drift_2wiki_1/` | `DEBUG_ONLY` | N=1 proves only that the script executes. |
| `smoke_staleness_n1_n4/` | `INVALID_DO_NOT_CITE` | Incomplete output; no final summary. |
| `smoke_staleness_n1_n4_v2/` | `INVALID_DO_NOT_CITE` | Operational selectors were filtered using the true sampled stale mask, leaking oracle information. |
| `smoke_latency_trace_2wiki_2/` | `INVALID_DO_NOT_CITE` | Predates the cache-lifetime/memory-accounting fix; resident caches and returned values contaminated timing/memory accounting. |

## Reproduction setup

Use a new result directory for every fresh run. Do not overwrite the immutable submission results or any validated directory above.

```bash
export WORKSPACE=/workspace/safekv_acl_submission_files
export SUPPLEMENT="$WORKSPACE/safekv_acl_supplement 2"
export PY="$WORKSPACE/.venv/bin/python"
export PYTHONPATH="$SUPPLEMENT/code"
export HF_HOME="$WORKSPACE/.hf_cache"
export PYTHONHASHSEED=0
cd "$SUPPLEMENT"
```

CPU verification:

```bash
CUDA_VISIBLE_DEVICES='' "$PY" -B -m pytest -q -p no:cacheprovider code/tests
```

### Build a score-neutral shuffled input

```bash
"$PY" code/scripts/build_rebuttal_variants.py \
  --input data/external_hotpotqa_500.jsonl \
  --output "$WORKSPACE/rebuttal_experiments/data/rerun_hotpot_zero_shuffle101.jsonl" \
  --retrieval-mode zero \
  --shuffle-seed 101
```

For nested N-document inputs, add `--nested-single-evidence --max-documents N --max-examples 50` and use `data/noise_sweep_16_250.jsonl` as the input.

### True suffix-forward validation

```bash
"$PY" code/scripts/run_answer_eval.py \
  --config configs/acl_qwen25_7b_hotpotqa_500.yaml \
  --data-path data/external_hotpotqa_500.jsonl \
  --max-examples 500 \
  --methods actual_recompute::risk_guided_suffix_closure_k1,actual_recompute::risk_guided_suffix_closure_k2 \
  --results-dir "$WORKSPACE/rebuttal_experiments/rerun_actual_hotpot_500"
```

Replace the config/data/output names with the 2Wiki equivalents for the second run. On a fresh directory, omit `--resume`; current code writes a manifest. Resume only a manifest-bearing interrupted run with identical inputs/options.

### Frontier stress run

```bash
"$PY" code/scripts/run_rebuttal_frontier_eval.py \
  --config configs/acl_qwen25_7b_hotpotqa_500.yaml \
  --data-path "$WORKSPACE/rebuttal_experiments/data/hotpot_zero_shuffle101.jsonl" \
  --max-examples 100 \
  --results-dir "$WORKSPACE/rebuttal_experiments/rerun_frontier_hotpot_zero_shuffle101_100"
```

To regenerate only the schema-v2 summaries from an existing `frontier_outputs.jsonl`, rerun the same command with `--summarize-only`.

### CPU selector audit

```bash
"$PY" code/scripts/run_rebuttal_cpu_selector_audit.py \
  --out-dir "$WORKSPACE/rebuttal_experiments/rerun_cpu_selector_audit" \
  --latency-repeats 20 \
  --latency-max-examples 500 \
  --shuffle-seeds 101,202,303 \
  --random-seeds 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
```

### Staleness probability × document count sweep

Do not launch a second copy while `staleness_doccount_full_50_v3/` is running.

```bash
"$PY" code/scripts/run_staleness_doccount_sweep.py \
  --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-spec "N1=$WORKSPACE/rebuttal_experiments/data/single_nested_n1_zero_layout101.jsonl" \
  --data-spec "N2=$WORKSPACE/rebuttal_experiments/data/single_nested_n2_zero_layout101.jsonl" \
  --data-spec "N4=$WORKSPACE/rebuttal_experiments/data/single_nested_n4_zero_layout101.jsonl" \
  --data-spec "N8=$WORKSPACE/rebuttal_experiments/data/single_nested_n8_zero_layout101.jsonl" \
  --data-spec "N16=$WORKSPACE/rebuttal_experiments/data/single_nested_n16_zero_layout101.jsonl" \
  --max-examples 50 \
  --probabilities 0,0.25,0.5,0.75,1 \
  --mask-seeds 13,29,47 \
  --strict-invariants \
  --require-paired-examples \
  --results-dir "$WORKSPACE/rebuttal_experiments/rerun_staleness_doccount_full_50_v3"
```

For an interrupted manifest-bearing directory, use the identical command plus `--resume`.

### Oracle token-local diagnostic — not Cache-Craft

```bash
"$PY" code/scripts/run_oracle_kv_drift_local_baseline.py \
  --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-path data/external_2wiki_500.jsonl \
  --max-examples 100 \
  --budgets 0.20,0.30,0.45,0.60 \
  --results-dir "$WORKSPACE/rebuttal_experiments/rerun_oracle_kv_drift_2wiki_100"
```

### Corrected warm latency trace

```bash
"$PY" code/scripts/run_rebuttal_latency_trace.py \
  --config configs/acl_qwen25_7b_2wiki_500.yaml \
  --data-path "$WORKSPACE/rebuttal_experiments/data/2wiki_zero_shuffle101.jsonl" \
  --max-examples 100 \
  --repeats 5 \
  --warmup-examples 5 \
  --results-dir "$WORKSPACE/rebuttal_experiments/rerun_latency_2wiki_zero_shuffle101_100"
```

This is batch-1, existing-cache, time-to-first-logit measurement on one L40S. Even a valid run must not be described as vLLM, serving throughput, continuous batching, or production load.

## Completion checks before citing a rerun

1. The process exited with status 0.
2. A final summary and metrics CSV exist; a growing JSONL alone is insufficient.
3. `num_failed_rows == 0` for answer runs, and raw row counts match `N × number_of_methods` with unique `(example_id, method)` keys.
4. Staleness runs have `num_invariant_failures == 0`, paired IDs across N, and a manifest whose config/data/implementation hashes match the run.
5. Frontier summaries state the equivalence definition and availability count; do not report token-exact metrics when availability is zero.
6. Timing runs use the post-fix script, include warmup/repeats, and report incremental peak memory separately from the resident cache pool.
7. Every claim repeats its scope caveat: original-data selector leakage, neutral/shuffle sample size, oracle-only diagnostics, or non-production timing as applicable.
