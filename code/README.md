# SAFE-KV v0

SAFE-KV is a feasibility experiment for studying semantic drift in non-prefix KV cache composition for retrieval-augmented generation.

This repository currently implements **Milestone 1 / 1.5 / 2 / 3A / 3B / 3C / 3D / 4A / 4B / 5A / 5B / 6A**:

- synthetic diagnostic RAG data schemas
- deterministic dataset generation for five risk categories
- fixed plain RAG prompt construction
- title-aware document prompt formatting
- full-prompt one-pass tokenization with offset-based token/span range mapping
- fallback offset support for the test tokenizer
- tests for prompt reconstruction, span validity, and char/token alignment invariants
- deterministic HuggingFace full-prefill reference inference
- stratified smoke selection with `data.max_examples_per_category`
- sidecar full-logit and prompt-pack metadata export
- optional `chat_rag` rendering through tokenizer chat templates
- configurable generation stop strings and adaptive boundary windows
- sequential-prefill cache sanity checks
- doc-only naive local/global KV composition smoke baselines
- prefix-controlled naive local/global KV composition smoke baselines
- prefix-conditioned naive local/global composition ablations
- configurable composition method selection, bootstrap CIs, compact CSV export, and failure-analysis Markdown
- oracle full-document and evidence patch diagnostics against the strongest prefix-conditioned baseline
- patch granularity and causal-closure ablations with budget-matched random controls
- document-level non-oracle selectors and safe-composition gate sweeps
- document-selector stress tests with multi-seed random controls, repair-oracle document subsets, budget-normalized summaries, gate random baselines, and a noisy retrieval diagnostic variant
- answer-level behavior evaluation for full prefill, composition, document patching, and gate methods

It intentionally does **not** implement a final span-level risk-guided SAFE-KV
selector or production recompute system yet.

## v0 Feasibility Goal

The full v0 experiment will test whether semantic risk signals can identify which document spans should be recomputed so composed-cache inference better preserves full-prefill behavior under a fixed recompute budget.

The first milestone is narrower: build a clean, deterministic diagnostic dataset and reliable token-span mapping before any cache mechanics are introduced.

## Repository Layout

```text
safe-kv/
  configs/
  data/
  safekv/
  scripts/
  tests/
```

Important modules:

- `safekv/data_schema.py`: typed schema for diagnostic examples and prompt packs
- `safekv/build_diagnostic.py`: deterministic synthetic data generator
- `safekv/prompting.py`: fixed plain RAG prompt builder and offset-based range mapper
- `safekv/token_spans.py`: segment-wise tokenizer helpers and document span splitting
- `safekv/modeling.py`: HuggingFace tokenizer/model loading utilities
- `safekv/full_prefill.py`: full-prefill forward pass, greedy decoding, and output schema
- `safekv/cache_ops.py`: legacy-cache conversion, validation, and concatenation helpers
- `safekv/naive_composition.py`: sequential prefill and naive composition smoke utilities
- `safekv/patch_recompute.py`: oracle cache-slice patching helpers for Milestone 4A
- `safekv/patch_granularity.py`: patch granularity method definitions and summary helpers
- `safekv/doc_selector.py`: document-level scoring, selector, and safe-gate helpers
- `safekv/doc_selector_stress.py`: multi-seed random baselines, repair-oracle enumeration, and budget-normalized stress summaries
- `safekv/answer_eval.py`: answer normalization, answer-drift summaries, KL/mismatch analysis, and answer failure reports
- `scripts/build_diagnostic_data.py`: CLI for writing JSONL diagnostic data
- `scripts/run_full_prefill.py`: CLI for Milestone 2 reference inference
- `scripts/run_naive_composition.py`: CLI for Milestone 3A/3B/3C/3D composition checks
- `scripts/run_patch_recompute.py`: CLI for Milestone 4A oracle patch diagnostics
- `scripts/run_patch_granularity.py`: CLI for Milestone 4B granularity ablations
- `scripts/run_doc_selector.py`: CLI for Milestone 5A document selector and gate runs
- `scripts/run_doc_selector_stress.py`: CLI for Milestone 5B selector validity stress tests
- `scripts/run_answer_eval.py`: CLI for Milestone 6A answer-level behavior evaluation

## Prompt Format

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

## Setup

```bash
python -m pip install -r requirements.txt
```

## Build Diagnostic Data

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

## Run Tests

```bash
python -m pytest
```

## Run Full Prefill Smoke

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

## Run Naive Composition Smoke

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

## Run Oracle Patch Diagnostics

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

## Run Patch Granularity Ablations

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

## Run Document Selector And Gate Ablations

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

## Run Document Selector Stress Tests

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

## Run Answer-Level Evaluation

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

## Current Scope Boundary

The following are intentionally deferred:

- risk-guided recompute selectors
- final SAFE-KV method selection
- full plotting and paper tables

Those belong to later milestones after the oracle patch upper bound is validated.
