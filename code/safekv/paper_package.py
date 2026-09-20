"""Build the SAFE-KV paper drafting package from existing result files."""

from __future__ import annotations

import csv
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

from safekv.paper_analysis import mean, read_csv_rows, truthy, write_csv_rows


SAFE_KV_TITLE = (
    "SAFE-KV: Semantics-Aware Safety Analysis and Document-Level Repair for "
    "Non-Prefix KV Cache Reuse in RAG"
)

REQUIRED_RESULT_FILES = [
    "results_paper/table1_composition_ablation.csv",
    "results_paper/table2_repair_granularity.csv",
    "results_paper/table3_answer_level_synthetic.csv",
    "results_paper/table4_answer_level_external.csv",
    "results_paper/table5_external_full_prefill_correct_subset.csv",
    "results_paper/table6_budget_gate_pareto.csv",
    "results_paper/table7_cost_accounting.csv",
    "results_paper/heldout_gate_calibration_metrics.csv",
    "results_qwen05_100/patch_recompute_metrics.csv",
    "results_qwen05_100_answer/answer_eval_metrics.csv",
    "results_qwen05_100_noisy_answer/answer_eval_metrics.csv",
    "results_qwen15_100_answer/answer_eval_metrics.csv",
    "results_qwen15_100_noisy_answer/answer_eval_metrics.csv",
    "results_qwen05_external_answer/answer_eval_metrics.csv",
    "results_qwen15_external_answer/answer_eval_metrics.csv",
    "results_smollm17_noisy_answer/answer_eval_metrics.csv",
    "results_smollm17_external_answer/answer_eval_metrics.csv",
]

ANSWER_METHODS = [
    "full_prefill",
    "prefix_conditioned_naive_global",
    "oracle_evidence_doc_patch",
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_k2",
    "safe_gate_t0.45",
    "safe_gate_t0.60",
    "random_doc_patch_k2_seeded",
]

CORE_METHODS = [
    "prefix_conditioned_naive_global",
    "oracle_evidence_doc_patch",
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_k2",
    "safe_gate_t0.60",
    "random_doc_patch_k2_seeded",
]

METHOD_LABELS = {
    "full_prefill": "Full prefill",
    "doc_only_naive_global": "Doc-only global",
    "prefix_plus_naive_global": "Prefix-plus global",
    "prefix_conditioned_naive_global": "Prefix-conditioned",
    "prefix_conditioned_naive_local": "Prefix-conditioned local",
    "oracle_evidence_doc_patch": "Oracle doc patch",
    "oracle_evidence_span_patch": "Oracle span patch",
    "oracle_evidence_span_window_0": "Evidence span",
    "oracle_evidence_span_window_16": "Evidence span +16",
    "oracle_support_and_conflict_suffix_patch": "Support+conflict suffix",
    "random_patch_same_budget::oracle_support_and_conflict_suffix_patch": "Matched random suffix",
    "full_doc_cache_patch_sanity": "Full-doc sanity",
    "query_similarity_doc_patch_k2": "Query K2",
    "entity_overlap_doc_patch_k2": "Entity K2",
    "risk_guided_doc_patch_k2": "Risk K2",
    "safe_gate_t0.45": "Gate .45",
    "safe_gate_t0.60": "Gate .60",
    "random_doc_patch_k2_seeded": "Random K2",
}


def latex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def fmt(value: Any, digits: int = 3) -> str:
    try:
        number = float(value)
    except Exception:
        return str(value)
    if math.isnan(number):
        return ""
    return f"{number:.{digits}f}"


def method_label(method: str) -> str:
    return METHOD_LABELS.get(method, method.replace("_", " "))


Column = tuple[str, str, Callable[[Any], str]]


def render_latex_table(
    *,
    rows: list[dict[str, Any]],
    columns: list[Column],
    caption: str,
    label: str,
    align: str | None = None,
    notes: str | None = None,
) -> str:
    if align is None:
        align = "c" * len(columns)
    else:
        align = "c" * len(columns)
    header = " & ".join(latex_escape(column[1]) for column in columns)
    body = []
    for row in rows:
        cells = []
        for key, _label, formatter in columns:
            cells.append(latex_escape(formatter(row.get(key, ""))))
        body.append(" & ".join(cells) + r" \\")
    note_text = ""
    if notes:
        note_text = "\n\\vspace{0.25em}\n{\\footnotesize " + latex_escape(notes) + "}\n"
    return (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\footnotesize\n"
        "\\begin{adjustbox}{max width=\\textwidth}\n"
        f"\\begin{{tabular}}{{{align}}}\n"
        "\\toprule\n"
        f"{header} \\\\\n"
        "\\midrule\n"
        + "\n".join(body)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{adjustbox}\n"
        f"\\caption{{{latex_escape(caption)}}}\n"
        f"\\label{{{latex_escape(label)}}}"
        f"{note_text}"
        "\\end{table*}\n"
    )


