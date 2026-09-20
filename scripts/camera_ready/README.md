# Camera-ready table/figure generators

Run from the repository root, e.g. `python -B scripts/camera_ready/build_tables.py`. They read only files inside this
repository (`results/`, `results_rebuttal/`, `results_august/`, `data/`) and write LaTeX tables to
`paper_reference/camera_ready_tables/` and the five paper figures plus the plotted-value CSV of each data figure to `paper_reference/final_figures/`
(`make_figures.py`; the schematic Figure 1 has no data).
`tie_break_audit.py` imports the shipped `code/safekv` package unchanged. Requires Python >= 3.10, matplotlib (figure only).
