# ARR Submission Checklist

- [x] ACL review style is used: `\usepackage[review]{acl}`.
- [x] Anonymous author field is used.
- [x] Abstract is under 200 words and avoids nonessential markup.
- [x] Main content before Limitations resolves to 8 pages.
- [x] Limitations appears after Discussion and before References, beginning at the top of page 9 without a page-break command.
- [x] Limitations contains no new tables, figures, methods, or experimental results.
- [x] PDF compiles with two clean `pdflatex -interaction=nonstopmode main.tex` passes.
- [x] Unresolved citations: 0.
- [x] Undefined references: 0.
- [x] Overfull boxes: 0.
- [x] Verified references with URL fields: 87.
- [x] Citation placeholder markers: 0.
- [x] Figure 1 appears early and explains the setup.
- [x] Main figures are real PDF assets.
- [x] Main tables are compact, centered, and captioned with takeaways.
- [x] Appendix includes datasets, prompts/tokenization, cache sanity checks, algorithms, full tables, robustness/calibration checks, selector analysis, design ledger, result inventory, restored compact diagnostics, external sanity, held-out calibration, cost accounting, failure examples, related-work comparison, and artifact checklist.
- [x] Claim boundaries avoid production speedups, universal selector dominance, SOTA QA, Qwen7B evidence, and serving-system replacement.
- [x] PDF metadata does not expose author identity.
- [x] Extracted PDF text scan found no local paths, host identifiers, GitHub username, email, or acknowledgments.
- [x] ACL pubcheck completed. Review PDF reports expected line-number margin errors; layout-only `main_pubcheck.pdf` passes `All Clear!`.

## Remaining Pre-Submission Actions

1. Recompile after any official template update and verify `page:mainend` remains page 8.
2. For final submission, run pubcheck on the exact submission PDF mode required by ARR/ACL.
3. Human spot-check references for preferred venue metadata formatting.
