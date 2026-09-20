# Pubcheck Report

## Installation

`aclpubcheck` was installed into the project virtual environment with:

```bash
python -m pip install 'git+https://github.com/acl-org/aclpubcheck'
```

Installed commit reported by pip: `19de736f3ff4d6f766bb65bd9a7bef54ea28df6f`.

Polish-pass note: `aclpubcheck` was rerun on 2026-05-23 after the abstract/page-flow/result-inventory/prose revision.

## Review PDF Check

Command:

```bash
cd SAFE_KV__Semantic_State_Reuse_and_Document_Level_Repair_for_Non_Prefix_KV_Caches_in_RAG
aclpubcheck --paper_type long main.pdf > aclpubcheck_review_second_pass.log 2>&1
```

Result:

```text
We detected 1815 errors and 0 warnings in your paper.
```

Interpretation: these are expected margin errors from ACL review-mode line numbers and bottom page marks. The review PDF uses `\usepackage[review]{acl}`, which intentionally places line numbers in the margins. This makes the review PDF unsuitable for a strict margin-only pubcheck run.

## Layout Pubcheck PDF

To check the actual paper layout without review-mode line numbers, I compiled the same source with `\SAFEKVPUBCHECK` defined, which selects the non-review ACL style branch in `main.tex`.

Then I compiled and checked:

```bash
cd SAFE_KV__Semantic_State_Reuse_and_Document_Level_Repair_for_Non_Prefix_KV_Caches_in_RAG
pdflatex -jobname=main_pubcheck -interaction=nonstopmode '\def\SAFEKVPUBCHECK{1}\input{main.tex}'
bibtex main_pubcheck
pdflatex -jobname=main_pubcheck -interaction=nonstopmode '\def\SAFEKVPUBCHECK{1}\input{main.tex}'
pdflatex -jobname=main_pubcheck -interaction=nonstopmode '\def\SAFEKVPUBCHECK{1}\input{main.tex}'
aclpubcheck --paper_type long main_pubcheck.pdf > aclpubcheck_polish_pass.log 2>&1
```

Result:

```text
All Clear!
```

## Manual Checks

- Total PDF pages: 26.
- Main content before Limitations: 8 pages.
- Limitations correctly placed after Discussion and before References, starting at the top of page 9.
- References start on page 9.
- Appendix starts on page 13.
- Unresolved citations: 0.
- Undefined references: 0.
- Overfull boxes: 0.

Conclusion: the review-mode PDF is still the intended anonymous review draft; the non-review layout PDF passes ACL pubcheck.
