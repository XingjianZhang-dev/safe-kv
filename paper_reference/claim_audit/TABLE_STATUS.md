# Table Status

## Main Tables

1. `tables/table1_external_7b_main.tex` — main external 7B-scale composition result; centered and compact.
2. `tables/table2_local_vs_suffix.tex` — repair granularity and causal-frontier evidence; header clarifies patched-token ratios and changed-wrong counts.
3. `tables/table3_position_sensitivity.tex` — lost-in-the-middle style position sensitivity; compact table supporting Figure 2.

All main tables use centered cells, `\footnotesize`, and `adjustbox` max-width fitting. Captions state the key interpretation rather than only describing columns. Selector, robustness/calibration, budget, and cross-model detail tables were moved to the appendix to keep the main content within the 8-page ARR/ACL long-paper budget.

## Appendix Tables

Appendix tables contain full composition ablations, repair granularity results, answer-level synthetic/external results, robustness/calibration checks, selector/budget analysis, held-out calibration, cost accounting, the design ledger, result inventory, restored compact diagnostic tables, and related-work positioning. They also use centered cells and `\footnotesize`.

## Remaining Table Risks

No table currently overflows or triggers overfull boxes. The main tables are compact but readable. If final template changes alter float placement, move secondary table detail to appendix rather than shrinking fonts further.