def markdown_table(rows: list[dict[str, Any]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(headers) - 1)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def _write_table_sidecars(
    out_dir: Path,
    stem: str,
    rows: list[dict[str, Any]],
    columns: list[Column],
) -> None:
    headers = [column[1] for column in columns]
    display_rows = []
    for row in rows:
        display_rows.append(
            {
                header: formatter(row.get(key, ""))
                for key, header, formatter in columns
            }
        )
    write_csv_rows(out_dir / "tables" / f"{stem}.csv", display_rows, headers)
    _write_text(out_dir / "tables" / f"{stem}.md", markdown_table(display_rows, headers))


def build_paper_package(results_root: Path, out_dir: Path) -> dict[str, Any]:
    missing = [path for path in REQUIRED_RESULT_FILES if not (results_root / path).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required paper-package inputs:\n" + "\n".join(f"- {item}" for item in missing)
        )

    _ensure_dirs(out_dir)
    _ensure_acl_style_files(out_dir)
    _write_main_tex(out_dir)
    _write_sections(out_dir)
    _write_tables(results_root, out_dir)
    _write_figures(results_root, out_dir)
    _write_appendix(out_dir)
    _write_markdown_docs(results_root, out_dir)
    _write_arr_long_draft(results_root, out_dir)

    return {
        "out_dir": str(out_dir),
        "required_inputs": REQUIRED_RESULT_FILES,
        "non_blocking_gaps": [
            "Replace citation placeholders with exact BibTeX before submission.",
            "Review ACL/ARR style compliance once the final submission template is chosen.",
            "Convert figure data into final camera-ready plots.",
        ],
    }


def _ensure_dirs(out_dir: Path) -> None:
    for rel in ["sections", "tables", "figures", "appendix"]:
        (out_dir / rel).mkdir(parents=True, exist_ok=True)


def _ensure_acl_style_files(out_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for filename in ["acl.sty", "acl_natbib.bst"]:
        source = repo_root / "paper" / filename
        target = out_dir / filename
        if source.exists() and source.resolve() != target.resolve():
            shutil.copyfile(source, target)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _rows(results_root: Path, rel: str) -> list[dict[str, str]]:
    return read_csv_rows(results_root / rel)


def _answer_summary_by_method(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["method"]].append(row)
    out: dict[str, dict[str, Any]] = {}
    for method, group in groups.items():
        out[method] = {
            "answer_equivalence": mean(
                1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0
                for row in group
            ),
            "gold_em": mean(1.0 if truthy(row["gold_exact_match"]) else 0.0 for row in group),
            "gold_f1": mean(float(row["gold_token_f1"]) for row in group),
            "changed": mean(1.0 if truthy(row["answer_changed_from_full"]) else 0.0 for row in group),
            "changed_wrong": sum(1 for row in group if truthy(row["answer_changed_and_gold_wrong"])),
            "patch_ratio": mean(float(row["patched_token_ratio"]) for row in group),
            "kl": mean(float(row["first_token_kl_full_to_method"]) for row in group),
            "top1": mean(1.0 if truthy(row["top1_match"]) else 0.0 for row in group),
        }
    return out


def _answer_summary(results_root: Path, rel: str) -> dict[str, dict[str, Any]]:
    return _answer_summary_by_method(_rows(results_root, rel))


def _aggregate_first_token_rows(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["method"]].append(row)
    out = {}
    for method, group in groups.items():
        out[method] = {
            "method": method,
            "n": len(group),
            "avg_kl": mean(float(row["first_token_kl_full_to_method"]) for row in group),
            "top1": mean(1.0 if truthy(row["top1_match"]) else 0.0 for row in group),
            "top10": mean(float(row.get("top10_overlap", 0.0)) for row in group),
            "patch_ratio": mean(float(row.get("patched_token_ratio", 0.0) or 0.0) for row in group),
        }
    return out


def _write_main_tex(out_dir: Path) -> None:
    _write_text(
        out_dir / "main.tex",
        r"""
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{adjustbox}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{microtype}

\title{SAFE-KV: Semantics-Aware Safety Analysis and Document-Level Repair for Non-Prefix KV Cache Reuse in RAG}
\author{Anonymous Authors}
\date{}

\begin{document}
\maketitle

\input{sections/00_abstract}
\input{sections/01_introduction}
\input{sections/02_related_work}
\input{sections/03_problem_setup}
\input{sections/04_method_and_diagnostics}
\input{sections/05_experiments}
\input{sections/06_results}
\input{sections/07_discussion}
\input{sections/08_limitations}

\clearpage
\input{tables/table1_composition_ablation}
\input{tables/table2_repair_granularity}
\input{tables/table3_answer_level_synthetic}
\input{tables/table4_cross_model_summary}
\input{tables/table5_external_sanity}
\input{tables/table6_budget_gate}
\input{tables/table7_cost_accounting}

\paragraph{Latency scope.}
We report patched-token and recomputation-budget proxies only. SAFE-KV is a semantic safety and repair analysis, not an optimized serving system, and we do not claim measured TTFT or throughput improvements.

\end{document}
""",
    )


def _write_sections(out_dir: Path) -> None:
    sections = {
        "00_abstract.tex": r"""
\begin{abstract}
Retrieval-augmented generation repeatedly places related documents into different prompts, making non-prefix KV cache reuse an attractive optimization target. Exact prefix caching is semantically safe but limited, while non-prefix cache composition can alter model behavior. SAFE-KV studies when such reuse is safe by comparing composed-cache inference against a full-prefill oracle. Across controlled diagnostic data, noisy retrieval variants, three small-to-medium instruction-tuned models, and external HotpotQA/2Wiki sanity data, we find that non-prefix composition can change generated answers, that prefix-conditioned document caches are a much stronger baseline than doc-only reuse, and that residual drift is structured by semantic risk. We further show that span-level repair is unreliable, while document-level repair is a more coherent unit. Finally, we evaluate document repair and gates using patched-token recomputation-budget proxies and matched random controls. SAFE-KV does not claim production serving speedups; it provides a semantic safety analysis and a paper-ready framework for behavior-preserving non-prefix KV reuse.
\end{abstract}
""",
        "01_introduction.tex": r"""
\section{Introduction}

RAG systems repeatedly retrieve and reuse documents across user queries. KV caching can reduce repeated prefill work, but standard prefix caching only applies when prompts share exact prefixes. Non-prefix document cache reuse is tempting because retrieved documents recur even when their prompt position and surrounding context differ.

The central risk is semantic: a composed KV cache may not preserve the behavior of a full-prefill run over the same prompt. Existing serving-oriented work shows that non-prefix cache reuse can be operationally useful, but the conditions under which it preserves generated answers remain underexplored. SAFE-KV asks: when is non-prefix KV reuse safe, and what repair granularity is coherent?

Our contributions are: (1) a semantic safety framework measuring behavior drift between full-prefill and composed-cache RAG inference; (2) controlled clean/noisy diagnostics showing structured drift; (3) a composition and repair analysis showing that prefix-conditioned caching is strong and document-level repair is more coherent than span/window repair; (4) budgeted repair and gating analysis with matched random controls and held-out calibration; and (5) robustness checks across Qwen2.5-0.5B, Qwen2.5-1.5B, SmolLM2-1.7B, and external HotpotQA/2Wiki sanity data.
""",
        "02_related_work.tex": r"""
\section{Related Work}

\paragraph{Prefix caching.}
Prefix caching safely reuses KV states when prompts share an exact prefix. SAFE-KV studies a harder non-prefix setting where RAG documents may recur without occupying the same prefix position.

\paragraph{Efficient LLM serving.}
Systems such as vLLM/PagedAttention and LMCache improve memory management and cache reuse for serving. SAFE-KV is complementary: it studies behavior preservation and repair granularity rather than implementing a production serving stack.

\paragraph{Non-prefix cache reuse.}
CacheBlend and KVLink study non-prefix cache fusion and document-cache reuse mechanisms. SAFE-KV differs by focusing on training-free semantic safety analysis, full-prefill behavior preservation, answer-level drift, and document-level repair/gating under recomputation-budget proxies.

\paragraph{RAG and multi-hop QA evaluation.}
HotpotQA and 2WikiMultihopQA provide natural multi-hop questions. We use them only as external sanity checks because mapping evidence documents and interpreting gold-answer quality introduces additional noise; our main controlled conclusions come from diagnostic clean/noisy settings.
""",
        "03_problem_setup.tex": r"""
\section{Problem Setup}

Given a RAG prompt containing a static instruction/chat prefix, retrieved documents, and a query, the full-prefill oracle computes KV states over the complete prompt in order. A non-prefix composed-cache method instead precomputes or reuses document KV states and composes them into a context cache before decoding the query answer.

We define semantic safety relative to full prefill. A method is safer when its first-token distribution, top prediction, and generated answer match the full-prefill oracle. We measure first-token KL, top-1 agreement, answer equivalence, changed answers, changed-and-gold-wrong answers, and patched-token ratio. Patched-token ratio is a recomputation-budget proxy, not a measured latency quantity.
""",
        "04_method_and_diagnostics.tex": r"""
\section{Method and Diagnostics}

SAFE-KV evaluates several composition variants. The key baseline is prefix-conditioned document composition, where document cache states are encoded under the static prompt/chat prefix before composition. This is stronger than doc-only or prefix-plus-unconditioned variants.

For repair, SAFE-KV compares span/window/suffix recomputation against document-level patching. The central empirical finding is that isolated evidence spans do not reliably close the causal context needed for behavior preservation, while document-level repair is a coherent unit.

The diagnostic data contains single-evidence, multi-hop, conflict, boundary-sensitive, and distractor-heavy categories, plus a noisy retrieval variant. These controlled categories make it possible to attribute drift to semantic risk rather than treating all examples as exchangeable.
""",
        "05_experiments.tex": r"""
\section{Experiments}

We evaluate Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct, and SmolLM2-1.7B-Instruct with deterministic generation and manual position-id cache decoding. Experiments compare full prefill, prefix-conditioned composition, oracle document repair, query/entity document selectors, safe gates, and matched random document controls.

External HotpotQA/2Wiki data is used as a small sanity check. It is not treated as a main benchmark, because full-prefill QA quality and evidence mapping are noisier than in the controlled diagnostic data.
""",
        "06_results.tex": r"""
\section{Results}

The main results are organized around seven tables. Table~\ref{tab:composition} shows that prefix-conditioned composition substantially reduces first-token drift relative to doc-only and prefix-plus composition. Table~\ref{tab:granularity} shows that document repair is more coherent than span/window repair. Table~\ref{tab:synthetic} shows answer-level drift and repair on clean/noisy diagnostics. Tables~\ref{tab:crossmodel} and~\ref{tab:external} show cross-model and external sanity results. Table~\ref{tab:budget} summarizes budgeted gates and matched random controls, while Table~\ref{tab:cost} reports recomputation-budget proxy accounting.
""",
        "07_discussion.tex": r"""
\section{Discussion}

The evidence supports a safety-analysis framing rather than a universal selector-dominance claim. Semantic selectors are useful in controlled noisy diagnostics, but external data remains mixed and random K2 is a strong baseline. Budgeted gates are best viewed as calibrated quality-budget tools: they are useful in controlled settings and informative under held-out calibration, but fixed thresholds are not portable.
""",
        "08_limitations.tex": r"""
\section{Limitations}

SAFE-KV does not report measured production serving latency, TTFT, or throughput. Patched-token ratio and estimated prefill saving are recomputation-budget proxies only. External HotpotQA/2Wiki mapping is noisy, and full-prefill generations can be gold-wrong, so external gold EM/F1 are secondary. We evaluate small-to-medium instruction-tuned models and do not claim Qwen7B evidence. We do not integrate with vLLM, LMCache, CacheBlend, or KVLink, and we do not train or fine-tune models. Finally, we do not claim universal semantic selector or gate dominance over matched random controls.
""",
    }
    for name, text in sections.items():
        _write_text(out_dir / "sections" / name, text)


def _write_tables(results_root: Path, out_dir: Path) -> None:
    _write_table1(results_root, out_dir)
    _write_table2(results_root, out_dir)
    _write_table3(results_root, out_dir)
    _write_table4(results_root, out_dir)
    _write_table5(results_root, out_dir)
    _write_table6(results_root, out_dir)
    _write_table7(results_root, out_dir)


def _write_table1(results_root: Path, out_dir: Path) -> None:
    rows = _rows(results_root, "results_paper/table1_composition_ablation.csv")
    wanted = ["doc_only_naive_global", "prefix_plus_naive_global", "prefix_conditioned_naive_global"]
    rows = [{**row, "label": method_label(row["method"])} for row in rows if row["method"] in wanted]
    columns = [
        ("label", "Method", str),
        ("avg_kl", "KL", lambda x: fmt(x, 3)),
        ("top1", "Top-1", lambda x: fmt(x, 2)),
        ("top10", "Top-10", lambda x: fmt(x, 2)),
        ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table1_composition_ablation.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Composition ablation on the clean diagnostic set. Prefix-conditioned composition is the strongest non-repair baseline.",
            label="tab:composition",
        ),
    )
    _write_table_sidecars(out_dir, "table1_composition_ablation", rows, columns)


def _write_table2(results_root: Path, out_dir: Path) -> None:
    table1 = {row["method"]: row for row in _rows(results_root, "results_paper/table1_composition_ablation.csv")}
    granularity = {row["method"]: row for row in _rows(results_root, "results_paper/table2_repair_granularity.csv")}
    patch_recompute = _aggregate_first_token_rows(_rows(results_root, "results_qwen05_100/patch_recompute_metrics.csv"))
    ordered = []
    base = table1["prefix_conditioned_naive_global"]
    ordered.append({"method": "prefix_conditioned_naive_global", **base})
    for method in [
        "oracle_evidence_span_patch",
        "oracle_evidence_span_window_16",
        "oracle_support_and_conflict_suffix_patch",
        "random_patch_same_budget::oracle_support_and_conflict_suffix_patch",
        "oracle_evidence_doc_patch",
        "full_doc_cache_patch_sanity",
    ]:
        source = patch_recompute.get(method) or granularity.get(method)
        if source:
            ordered.append({"method": method, **source})
    rows = [{**row, "label": method_label(row["method"])} for row in ordered]
    columns = [
        ("label", "Repair unit", str),
        ("avg_kl", "KL", lambda x: fmt(x, 3)),
        ("top1", "Top-1", lambda x: fmt(x, 2)),
        ("top10", "Top-10", lambda x: fmt(x, 2)),
        ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table2_repair_granularity.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Repair granularity comparison. Document-level repair is the coherent unit; span and suffix repairs are weaker and often close to matched random baselines.",
            label="tab:granularity",
        ),
    )
    _write_table_sidecars(out_dir, "table2_repair_granularity", rows, columns)


def _write_table3(results_root: Path, out_dir: Path) -> None:
    runs = [
        ("Qwen0.5B", "clean", "results_qwen05_100_answer/answer_eval_metrics.csv"),
        ("Qwen0.5B", "noisy", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "clean", "results_qwen15_100_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "noisy", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
    ]
    rows = []
    for model, split, rel in runs:
        summary = _answer_summary(results_root, rel)
        for method in ANSWER_METHODS:
            if method in summary:
                rows.append({"model": model, "split": split, "method": method_label(method), **summary[method]})
    columns = [
        ("model", "Model", str),
        ("split", "Split", str),
        ("method", "Method", str),
        ("answer_equivalence", "AnsEq", lambda x: fmt(x, 2)),
        ("gold_em", "EM", lambda x: fmt(x, 2)),
        ("gold_f1", "F1", lambda x: fmt(x, 2)),
        ("changed_wrong", "ChgWrong", str),
        ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
        ("kl", "KL", lambda x: fmt(x, 3)),
    ]
    _write_text(
        out_dir / "tables/table3_answer_level_synthetic.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Answer-level clean/noisy diagnostic results for Qwen models.",
            label="tab:synthetic",
        ),
    )
    _write_table_sidecars(out_dir, "table3_answer_level_synthetic", rows, columns)


