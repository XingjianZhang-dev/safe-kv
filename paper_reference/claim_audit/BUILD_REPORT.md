# Build Report

## Compile Status

The 8G draft compiles with:

```bash
cd SAFE_KV__Semantic_State_Reuse_and_Document_Level_Repair_for_Non_Prefix_KV_Caches_in_RAG
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Output PDF: `SAFE_KV__Semantic_State_Reuse_and_Document_Level_Repair_for_Non_Prefix_KV_Caches_in_RAG/main.pdf`

## Page Segments

- Total PDF pages: 26.
- Main-content pages before Limitations: 8 (`page:mainend` resolves to page 8).
- Limitations placement: after Discussion/Conclusion and before References.
- Limitations starts at the top of page 9 without a manual page break.
- References start: page 9.
- Appendix starts: page 13.
- Appendix pages: approximately pages 13--26.
- Main content exceeds 8 pages: no.

## Build Warnings

- Unresolved citations: 0.
- Undefined references: 0.
- Overfull boxes: 0.
- Missing figures: 0.
- Citation placeholder markers in paper TeX/BibTeX: 0.

## References

- Verified references in `references.bib`: 87.
- Entries with URL fields: 87.
- Remaining uncertain citations: 0.
- Second-pass online URL failures: 0.

## Pubcheck

`aclpubcheck` was installed in the current environment for the second-pass audit. Running it directly on the review-mode `main.pdf` reports margin errors caused by ACL review line numbers. A layout-only PDF generated from the same source without `[review]` mode (`main_pubcheck.pdf`) passes:

```text
All Clear!
```

See `paper_reference/claim_audit/PUBCHECK_REPORT.md`.

## Tests

This pass was a paper-writing and audit pass; project code tests were not rerun. The previous project test snapshot was:

```text
106 passed, 1 skipped
```

## Typography Pass

All generated LaTeX tables use centered cells and `\footnotesize`. Tables are wrapped in `adjustbox` with `max width` so they can shrink if necessary but are never scaled up. Main table headers were clarified while secondary selector, robustness/calibration, budget, and design-ledger material was moved to the appendix to preserve the 8-page main-content target.

The current abstract is 137 words under a conservative script count and contains no emphasis or other semantic markup.
PDF page size checked with PyMuPDF: first and last pages are 595.276 x 841.890 pt (A4).
