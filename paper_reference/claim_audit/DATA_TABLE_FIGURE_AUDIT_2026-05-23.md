# Data, Table, and Figure Audit (2026-05-23)

## Scope

Audited the current manuscript tables and figures against the source result files under `results/`.

## New Incremental Run

- Added the missing HotpotQA-500 Hybrid K1 run with:
  - command: `python -u code/scripts/run_answer_eval.py --config configs/acl_qwen25_7b_hotpotqa_500.yaml --results-dir results/acl_qwen25_7b_hotpotqa_suffix_main_500 --methods hybrid_query_risk_union_suffix_k1 --resume`
  - log: `results/acl_qwen25_7b_hotpotqa_suffix_main_500/hybrid_k1_incremental_2026-05-23.log`
  - examples: 500/500
  - failed rows: 0
  - answer equivalence: 0.996
  - Gold EM/F1: 0.542 / 0.708
  - changed-and-gold-wrong: 2
  - patch ratio: 0.904

## Main External 7B Consistency

- `tables/table1_external_7b_main.tex` now includes HotpotQA-500 Hybrid suffix K1.
- `tables/appendix_full_external_sanity.tex` mirrors the full external table and now includes the same HotpotQA-500 Hybrid suffix K1 row.
- The HotpotQA Query suffix K1 Gold EM was corrected from 0.528 to the source value 0.522.
- `figures/figure2_category_drift.pdf` was regenerated from `answer_eval_summary.json` and now includes Hybrid K1 bars for both HotpotQA-500 and 2Wiki-500.

## Questioned Figure Points

- Figure 5 prefix at the far lower-left is correct:
  - x-axis patch ratio = 0.000 for prefix composition
  - y-axis 2Wiki answer equivalence = 0.378
- Figure 4 low prefix values are correct:
  - HotpotQA full-prefill-correct subset prefix equivalence = 0.566
  - 2Wiki full-prefill-correct subset prefix equivalence = 0.518
  - Mistral-7B noisy prefix equivalence = 0.312

## Audit Result

- Rechecked main external rows, exact-correct subset values, selector/budget values, noise closure values, and the questioned figure coordinates.
- No remaining numeric mismatch found in the checked values after the HotpotQA Hybrid K1 addition and the Hotpot Query K1 Gold EM correction.
