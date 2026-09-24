# `safekv`: the package and scripts behind the paper

This directory holds the code that produced every run in the paper: the `safekv` package, the experiment scripts, and
the CPU test suite (135 passed, 1 skipped; `../TEST_LOG.txt`). For a compact implementation of the method, see
[`../minimal/safekv_minimal.py`](../minimal/safekv_minimal.py); for the command behind each table and figure, see the
[top-level README](../README.md) and [`../FULL_REPRODUCTION.md`](../FULL_REPRODUCTION.md).

## Method names in the result files

| Name in `answer_eval_*` files | Paper name |
|---|---|
| `full_prefill` | full prefill (the reference) |
| `prefix_conditioned_naive_global` | prefix-conditioned composition (Prefix-comp.) |
| `risk_guided_suffix_closure_k1`, `_k2` | risk suffix K1 / K2 (SAFE-KV) |
| `query_similarity_suffix_closure_k1`, `_k2` | query suffix K1 / K2 |
| `hybrid_query_risk_union_suffix_k1` | hybrid suffix K1 |
| `random_suffix_closure_k1_seeded`, `_k2_seeded` | random suffix K1 / K2 |
| `risk_guided_doc_patch_k1` | document-only repair (Doc K1) |
| `risk_guided_downstream_w2_k1` ... `_w4_k1` | window repair w2–w4 |
| `oracle_evidence_doc_patch`, `oracle_evidence_doc_suffix_closure_patch` | oracle document patch, oracle suffix repair |
| `actual_recompute::<method>` | `<method>` with actual suffix forwarding; without the prefix, the donor-copy protocol |

`answer_equivalence_to_full_prefill` is answer preservation and `avg_patched_token_ratio` the recomputed context ratio.
A K-suffix method scores every document, takes the top K (ties to the lower document id), and re-encodes from the
earliest of them to the last document.

## Entry points used in the paper

| Script | Runs |
|---|---|
| `scripts/run_answer_eval.py` | every answer-level run (donor copy; `actual_recompute::*` methods for actual forwarding) |
| `scripts/build_rebuttal_variants.py` | score-neutral shuffled and nested staleness inputs (`../results_rebuttal/data/`) |
| `scripts/run_staleness_doccount_sweep.py` | staleness x document-count grid (Tables 6, 33) |
| `scripts/run_rebuttal_latency_trace.py`, `validate_rebuttal_latency_results.py`, `summarize_latency_paired_bootstrap.py` | L40S latency (Tables 7, 18, 19) |
| `scripts/bootstrap_answer_eval_ci.py` | paired bootstrap intervals |
| `scripts/heldout_method_calibration.py` | held-out calibration (Table 16) |
| `scripts/run_oracle_kv_drift_local_baseline.py` | oracle KV-drift token-local diagnostic (Table 23) |
| `../results_august/code/scripts/run_query_attention_local_baseline.py` | operational token-local baseline (Tables 4, 22) |

## Package layout

```text
code/
  configs/     configs used by the commands below (every run's config is also in ../configs/)
  safekv/      the package
  scripts/     experiment, summary and validation CLIs
  tests/       CPU test suite
```

- `safekv/data_schema.py`: typed schema for examples and prompt packs
- `safekv/build_diagnostic.py`, `build_external.py`: synthetic diagnostic generator and HotpotQA/2Wiki conversion
- `safekv/prompting.py`: RAG prompt builder (plain and chat) with offset-based document/span ranges
- `safekv/token_spans.py`: segment-wise tokenizer helpers and document span splitting
- `safekv/modeling.py`: Hugging Face tokenizer/model loading
- `safekv/full_prefill.py`: full-prefill forward pass, greedy decoding, and output schema
- `safekv/cache_ops.py`: legacy-cache conversion, slicing, validation, and concatenation
- `safekv/naive_composition.py`: sequential prefill and composition baselines
- `safekv/patch_recompute.py`: patch-range construction (oracle, random, document, suffix) and cache-slice replacement
- `safekv/patch_granularity.py`: repair-granularity method definitions and summaries
- `safekv/doc_selector.py`: retrieval, query, entity and risk document selectors, and the safe-composition gate
- `safekv/doc_selector_stress.py`: multi-seed random baselines, repair-oracle enumeration, budget-normalized summaries
- `safekv/answer_eval.py`: answer normalization, answer-drift summaries, KL/mismatch analysis, failure reports
- `safekv/bootstrap.py`, `heldout_gate.py`, `budget_gate.py`, `cost_accounting.py`: intervals, calibration, gates, cost

