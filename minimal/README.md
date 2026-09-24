# SAFE-KV in one file

`safekv_minimal.py` is a compact reference implementation of the SAFE-KV protocol for any Hugging Face decoder-only
model with a standard `DynamicCache` (tested with the Qwen2 family); it needs only `torch` and `transformers`.

| Step | Function |
|---|---|
| Full prefill: the reference cache, one causal pass | `SafeKV.full_prefill` |
| Prefix-conditioned composition: each document encoded after the static prefix alone, at its target position | `SafeKV.compose` |
| Causal suffix repair (actual forwarding) or document-only repair from a start document | `SafeKV.repair(..., mode="suffix" \| "document")` |
| The contract: re-encode the query, decode greedily, compare normalized answers with full prefill | `SafeKV.answer`, `normalize_answer` |
| Start selection: query selector (built in), risk selector (imported from `code/safekv/doc_selector.py`) | `query_scores`, `risk_scores`, `select_start` |

```bash
python minimal/safekv_minimal.py                                            # built-in example
python minimal/safekv_minimal.py --jsonl data/external_hotpotqa_500.jsonl --limit 50 --selector risk --k 2
python -m pytest -q minimal                                                  # CPU tests, tiny random model, no download
```

The tests check that suffix repair from the first document reproduces full prefill, that composition changes every
state after the first document while document-only repair leaves later slices stale, that cached and uncached greedy
decoding agree, and that the selectors reproduce the repaired-suffix lengths of all 4,000 K1/K2 selections in the
paper's main runs.

The paper's numbers were produced by `code/scripts/run_answer_eval.py`, which tokenizes the rendered prompt in one pass
and maps segments through character offsets. This file tokenizes the prefix, each document and the query separately
(so segment boundaries are exact), which can change a few boundary tokens; expect close but not identical numbers.
