# Camera-ready table/figure generators

Run from the repository root, e.g. `python -B scripts/camera_ready/build_tables.py`. They read only files inside this
repository (`results/`, `results_rebuttal/`, `results_august/`, `data/`).

| Script | Writes |
|---|---|
| `build_tables.py` | the 11 generated LaTeX tables in `paper_reference/camera_ready_tables/` (+ `generated_numbers.json`) |
| `tie_break_audit.py` | Table 24, `paper_reference/camera_ready_tables/appendix_tie_break.tex` (+ `tie_break_audit.json`); imports the shipped `code/safekv` package unchanged |
| `make_figures.py` | the plotted-value CSVs of Figures 2–5 in `paper_reference/final_figures/`, then calls `draw_figures.py` (`--csv-only` skips drawing) |
| `draw_figures.py` | the five figure PDFs, drawn from the CSVs only (`python -B scripts/camera_ready/draw_figures.py [OUTPUT_DIR]`) |

Requires Python >= 3.10; matplotlib for drawing only. Tables and CSVs are byte-identical to the shipped files. The
shipped PDFs are the paper's files: redrawing reproduces their bytes with matplotlib 3.10 and Liberation Serif, and
visually identical PDFs with other matplotlib versions or Times-like fonts.