## Development-stage pipeline

The sections below document the scripts of the early development runs (Qwen2.5-0.5B/1.5B on synthetic diagnostics;
Appendix Tables 8–10 and 29–31). Commands are run from `code/`; configs are in `code/configs/`.

### Prompt Format

Document blocks use this format:

```text
[Document 1 | Title: Archive Note A]
{doc.text}
```

The query suffix is unchanged:

```text
Question: {question}
Answer with the shortest exact answer phrase from the documents.
Answer:
```

Prompt construction is split into two stages:

1. `build_prompt_text_and_char_ranges(example)` creates `full_text` and global character ranges.
2. `tokenize_prompt_with_offsets(prompt, tokenizer)` tokenizes `full_text` once with `add_special_tokens=False` and maps document/span character ranges through `offset_mapping`.

For HuggingFace fast tokenizers, the canonical `full_input_ids` come from:

```python
tokenizer(full_text, add_special_tokens=False, return_offsets_mapping=True)
```

Tokenizers without `offset_mapping` must provide an explicit `encode_with_offsets(text)` fallback. The included `RegexTokenizer` does this for unit tests only.

### Setup

```bash
python -m pip install -r requirements.txt
```

### Build Diagnostic Data

From the repository root:

```bash
python scripts/build_diagnostic_data.py \
  --n-per-category 20 \
  --seed 13 \
  --out data/diagnostic_100.jsonl
```

The noisy retrieval stress variant keeps evidence labels valid but shuffles
document order, weakens evidence retrieval scores, raises some distractor or
conflict retrieval scores, and injects lexical overlap into distractors:

```bash
python scripts/build_diagnostic_data.py \
  --n-per-category 20 \
  --seed 13 \
  --variant noisy_retrieval \
  --out data/diagnostic_100_noisy.jsonl
```

### Run Tests

```bash
python -m pytest
```

### Run Full Prefill Smoke

```bash
python scripts/run_full_prefill.py --config configs/v0_smoke.yaml
```

Outputs:

```text
results/full_prefill_outputs.jsonl
results/full_prefill_summary.json
results/logits/full_prefill/
results/prompt_packs/
```

### Run Naive Composition Smoke

```bash
python scripts/run_naive_composition.py --config configs/v0_smoke.yaml
```

The script first checks that chunked sequential prefill reproduces full
single-pass prefill. It then compares six non-prefix composition baselines:

- `doc_only_naive_global`: document caches only, original global positions
- `doc_only_naive_local`: document caches only, local document positions
- `prefix_plus_naive_global`: exact prompt prefix cache plus unconditioned global-position document caches
- `prefix_plus_naive_local`: exact prompt prefix cache plus unconditioned local-position document caches
- `prefix_conditioned_naive_global`: exact prompt prefix cache plus document caches encoded with that prefix and original global positions
- `prefix_conditioned_naive_local`: exact prompt prefix cache plus document caches encoded with that prefix and local positions after the prefix

`naive_global` and `naive_local` output files are kept as aliases for the
doc-only baselines for backward compatibility.

For the full 100-example Qwen 0.5B smoke run, use:

```bash
python scripts/run_naive_composition.py --config configs/v0_qwen05_100.yaml
```

This 100-example run is intended for local validation and may take noticeably
longer on CPU. It is not part of the unit test suite.

Additional composition outputs:

```text
results/composition_metrics.csv
results/composition_failure_analysis.md
results/naive_composition_summary.json
```

The JSON summary includes fixed-seed bootstrap 95% confidence intervals for
the main behavior-preservation metrics at method and category-method levels.

### Run Oracle Patch Diagnostics

```bash
python scripts/run_patch_recompute.py --config configs/v0_smoke.yaml
```

The script starts from `prefix_conditioned_naive_global`, computes full-prefill
KV in memory, and tests four patch diagnostics:

- `full_doc_cache_patch_sanity`: replace all document KV slices from full prefill
- `oracle_evidence_doc_patch`: replace oracle evidence document slices, plus conflict documents when marked
- `oracle_evidence_span_patch`: replace expanded oracle evidence span slices clipped to document text
- `random_span_patch_same_budget`: patch a deterministic random token budget matched to oracle evidence spans

