# Figures

The camera-ready figures, byte-identical to the ones in the paper. `scripts/camera_ready/make_figures.py` writes the
plotted values of every data figure to `<name>.data.csv` (with the source result file and the NUMBERS id of each value)
and then calls `scripts/camera_ready/draw_figures.py`, which draws the PDFs from those CSVs alone, at the physical size
used in the paper, with TrueType fonts and no text below 7.5 pt.

| Paper figure | PDF | Plotted values |
|---|---|---|
| Figure 1 (Section 1, causal-state schematic) | `figure1_setup.pdf` | none (conceptual) |
| Figure 2 (Section 6.2, local vs suffix repair, 2Wiki-100) | `figure_local_vs_suffix.pdf` | `figure_local_vs_suffix.data.csv` |
| Figure 3 (Section 6.3, position sweep) | `figure_position_sweep.pdf` | `figure_position_sweep.data.csv` |
| Figure 4 (Appendix H, robustness checks) | `figure5_external_sanity.pdf` | `figure5_external_sanity.data.csv` |
| Figure 5 (Appendix K, quality-budget points and L40S latency) | `figure4_budget_gate_pareto.pdf` | `figure4_budget_gate_pareto.data.csv` |

File names predate the final figure order and are kept because the paper cites them.

Review-time material kept for comparison: `submitted_figure1_setup.pdf` and `submitted_figure5_external_sanity.pdf`
(the review-time drawings of Figures 1 and 4), `figure2_category_drift.pdf` + `figure2_category_drift.csv` (the
review-time bar chart of the main external result, removed from the camera-ready because it duplicated Table 1),
`figure3_repair_granularity.pdf` (the review-time two-panel mechanism figure, now split into Figures 2 and 3),
`figure3_patch_granularity.csv`, `figure4_budget_gate_pareto.csv`, `figure4_heldout_gate_calibration.csv` and the
`fig*.tex` placeholders from the review-time build.
