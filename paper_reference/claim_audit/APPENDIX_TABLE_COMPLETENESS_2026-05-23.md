# Appendix Table Completeness Audit

This pass checked the appendix tables shown in the review PDF for placeholder values.
The missing-looking cells were not caused by unrun experiments; the underlying results
were already present in the result tree. The paper tables were updated to expose those
values directly.

## Filled Values

- Table 7 exact-correct subset patch ratios:
  - HotpotQA exact-correct risk suffix K2: 0.949.
  - 2Wiki exact-correct risk suffix K2: 0.921.
  - Source: `results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_metrics.csv`
    and `results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_metrics.csv`,
    restricted to examples where `full_prefill` has `gold_exact_match=True`.
- Table 8 full-prefill patch ratios:
  - Full prefill patch ratio is now reported as 0.000 rather than a dash.
  - Source: full-prefill rows in the same answer-eval summaries.
- Table 9 robustness/calibration details:
  - Bootstrap rows now include patch deltas.
  - Latency rows now report sample sizes rather than blank changed-wrong cells.
  - Sources: bootstrap summaries, answer-eval summaries, and latency summaries.
- Table 11 latency table:
  - Median TTFT, p95 TTFT, average peak CUDA memory, and full-prefill patch ratios
    are now filled for every latency method.
  - Sources: `results/acl_qwen25_7b_2wiki_latency_suffix_50_with_hybrid/latency_summary.json`
    and `results/acl_qwen25_7b_noise64_latency_suffix_20_with_hybrid/latency_summary.json`.
- Table 12 closure table:
  - Noise16 all-document sanity now reports Gold EM 0.904 and changed-wrong count 1.
  - Source: `results/acl_qwen25_7b_noise16_closure_250/answer_eval_summary.json`.

## Verification

- Review PDF rebuilt: `main.pdf`.
- Layout-only pubcheck rebuilt: `main_pubcheck.pdf`.
- `aclpubcheck --paper_type long main_pubcheck.pdf`: All Clear.
- Grep over paper table sources finds no remaining placeholder `--` cells.