def _write_table4(results_root: Path, out_dir: Path) -> None:
    runs = [
        ("Qwen0.5B noisy", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B noisy", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
        ("SmolLM2 noisy", "results_smollm17_noisy_answer/answer_eval_metrics.csv"),
    ]
    rows = []
    for label, rel in runs:
        summary = _answer_summary(results_root, rel)
        rows.append(
            {
                "model": label,
                "base": summary["prefix_conditioned_naive_global"]["answer_equivalence"],
                "oracle": summary["oracle_evidence_doc_patch"]["answer_equivalence"],
                "query": summary["query_similarity_doc_patch_k2"]["answer_equivalence"],
                "entity": summary["entity_overlap_doc_patch_k2"]["answer_equivalence"],
                "safe": summary["safe_gate_t0.60"]["answer_equivalence"],
                "random": summary["random_doc_patch_k2_seeded"]["answer_equivalence"],
            }
        )
    columns = [
        ("model", "Run", str),
        ("base", "Base", lambda x: fmt(x, 2)),
        ("oracle", "Oracle doc", lambda x: fmt(x, 2)),
        ("query", "Query K2", lambda x: fmt(x, 2)),
        ("entity", "Entity K2", lambda x: fmt(x, 2)),
        ("safe", "Gate 0.60", lambda x: fmt(x, 2)),
        ("random", "Random K2", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table4_cross_model_summary.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Cross-model noisy diagnostic answer equivalence. Drift and document repair transfer beyond the Qwen family.",
            label="tab:crossmodel",
        ),
    )
    _write_table_sidecars(out_dir, "table4_cross_model_summary", rows, columns)


def _write_table5(results_root: Path, out_dir: Path) -> None:
    runs = [
        ("Qwen0.5B", "results_qwen05_external_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "results_qwen15_external_answer/answer_eval_metrics.csv"),
        ("SmolLM2", "results_smollm17_external_answer/answer_eval_metrics.csv"),
    ]
    rows = []
    for label, rel in runs:
        summary = _answer_summary(results_root, rel)
        rows.append(
            {
                "model": label,
                "full_em": summary["full_prefill"]["gold_em"],
                "full_f1": summary["full_prefill"]["gold_f1"],
                "base": summary["prefix_conditioned_naive_global"]["answer_equivalence"],
                "oracle": summary["oracle_evidence_doc_patch"]["answer_equivalence"],
                "query": summary["query_similarity_doc_patch_k2"]["answer_equivalence"],
                "entity": summary["entity_overlap_doc_patch_k2"]["answer_equivalence"],
                "safe": summary["safe_gate_t0.60"]["answer_equivalence"],
                "random": summary["random_doc_patch_k2_seeded"]["answer_equivalence"],
            }
        )
    columns = [
        ("model", "Model", str),
        ("full_em", "Full EM", lambda x: fmt(x, 2)),
        ("full_f1", "Full F1", lambda x: fmt(x, 2)),
        ("base", "Base", lambda x: fmt(x, 2)),
        ("oracle", "Oracle", lambda x: fmt(x, 2)),
        ("query", "Query", lambda x: fmt(x, 2)),
        ("entity", "Entity", lambda x: fmt(x, 2)),
        ("safe", "Gate", lambda x: fmt(x, 2)),
        ("random", "Random", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table5_external_sanity.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="External HotpotQA/2Wiki sanity results. External data confirms answer drift and partial repair, but random K2 remains competitive.",
            label="tab:external",
        ),
    )
    _write_table_sidecars(out_dir, "table5_external_sanity", rows, columns)


def _write_table6(results_root: Path, out_dir: Path) -> None:
    rows = _rows(results_root, "results_paper/table6_budget_gate_pareto.csv")
    columns = [
        ("run", "Run", str),
        ("target_budget", "Target", lambda x: fmt(x, 2)),
        ("actual_budget", "Actual", lambda x: fmt(x, 2)),
        ("answer_equivalence", "AnsEq", lambda x: fmt(x, 2)),
        ("random_mean", "RandMean", lambda x: fmt(x, 2)),
        ("percentile_vs_random", "Pct", lambda x: fmt(x, 2)),
        ("changed_wrong", "ChgWrong", str),
    ]
    _write_text(
        out_dir / "tables/table6_budget_gate.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Budget-gate Pareto results against matched random gates. Held-out calibration is summarized in the paper package notes.",
            label="tab:budget",
        ),
    )
    _write_table_sidecars(out_dir, "table6_budget_gate", rows, columns)


def _write_table7(results_root: Path, out_dir: Path) -> None:
    rows = _rows(results_root, "results_paper/table7_cost_accounting.csv")
    wanted_methods = {"prefix_conditioned_naive_global", "oracle_evidence_doc_patch", "safe_gate_t0.60", "random_doc_patch_k2_seeded"}
    wanted_datasets = {"diagnostic_noisy", "external_multihop"}
    curated = [
        {**row, "method_label": method_label(row["method"])}
        for row in rows
        if row["method"] in wanted_methods and row["dataset"] in wanted_datasets
    ]
    columns = [
        ("model", "Model", str),
        ("dataset", "Dataset", str),
        ("method_label", "Method", str),
        ("answer_equivalence_to_full_prefill", "AnsEq", lambda x: fmt(x, 2)),
        ("changed_wrong_rate", "Wrong", lambda x: fmt(x, 2)),
        ("patched_token_ratio", "Patch", lambda x: fmt(x, 2)),
        ("estimated_prefill_saving", "Est. saving", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table7_cost_accounting.tex",
        render_latex_table(
            rows=curated,
            columns=columns,
            caption="Cost accounting with recomputation-budget proxies. These are not measured serving-latency results.",
            label="tab:cost",
        ),
    )
    _write_table_sidecars(out_dir, "table7_cost_accounting", curated, columns)


def _write_figures(results_root: Path, out_dir: Path) -> None:
    figures_dir = out_dir / "figures"
    _write_text(
        figures_dir / "README.md",
        """# SAFE-KV Figure Plan

Figure 1: conceptual problem setup showing full prefill, non-prefix composition, prefix-conditioned document cache, and document-level repair/gating.

Figure 2: category-level drift from `figure2_category_drift.csv`; x-axis category, y-axis answer mismatch or first-token KL.

Figure 3: patch granularity from `figure3_patch_granularity.csv`; x-axis patch unit, y-axis KL or top-1, marker size/color for patched-token ratio.

Figure 4: budget gate Pareto from `figure4_budget_gate_pareto.csv`; x-axis actual patched-token ratio, y-axis answer equivalence, with matched random controls.
""",
    )
    write_csv_rows(figures_dir / "figure2_category_drift.csv", _category_drift_rows(results_root), [
        "model", "split", "category", "method", "answer_equivalence", "changed_rate", "changed_wrong_rate", "avg_kl"
    ])
    shutil.copyfile(
        results_root / "results_paper/table2_repair_granularity.csv",
        figures_dir / "figure3_patch_granularity.csv",
    )
    shutil.copyfile(
        results_root / "results_paper/table6_budget_gate_pareto.csv",
        figures_dir / "figure4_budget_gate_pareto.csv",
    )
    shutil.copyfile(
        results_root / "results_paper/heldout_gate_calibration_metrics.csv",
        figures_dir / "figure4_heldout_gate_calibration.csv",
    )


def _category_drift_rows(results_root: Path) -> list[dict[str, Any]]:
    runs = [
        ("qwen05", "clean", "results_qwen05_100_answer/answer_eval_metrics.csv"),
        ("qwen05", "noisy", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
        ("qwen15", "clean", "results_qwen15_100_answer/answer_eval_metrics.csv"),
        ("qwen15", "noisy", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
        ("smollm17", "noisy", "results_smollm17_noisy_answer/answer_eval_metrics.csv"),
    ]
    out = []
    for model, split, rel in runs:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in _rows(results_root, rel):
            if row["method"] == "prefix_conditioned_naive_global":
                grouped[row["category"]].append(row)
        for category, rows in sorted(grouped.items()):
            out.append(
                {
                    "model": model,
                    "split": split,
                    "category": category,
                    "method": "prefix_conditioned_naive_global",
                    "answer_equivalence": mean(1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0 for row in rows),
                    "changed_rate": mean(1.0 if truthy(row["answer_changed_from_full"]) else 0.0 for row in rows),
                    "changed_wrong_rate": mean(1.0 if truthy(row["answer_changed_and_gold_wrong"]) else 0.0 for row in rows),
                    "avg_kl": mean(float(row["first_token_kl_full_to_method"]) for row in rows),
                }
            )
    return out


def _write_appendix(out_dir: Path) -> None:
    appendix = {
        "appendix_outline.md": """# Appendix Outline

1. Dataset construction and diagnostic category details.
2. Prompt/token span alignment and generation sanity checks.
3. Extended composition, repair, selector, and gate tables.
4. External data construction and full-prefill-quality subset analysis.
5. Failure examples illustrating base drift, document repair, and random-control cases.
""",
        "dataset_details.tex": r"""\section{Dataset Details}
The controlled diagnostic set contains single-evidence, multi-hop, conflict, boundary-sensitive, and distractor-heavy examples. The noisy variant injects additional retrieval distractors. External HotpotQA/2Wiki examples are converted into the same document-level schema and used only as sanity checks.
""",
        "implementation_sanity.tex": r"""\section{Implementation Sanity Checks}
Prompt/token span alignment uses one-pass tokenization and offset mapping. Generation uses deterministic greedy decoding with manual position IDs. Full-doc cache patch sanity verifies that replacing all document cache slices recovers full-prefill behavior.
""",
        "extended_tables.tex": r"""\section{Extended Tables}
Full CSV tables are available under \texttt{results\_paper/}. Main paper tables are curated for readability; appendix tables should include local composition variants, all repair windows, external full-prefill-quality subsets, and held-out calibration.
""",
        "failure_examples.tex": r"""\section{Failure Examples}
Failure analysis should include examples where base composition differs from full prefill, examples repaired by document patching, and cases where random K2 beats semantic selectors. Existing source files include \texttt{answer\_failure\_analysis.md} in each result directory.
""",
    }
    for name, text in appendix.items():
        _write_text(out_dir / "appendix" / name, text)


def _write_markdown_docs(results_root: Path, out_dir: Path) -> None:
    _write_text(out_dir / "CLAIM_AUDIT.md", _claim_audit_text())
    _write_text(out_dir / "PAPER_OUTLINE.md", _paper_outline_text())
    _write_text(out_dir / "TABLE_PLAN.md", _table_plan_text())
    _write_text(out_dir / "FIGURE_PLAN.md", _figure_plan_text())
    _write_text(out_dir / "LIMITATIONS_DRAFT.md", _limitations_text())
    _write_text(out_dir / "RELATED_WORK_NOTES.md", _related_work_text())
    _write_text(out_dir / "PACKAGE_SUMMARY.md", _package_summary_text(results_root))


def _claim_audit_text() -> str:
    return """# SAFE-KV Claim Audit

## Strongly Supported

- Non-prefix KV cache composition causes answer-level drift: see Tables 3-5.
- Prefix-conditioned composition is stronger than doc-only composition: see Table 1.
- Residual drift is structured by conflict, multi-hop, noisy retrieval, and boundary cases: see Figure 2 data.
- First-token KL is useful as a diagnostic risk signal, though not a guarantee: see 6A/6B reports and answer-level tables.
- Span/window patching is unreliable as the main repair mechanism: see Table 2.
- Document-level repair is the most coherent repair unit: see Tables 2-5.
- Cross-family SmolLM2 results show the phenomenon is not Qwen-only: see Table 4.
- External HotpotQA/2Wiki sanity confirms drift is not synthetic-only: see Table 5.

## Supported With Caveat

- Semantic document selectors help under controlled noisy diagnostic settings, but they do not universally dominate random K2.
- Budgeted gates provide quality-budget trade-offs, but fixed thresholds are not portable.
- Held-out gate calibration reduces post-hoc selection risk, but external results remain mixed.
- External multi-hop QA supports drift and partial repair, but evidence mapping and full-prefill gold quality are noisy.

## Unsupported / Do Not Claim

- SAFE-KV universally beats random patching.
- SAFE-KV improves measured TTFT, throughput, or production serving latency.
- SAFE-KV replaces vLLM, LMCache, CacheBlend, or KVLink.
- Span-level recomputation is the final successful method.
- SAFE-KV is SOTA on HotpotQA or 2Wiki.
- External natural data proves semantic selector dominance.

## Future Work

- Better external retrieval and evidence calibration.
- More robust gate calibration for natural data.
- Real serving integration and measured latency.
- Larger-model evaluation after the paper core is stable.
"""


def _paper_outline_text() -> str:
    return f"""# Paper Outline

Working title: *{SAFE_KV_TITLE}*

## Abstract
State the semantic safety problem, full-prefill reference, main findings, and no-serving-speedup scope.

## 1. Introduction
Motivate RAG document reuse, limits of prefix caching, risk of non-prefix composition, research question, and five contributions.

## 2. Related Work
Position against prefix caching, vLLM/PagedAttention, LMCache, CacheBlend, KVLink, and RAG/multi-hop QA evaluation.

## 3. Problem Setup
Define full prefill, composed-cache inference, behavior preservation, answer equivalence, KL, and recomputation-budget proxies.

## 4. Method and Diagnostics
Describe prefix-conditioned composition, diagnostic categories, span/document repair units, gates, and random controls.

## 5. Experiments
List models, datasets, generation mode, methods, held-out calibration, and external sanity treatment.

## 6. Results
Walk through Tables 1-7 and Figures 1-4.

## 7. Discussion
Emphasize safety-analysis framing, document repair coherence, selector caveats, and gate calibration limits.

## 8. Limitations
Use `LIMITATIONS_DRAFT.md` as the source.
"""


def _table_plan_text() -> str:
    return """# Table Plan

| table | source | purpose | takeaway |
|---|---|---|---|
| 1 Composition | `results_paper/table1_composition_ablation.csv` | compare naive composition variants | prefix conditioning matters |
| 2 Repair granularity | `results_paper/table2_repair_granularity.csv` plus patch sanity | compare span/window/suffix/doc repair | document repair is coherent |
| 3 Synthetic answer-level | answer-eval CSVs for Qwen clean/noisy | show answer drift and repair | drift reaches generated answers |
| 4 Cross-model | Qwen and SmolLM2 noisy answer outputs | show robustness | not Qwen-family-only |
| 5 External sanity | external answer outputs | sanity check natural data | drift persists; selectors mixed |
| 6 Budget gate | `results_paper/table6_budget_gate_pareto.csv` | gate vs random controls | trade-off, not dominance |
| 7 Cost accounting | `results_paper/table7_cost_accounting.csv` | recomputation-budget proxies | no serving-speedup claim |
"""


def _figure_plan_text() -> str:
    return """# Figure Plan

## Figure 1: Problem Setup
Conceptual diagram of full prefill, non-prefix composition, prefix-conditioned document cache, and document-level repair/gating.

## Figure 2: Category-Level Drift
Use `figures/figure2_category_drift.csv`. Plot category against answer mismatch or KL. Message: drift is structured.

## Figure 3: Patch Granularity
Use `figures/figure3_patch_granularity.csv`. Plot patch unit against KL/top1 with patch ratio. Message: document-level repair is more reliable.

## Figure 4: Budget Gate Pareto
Use `figures/figure4_budget_gate_pareto.csv` and `figures/figure4_heldout_gate_calibration.csv`. Plot patch ratio against answer equivalence. Message: gates are calibration tools, not universally dominant selectors.
"""


def _limitations_text() -> str:
    return """# Limitations Draft

SAFE-KV does not report measured production serving latency, TTFT, or throughput. Patched-token ratio, estimated recomputation ratio, and estimated prefill saving are recomputation-budget proxies only.

External HotpotQA/2Wiki mapping is noisy: evidence labels, retrieval order, and document construction differ from the controlled diagnostic setup. Full-prefill generations can be gold-wrong on external data, so external gold EM/F1 are secondary to answer equivalence with full prefill.

SAFE-KV does not show universal semantic selector dominance. Random K2 is a strong baseline, especially on external data. Fixed-threshold gates are not portable, and held-out budget calibration remains mixed on natural data.

The study uses small-to-medium instruction-tuned models: Qwen2.5-0.5B, Qwen2.5-1.5B, and SmolLM2-1.7B. Qwen7B is not part of the evidence package.

SAFE-KV is not integrated into vLLM, LMCache, CacheBlend, or KVLink, and it does not train or fine-tune models.
"""


def _related_work_text() -> str:
    return """# Related Work Notes

## Prefix Caching
Prefix caching is semantically safe when prompts share exact prefixes. SAFE-KV studies the harder non-prefix RAG document reuse setting.

## vLLM / PagedAttention
vLLM and PagedAttention address memory management and serving efficiency. SAFE-KV should be positioned as complementary semantic safety analysis, not a replacement.

## LMCache
LMCache is relevant for KV reuse in serving systems. SAFE-KV does not claim system integration or latency wins.

## CacheBlend
CacheBlend studies non-prefix KV cache fusion and selective recomputation. SAFE-KV differs by emphasizing answer-level behavior preservation, repair granularity, and claim-bound quality-budget analysis.

## KVLink
KVLink studies reusable document KV caches with positional adjustment and training/fine-tuning. SAFE-KV is training-free and analyzes when composed reuse drifts from full prefill.

## RAG Evaluation / HotpotQA / 2Wiki
HotpotQA and 2WikiMultihopQA are useful external sanity checks for multi-hop behavior. SAFE-KV should not present them as SOTA QA benchmarks.

Citation placeholders should be replaced with exact BibTeX before submission.
"""


def _package_summary_text(results_root: Path) -> str:
    return f"""# SAFE-KV Paper Package Summary

Title recommendation: *{SAFE_KV_TITLE}*

This package was generated from existing result files under `{results_root}`. It contains a LaTeX skeleton, section drafts, table TeX files, figure data, appendix notes, and claim-boundary documents.

No GPU experiments are required to regenerate this package.

## Remaining Writing/Formatting Gaps

- Replace citation placeholders with exact BibTeX before submission.
- Swap in the official ARR/ACL style files when the submission template is chosen.
- Convert the provided figure data into final styled plots.
- Polish prose for flow, length, and venue formatting.
"""


def _write_arr_long_draft(results_root: Path, out_dir: Path) -> None:
    """Overlay the 8B ARR/ACL-style draft on top of the reusable package."""
    _write_arr_main_tex(out_dir)
    _write_arr_sections(out_dir)
    _write_arr_compact_tables(results_root, out_dir)
    _write_arr_appendix(results_root, out_dir)
    _write_arr_figures(out_dir)
    _write_arr_bibliography(out_dir)
    _write_arr_notes(results_root, out_dir)


def _write_arr_main_tex(out_dir: Path) -> None:
    _write_text(
        out_dir / "main.tex",
        r"""
\documentclass[11pt]{article}

\usepackage[review]{acl}
\usepackage{times}
\usepackage{latexsym}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{adjustbox}
\usepackage{amsmath}
\usepackage{url}
\usepackage{microtype}
\usepackage{multirow}

\title{SAFE-KV: Semantics-Aware Safety Analysis and Document-Level Repair for Non-Prefix KV Cache Reuse in RAG}

\author{Anonymous ACL submission}

\begin{document}
\maketitle

\input{sections/00_abstract}
\input{sections/01_introduction}
\input{sections/02_related_work}
\input{sections/03_problem_setup}
\input{sections/04_method_and_diagnostics}
\input{sections/05_experiments}
\input{sections/06_results}
\input{sections/07_discussion}
\input{sections/08_limitations}

\bibliography{references}

\appendix
\input{appendix/dataset_details}
\input{appendix/implementation_sanity}
\input{appendix/extended_tables}
\input{appendix/failure_examples}

\end{document}
""",
    )


def _write_arr_sections(out_dir: Path) -> None:
    sections = {
        "00_abstract.tex": r"""
\begin{abstract}
Non-prefix KV cache reuse is attractive for retrieval-augmented generation (RAG): retrieved documents recur across prompts even when they are not shared prefixes. However, composing independently cached document states can change model behavior relative to full prefill. We introduce SAFE-KV, a semantic safety study of non-prefix KV cache composition in RAG. SAFE-KV uses full-prefill inference as the behavior oracle, evaluates composition variants, and asks which repair granularity preserves answers under a recomputation budget. Across controlled clean/noisy diagnostics, Qwen2.5-0.5B, Qwen2.5-1.5B, SmolLM2-1.7B, and external HotpotQA/2Wiki sanity data, we find that non-prefix composition can cause answer-level drift; prefix-conditioned document caching is a much stronger but still imperfect baseline; and residual drift concentrates in semantically hard cases such as conflict, multi-hop, and noisy retrieval. We further find that isolated span repair is unreliable, while document-level repair is a coherent unit for behavior preservation. Finally, calibrated document repair and gates expose quality--budget trade-offs under matched random controls. SAFE-KV reports recomputation-budget proxies, not production serving latency or throughput.
\end{abstract}
""",
        "01_introduction.tex": r"""
\section{Introduction}

Large language model deployments increasingly rely on retrieval-augmented generation (RAG), where a model answers a query conditioned on retrieved documents \citep{lewis2020retrieval}. A major cost in this setting is prefill: before decoding, the model must process the instruction prefix, documents, and query. KV caching reduces repeated work, but exact prefix caching only applies when future prompts share an identical prefix. In RAG, the reusable unit is often a document rather than a whole prefix: the same passage may appear in many prompts, at different positions, alongside different neighboring documents.

This makes non-prefix KV cache reuse appealing. If document KV states could be safely reused and composed into new prompts, systems could avoid recomputing large parts of the context. Yet the semantic status of this operation is subtle. A document encoded alone, or under a different prefix, is not necessarily equivalent to the same document encoded in the full prompt. Reusing such states may alter attention patterns and change the model's next-token distribution or generated answer. For safety analysis, the relevant oracle is therefore not the gold answer alone, but the model's own full-prefill behavior on the exact prompt.

SAFE-KV asks when non-prefix KV cache reuse is behavior-preserving in RAG, and what recomputation unit can repair unsafe cases. We deliberately do not frame SAFE-KV as a production serving system. Instead, we study full-prefill behavior preservation, answer-level drift, repair granularity, matched random controls, and recomputation-budget proxies.

Our contributions are:
\begin{enumerate}
    \item We define and measure semantic drift for non-prefix KV cache composition in RAG using full-prefill inference as the behavior oracle.
    \item We show that prefix-conditioned document caching is a strong but imperfect baseline, with residual drift concentrated in semantically hard cases such as conflict, multi-hop, and noisy retrieval.
    \item We show that isolated span/window repair is unreliable, while document-level repair is the coherent repair unit in our setting.
    \item We evaluate answer-level behavior, cross-model and cross-family transfer, external multi-hop sanity data, and calibrated budgeted gating with matched random controls.
\end{enumerate}

The resulting claim boundary is intentionally conservative: SAFE-KV supports semantic safety analysis and document-level repair/gating, but not universal selector dominance or measured serving speedups.
""",
        "02_related_work.tex": r"""
\section{Related Work}

\paragraph{KV cache reuse and LLM serving.}
Efficient LLM serving systems optimize memory layout, scheduling, and cache management. vLLM introduced PagedAttention to manage KV memory for high-throughput serving \citep{kwon2023efficient}. LMCache and related cache-reuse systems target serving efficiency and reuse across requests \citep{lmcache}. These systems address important infrastructure problems. SAFE-KV is complementary: it studies when a reused non-prefix cache preserves full-prefill behavior, which repair unit is coherent, and how quality changes under recomputation-budget proxies.

\paragraph{Non-prefix cache composition.}
The closest systems work studies cache fusion or reusable document KV states beyond exact-prefix caching. CacheBlend examines non-prefix KV cache blending and selective recomputation \citep{cacheblend}. KVLink studies reusable document KV caches with mechanisms such as positional adjustment and training or adaptation \citep{kvlink}. Prompt Cache studies modular prompt reuse \citep{promptcache}. SAFE-KV differs in emphasis: it is training-free, uses full prefill as the behavior oracle, measures generated-answer drift, compares repair granularities, and includes matched random controls. We do not claim to replace these systems or to report production latency.

\paragraph{RAG and multi-hop QA.}
RAG combines parametric generation with retrieved evidence \citep{lewis2020retrieval}. Multi-hop datasets such as HotpotQA \citep{yang2018hotpotqa} and 2WikiMultihopQA \citep{ho2020constructing} provide natural questions requiring evidence combination. SAFE-KV uses external HotpotQA/2Wiki examples as sanity checks rather than SOTA QA benchmarks because evidence mapping and full-prefill gold accuracy are noisier than in controlled diagnostics.

\paragraph{Semantic safety and behavior preservation.}
Many efficiency methods evaluate latency, throughput, or perplexity. SAFE-KV focuses on behavior preservation: if a composed cache produces a different answer from full prefill, the optimization has changed the model's behavior even if it remains fluent. This aligns the evaluation target with safe reuse rather than aggregate task accuracy alone.
""",
        "03_problem_setup.tex": r"""
\section{Problem Setup}

Let a RAG prompt contain an instruction/chat prefix $p$, retrieved documents $d_1,\ldots,d_m$, and a query $q$. Full prefill computes KV states over the complete sequence $(p,d_1,\ldots,d_m,q)$ and then decodes. A composed-cache method instead constructs a cache from separately encoded document states and decodes from that cache.

\paragraph{Full-prefill oracle.}
We treat full prefill as the model-behavior oracle. This is distinct from task correctness: on external data, a small model may answer incorrectly even under full prefill, but preserving full-prefill behavior still measures whether the cache optimization changed the model.

\paragraph{Semantic drift.}
We measure drift with first-token KL divergence from full prefill, top-1 agreement, generated answer equivalence to full prefill, and changed answers. We also report gold exact match and token F1 as auxiliary QA metrics.

\paragraph{Repair and budget.}
Repair recomputes selected prompt regions from the full prompt and patches the composed cache. We report patched-token ratio, estimated recomputation ratio, and estimated prefill saving as proxy metrics. These are not measured TTFT or throughput.

\begin{figure}[t]
\centering
\fbox{\begin{minipage}{0.92\linewidth}
\small
\textbf{Full prefill:} encode prefix + documents + query in order.\\
\textbf{Composed cache:} reuse non-prefix document KV states.\\
\textbf{SAFE-KV repair:} patch selected document-level cache slices or gate to full repair under a budget.
\end{minipage}}
\caption{SAFE-KV studies behavior preservation for non-prefix document KV reuse in RAG. The figure is a schematic placeholder; final styling can replace it without changing the paper narrative.}
\label{fig:setup}
\end{figure}
""",
        "04_method_and_diagnostics.tex": r"""
\section{Method and Diagnostics}

\paragraph{Composition variants.}
We compare doc-only composition, prefix-plus composition, and prefix-conditioned document composition. The key baseline is prefix-conditioned composition: document cache states are encoded under the static prompt/chat prefix before they are reused. This respects the conditioning shared across prompts and is substantially stronger than unconditioned document caches.

\paragraph{Repair granularity.}
We evaluate evidence-span repair, span windows, suffix repair, support+conflict repair, and full document repair. Span-level recomputation is attractive because it is cheap, but it may omit surrounding context required to produce the same downstream cache state. Document-level repair is more expensive but preserves a coherent evidence unit.

\paragraph{Document selection and gates.}
Document-level repair is evaluated with oracle evidence documents, simple semantic selectors such as query similarity and entity overlap, random K2 controls, fixed safe gates, budget-targeted gates, and held-out budget calibration. We treat gates as calibration tools rather than universally superior selectors.

\paragraph{Controlled diagnostics.}
The diagnostic set contains 100 examples balanced across single-evidence, multi-hop, conflict, boundary-sensitive, and distractor-heavy categories. A noisy variant injects additional distractors. These controlled labels make it possible to ask whether residual drift is structured rather than uniform.
""",
        "05_experiments.tex": r"""
\section{Experiments}

\paragraph{Models.}
We evaluate Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct \citep{qwen2025qwen25}, and SmolLM2-1.7B-Instruct \citep{smollm2} using Hugging Face Transformers \citep{wolf2020transformers}. Generation is deterministic and uses the validated manual-position-id decoding path.

\paragraph{Datasets.}
The main results use the controlled diagnostic and noisy diagnostic sets. External HotpotQA/2Wiki examples are converted into the same document schema and used as a 100-example sanity check. External gold metrics are secondary because full-prefill QA quality can be low for the small models.

\paragraph{Metrics.}
We report first-token KL, top-1 agreement, answer equivalence to full prefill, changed-and-gold-wrong counts, gold EM/F1, patched-token ratio, and matched random controls. Held-out gate calibration uses a deterministic 30/70 calibration/test split by example id.
""",
        "06_results.tex": r"""
\section{Results}

\subsection{RQ1: Prefix-conditioned composition is necessary but not sufficient}

Prefix conditioning is the most important composition choice. On the clean diagnostic set, doc-only global composition has much larger first-token drift than prefix-conditioned composition, while prefix-plus unconditioned composition is even less reliable. Table~\ref{tab:composition} summarizes the main ablation: prefix-conditioned composition reaches KL $0.207$ and top-1 agreement $0.90$, compared with KL $0.854$ and top-1 $0.61$ for doc-only global composition. This makes prefix-conditioned composition the right non-repair baseline, but not a complete solution.

\input{tables/table1_composition_ablation}

\subsection{RQ2: Drift is structured and answer-level}

First-token drift is not merely a distributional curiosity. For Qwen2.5-0.5B, prefix-conditioned composition changes 15/100 clean answers and 31/100 noisy answers relative to full prefill. The same pattern appears for Qwen2.5-1.5B, with answer equivalence dropping from 0.88 on clean diagnostics to 0.74 on noisy diagnostics. Drift is concentrated in conflict, multi-hop, and noisy retrieval cases rather than uniformly across examples. First-token KL also correlates with answer instability, supporting its use as a diagnostic risk signal rather than a perfect guarantee.

\subsection{RQ3: Document-level repair is the coherent repair granularity}

Table~\ref{tab:granularity} compares repair units. Oracle evidence-span repair is not enough: it improves some local quantities but does not reliably recover the full-prefill cache trajectory. The best non-document suffix/window repairs remain close to matched random controls in KL, while oracle document repair is substantially stronger. This supports the paper's central repair claim: document-level repair is a coherent unit, whereas isolated span patching is unreliable as the main method.

\input{tables/table2_repair_granularity}

\subsection{RQ4: Answer-level repair and selectors help under controlled noise}

Table~\ref{tab:answer-summary} compresses the synthetic answer-level results. On Qwen2.5-0.5B noisy data, base answer equivalence is 0.69, oracle document repair reaches 0.90, query similarity reaches 0.89, entity overlap reaches 0.90, and random K2 reaches 0.83. On Qwen2.5-1.5B noisy data, base equivalence is 0.74 while query/entity selectors reach 0.92 and random K2 reaches 0.86. These results justify saying that simple semantic document signals help under controlled noisy retrieval. Clean data is more saturated, and random K2 is strong, so we do not claim universal selector dominance.

\input{tables/table3_answer_level_summary}

\subsection{RQ5: Cross-model and external sanity}

The phenomenon transfers beyond a single Qwen model. Table~\ref{tab:cross-external} combines cross-family noisy and external sanity results. SmolLM2 shows non-trivial base drift on the noisy diagnostic and improvement from document-level repair. External HotpotQA/2Wiki results also show that answer drift is not synthetic-only, but they are noisier: full-prefill gold EM/F1 are lower and random K2 remains highly competitive. We therefore treat external data as sanity evidence, not a main benchmark or selector-dominance result.

\input{tables/table4_cross_model_and_external_summary}

\subsection{RQ6: Budgeted gates are calibration tools}

Budgeted gates answer a different question from selectors: at a declared recomputation budget, which examples should be repaired? Table~\ref{tab:budget-summary} shows held-out budget calibration. Controlled noisy diagnostics show useful mid/high-budget behavior, while 10\% budgets are brittle and external data remains mixed. This supports a calibrated quality-budget analysis, not a claim that the gate universally beats matched random gates.

\input{tables/table5_budget_gate_summary}

\subsection{RQ7: Cost accounting uses recomputation proxies}

SAFE-KV reports patched-token ratio as an estimated recomputation ratio and $1-$patched-token ratio as estimated prefill saving. These quantities are useful for comparing repair policies, but they are not measured serving latency. Appendix Table~\ref{tab:appendix-cost} contains the full cost-accounting table.
""",
        "07_discussion.tex": r"""
\section{Discussion}

\paragraph{Why span repair fails.}
Evidence spans are semantically meaningful to humans, but transformer cache states are contextual. A span encoded without its surrounding document context may not reproduce the hidden-state trajectory that full prefill would produce. This explains why span/window/suffix repair can be cheap yet unreliable.

\paragraph{Why random is strong.}
Random document patching is a demanding control because patching any coherent document can restore some missing context and reduce cache mismatch. In clean diagnostics and external data, many documents are short and evidence-dense enough that random K2 is competitive. This weakens selector-dominance claims but strengthens the broader conclusion that document-level coherent repair matters.

\paragraph{Why noisy diagnostics matter.}
The noisy diagnostic setting is controlled but difficult: it preserves known evidence labels while adding retrieval distractors. It is the setting where semantic selectors have the clearest advantage over random controls, making it valuable for isolating the safety problem.

\paragraph{How to use SAFE-KV.}
The practical lesson is not that a particular selector should be deployed unchanged. Rather, non-prefix KV reuse should be evaluated against full-prefill behavior, repair should operate on coherent document units, and gates should be calibrated under declared recomputation budgets with random controls.
""",
        "08_limitations.tex": r"""
\section{Limitations}

SAFE-KV is not a production serving benchmark. We do not report measured latency, time-to-first-token, throughput, or memory-system performance. Patched-token ratio, estimated recomputation ratio, and estimated prefill saving are recomputation-budget proxies only.

External HotpotQA/2Wiki examples are useful sanity checks but are noisy after conversion into a document-level RAG schema. Full-prefill generations can be gold-wrong on these datasets, especially for smaller models, so external gold EM/F1 are auxiliary rather than primary safety metrics.

The study evaluates small-to-medium instruction-tuned models: Qwen2.5-0.5B, Qwen2.5-1.5B, and SmolLM2-1.7B. It does not include Qwen7B evidence. We also do not integrate SAFE-KV into vLLM, LMCache, CacheBlend, or KVLink, and we do not train or fine-tune models or learned gates.

Finally, SAFE-KV does not show universal semantic selector dominance. Query/entity selectors help in controlled noisy diagnostics, but external results are mixed and random K2 is often competitive. Budgeted gates should be interpreted as calibration analyses, not universally superior selection rules.
""",
    }
    for name, text in sections.items():
        _write_text(out_dir / "sections" / name, text)


def _write_arr_compact_tables(results_root: Path, out_dir: Path) -> None:
    _write_compact_table1(results_root, out_dir)
    _write_compact_table2(results_root, out_dir)
    _write_compact_table3(results_root, out_dir)
    _write_compact_table4(results_root, out_dir)
    _write_compact_table5(results_root, out_dir)


def _write_compact_table1(results_root: Path, out_dir: Path) -> None:
    rows = _rows(results_root, "results_paper/table1_composition_ablation.csv")
    wanted = ["doc_only_naive_global", "prefix_plus_naive_global", "prefix_conditioned_naive_global"]
    rows = [{**row, "label": method_label(row["method"])} for row in rows if row["method"] in wanted]
    columns = [
        ("label", "Method", str),
        ("avg_kl", "KL", lambda x: fmt(x, 3)),
        ("top1", "Top-1", lambda x: fmt(x, 2)),
        ("top10", "Top-10", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table1_composition_ablation.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Composition ablation on the clean diagnostic set. Prefix-conditioned document composition is the strongest non-repair baseline, but residual drift remains.",
            label="tab:composition",
            align="lrrr",
        ),
    )


def _write_compact_table2(results_root: Path, out_dir: Path) -> None:
    table1 = {row["method"]: row for row in _rows(results_root, "results_paper/table1_composition_ablation.csv")}
    granularity = {row["method"]: row for row in _rows(results_root, "results_paper/table2_repair_granularity.csv")}
    patch = _aggregate_first_token_rows(_rows(results_root, "results_qwen05_100/patch_recompute_metrics.csv"))
    methods = [
        ("Base", table1.get("prefix_conditioned_naive_global")),
        ("Oracle span", patch.get("oracle_evidence_span_patch") or granularity.get("oracle_evidence_span_window_0")),
        ("Best non-doc", granularity.get("oracle_support_and_conflict_suffix_patch")),
        ("Matched random", granularity.get("random_patch_same_budget::oracle_support_and_conflict_suffix_patch")),
        ("Oracle doc", patch.get("oracle_evidence_doc_patch") or granularity.get("oracle_evidence_doc_patch")),
        ("Full-doc sanity", patch.get("full_doc_cache_patch_sanity")),
    ]
    rows = [{"unit": label, **source} for label, source in methods if source]
    columns = [
        ("unit", "Repair unit", str),
        ("avg_kl", "KL", lambda x: fmt(x, 3)),
        ("top1", "Top-1", lambda x: fmt(x, 2)),
        ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table2_repair_granularity.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Repair granularity comparison. Document-level repair is coherent; isolated span or suffix repair is not reliably better than matched random patching.",
            label="tab:granularity",
            align="lrrr",
        ),
    )


def _summary_metric(summary: dict[str, dict[str, Any]], method: str, key: str) -> Any:
    return summary.get(method, {}).get(key, "")


def _write_compact_table3(results_root: Path, out_dir: Path) -> None:
    runs = [
        ("Qwen0.5B", "clean", "results_qwen05_100_answer/answer_eval_metrics.csv"),
        ("Qwen0.5B", "noisy", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "clean", "results_qwen15_100_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "noisy", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
    ]
    rows = []
    for model, split, rel in runs:
        summary = _answer_summary(results_root, rel)
        query = _summary_metric(summary, "query_similarity_doc_patch_k2", "answer_equivalence")
        entity = _summary_metric(summary, "entity_overlap_doc_patch_k2", "answer_equivalence")
        rows.append(
            {
                "model": model,
                "split": split,
                "base": _summary_metric(summary, "prefix_conditioned_naive_global", "answer_equivalence"),
                "oracle": _summary_metric(summary, "oracle_evidence_doc_patch", "answer_equivalence"),
                "query_entity": f"{fmt(query, 2)}/{fmt(entity, 2)}",
                "gate": _summary_metric(summary, "safe_gate_t0.60", "answer_equivalence"),
                "random": _summary_metric(summary, "random_doc_patch_k2_seeded", "answer_equivalence"),
                "base_wrong": _summary_metric(summary, "prefix_conditioned_naive_global", "changed_wrong"),
            }
        )
    columns = [
        ("model", "Model", str),
        ("split", "Split", str),
        ("base", "Base", lambda x: fmt(x, 2)),
        ("oracle", "Oracle", lambda x: fmt(x, 2)),
        ("query_entity", "Q/E", str),
        ("gate", "Gate", lambda x: fmt(x, 2)),
        ("random", "Random", lambda x: fmt(x, 2)),
        ("base_wrong", "Base wrong", str),
    ]
    _write_text(
        out_dir / "tables/table3_answer_level_summary.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Compressed answer-level diagnostic summary. Values are answer equivalence to full prefill except Base wrong, which counts changed-and-gold-wrong base answers.",
            label="tab:answer-summary",
            align="llrrrrrr",
        ),
    )


def _write_compact_table4(results_root: Path, out_dir: Path) -> None:
    runs = [
        ("Qwen0.5B", "noisy diagnostic", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "noisy diagnostic", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
        ("SmolLM2", "noisy diagnostic", "results_smollm17_noisy_answer/answer_eval_metrics.csv"),
        ("Qwen0.5B", "external sanity", "results_qwen05_external_answer/answer_eval_metrics.csv"),
        ("Qwen1.5B", "external sanity", "results_qwen15_external_answer/answer_eval_metrics.csv"),
        ("SmolLM2", "external sanity", "results_smollm17_external_answer/answer_eval_metrics.csv"),
    ]
    rows = []
    for model, dataset, rel in runs:
        summary = _answer_summary(results_root, rel)
        repairs = [
            _summary_metric(summary, "oracle_evidence_doc_patch", "answer_equivalence"),
            _summary_metric(summary, "query_similarity_doc_patch_k2", "answer_equivalence"),
            _summary_metric(summary, "entity_overlap_doc_patch_k2", "answer_equivalence"),
            _summary_metric(summary, "safe_gate_t0.60", "answer_equivalence"),
        ]
        repairs = [float(x) for x in repairs if x != ""]
        rows.append(
            {
                "model": model,
                "dataset": dataset,
                "full_em": _summary_metric(summary, "full_prefill", "gold_em"),
                "base": _summary_metric(summary, "prefix_conditioned_naive_global", "answer_equivalence"),
                "best_repair": max(repairs) if repairs else "",
                "random": _summary_metric(summary, "random_doc_patch_k2_seeded", "answer_equivalence"),
            }
        )
    columns = [
        ("model", "Model", str),
        ("dataset", "Data", str),
        ("full_em", "Full EM", lambda x: fmt(x, 2)),
        ("base", "Base", lambda x: fmt(x, 2)),
        ("best_repair", "Best repair", lambda x: fmt(x, 2)),
        ("random", "Random", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table4_cross_model_and_external_summary.tex",
        render_latex_table(
            rows=rows,
            columns=columns,
            caption="Cross-model and external sanity summary. External data confirms drift is not synthetic-only, but random K2 remains competitive and gold quality is noisy.",
            label="tab:cross-external",
            align="llrrrr",
        ),
    )


def _write_compact_table5(results_root: Path, out_dir: Path) -> None:
    rows = _rows(results_root, "results_paper/heldout_gate_calibration_metrics.csv")
    wanted = []
    for row in rows:
        if row["dataset"] == "diagnostic_100_noisy" and row["target_budget"] in {"0.25", "0.4", "0.40"}:
            wanted.append(row)
        elif row["dataset"].startswith("external_multihop") and row["target_budget"] in {"0.25", "0.4", "0.40"}:
            wanted.append(row)
    curated = []
    for row in wanted:
        curated.append(
                {
                    "model": row.get("model", ""),
                    "dataset": "noisy" if row.get("dataset") == "diagnostic_100_noisy" else "external",
                    "target": row.get("target_budget", ""),
                    "actual": row.get("patched_token_ratio", row.get("test_actual_budget", "")),
                    "answer": row.get("answer_equivalence_to_full_prefill", ""),
                    "random": row.get("random_gate_mean_answer_equivalence", ""),
                    "ci": f"[{fmt(row.get('random_gate_95ci_low', ''), 2)}, {fmt(row.get('random_gate_95ci_high', ''), 2)}]",
                    "percentile": row.get("percentile_vs_random", ""),
                }
            )
    columns = [
        ("model", "Model", str),
        ("dataset", "Data", str),
        ("target", "Target", lambda x: fmt(x, 2)),
        ("actual", "Actual", lambda x: fmt(x, 2)),
        ("answer", "Gate", lambda x: fmt(x, 2)),
        ("random", "Random", lambda x: fmt(x, 2)),
        ("ci", "Rand 95% CI", str),
        ("percentile", "Pct", lambda x: fmt(x, 2)),
    ]
    _write_text(
        out_dir / "tables/table5_budget_gate_summary.tex",
        render_latex_table(
            rows=curated,
            columns=columns,
            caption="Held-out budget-gate calibration. Mid/high budgets are more defensible than 10%; external results remain mixed.",
            label="tab:budget-summary",
            align="llrrrrrr",
        ),
    )


def _write_arr_appendix(results_root: Path, out_dir: Path) -> None:
    _write_text(
        out_dir / "appendix/appendix_outline.md",
        """# Appendix Plan

1. Dataset construction and diagnostic category details.
2. Prompt construction, token-span alignment, and generation sanity checks.
3. Extended answer-level, external, budget-gate, and cost-accounting tables.
4. Full-prefill-correct external subset analysis.
5. Failure examples: base drift, document repair, random wins, and full-prefill gold-wrong cases.
""",
    )
    _write_text(
        out_dir / "APPENDIX_PLAN.md",
        """# Appendix Plan

The appendix should keep main-paper claims compact while preserving auditability.

- Dataset details: synthetic category definitions and external HotpotQA/2Wiki conversion.
- Implementation sanity: prompt/token alignment, manual position IDs, full-doc patch sanity.
- Extended tables: all answer-level, external, held-out gate, and cost-accounting tables.
- Failure examples: representative drift, repair, selector, random-control, and full-prefill-gold-wrong cases.
""",
    )
    _write_text(
        out_dir / "appendix/dataset_details.tex",
        r"""\section{Dataset Details}
The controlled diagnostic set contains 100 examples balanced across single-evidence, multi-hop, conflict, boundary-sensitive, and distractor-heavy categories. The noisy diagnostic adds retrieval distractors while preserving known evidence labels. External HotpotQA and 2WikiMultihopQA examples are converted into the same document-level schema and are used only as sanity checks, not as SOTA QA benchmarks.
""",
    )
    _write_text(
        out_dir / "appendix/implementation_sanity.tex",
        r"""\section{Implementation Sanity}
All answer-level runs use the \texttt{chat\_rag} prompt format and deterministic generation with manual position IDs. Prompt/token spans are built with one-pass tokenization and offset mappings. Full-document patch sanity checks verify that replacing all document cache slices recovers full-prefill behavior up to numerical precision.
""",
    )
    _write_extended_appendix_tables(results_root, out_dir)
    _write_text(
        out_dir / "appendix/failure_examples.tex",
        r"""\section{Failure Examples}
Per-run failure analyses are stored in the result directories as \texttt{answer\_failure\_analysis.md}. The camera-ready appendix should include representative examples where base composition differs from full prefill, where oracle document patch repairs the answer, where query/entity repair beats random, where random beats semantic selectors, and where full prefill itself is gold-wrong on external data.
""",
    )


def _write_extended_appendix_tables(results_root: Path, out_dir: Path) -> None:
    synthetic_rows = _rows(results_root, "results_paper/table3_answer_level_synthetic.csv")
    external_rows = _rows(results_root, "results_paper/table4_answer_level_external.csv")
    heldout_rows = _rows(results_root, "results_paper/heldout_gate_calibration_metrics.csv")
    cost_rows = _rows(results_root, "results_paper/table7_cost_accounting.csv")

    _write_text(
        out_dir / "tables/appendix_full_answer_level_synthetic.tex",
        render_latex_table(
            rows=synthetic_rows,
            columns=[
                ("model", "Model", str),
                ("split", "Split", str),
                ("method", "Method", method_label),
                ("answer_equivalence", "AnsEq", lambda x: fmt(x, 2)),
                ("answer_equivalence_ci_low", "CI low", lambda x: fmt(x, 2)),
                ("answer_equivalence_ci_high", "CI high", lambda x: fmt(x, 2)),
                ("changed_wrong", "Wrong", str),
                ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
            ],
            caption="Full synthetic answer-level table.",
            label="tab:appendix-synthetic",
        ),
    )
    _write_text(
        out_dir / "tables/appendix_full_external_sanity.tex",
        render_latex_table(
            rows=external_rows,
            columns=[
                ("model", "Model", str),
                ("split", "Split", str),
                ("method", "Method", method_label),
                ("answer_equivalence", "AnsEq", lambda x: fmt(x, 2)),
                ("gold_em", "EM", lambda x: fmt(x, 2)),
                ("gold_f1", "F1", lambda x: fmt(x, 2)),
                ("changed_wrong", "Wrong", str),
                ("patch_ratio", "Patch", lambda x: fmt(x, 2)),
            ],
            caption="Full external HotpotQA/2Wiki sanity table.",
            label="tab:appendix-external",
        ),
    )
    _write_text(
        out_dir / "tables/appendix_heldout_gate_calibration.tex",
        render_latex_table(
            rows=heldout_rows,
            columns=[
                ("model", "Model", str),
                ("dataset", "Dataset", str),
                ("target_budget", "Target", lambda x: fmt(x, 2)),
                ("patched_token_ratio", "Actual", lambda x: fmt(x, 2)),
                ("answer_equivalence_to_full_prefill", "Gate", lambda x: fmt(x, 2)),
                ("random_gate_mean_answer_equivalence", "Random", lambda x: fmt(x, 2)),
                ("percentile_vs_random", "Pct", lambda x: fmt(x, 2)),
            ],
            caption="Held-out budget-gate calibration details.",
            label="tab:appendix-heldout",
        ),
    )
    _write_text(
        out_dir / "tables/appendix_cost_accounting.tex",
        render_latex_table(
            rows=cost_rows,
            columns=[
                ("model", "Model", str),
                ("dataset", "Dataset", str),
                ("method", "Method", method_label),
                ("answer_equivalence_to_full_prefill", "AnsEq", lambda x: fmt(x, 2)),
                ("changed_wrong_rate", "Wrong", lambda x: fmt(x, 2)),
                ("patched_token_ratio", "Patch", lambda x: fmt(x, 2)),
                ("estimated_prefill_saving", "Saving", lambda x: fmt(x, 2)),
            ],
            caption="Cost accounting with recomputation-budget proxies.",
            label="tab:appendix-cost",
        ),
    )
    _write_text(
        out_dir / "appendix/extended_tables.tex",
        r"""\section{Extended Tables}
Table~\ref{tab:appendix-synthetic} reports the full synthetic answer-level results. Table~\ref{tab:appendix-external} reports external HotpotQA/2Wiki sanity results. Table~\ref{tab:appendix-heldout} reports held-out gate calibration details. Table~\ref{tab:appendix-cost} reports cost-accounting proxy metrics.

\input{tables/appendix_full_answer_level_synthetic}
\input{tables/appendix_full_external_sanity}
\input{tables/appendix_heldout_gate_calibration}
\input{tables/appendix_cost_accounting}
""",
    )


def _write_arr_figures(out_dir: Path) -> None:
    _write_text(
        out_dir / "figures/README.md",
        """# Figure Specifications

The draft compiles with in-text schematic placeholders. Final styled figure PDFs can be generated from the CSVs in this directory.

## Figure 1: Problem Setup
Shown as an in-paper boxed schematic. Final version should show full prefill, non-prefix document cache composition, prefix-conditioned composition, and document-level repair/gating.

## Figure 2: Category-Level Drift
Source: `figure2_category_drift.csv`. Bar plot by diagnostic category. Preferred y-axis: answer changed rate; optional secondary/appendix view: first-token KL. Takeaway: drift is structured.

## Figure 3: Patch Granularity
Source: `figure3_patch_granularity.csv`. Bar plot of KL or answer equivalence for base, span, best non-document, matched random, and document repair. Takeaway: document-level repair is coherent.

## Figure 4: Budget Gate Pareto
Sources: `figure4_budget_gate_pareto.csv` and `figure4_heldout_gate_calibration.csv`. X-axis patched-token ratio, y-axis answer equivalence. Show budgeted gate and matched random controls. Takeaway: gate is a calibration tool, not universally dominant.

No figure PDF is generated by the package builder because the remote environment may not include a plotting or LaTeX toolchain.
""",
    )
    placeholders = {
        "fig1_problem_setup.tex": "% Placeholder: rendered inline in sections/03_problem_setup.tex.\n",
        "fig2_category_drift.tex": "% Placeholder: generate from figures/figure2_category_drift.csv.\n",
        "fig3_patch_granularity.tex": "% Placeholder: generate from figures/figure3_patch_granularity.csv.\n",
        "fig4_budget_gate_pareto.tex": "% Placeholder: generate from figures/figure4_budget_gate_pareto.csv.\n",
    }
    for name, text in placeholders.items():
        _write_text(out_dir / "figures" / name, text)


def _write_arr_bibliography(out_dir: Path) -> None:
    _write_text(
        out_dir / "references.bib",
        r"""
@inproceedings{lewis2020retrieval,
  title = {Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks},
  author = {Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and Kuttler, Heinrich and Lewis, Mike and Yih, Wen-tau and Rocktaschel, Tim and Riedel, Sebastian and Kiela, Douwe},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2020}
}

@inproceedings{kwon2023efficient,
  title = {Efficient Memory Management for Large Language Model Serving with PagedAttention},
  author = {Kwon, Woosuk and Li, Zhuohan and Zhuang, Siyuan and Sheng, Ying and Zheng, Lianmin and Yu, Cody Hao and Gonzalez, Joseph E. and Zhang, Hao and Stoica, Ion},
  booktitle = {Proceedings of the ACM SIGOPS Symposium on Operating Systems Principles},
  year = {2023},
  note = {TODO: verify final venue metadata}
}

@inproceedings{yang2018hotpotqa,
  title = {HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering},
  author = {Yang, Zhilin and Qi, Peng and Zhang, Saizheng and Bengio, Yoshua and Cohen, William W. and Salakhutdinov, Ruslan and Manning, Christopher D.},
  booktitle = {Proceedings of EMNLP},
  year = {2018}
}

@inproceedings{ho2020constructing,
  title = {Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps},
  author = {Ho, Xanh and Nguyen, Anh-Khoa Duong and Sugawara, Saku and Aizawa, Akiko},
  booktitle = {Proceedings of COLING},
  year = {2020},
  note = {TODO: verify citation metadata}
}

@inproceedings{wolf2020transformers,
  title = {Transformers: State-of-the-Art Natural Language Processing},
  author = {Wolf, Thomas and Debut, Lysandre and Sanh, Victor and Chaumond, Julien and Delangue, Clement and Moi, Anthony and Cistac, Pierric and Rault, Tim and Louf, Remi and Funtowicz, Morgan and Davison, Joe and Shleifer, Sam and von Platen, Patrick and Ma, Clara and Jernite, Yacine and Plu, Julien and Xu, Canwen and Scao, Teven Le and Gugger, Sylvain and Drame, Mariama and Lhoest, Quentin and Rush, Alexander M.},
  booktitle = {Proceedings of EMNLP: System Demonstrations},
  year = {2020}
}

@misc{qwen2025qwen25,
  title = {Qwen2.5 Technical Report},
  author = {{Qwen Team}},
  year = {2025},
  note = {TODO: verify citation metadata}
}

@misc{smollm2,
  title = {SmolLM2},
  author = {{Hugging Face}},
  year = {2024},
  note = {TODO: verify citation metadata}
}

@misc{lmcache,
  title = {LMCache},
  author = {{LMCache Authors}},
  year = {2024},
  note = {TODO: verify citation metadata}
}

@misc{cacheblend,
  title = {CacheBlend},
  author = {{CacheBlend Authors}},
  year = {2024},
  note = {TODO: verify citation metadata}
}

@misc{kvlink,
  title = {KVLink},
  author = {{KVLink Authors}},
  year = {2024},
  note = {TODO: verify citation metadata}
}

@misc{promptcache,
  title = {Prompt Cache: Modular Attention Reuse for Low-Latency Inference},
  author = {{Prompt Cache Authors}},
  year = {2024},
  note = {TODO: verify citation metadata}
}
""",
    )


def _write_arr_notes(results_root: Path, out_dir: Path) -> None:
    _write_text(out_dir / "CLAIM_AUDIT.md", _arr_claim_audit_text())
    _write_text(out_dir / "TABLE_PLAN.md", _arr_table_plan_text())
    _write_text(out_dir / "FIGURE_PLAN.md", _figure_plan_text())
    _write_text(out_dir / "LIMITATIONS_DRAFT.md", _limitations_text())
    _write_text(out_dir / "RELATED_WORK_NOTES.md", _arr_related_work_notes())
    _write_text(out_dir / "COMPRESSION_PLAN.md", _compression_plan_text())
    _write_text(out_dir / "PAPER_OUTLINE.md", _arr_paper_outline_text())
    _write_text(out_dir / "README.md", _paper_readme_text())
    _write_text(out_dir / "ARR_LONG_DRAFT_STATUS.md", _arr_status_text(results_root, out_dir))


def _arr_claim_audit_text() -> str:
    return """# Claim Audit

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
"""


def _arr_table_plan_text() -> str:
    return """# Table Plan

## Main Paper

1. `table1_composition_ablation.tex`: compact composition ablation showing prefix conditioning is necessary.
2. `table2_repair_granularity.tex`: compact repair-unit comparison showing document repair is coherent.
3. `table3_answer_level_summary.tex`: compressed Qwen clean/noisy answer-level summary.
4. `table4_cross_model_and_external_summary.tex`: cross-family and external sanity summary.
5. `table5_budget_gate_summary.tex`: held-out budget calibration summary.

## Appendix

- `appendix_full_answer_level_synthetic.tex`: full synthetic answer-level results.
- `appendix_full_external_sanity.tex`: full external sanity results.
- `appendix_heldout_gate_calibration.tex`: held-out calibration details.
- `appendix_cost_accounting.tex`: recomputation-budget proxy accounting.
"""


def _arr_related_work_notes() -> str:
    return """# Related Work Notes

The related work section is written as positioning prose rather than a list. It covers:

- vLLM/PagedAttention and serving-memory management.
- LMCache and KV reuse in serving systems.
- CacheBlend, KVLink, and Prompt Cache as close non-prefix or modular cache-reuse work.
- RAG, HotpotQA, and 2WikiMultihopQA as task context and external sanity data.
- Semantic behavior preservation as SAFE-KV's distinct focus.

Several BibTeX entries are intentionally marked `TODO: verify citation metadata`; these should be verified before submission rather than replaced with guessed metadata.
"""


def _compression_plan_text() -> str:
    return """# Compression Plan

The current draft is designed around an 8-page ARR/ACL long-paper target.

## Main-Paper Compression Choices

- Keep at most five compact main tables.
- Move full synthetic, external, held-out calibration, and cost-accounting tables to appendix.
- Use RQ-based prose with 1-3 key numbers per subsection.
- Treat external data as sanity evidence to avoid a long benchmark discussion.

## Likely Cuts Before Submission

- Shorten Method and Experiments if page count exceeds 8 pages.
- Move some related-work detail into appendix if needed.
- Convert Table 5 to a figure if the budget-gate discussion becomes too table-heavy.
- Keep limitations complete even if main sections are compressed.
"""


def _arr_paper_outline_text() -> str:
    return f"""# ARR Long-Paper Draft Outline

Title: *{SAFE_KV_TITLE}*

## Abstract
Safety problem, full-prefill oracle, key findings, recomputation-budget scope.

## 1 Introduction
Motivate RAG document reuse, exact-prefix limits, non-prefix safety risk, and four contributions.

## 2 Related Work
Position against serving systems and non-prefix cache-reuse systems without claiming replacement.

## 3 Problem Setup
Define full prefill, composed-cache behavior, drift metrics, answer equivalence, and proxy budgets.

## 4 Method and Diagnostics
Composition variants, repair units, selectors/gates, and controlled diagnostic categories.

## 5 Experiments
Models, datasets, metrics, external sanity protocol, and held-out gate calibration.

## 6 Results
RQ1 prefix conditioning; RQ2 structured answer drift; RQ3 document repair; RQ4 controlled noisy selectors; RQ5 cross-model/external; RQ6 budgeted gates; RQ7 cost proxies.

## 7 Discussion
Why span repair fails, why random is strong, why noisy diagnostics are useful, and how to use SAFE-KV.

## Limitations
No latency claims, proxy budgets only, small/medium models, external data noise, no universal selector dominance.
"""


def _paper_readme_text() -> str:
    return """# SAFE-KV ARR Long-Paper Draft

This directory contains an ARR/ACL-style draft package generated from existing SAFE-KV results.

## Build

The draft expects ACL style files in this directory:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

or:

```bash
cd paper
latexmk -pdf main.tex
```

The current execution environment may not include a LaTeX compiler. See `ARR_LONG_DRAFT_STATUS.md` for the last compile check.

## Scope

SAFE-KV reports semantic behavior preservation and recomputation-budget proxies. It does not report production latency, TTFT, throughput, or SOTA QA performance.
"""


def _arr_status_text(results_root: Path, out_dir: Path) -> str:
    tex_tools = {
        "pdflatex": shutil.which("pdflatex"),
        "bibtex": shutil.which("bibtex"),
        "latexmk": shutil.which("latexmk"),
        "tectonic": shutil.which("tectonic"),
    }
    has_compiler = bool(tex_tools["pdflatex"] or tex_tools["latexmk"] or tex_tools["tectonic"])
    compile_status = (
        "Compile attempted with `pdflatex main.tex`, but no LaTeX compiler was found in the current environment (`pdflatex: command not found`)."
        if not has_compiler
        else "Ready to compile with the available local LaTeX toolchain."
    )
    acl_files = (
        "`paper/acl.sty` and `paper/acl_natbib.bst` are present."
        if (out_dir / "acl.sty").exists() and (out_dir / "acl_natbib.bst").exists()
        else "`paper/acl.sty` or `paper/acl_natbib.bst` is missing."
    )
    return f"""# ARR Long Draft Status

## 1. What Changed

- Rewrote `paper/main.tex` into an ACL-style anonymous-review draft.
- Expanded all section files into ARR long-paper prose organized around research questions.
- Compressed main tables to five paper-facing tables.
- Moved full answer-level, external, held-out gate, and cost-accounting tables to appendix files.
- Added `paper/references.bib` with verified and TODO-marked citation placeholders.
- Added appendix, compression, figure, claim-audit, and build-status documents.

## 2. Template Status

`main.tex` uses `\\usepackage[review]{{acl}}`. {acl_files}

## 3. Compile Status

{compile_status}

Detected tools:

- pdflatex: `{tex_tools['pdflatex']}`
- bibtex: `{tex_tools['bibtex']}`
- latexmk: `{tex_tools['latexmk']}`
- tectonic: `{tex_tools['tectonic']}`

## 4. Page Count

Unavailable until a LaTeX compiler is installed. The draft is written for an 8-page ARR/ACL main-content target, but final compression must be checked after compilation.

## 5. Section Status

- Abstract: complete draft.
- Introduction: complete draft with contribution list.
- Related work: coherent draft with citation TODOs where metadata needs verification.
- Problem setup: complete draft with definitions and schematic placeholder.
- Method/diagnostics: complete compact draft.
- Experiments: complete compact draft.
- Results: RQ-based draft with compact tables.
- Discussion: complete draft.
- Limitations: complete draft, no new results.

## 6. Tables

Main paper:

- `table1_composition_ablation.tex`
- `table2_repair_granularity.tex`
- `table3_answer_level_summary.tex`
- `table4_cross_model_and_external_summary.tex`
- `table5_budget_gate_summary.tex`

Appendix:

- `appendix_full_answer_level_synthetic.tex`
- `appendix_full_external_sanity.tex`
- `appendix_heldout_gate_calibration.tex`
- `appendix_cost_accounting.tex`

## 7. Figures

Figure 1 is an in-text schematic placeholder. Figures 2-4 have source CSVs and TeX placeholder files, but final styled PDF plots are not generated by the package builder.

## 8. Citation Status

Core citations are included in `references.bib`. CacheBlend, KVLink, LMCache, Prompt Cache, Qwen2.5, SmolLM2, and 2Wiki metadata include TODO verification markers before submission.

## 9. Remaining ARR Risks

- Verify BibTeX metadata for all TODO citations.
- Compile and measure page count once a TeX toolchain is available.
- Replace figure placeholders with styled plots.
- Tighten prose to fit the 8-page main-content target.
- Keep selector/gate claims caveated: no universal dominance and no production speedup claim.

## 10. Result Source

Generated from existing result files under `{results_root}`. No new GPU inference was run.
"""