Outputs:

```text
results/patch_recompute_outputs.jsonl
results/patch_recompute_metrics.csv
results/patch_recompute_summary.json
results/patch_failure_analysis.md
```

### Run Patch Granularity Ablations

```bash
python scripts/run_patch_granularity.py --config configs/v0_smoke.yaml
```

The script starts from `prefix_conditioned_naive_global` and compares:

- evidence span windows at 0, 4, 8, 16, and 32 tokens
- evidence suffix-to-document-end patching
- sentence-to-document-end patching
- support-plus-conflict span and suffix patching
- deterministic budget-matched random baselines for each non-document oracle method
- oracle evidence document patch as the coarse reference

Outputs:

```text
results/patch_granularity_outputs.jsonl
results/patch_granularity_metrics.csv
results/patch_granularity_summary.json
results/patch_granularity_failure_analysis.md
```

### Run Document Selector And Gate Ablations

```bash
python scripts/run_doc_selector.py --config configs/v0_smoke.yaml
```

The script starts from `prefix_conditioned_naive_global` and compares:

- oracle evidence document patch
- random document patch with the same document count as the oracle
- random document-text token patch with the same token budget as the oracle
- retrieval, query-similarity, entity-overlap, conflict-aware, and risk-guided document selectors
- safe-composition gate thresholds that either keep the base composition or patch risk-guided top-2 documents

Outputs:

```text
results/doc_selector_outputs.jsonl
results/doc_selector_metrics.csv
results/doc_selector_summary.json
results/doc_selector_failure_analysis.md
results/doc_selector_pareto.csv
```

### Run Document Selector Stress Tests

```bash
python scripts/run_doc_selector_stress.py \
  --config configs/v0_smoke.yaml \
  --num-random-seeds 10
```

The stress runner does not add new heuristic selectors. It compares existing
document selectors against:

- multi-seed random document baselines for same-count, k=1, and k=2
- exhaustive repair oracles for best k=1, best k=2, same-count, and minimum-KL subsets up to a configured max k
- random gate baselines that match gate patch rate or number of patched examples
- budget-normalized KL reductions per patched token ratio and per patched document

Outputs:

```text
results/doc_selector_stress_outputs.jsonl
results/doc_selector_stress_metrics.csv
results/doc_selector_stress_random_baseline_distribution.csv
results/doc_selector_stress_summary.json
results/doc_selector_stress_failure_analysis.md
```

For the full clean and noisy 100-example runs:

```bash
python scripts/run_doc_selector_stress.py \
  --config configs/v0_qwen05_100.yaml \
  --results-dir results_qwen05_100 \
  --num-random-seeds 100

python scripts/run_doc_selector_stress.py \
  --config configs/v0_qwen05_100_noisy.yaml \
  --results-dir results_qwen05_100_noisy \
  --num-random-seeds 100
```

### Run Answer-Level Evaluation

Tiny CPU-compatible smoke:

```bash
python scripts/run_answer_eval.py \
  --config configs/v0_smoke.yaml \
  --max-examples 2 \
  --methods full_prefill,prefix_conditioned_naive_global \
  --results-dir results_answer_smoke
```

Full clean/noisy answer evaluation is intended for GPU:

```bash
python scripts/run_answer_eval.py \
  --config configs/v0_qwen05_100.yaml \
  --results-dir results_qwen05_100_answer \
  --resume

python scripts/run_answer_eval.py \
  --config configs/v0_qwen05_100_noisy.yaml \
  --results-dir results_qwen05_100_noisy_answer \
  --resume
```

Default answer-eval methods:

- `full_prefill`
- `prefix_conditioned_naive_global`
- `oracle_evidence_doc_patch`
- `query_similarity_doc_patch_k2`
- `entity_overlap_doc_patch_k2`
- `risk_guided_doc_patch_k2`
- `safe_gate_t0.45`
- `safe_gate_t0.60`
- `random_doc_patch_k2_seeded`

Outputs:

```text
results/answer_eval_outputs.jsonl
results/answer_eval_metrics.csv
results/answer_eval_summary.json
results/answer_failure_analysis.md
```

For instruct-model experiments, set `experiment.prompt_format: chat_rag`.
The default remains `plain_rag`.
