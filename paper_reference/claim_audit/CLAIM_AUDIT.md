# Claim Audit

## Strongly Supported

- Non-prefix KV cache composition can cause answer-level drift. Evidence: `paper/tables/table3_answer_level_summary.tex`, `paper/tables/table4_cross_model_and_external_summary.tex`.
- Prefix-conditioned composition is much stronger than doc-only or prefix-plus-unconditioned composition. Evidence: `paper/tables/table1_composition_ablation.tex`.
- Residual drift is structured and concentrated in conflict, multi-hop, and noisy retrieval settings. Evidence: `paper/figures/figure2_category_drift.csv`.
- Span/window/suffix repair is unreliable as the primary repair unit. Evidence: `paper/tables/table2_repair_granularity.tex`.
- Document-level repair is the most coherent repair unit observed. Evidence: `paper/tables/table2_repair_granularity.tex`, `paper/tables/table3_answer_level_summary.tex`.
- First-token KL is a useful diagnostic risk signal, but not a guarantee. Evidence: 6A/6B answer-level reports and category drift data.
- Qwen2.5-0.5B, Qwen2.5-1.5B, and SmolLM2 show directionally consistent drift and repair. Evidence: `paper/tables/table4_cross_model_and_external_summary.tex`.

## Supported With Caveat

- Semantic document selectors help under controlled noisy diagnostics, especially query/entity K2, but they do not universally beat random K2.
- Budgeted gates provide a quality-budget analysis, but 10% budgets are brittle and external transfer is mixed.
- External HotpotQA/2Wiki confirms drift is not synthetic-only, but it is a sanity check rather than a benchmark claim.

## Unsupported / Do Not Claim

- Universal semantic selector dominance.
- SAFE-KV improves measured TTFT, throughput, or production serving latency.
- Production serving latency, TTFT, throughput, or memory-system improvements.
- SAFE-KV as a replacement for vLLM, LMCache, CacheBlend, or KVLink.
- Span-level recomputation as the final effective method.
- SOTA QA performance on HotpotQA or 2Wiki.
- Qwen7B evidence.

## Future Work

- Better natural-data retrieval calibration.
- Learned or more robust gate calibration.
- Integration into serving systems with measured latency.
- Larger model and production workload evaluation.
