#!/usr/bin/env python
"""Build the expanded SAFE-KV ARR-quality internal draft.

This script is intentionally non-GPU: it reads existing paper/result CSVs,
rewrites the paper draft, generates PDF figures with matplotlib, and writes
status reports. It never imports model code or runs inference.
"""

from __future__ import annotations

import csv
import math
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RESULTS = ROOT / "results_paper"
TITLE = "SAFE-KV: Semantics-Aware Safety Analysis and Document-Level Repair for Non-Prefix KV Cache Reuse in RAG"


METHOD_LABELS = {
    "full_prefill": "Full",
    "doc_only_naive_global": "Doc-only",
    "doc_only_naive_local": "Doc-only local",
    "prefix_plus_naive_global": "Prefix-plus",
    "prefix_plus_naive_local": "Prefix-plus local",
    "prefix_conditioned_naive_global": "Prefix-cond.",
    "prefix_conditioned_naive_local": "Prefix-cond. local",
    "oracle_evidence_doc_patch": "Oracle doc",
    "oracle_evidence_sentence_to_doc_end_patch": "Sent. to doc end",
    "oracle_evidence_span_patch": "Span",
    "oracle_evidence_span_window_0": "Span",
    "oracle_evidence_span_window_4": "Span+4",
    "oracle_evidence_span_window_8": "Span+8",
    "oracle_evidence_span_window_16": "Span+16",
    "oracle_evidence_span_window_32": "Span+32",
    "oracle_evidence_suffix_patch": "Evidence suffix",
    "oracle_support_and_conflict_span_patch": "S+C span",
    "oracle_support_and_conflict_suffix_patch": "S+C suffix",
    "random_patch_same_budget::oracle_evidence_sentence_to_doc_end_patch": "Rand sent-doc",
    "random_patch_same_budget::oracle_evidence_span_window_0": "Rand span",
    "random_patch_same_budget::oracle_evidence_span_window_4": "Rand span+4",
    "random_patch_same_budget::oracle_evidence_span_window_8": "Rand span+8",
    "random_patch_same_budget::oracle_evidence_span_window_16": "Rand span+16",
    "random_patch_same_budget::oracle_evidence_span_window_32": "Rand span+32",
    "random_patch_same_budget::oracle_evidence_suffix_patch": "Rand suffix",
    "random_patch_same_budget::oracle_support_and_conflict_span_patch": "Rand S+C span",
    "random_patch_same_budget::oracle_support_and_conflict_suffix_patch": "Matched random",
    "full_doc_cache_patch_sanity": "Full-doc sanity",
    "query_similarity_doc_patch_k2": "Query K2",
    "entity_overlap_doc_patch_k2": "Entity K2",
    "risk_guided_doc_patch_k2": "Risk K2",
    "safe_gate_t0.45": "Gate .45",
    "safe_gate_t0.60": "Gate .60",
    "random_doc_patch_k2_seeded": "Random K2",
}


def main() -> None:
    ensure_dirs()
    write_main()
    write_sections()
    write_tables()
    write_appendix()
    write_bibliography()
    write_citation_verification()
    write_figures()
    write_plans_and_reports()


def ensure_dirs() -> None:
    for rel in ["sections", "tables", "figures", "appendix"]:
        (PAPER / rel).mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def fnum(value: Any, digits: int = 2) -> str:
    try:
        x = float(value)
    except Exception:
        return str(value)
    if math.isnan(x):
        return ""
    return f"{x:.{digits}f}"


def esc(text: Any) -> str:
    s = str(text)
    repl = {
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
    return "".join(repl.get(ch, ch) for ch in s)


def latex_table(
    rows: list[dict[str, Any]],
    columns: list[tuple[str, str, str]],
    *,
    caption: str,
    label: str,
    align: str,
    star: bool = False,
    font_size: str = "footnotesize",
    resize_to_width: bool = False,
) -> str:
    env = "table*" if star else "table"
    header = " & ".join(esc(name) for _, name, _ in columns)
    lines = []
    for row in rows:
        cells = []
        for key, _name, kind in columns:
            value = row.get(key, "")
            cells.append(esc(fnum(value, int(kind[1:])) if kind.startswith("f") else value))
        lines.append(" & ".join(cells) + r" \\")
    centered_align = "c" * len(columns)
    tabular = (
        f"\\begin{{tabular}}{{{centered_align}}}\n"
        "\\toprule\n"
        f"{header} \\\\\n"
        "\\midrule\n"
        + "\n".join(lines)
        + "\n\\bottomrule\n"
        "\\end{tabular}\n"
    )
    max_width = r"\textwidth" if star else r"\linewidth"
    tabular = f"\\begin{{adjustbox}}{{max width={max_width}}}\n" + tabular + "\\end{adjustbox}\n"
    return (
        f"\\begin{{{env}}}[t]\n"
        "\\centering\n"
        f"\\{font_size}\n"
        + tabular
        + f"\\caption{{{esc(caption)}}}\n"
        f"\\label{{{label}}}\n"
        f"\\end{{{env}}}\n"
    )


def write_main() -> None:
    write_text(
        PAPER / "main.tex",
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
\label{page:mainend}
\input{sections/08_limitations}

\bibliography{references}

\appendix
\input{appendix/dataset_details}
\input{appendix/prompt_tokenization}
\input{appendix/cache_sanity}
\input{appendix/algorithms}
\input{appendix/full_composition_tables}
\input{appendix/full_repair_tables}
\input{appendix/full_answer_tables}
\input{appendix/external_sanity}
\input{appendix/heldout_gate}
\input{appendix/cost_accounting}
\input{appendix/failure_examples}
\input{appendix/related_work_comparison}
\input{appendix/artifact_checklist}

\end{document}
""",
    )


def write_sections() -> None:
    section_texts = {
        "00_abstract.tex": r"""
\begin{abstract}
Non-prefix KV cache reuse is attractive for retrieval-augmented generation (RAG): retrieved documents recur across requests even when they are not shared as exact prompt prefixes. Yet a cached document state is not a reusable text embedding. It is a context-conditioned causal state, and composing it under a new prompt can make the model decode from a state that no full-context forward pass would have produced. We introduce SAFE-KV, a semantics-aware study of when non-prefix cache composition preserves model behavior in RAG. SAFE-KV uses full-prefill inference as the behavioral oracle, evaluates composition baselines, studies repair granularity, and measures answer-level drift under recomputation-budget proxies. Across controlled clean/noisy diagnostics, Qwen2.5-0.5B, Qwen2.5-1.5B, SmolLM2-1.7B, and external HotpotQA/2Wiki sanity data, we find that prefix-conditioned document caching is necessary but imperfect; residual drift is structured by conflict, multi-hop, and noisy retrieval; first-token drift predicts answer instability; span-level repair is unreliable; and document-level repair is the coherent recomputation unit. Budgeted gates expose quality--budget trade-offs under matched random controls, but do not universally dominate them. SAFE-KV is a semantic safety and repair analysis, not a production latency benchmark.
\end{abstract}
""",
        "01_introduction.tex": r"""
\section{Introduction}

Modern RAG systems are increasingly dominated by context prefill. A model may read a long instruction wrapper, several retrieved passages, and a short query before producing a short answer. Because the same documents recur across users, sessions, and related questions, the natural systems instinct is to reuse their key--value (KV) cache states. Exact prefix reuse is safe but narrow: if the reused text is literally the same prefix, the cached model state is identical. RAG exposes the harder case. The reusable object is often a document, and the same document is not the same model state when it is encoded before a conflicting source, after a system instruction, or beside a multi-hop bridge document.

Non-prefix KV cache reuse therefore promises efficiency, but it also creates a semantic state-mismatch problem. A transformer's KV cache is not an isolated memory of token strings. Each key and value is produced by layer-wise hidden states that depend on prefix, position, prompt formatting, and previous tokens. If a document cache is computed independently and later spliced into a new prompt, the resulting cache can be a counterfactual hybrid. A system may decode fluently from that cache while silently changing the answer that the same model would have generated under full prefill. That silent behavior change is qualitatively different from an ordinary latency/accuracy trade-off: the user sees a normal answer, but the system has changed the model's semantic state.

SAFE-KV studies this semantic safety problem. We take full-prefill behavior on the exact RAG prompt as the oracle and ask when composed-cache inference preserves that behavior. This choice deliberately separates safety from task accuracy. If a small model answers an external QA question incorrectly under full prefill, preserving that answer is still the right test of whether cache reuse changed the model. Gold EM/F1 remain useful auxiliary metrics, but the primary safety target is behavioral equivalence to full prefill.

The core thesis is that non-prefix cache composition is not merely an engineering trick. It has structured semantic failure modes. Prefix-conditioned document caches---where each document is encoded under the static chat/instruction prefix---are much safer than doc-only caches, but they still lack cross-document interactions. Drift is concentrated where those interactions matter: conflict, multi-hop evidence, boundary-sensitive examples, and noisy retrieval. Repair also has structure. Token or evidence-span recomputation seems attractive because it is cheap, but local patching can create an internally inconsistent cache. In our experiments, document-level repair is the coherent unit: it recomputes enough causal context to restore behavior more reliably.

We do not claim to build a production serving system or to replace serving frameworks such as vLLM, LMCache, CacheBlend, or KVLink. Instead, SAFE-KV provides a diagnostic and repair framework for future systems that want to exploit non-prefix reuse without silently changing model behavior.

Our contributions are:
\begin{enumerate}
    \item We define semantic drift for non-prefix KV cache composition in RAG, using full-prefill behavior as the reference.
    \item We show that prefix-conditioned document caching is a necessary baseline, but residual drift remains structured by conflict, multi-hop evidence, and noisy retrieval.
    \item We show that span/window/suffix repair is unreliable and that document-level repair is the coherent repair unit in our setting.
    \item We validate answer-level drift across clean/noisy diagnostics, Qwen and SmolLM2 models, and external HotpotQA/2Wiki sanity data, and evaluate budgeted gates with matched random controls.
\end{enumerate}
""",
        "02_related_work.tex": r"""
\section{Related Work}

\paragraph{Prefix caching and LLM serving systems.}
KV caching is central to efficient autoregressive inference: after prefill, the model reuses cached keys and values rather than recomputing attention over previous tokens. Exact-prefix caching reuses this state across requests that share an identical prefix, and is semantically safe because the reused cache corresponds to the same forward pass. Serving systems also optimize cache allocation, batching, and scheduling. vLLM and PagedAttention address KV memory fragmentation and high-throughput serving by paging cache blocks \citep{kwon2023efficientmemorymanagementlarge}. LMCache exposes KV cache as a reusable layer for offloading, transfer, and cross-query reuse \citep{liu2025lmcacheefficientkvcache}. These systems motivate the importance of cache reuse, but their primary axis is system efficiency. SAFE-KV asks a complementary question: if a cache is reused outside the exact-prefix setting, when does the model's behavior remain faithful to full prefill?

\paragraph{Non-prefix KV cache reuse and cache composition.}
Several recent systems study non-prefix or modular cache reuse. Prompt Cache proposes modular attention reuse for recurring prompt segments \citep{gim2024promptcachemodularattention}. CacheBlend studies cached knowledge fusion for RAG and selective recomputation \citep{yao2025cacheblendfastlargelanguage}. KVLink studies independent document cache reuse with positional adjustment, special link tokens, and training \citep{yang2025kvlinkacceleratinglargelanguage}. SAFE-KV is closest in spirit to these efforts, but differs in its acceptance criterion. CacheBlend and KVLink ask how to make non-prefix reuse work efficiently and maintain useful generation quality. SAFE-KV asks when reuse preserves the behavior of the original full-context computation, which repair unit is coherent, and whether selectors/gates survive matched random controls. Appendix~\ref{sec:app-related-comparison} summarizes this positioning.

\paragraph{KV compression and memory reduction.}
KV compression methods reduce memory or bandwidth by quantizing, evicting, or sparsifying cached states. KIVI quantizes key and value caches with asymmetric low-bit schemes \citep{liu2024kivituningfreeasymmetric2bit}; Scissorhands exploits persistence of token importance for KV cache compression \citep{liu2023scissorhandsexploitingpersistenceimportance}. These approaches ask which existing cache entries can be represented more compactly or retained under a memory budget. SAFE-KV asks a different question: if KV states are computed independently for documents and then composed into a new RAG prompt, is the resulting state semantically equivalent to full prefill?

\paragraph{RAG and multi-hop QA.}
RAG conditions generation on retrieved evidence \citep{lewis2021retrievalaugmentedgenerationknowledgeintensivenlp}. Multi-hop QA datasets such as HotpotQA \citep{yang2018hotpotqadatasetdiverseexplainable} and 2WikiMultihopQA \citep{ho2020constructingmultihopqadataset} stress evidence combination, distractors, and reasoning chains. These are natural stress tests for non-prefix composition because cross-document interactions matter. We use external HotpotQA/2Wiki data as sanity evidence, but our main claims rely on controlled diagnostics where evidence roles, conflict, and noisy retrieval are known.

\paragraph{Models and tooling.}
Our robustness checks use Qwen2.5 \citep{qwen2025qwen25technicalreport}, SmolLM2 \citep{allal2025smollm2smolgoesbig}, and Hugging Face Transformers \citep{wolf2020huggingfacestransformersstateoftheartnatural}. The goal of these checks is not model benchmarking, but to verify that non-prefix drift and document-level repair are not artifacts of a single small model family.
""",
        "03_problem_setup.tex": r"""
\section{Problem Setup}

\paragraph{Full prefill as coherent causal state.}
Consider a RAG prompt with a static chat/instruction prefix $p$, documents $d_1,\ldots,d_m$, and query $q$. Full prefill runs the transformer over the entire sequence $(p,d_1,\ldots,d_m,q)$ and stores per-layer keys and values for every token. This cache is coherent: every state was produced under the same causal history. A composed-cache method instead reuses document states computed elsewhere and assembles them into a cache for the new prompt. Even when token positions are adjusted, the states may have been conditioned on the wrong prefix or may lack earlier documents. The composed cache can therefore be a plausible but counterfactual model state.

SAFE-KV distinguishes three states. The \emph{full-prefill state} is produced by one forward pass over the complete prompt. The \emph{composed state} concatenates separately encoded reusable document states with the prefix and query. The \emph{repaired state} starts from the composed state but patches selected document slices from full-context recomputation. The safety question is whether the composed or repaired state preserves the behavior of the full-prefill state.

\paragraph{Intuition.}
Suppose one retrieved document states that an official schedule lists an event at 8 AM, while another old blog post says 10 AM. Full prefill allows the model to encode both documents in a single causal context, including order, source framing, and the query instruction. Independently cached documents preserve each passage locally, but may weaken the global comparison that makes the official source preferred. The model can still produce a fluent answer, but the answer may differ from full prefill. SAFE-KV studies exactly this gap.

\paragraph{Behavioral oracle and drift.}
Let $P_{\mathrm{full}}$ be the first-answer-token distribution under full prefill and $P_{\mathrm{comp}}$ the distribution under a composed cache. We measure first-token drift with $\mathrm{KL}(P_{\mathrm{full}}\Vert P_{\mathrm{comp}})$ and top-1 agreement. We measure answer-level drift by deterministic generation and normalized answer equivalence to full prefill. A changed-and-gold-wrong answer counts cases where cache composition both differs from full prefill and fails the gold-answer check.

Formally, for prompt $x=(p,d_1,\ldots,d_m,q)$, semantic drift at the first answer token is
\[
D_{\mathrm{KL}}\!\left(p_{\mathrm{full}}(\cdot \mid x)\;\|\;p_{\mathrm{comp}}(\cdot \mid x)\right).
\]
At the answer level, we decode deterministic answers $a_{\mathrm{full}}$ and $a_{\mathrm{comp}}$ and record
\[
\mathbf{1}\{\mathrm{norm}(a_{\mathrm{full}}) \neq \mathrm{norm}(a_{\mathrm{comp}})\}.
\]
These two views are complementary. The distributional view is sensitive and local; the answer view measures the user-visible consequence. SAFE-KV uses both because a cache method can be numerically close while still flipping a short answer, or numerically far while preserving a robust answer string.

\paragraph{Repair and budget.}
Repair recomputes selected prompt regions from the true full prompt and patches the corresponding cache slices. We compare span, window, suffix, and document repair. We report patched-token ratio as an estimated recomputation ratio and $1-$patched-token ratio as estimated prefill saving. These are accounting proxies, not measured latency, throughput, or time-to-first-token.

\begin{figure*}[t]
\centering
\includegraphics[width=0.92\linewidth]{figures/figure1_setup.pdf}
\caption{SAFE-KV problem setup. Full prefill creates a coherent causal state. Non-prefix reuse composes prefix-conditioned document states into a cheaper but potentially counterfactual state. Document repair and gates spend recomputation budget to move the composed state back toward full-prefill behavior.}
\label{fig:setup}
\end{figure*}
""",
        "04_method_and_diagnostics.tex": r"""
\section{Method and Diagnostic Design}

\subsection{Full-prefill oracle}

Every experiment begins with a full-prefill run over the exact prompt used for generation. This run supplies the reference first-token distribution, the reference generated answer, and cache slices used by oracle repair analyses. Using full prefill as the oracle is essential because SAFE-KV is not asking whether a model is correct in the abstract; it asks whether cache reuse changes the model. This distinction matters on external data, where small models may be gold-wrong even without cache composition.

\subsection{Composition baselines}

We evaluate three families of non-prefix composition. \emph{Doc-only} composition encodes documents independently and then composes their states into the prompt. \emph{Prefix-plus} composition concatenates static prefix states with independently encoded document states. Both ignore part of the context that full prefill would use. The strongest baseline is \emph{prefix-conditioned} document composition: each document is encoded under the static chat and instruction prefix before reuse. This gives the document the same prompt wrapper and answer instruction seen in full prefill, while still withholding cross-document context. Prefix-conditioned composition therefore isolates the remaining semantic risk: interactions among documents and the query that cannot be recovered by conditioning on the static prefix alone.

\subsection{Repair granularity}

The natural engineering temptation is to repair as little as possible. If a question's answer appears in one sentence, why not recompute only that span? SAFE-KV tests this directly with evidence-span repair, span windows, suffix repair, support+conflict spans, and document-level repair. The reason to suspect small patches is that cache states are causally entangled. Replacing a few local states can produce a hybrid cache in which upstream and downstream states disagree about the context. Document-level repair recomputes a coherent evidence unit and is therefore a more conservative repair hypothesis.

\subsection{Document-level repair and selectors}

At the document level we compare several selectors. Oracle evidence document patching uses gold evidence labels and provides an upper bound on label-aware repair. Query similarity and entity overlap are simple semantic selectors. A risk-guided selector is included in the broader results but is not the central winner. Random K2 document patching is a critical control: if any coherent document patch repairs much of the drift, then semantic selectors must be compared against strong random baselines rather than against no repair.

\subsection{Safe-composition gating}

Gates decide whether to trust composed-cache inference or spend budget on document-level repair. We evaluate fixed thresholds, budget-targeted gates, and held-out calibration. Budgeted gates select high-risk examples until a declared patched-token budget is reached. Held-out calibration uses 30\% of examples to determine a risk cutoff and evaluates on the remaining 70\%. We also run matched random gates with the same budget. This protocol treats gating as safety analysis rather than post-hoc tuning.

\subsection{Diagnostics}

The controlled diagnostic set contains single-evidence, multi-hop, conflict, boundary-sensitive, and distractor-heavy examples. The noisy variant injects additional retrieval distractors. These categories are deliberately simple: they make it possible to localize semantic failure modes. External HotpotQA/2Wiki examples are converted into the same schema only after the controlled story is established.

\subsection{Sanity checks}

Because cache-composition experiments can fail for mundane implementation reasons, SAFE-KV includes several sanity checks before interpreting semantic drift. Manual cached decoding is checked against standard deterministic generation. Sequential prefill verifies that splitting a prompt and feeding pieces in order preserves full-prefill behavior. Full-document patch sanity recomputes all document slices from the full prompt and checks that the patched cache recovers the full-prefill first-token behavior. These checks make the residual errors in the main experiments more interpretable: they are not caused by a broken decoding path or by an inability to splice cache tensors at all.
""",
        "05_experiments.tex": r"""
\section{Experiments}

\paragraph{Datasets.}
The main diagnostic set has 100 examples, balanced across five semantic categories. The noisy diagnostic adds distractor documents while preserving evidence labels. External sanity data contains 50 HotpotQA and 50 2WikiMultihopQA examples after filtering yes/no answers and examples without usable evidence mappings. External examples are valuable because they are natural, but they also introduce noise in document construction and gold-answer quality.

\paragraph{Models and decoding.}
We evaluate Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct, and SmolLM2-1.7B-Instruct. All answer-level runs use deterministic decoding with a maximum of 16 new tokens, the \texttt{chat\_rag} prompt format, and the validated manual-position-id generation path. This keeps differences attributable to cache composition rather than sampling.

\paragraph{Metrics.}
First-token metrics include KL divergence, top-1 agreement, and top-10 overlap. Answer metrics include answer equivalence to full prefill, gold EM/F1, answer contains gold, changed answer rate, and changed-and-gold-wrong counts. Repair metrics include patched document count and patched-token ratio. For gates, we report matched random means, confidence intervals, and percentile ranks where available.

\paragraph{Scope of external evaluation.}
External HotpotQA/2Wiki is not used as a main benchmark. Full-prefill gold EM is only 0.25--0.41 for Qwen models in our external setup, so gold correctness is a noisy secondary measure. The primary external question is whether answer drift and partial repair occur outside synthetic diagnostics.
""",
        "06_results.tex": r"""
\section{Results}

\subsection{RQ1: Does non-prefix composition drift from full prefill?}

Yes. Table~\ref{tab:composition} shows that naive non-prefix composition can substantially change the first-token distribution. Doc-only global composition reaches KL 0.854 and top-1 agreement 0.61 on the clean diagnostic set; prefix-plus global composition is even worse at KL 1.205 and top-1 0.47. Prefix-conditioned composition is far stronger, reducing KL to 0.207 and raising top-1 agreement to 0.90, but it is not exact. This result supports two claims at once: conditioning documents on the static prompt wrapper is necessary, and residual non-prefix drift remains even after this strong baseline.

\input{tables/table1_composition_ablation}

Drift is also structured. In the clean Qwen0.5B diagnostic, conflict examples have much higher answer-change rates than single-evidence or distractor-heavy examples. Noisy retrieval magnifies this pattern because irrelevant documents increase the chance that local document states fail to represent global evidence preference. Figure~\ref{fig:category-drift} makes this visible: the hard categories are not random failures, but the settings where cross-document conditioning matters most.

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figures/figure2_category_drift.pdf}
\caption{Category-level answer drift for prefix-conditioned composition. Conflict and multi-hop/noisy settings are consistently harder than single-evidence cases, showing that residual drift is semantically structured.}
\label{fig:category-drift}
\end{figure}

\subsection{RQ2: Does first-token drift translate into answer-level drift?}

Yes. Distributional drift changes generated answers under deterministic decoding. On Qwen2.5-0.5B, prefix-conditioned composition changes 15/100 clean answers and 31/100 noisy answers relative to full prefill; 14 and 23 of those changed answers are also gold-wrong. On Qwen2.5-1.5B, the base answer equivalence is 0.88 on clean data and 0.74 on noisy data. This matters because an optimization that only changes logits but not outputs might be acceptable in some applications; SAFE-KV shows that the drift reaches the user-visible answer level.

First-token KL is not a perfect predictor. Some high-KL examples decode to the same short answer, and some low-KL examples can flip when competing answers are close. Still, it is meaningful as a risk signal: low KL usually corresponds to stable answers, while high KL sharply increases mismatch risk. This justifies using first-token drift for diagnostics and gates, provided it is not treated as a formal guarantee.

\subsection{RQ3: What repair granularity is coherent?}

Table~\ref{tab:granularity} answers the repair question. Full-document patch sanity nearly recovers full prefill, confirming that the cache patching mechanics are sound. Oracle evidence document repair reduces KL to 0.090 and raises top-1 agreement to 0.97. In contrast, oracle evidence-span repair remains weaker, and support+conflict suffix repair does not reliably beat matched random patching on KL. Appendix Figure~\ref{fig:app-repair} visualizes the full pattern.

\input{tables/table2_repair_granularity}

The interpretation is that evidence spans are semantic units for humans, but not necessarily causal units for transformer caches. A local replacement may repair the answer token's immediate evidence while leaving surrounding document states and later states inconsistent. Document-level repair recomputes the larger unit over which evidence is framed, source reliability is expressed, and local discourse is preserved.

\subsection{RQ4: Can document-level repair improve answer preservation?}

Yes, especially in controlled noisy settings. Table~\ref{tab:answer-summary} compresses the answer-level results. On Qwen0.5B noisy data, base answer equivalence is 0.69. Oracle document repair reaches 0.90, query similarity reaches 0.89, entity overlap reaches 0.90, and random K2 reaches 0.83. On Qwen1.5B noisy data, base equivalence is 0.74, query/entity selectors reach 0.92, and random K2 reaches 0.86. These results support the claim that simple semantic document signals are useful under controlled noisy retrieval.

\input{tables/table3_answer_level_summary}

Clean diagnostics are more saturated. Random document patching can be very strong because many clean prompts contain a small number of short, evidence-dense documents. This is not a failure of the document-level thesis; it is a warning against overclaiming selector superiority. The robust claim is that coherent document repair improves behavior preservation, while semantic selectors are most clearly useful when retrieval is noisy and labels are controlled.

\subsection{RQ5: Do the findings generalize across models and external data?}

Table~\ref{tab:cross-external} summarizes cross-model and external sanity checks. The noisy diagnostic trend appears in Qwen0.5B, Qwen1.5B, and SmolLM2. SmolLM2 has base answer equivalence 0.68 on noisy diagnostics, while the best document repair reaches 0.94 and random K2 reaches 0.84. This reduces the risk that the phenomenon is a Qwen-only artifact.

\input{tables/table4_cross_model_and_external_summary}

External HotpotQA/2Wiki data is messier but still informative. Base answer equivalence is low for all three models, confirming that answer drift is not synthetic-only. Document repair partially improves behavior, especially for Qwen1.5B, but random K2 remains competitive and sometimes stronger than semantic selectors. This is why the paper treats external data as sanity evidence rather than a selector benchmark. It supports the existence of non-prefix drift in natural multi-hop data, but not universal selector dominance.

\subsection{RQ6: Are gate and selector gains robust under random controls?}

Random controls are essential. On clean diagnostics, random K2 is often too strong for semantic selectors to dominate. On noisy diagnostics, semantic selectors and budgeted gates are more informative: they exploit query/entity alignment and risk signals when distractors make arbitrary patching less reliable. Held-out calibration further reduces post-hoc risk by choosing cutoffs on a calibration split and evaluating on a held-out test split.

Table~\ref{tab:budget-summary} shows the calibrated gate results. Mid/high budgets are more defensible than a brittle 10\% budget. For Qwen1.5B noisy data, the 0.40 target reaches answer equivalence 0.96 versus a matched random mean of 0.92. External data remains mixed: for Qwen1.5B external at 0.40, the gate trails random. This is an important negative result and sharpens the claim boundary. Gates are useful calibration tools, not universally superior selectors.

\input{tables/table5_budget_gate_summary}

\subsection{RQ7: What is the recomputation-budget trade-off?}

Figure~\ref{fig:budget} places answer equivalence against patched-token ratio. Full K2 repair policies often improve answer preservation but patch a large fraction of document tokens. Gates can operate at smaller budgets, sacrificing some answer equivalence for lower recomputation. This is the right way to report SAFE-KV's cost story: the paper measures how much prompt cache is repaired, not production latency.

The practical implication is that a future cache-reuse system should expose its safety budget. A high-reuse mode may be acceptable for low-risk single-evidence lookup, while conflict or multi-hop cases may need document repair or full prefill. SAFE-KV does not prescribe one universal operating point. It provides the measurement framework needed to choose an operating point honestly.

\begin{figure}[t]
\centering
\includegraphics[width=\linewidth]{figures/figure4_budget_gate_pareto.pdf}
\caption{Budget-quality trade-off on noisy diagnostic runs. Budgeted gates are compared with matched random gates at the same patched-token ratio. They are useful calibration tools, but not universal dominance claims.}
\label{fig:budget}
\end{figure}
""",
        "07_discussion.tex": r"""
\section{Discussion}

SAFE-KV changes the framing of non-prefix cache reuse. The first question should not be ``can this cache be composed?'' but ``does composing this cache preserve the model state that full prefill would have produced?'' The experiments show that this is a semantic question. Prefix conditioning removes a large amount of avoidable drift, but not the drift that depends on cross-document context. Conflict and multi-hop cases are therefore not edge cases; they are precisely the cases where document reuse is semantically delicate.

The repair results suggest a practical design principle. Future systems should treat documents, or similarly coherent retrieval units, as the natural repair granularity. Smaller local patches may be attractive for budget reasons, but they can leave the cache internally inconsistent. Conversely, document-level repair explains why random K2 is strong: even an arbitrary coherent document patch can restore some causal context. This makes random baselines indispensable.

The gate results should also be read conservatively. A gate that works on controlled noisy diagnostics may not transfer directly to natural data, where retrieval quality, evidence density, and model QA ability vary. The right contribution is therefore calibration analysis: report declared budgets, matched random controls, and held-out protocols. That is a stronger and more honest foundation for future serving systems than presenting one fixed threshold as universally safe.

\paragraph{Implications for future systems.}
SAFE-KV suggests that non-prefix reuse should expose a semantic contract, not only a cache API. A serving system may choose to compose caches, but it should also know which prompt regions were conditioned together, which documents were repaired, and how much recomputation budget was spent. This is especially important for RAG because the same efficiency optimization may be harmless for single-evidence lookup yet unsafe for conflict resolution or multi-hop aggregation. In this sense, SAFE-KV turns a hidden systems choice into an explicit behavior-preservation trade-off.

\paragraph{Why negative results are useful.}
Several findings constrain the paper's claims. Span repair does not become the final method, even with oracle evidence spans. Random K2 remains a strong baseline, especially on clean and external data. Fixed thresholds are not portable. These results are not incidental; they prevent SAFE-KV from becoming an overfit selector story. The stable contribution is broader: full-prefill behavior is a necessary reference point, prefix conditioning is the right baseline, document repair is the coherent repair unit, and budgeted gates must be evaluated against random controls.

\paragraph{How to read the external data.}
External HotpotQA/2Wiki results are valuable because they show that non-prefix drift is not purely synthetic. They should not be read as a leaderboard. Once natural retrieval artifacts, variable document length, and low full-prefill QA quality enter the setup, selector comparisons become less clean. This is exactly why the paper keeps controlled diagnostics as the main evidence and uses external data to test whether the phenomenon survives outside the synthetic setting.

\paragraph{What SAFE-KV claims.}
SAFE-KV claims that non-prefix cache reuse can change generated answers; that full-prefill behavior is the right behavioral oracle; that prefix-conditioned document caches are a strong but imperfect baseline; that span-level repair is unreliable; that document-level repair is coherent; and that budgeted gates expose quality--risk trade-offs under random controls. It does not claim production latency gains, universal selector dominance, replacement of serving systems, SOTA QA, learned-gate optimality, or span-level repair success.
""",
        "08_limitations.tex": r"""
\section{Limitations}

SAFE-KV is not a production serving benchmark. We do not report measured latency, time-to-first-token, throughput, memory bandwidth, or scheduler-level performance. Patched-token ratio, estimated recomputation ratio, and estimated prefill saving are accounting proxies only.

The controlled diagnostic data is synthetic by design. It is useful because it isolates conflict, multi-hop, boundary, and noisy-retrieval factors, but it cannot represent all natural RAG distributions. External HotpotQA/2Wiki examples provide sanity evidence, yet their conversion into document-level prompts is noisy and full-prefill generations can be gold-wrong, especially for small models.

The model scale is limited to Qwen2.5-0.5B, Qwen2.5-1.5B, and SmolLM2-1.7B. We do not claim evidence for Qwen7B or larger production deployments. We also do not integrate with vLLM, LMCache, CacheBlend, KVLink, or other serving systems.

Finally, SAFE-KV does not show universal semantic selector dominance. Query and entity selectors help under controlled noisy diagnostics, but random K2 remains strong and external results are mixed. Budgeted gates should be interpreted as calibrated safety analyses, not final deployment policies.
""",
    }
    for name, text in section_texts.items():
        write_text(PAPER / "sections" / name, text)


def write_tables() -> None:
    write_table1()
    write_table2()
    write_table3()
    write_table4()
    write_table5()
    write_appendix_tables()


def write_table1() -> None:
    rows = read_csv(RESULTS / "table1_composition_ablation.csv")
    wanted = ["doc_only_naive_global", "prefix_plus_naive_global", "prefix_conditioned_naive_global"]
    table_rows = [
        {
            "method": METHOD_LABELS[row["method"]],
            "kl": row["avg_kl"],
            "top1": row["top1"],
            "top10": row["top10"],
        }
        for row in rows
        if row["method"] in wanted
    ]
    write_text(
        PAPER / "tables/table1_composition_ablation.tex",
        latex_table(
            table_rows,
            [("method", "Method", "s"), ("kl", "KL", "f3"), ("top1", "Top-1", "f2"), ("top10", "Top-10", "f2")],
            caption="Composition ablation on the clean diagnostic set. Prefix-conditioned document composition is far safer than doc-only or prefix-plus composition, but it is still not exact.",
            label="tab:composition",
            align="lrrr",
        ),
    )


def write_table2() -> None:
    rows = {row["method"]: row for row in read_csv(RESULTS / "table2_repair_granularity.csv")}
    base = {row["method"]: row for row in read_csv(RESULTS / "table1_composition_ablation.csv")}["prefix_conditioned_naive_global"]
    patch = aggregate_patch_rows(ROOT / "results_qwen05_100/patch_recompute_metrics.csv")
    ordered = [
        ("Base", base),
        ("Span", patch.get("oracle_evidence_span_patch") or rows["oracle_evidence_span_window_0"]),
        ("Span+16", rows["oracle_evidence_span_window_16"]),
        ("S+C suffix", rows["oracle_support_and_conflict_suffix_patch"]),
        ("Matched random", rows["random_patch_same_budget::oracle_support_and_conflict_suffix_patch"]),
        ("Oracle doc", patch.get("oracle_evidence_doc_patch") or rows["oracle_evidence_doc_patch"]),
        ("Full-doc sanity", patch.get("full_doc_cache_patch_sanity")),
    ]
    table_rows = [
        {
            "unit": label,
            "kl": source["avg_kl"],
            "top1": source["top1"],
            "patch": source.get("patch_ratio", "0"),
        }
        for label, source in ordered
        if source
    ]
    write_text(
        PAPER / "tables/table2_repair_granularity.tex",
        latex_table(
            table_rows,
            [("unit", "Repair unit", "s"), ("kl", "KL", "f3"), ("top1", "Top-1", "f2"), ("patch", "Patch", "f2")],
            caption="Repair granularity comparison. Document-level repair is coherent; isolated span/window/suffix repair is weaker and often close to matched random patching.",
            label="tab:granularity",
            align="lrrr",
        ),
    )


def write_table3() -> None:
    rows = read_csv(RESULTS / "table3_answer_level_synthetic.csv")
    grouped = {(r["model"], r["split"], r["method"]): r for r in rows}
    table_rows = []
    for model in ["qwen05", "qwen15"]:
        for split in ["clean", "noisy"]:
            base = grouped[(model, split, "prefix_conditioned_naive_global")]
            oracle = grouped[(model, split, "oracle_evidence_doc_patch")]
            query = grouped[(model, split, "query_similarity_doc_patch_k2")]
            entity = grouped[(model, split, "entity_overlap_doc_patch_k2")]
            gate = grouped[(model, split, "safe_gate_t0.60")]
            random = grouped[(model, split, "random_doc_patch_k2_seeded")]
            table_rows.append(
                {
                    "model": "Qwen0.5B" if model == "qwen05" else "Qwen1.5B",
                    "split": split,
                    "base": base["answer_equivalence"],
                    "oracle": oracle["answer_equivalence"],
                    "qe": f"{fnum(query['answer_equivalence'])}/{fnum(entity['answer_equivalence'])}",
                    "gate": gate["answer_equivalence"],
                    "random": random["answer_equivalence"],
                    "wrong": base["changed_wrong"],
                }
            )
    write_text(
        PAPER / "tables/table3_answer_level_summary.tex",
        latex_table(
            table_rows,
            [
                ("model", "Model", "s"),
                ("split", "Split", "s"),
                ("base", "Base", "f2"),
                ("oracle", "Oracle", "f2"),
                ("qe", "Query/Entity", "s"),
                ("gate", "Gate .60", "f2"),
                ("random", "Random K2", "f2"),
                ("wrong", "Wrong changes", "s"),
            ],
            caption="Answer-level preservation on controlled diagnostics. Values are exact answer equivalence to full prefill except the final column, which counts base-composed answers that changed from full prefill and were gold-wrong. Document-level repair reduces changed behavior, especially in noisy diagnostics, while random K2 remains a strong required control.",
            label="tab:answer-summary",
            align="llrrrrrr",
            star=True,
        ),
    )


def write_table4() -> None:
    answer_paths = {
        ("qwen05", "noisy"): ROOT / "results_qwen05_100_noisy_answer/answer_eval_metrics.csv",
        ("qwen15", "noisy"): ROOT / "results_qwen15_100_noisy_answer/answer_eval_metrics.csv",
        ("smollm17", "noisy"): ROOT / "results_smollm17_noisy_answer/answer_eval_metrics.csv",
        ("qwen05", "external"): ROOT / "results_qwen05_external_answer/answer_eval_metrics.csv",
        ("qwen15", "external"): ROOT / "results_qwen15_external_answer/answer_eval_metrics.csv",
        ("smollm17", "external"): ROOT / "results_smollm17_external_answer/answer_eval_metrics.csv",
    }
    table_rows = []
    for model, label, split in [
        ("qwen05", "Qwen0.5B", "noisy"),
        ("qwen15", "Qwen1.5B", "noisy"),
        ("smollm17", "SmolLM2", "noisy"),
        ("qwen05", "Qwen0.5B", "external"),
        ("qwen15", "Qwen1.5B", "external"),
        ("smollm17", "SmolLM2", "external"),
    ]:
        summary = answer_summary(answer_paths[(model, split)])
        full = summary["full_prefill"]
        base = summary["prefix_conditioned_naive_global"]
        random = summary["random_doc_patch_k2_seeded"]
        repairs = [
            summary[m]["answer_equivalence"]
            for m in ["oracle_evidence_doc_patch", "query_similarity_doc_patch_k2", "entity_overlap_doc_patch_k2", "safe_gate_t0.60"]
        ]
        table_rows.append(
            {
                "model": label,
                "data": "Noisy diag." if split == "noisy" else "External",
                "full_em": full.get("gold_em", ""),
                "base": base["answer_equivalence"],
                "best": max(float(x) for x in repairs),
                "random": random["answer_equivalence"],
            }
        )
    write_text(
        PAPER / "tables/table4_cross_model_and_external_summary.tex",
        latex_table(
            table_rows,
            [
                ("model", "Model", "s"),
                ("data", "Data", "s"),
                ("full_em", "Full EM", "f2"),
                ("base", "Base Eq.", "f2"),
                ("best", "Best repair Eq.", "f2"),
                ("random", "Random K2 Eq.", "f2"),
            ],
            caption="Cross-model and external sanity summary. Eq. denotes answer equivalence to full prefill. External data confirms drift is not synthetic-only, but random K2 remains competitive and gold quality is noisy.",
            label="tab:cross-external",
            align="llrrrr",
            star=True,
        ),
    )


def answer_summary(path: Path) -> dict[str, dict[str, float]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(path):
        groups[row["method"]].append(row)
    out: dict[str, dict[str, float]] = {}
    for method, rows in groups.items():
        n = len(rows)
        out[method] = {
            "answer_equivalence": sum(1.0 if r["answer_equivalence_to_full_prefill"].lower() == "true" else 0.0 for r in rows) / n,
            "gold_em": sum(1.0 if r["gold_exact_match"].lower() == "true" else 0.0 for r in rows) / n,
            "gold_f1": sum(float(r["gold_token_f1"]) for r in rows) / n,
        }
    return out


def write_table5() -> None:
    rows = read_csv(RESULTS / "heldout_gate_calibration_metrics.csv")
    table_rows = []
    for row in rows:
        if row["target_budget"] not in {"0.25", "0.4", "0.40"}:
            continue
        if row["dataset"] not in {"diagnostic_100_noisy", "external_multihop_100"}:
            continue
        table_rows.append(
            {
                "model": "Qwen0.5B" if row["model"] == "qwen05" else "Qwen1.5B",
                "data": "Noisy" if row["dataset"] == "diagnostic_100_noisy" else "External",
                "target": row["target_budget"],
                "actual": row["patched_token_ratio"],
                "gate": row["answer_equivalence_to_full_prefill"],
                "random": row["random_gate_mean_answer_equivalence"],
                "pct": row["percentile_vs_random"],
            }
        )
    write_text(
        PAPER / "tables/table5_budget_gate_summary.tex",
        latex_table(
            table_rows,
            [
                ("model", "Model", "s"),
                ("data", "Data", "s"),
                ("target", "Target patch", "f2"),
                ("actual", "Actual patch", "f2"),
                ("gate", "Gate Eq.", "f2"),
                ("random", "Random Eq.", "f2"),
                ("pct", "Rand. pct.", "f2"),
            ],
            caption="Held-out budget-gate calibration. Target/actual patch columns report patched-token budget, Gate/Random report answer equivalence, and Rand. pct. is the gate percentile against matched random seeds. Gates expose quality--budget trade-offs, but external transfer remains mixed.",
            label="tab:budget-summary",
            align="llrrrrr",
            star=True,
        ),
    )


def aggregate_patch_rows(path: Path) -> dict[str, dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(path):
        groups[row["method"]].append(row)
    out: dict[str, dict[str, str]] = {}
    for method, rows in groups.items():
        out[method] = {
            "avg_kl": str(sum(float(r["first_token_kl_full_to_method"]) for r in rows) / len(rows)),
            "top1": str(sum(1.0 if r["top1_match"].lower() == "true" else 0.0 for r in rows) / len(rows)),
            "top10": str(sum(float(r["top10_overlap"]) for r in rows) / len(rows)),
            "patch_ratio": str(sum(float(r["patched_token_ratio"]) for r in rows) / len(rows)),
        }
    return out


def write_appendix_tables() -> None:
    write_full_csv_table(
        RESULTS / "table1_composition_ablation.csv",
        PAPER / "tables/appendix_full_composition_ablation.tex",
        "Full composition ablation, including local/global variants.",
        "tab:app-composition",
        ["method", "avg_kl", "top1", "top10", "patch_ratio"],
    )
    write_full_csv_table(
        RESULTS / "table2_repair_granularity.csv",
        PAPER / "tables/appendix_full_repair_granularity.tex",
        "Full repair granularity table with span windows, suffixes, and matched random baselines.",
        "tab:app-repair",
        ["method", "avg_kl", "top1", "top10", "patch_ratio"],
    )
    write_full_csv_table(
        RESULTS / "table3_answer_level_synthetic.csv",
        PAPER / "tables/appendix_full_answer_level_synthetic.tex",
        "Full synthetic answer-level table.",
        "tab:app-synthetic",
        ["model", "split", "method", "answer_equivalence", "changed_wrong", "patch_ratio"],
    )
    write_full_csv_table(
        RESULTS / "table4_answer_level_external.csv",
        PAPER / "tables/appendix_full_external_sanity.tex",
        "Full external HotpotQA/2Wiki sanity table.",
        "tab:app-external",
        ["model", "method", "answer_equivalence", "gold_em", "gold_f1", "changed_wrong", "patch_ratio"],
    )
    write_full_csv_table(
        RESULTS / "heldout_gate_calibration_metrics.csv",
        PAPER / "tables/appendix_heldout_gate_calibration.tex",
        "Held-out gate calibration details.",
        "tab:app-heldout",
        ["model", "dataset", "target_budget", "patched_token_ratio", "answer_equivalence_to_full_prefill", "random_gate_mean_answer_equivalence", "percentile_vs_random"],
    )
    write_full_csv_table(
        RESULTS / "table7_cost_accounting.csv",
        PAPER / "tables/appendix_cost_accounting.tex",
        "Cost accounting with recomputation-budget proxies.",
        "tab:app-cost",
        ["model", "dataset", "method", "answer_equivalence_to_full_prefill", "changed_wrong_rate", "patched_token_ratio", "estimated_prefill_saving"],
    )


def write_full_csv_table(path: Path, out: Path, caption: str, label: str, fields: list[str]) -> None:
    rows = read_csv(path)
    capped = rows[:40]
    table_rows = []
    for row in capped:
        display = {}
        for field in fields:
            value = row.get(field, "")
            if field == "method":
                value = METHOD_LABELS.get(value, value.replace("_", " "))
            display[field] = value
        table_rows.append(display)
    cols = []
    for field in fields:
        kind = "f2" if any(token in field for token in ["kl", "top", "ratio", "equivalence", "em", "f1", "saving", "budget"]) else "s"
        cols.append((field, field.replace("_", " "), kind))
    note = ""
    if len(rows) > len(capped):
        note = f"\n% Table truncated to {len(capped)} rows for appendix readability; source CSV has {len(rows)} rows.\n"
    write_text(
        out,
        latex_table(
            table_rows,
            cols,
            caption=caption,
            label=label,
            align="l" * len(cols),
            star=True,
            font_size="footnotesize",
            resize_to_width=True,
        )
        + note,
    )


def write_appendix() -> None:
    appendix = {
        "dataset_details.tex": r"""
\section{Diagnostic Data Construction}
The controlled diagnostic set is designed to expose semantic failure modes rather than to approximate a production traffic distribution. It contains five categories. \emph{Single-evidence} examples contain one sufficient evidence document. \emph{Multi-hop} examples require combining two evidence documents. \emph{Conflict} examples include plausible but incompatible claims, forcing the model to prefer the support document. \emph{Boundary-sensitive} examples place key evidence near document or span boundaries. \emph{Distractor-heavy} examples include irrelevant but lexically related documents.

The noisy diagnostic keeps the same gold evidence but adds additional retrieval distractors. This variant is crucial because clean diagnostics are often saturated: many document-level patches work, including random patches. Noisy retrieval preserves interpretability while making document selection non-trivial.

External HotpotQA and 2WikiMultihopQA examples are filtered to remove yes/no answers and cases without usable supporting evidence. Each context paragraph is mapped to a SAFE-KV document, with supporting titles marked as evidence and a limited number of distractors retained. The external set is intentionally treated as a sanity check because evidence mapping, retrieval order, and full-prefill QA quality are noisier than in the controlled data.

\paragraph{Category intent.}
The categories are deliberately diagnostic rather than natural-frequency labels. Single-evidence examples test whether cache composition can preserve straightforward lookup. Multi-hop examples test whether the composed cache preserves relations that are distributed across documents. Conflict examples test source preference when two plausible documents disagree. Boundary-sensitive examples stress span alignment and repair windows. Distractor-heavy examples test whether irrelevant but lexically related documents perturb behavior. This design lets the paper ask which semantic situations are fragile, rather than only reporting an aggregate error rate.

\paragraph{Noisy retrieval transformation.}
The noisy diagnostic preserves the same questions, gold answers, and evidence documents as the clean set, then injects additional documents that are plausible retrieval results. This creates a controlled version of a common RAG failure mode: the relevant evidence is present, but it is embedded in a less clean context. Because the evidence labels are unchanged, noisy results can be compared directly with clean results. The stronger selector performance under noisy retrieval is therefore interpretable as a selection effect rather than a change in task distribution.

\paragraph{External conversion caveats.}
HotpotQA and 2WikiMultihopQA are not originally cache-composition benchmarks. Their paragraphs become SAFE-KV documents, supporting-fact titles become evidence labels where available, and remaining context paragraphs become distractors. This mapping is useful for sanity checking natural multi-hop prompts, but it is not as controlled as the synthetic diagnostic. Some supporting facts are sentence-level while SAFE-KV repairs at document level; some evidence paragraphs are long; and full-prefill generations can be factually wrong. For this reason, the external experiments are used to test whether drift exists outside the diagnostic distribution, not to claim benchmark superiority.
""",
        "prompt_tokenization.tex": r"""
\section{Prompt Templates and Tokenization}
All answer-level experiments use the \texttt{chat\_rag} prompt format. The plain user content is:
\begin{verbatim}
[Document i | Title: <title>]
<document text>

Question: <question>
Answer with the shortest
exact answer phrase
from the documents.
Answer:
\end{verbatim}
This content is wrapped by the tokenizer's chat template with an added generation prompt. The implementation verifies that the chat template preserves the RAG content verbatim before shifting character ranges.

Token spans are computed by one-pass tokenization of the full rendered prompt with offset mappings. Document block ranges, document text ranges, evidence spans, boundary windows, and query suffix ranges are all derived from these offsets. This avoids retokenizing substrings independently and makes cache slicing consistent with the actual model input.

\paragraph{Why one-pass tokenization matters.}
KV cache slicing is sensitive to exact token boundaries. Retokenizing a document substring can produce a different tokenization at leading spaces, newlines, or chat-template boundaries, which would silently misalign cache slices. SAFE-KV instead tokenizes the full rendered prompt once, maps character offsets to token offsets, and stores all downstream ranges in that coordinate system. This is also why the prompt builder records both document-block ranges and document-text ranges: the block includes titles and delimiters, while text ranges support evidence-span diagnostics.

\paragraph{Answer instruction.}
The answer instruction asks for the shortest exact answer phrase from the documents. This keeps answer-level comparison focused: deterministic generations are short, normalization is meaningful, and changed answers usually correspond to evidence or source-selection changes rather than long-form stylistic variation. The instruction also reduces noise in full-prefill gold metrics, though it does not eliminate model mistakes on external data.

\paragraph{Stop behavior.}
Generation stops on newlines and on prompt-like markers such as \texttt{Human:}, \texttt{[Document}, \texttt{Question:}, and \texttt{Answer:}. These stops prevent pathological continuation into a new synthetic prompt and make answer equivalence easier to interpret. The same stops are used for full-prefill and composed-cache runs.
""",
        "cache_sanity.tex": r"""
\section{Cache Mechanics Sanity Checks}
The implementation includes generation sanity checks comparing manual cached decoding with Hugging Face generation. The matching mode uses manual position IDs. Sequential prefill sanity verifies that splitting the prompt into pieces and feeding them in order recovers full-prefill behavior. Full-document patch sanity replaces all document cache slices with full-prefill slices and recovers the full-prefill first-token behavior, validating the patching mechanism.

These checks are important because the central paper claim is semantic rather than mechanical. If manual decoding, position IDs, or cache slicing were wrong, drift could be explained by an implementation artifact. The sanity suite instead narrows the interpretation: full prefill, sequential prefill, and full-document patching agree when they should, so the remaining discrepancies arise from the conditioning assumptions made by non-prefix composition.

\paragraph{Position IDs and cache length.}
All answer-level experiments use the validated manual-position-id path. This is important for non-prefix composition because the cache can be assembled from pieces whose original local positions differ from their positions in the final prompt. SAFE-KV verifies expected cache lengths before decoding and treats length mismatches as errors rather than silently continuing. This guardrail prevents accidental comparisons between prompts with different effective contexts.

\paragraph{Full-document patch sanity.}
The full-document patch sanity condition is the most direct check of repair mechanics. Starting from a composed cache, the implementation replaces every document slice with the corresponding full-prefill slice. If patching is correct, the resulting first-token behavior should match full prefill. The observed near-zero KL for this sanity method establishes that document slices can be patched without corrupting the rest of the cache, so weaker span/window results reflect repair granularity rather than a broken patch operator.

\paragraph{Sequential prefill sanity.}
Sequential prefill is a second control. The prompt is split and fed through the model in order while preserving the past-key-value state. Agreement with one-shot full prefill confirms that the generation wrapper, attention mask, and position-id handling can reproduce the model's normal causal computation when the causal history is correct.
""",
        "algorithms.tex": r"""
\section{Algorithms}

\paragraph{Algorithm 1: prefix-conditioned document composition.}
For each example, SAFE-KV renders the same chat/instruction prefix used in the full RAG prompt. For every document $d_i$, it runs a prefill pass over $(p,d_i)$ and stores only the cache slice corresponding to the document block. At evaluation time, it assembles the static prefix cache, the cached document slices, and the query suffix into a single cache, then decodes with manual position IDs. This is stronger than doc-only reuse because every document sees the instruction wrapper and answer policy, but it still omits cross-document causal interactions.

\begin{enumerate}
    \item Render the full prompt and record token ranges for prefix, each document, and query suffix.
    \item For each document $d_i$, render $(p,d_i)$ using the same chat template and prefill with cache enabled.
    \item Extract the cache slice aligned to the document block.
    \item Concatenate prefix, document slices, and query suffix positions into the composed cache.
    \item Decode deterministically and compare with the full-prefill oracle.
\end{enumerate}

\paragraph{Algorithm 2: document-level patch repair.}
Document repair starts from the prefix-conditioned composed cache. Given a selected set of document ids, it copies the corresponding document cache slices from the full-prefill oracle into the composed cache. All unselected documents remain composed-cache states. This isolates the effect of recomputing coherent document units while preserving the same prompt, tokenizer ranges, and decoding path.

\begin{enumerate}
    \item Run full prefill and store oracle cache slices for all document ranges.
    \item Build the prefix-conditioned composed cache.
    \item Select documents using oracle evidence labels, query similarity, entity overlap, random K2, or a gate.
    \item Replace selected document slices with full-prefill slices.
    \item Decode and compute answer equivalence, KL, and patched-token ratio.
\end{enumerate}

\paragraph{Algorithm 3: budget-targeted gate.}
Budgeted gates use the existing risk score and existing document repair policy. The target budget is declared before evaluation. Examples are ranked by risk, the expected patch cost is computed from selected document spans, and examples are repaired until the global patched-token ratio approaches the target. Matched random gates use the same target budgets and repeat the selection with many random seeds.

\begin{enumerate}
    \item Compute risk score and patch cost for each example.
    \item Sort examples by decreasing risk.
    \item Select examples until the global patched-token ratio reaches the target budget.
    \item Apply document repair to selected examples and base composition to the rest.
    \item Report actual budget, answer equivalence, changed-and-wrong rate, and random-control percentile.
\end{enumerate}

\paragraph{Algorithm 4: held-out gate calibration.}
Held-out calibration prevents choosing a threshold on the same examples used for evaluation. SAFE-KV deterministically splits examples by id into 30\% calibration and 70\% test. The calibration set determines the risk cutoff needed for a target budget. That cutoff is then applied unchanged to the test examples. The test metrics are compared with matched random gates on the same held-out examples.

\begin{enumerate}
    \item Split examples into calibration and test sets using seed 13.
    \item On calibration examples, find the risk cutoff associated with each target budget.
    \item Apply the cutoff to test examples without retuning.
    \item Compute quality and budget metrics on the test set only.
    \item Compare with matched random gates over the same test set.
\end{enumerate}
""",
        "full_composition_tables.tex": r"""
\section{Full Composition Ablations}
Table~\ref{tab:app-composition} reports all composition variants, including local/global variants omitted from the main paper.
\input{tables/appendix_full_composition_ablation}
""",
        "full_repair_tables.tex": r"""
\section{Full Repair Granularity Results}
Table~\ref{tab:app-repair} reports span windows, suffix repair, support+conflict repair, and matched random baselines.
\input{tables/appendix_full_repair_granularity}

\begin{figure}[h]
\centering
\includegraphics[width=\linewidth]{figures/figure3_repair_granularity.pdf}
\caption{Repair granularity visualization. Human evidence spans are not necessarily causal cache repair units: document-level repair is the coherent unit, while span/window/suffix repair remains close to matched random baselines.}
\label{fig:app-repair}
\end{figure}
""",
        "full_answer_tables.tex": r"""
\section{Full Answer-Level Tables}
Table~\ref{tab:app-synthetic} reports the full synthetic clean/noisy answer-level table, including all main methods and patch ratios.
\input{tables/appendix_full_answer_level_synthetic}
""",
        "external_sanity.tex": r"""
\section{External HotpotQA/2Wiki Sanity}
External multi-hop QA confirms that answer drift is not synthetic-only, but it is noisy. Full-prefill gold EM is low for small models, and random K2 remains competitive. Table~\ref{tab:app-external} reports the full external answer-level table. Separate subset-analysis files under \texttt{results\_paper/} report full-prefill-correct and high-F1 subsets.
\input{tables/appendix_full_external_sanity}

\begin{figure}[h]
\centering
\includegraphics[width=\linewidth]{figures/figure5_external_sanity.pdf}
\caption{External sanity summary. External HotpotQA/2Wiki confirms answer drift and partial repair, but random K2 remains competitive; this is sanity evidence, not a selector-dominance benchmark.}
\label{fig:app-external}
\end{figure}

\paragraph{Interpreting external gold scores.}
The external setting is intentionally conservative. If full prefill is gold-wrong, a composed-cache method can appear to improve gold EM by changing the model's answer, but that is not a safety improvement. Conversely, a method can preserve full-prefill behavior and still be gold-wrong. For this reason, the external analysis reports gold metrics but treats answer equivalence to full prefill as the primary safety metric.

\paragraph{Why random remains strong.}
External examples often contain a small number of long, evidence-rich documents. Coherent recomputation of two random documents can therefore patch at least one useful evidence paragraph surprisingly often. This is why the paper does not claim selector dominance on external data. The positive external claim is narrower: non-prefix answer drift occurs in natural multi-hop prompts, and document-level repair can partially restore full-prefill behavior.

\paragraph{Subset analysis.}
The full-prefill-correct subset analysis is included to address the objection that preserving an incorrect full-prefill answer may not be meaningful. The subset analysis asks whether the same trends hold when full prefill is more likely to be a useful behavioral target: exact-match correct, answer-contains-gold, or high-F1 examples. Small subset sizes are marked explicitly in the CSV/Markdown outputs.
""",
        "heldout_gate.tex": r"""
\section{Held-Out Gate Calibration}
Held-out gate calibration uses a deterministic split by example id: 30\% calibration and 70\% test. The calibration set determines the risk cutoff for a target patched-token budget. The test set reports answer equivalence, changed-and-wrong rate, actual patched-token ratio, and matched random controls. Table~\ref{tab:app-heldout} gives the detailed results.
\input{tables/appendix_heldout_gate_calibration}
""",
        "cost_accounting.tex": r"""
\section{Cost Accounting}
The cost accounting is intentionally a proxy analysis. We define estimated recomputation ratio as patched-token ratio, and estimated prefill saving as one minus patched-token ratio. These quantities do not include kernel efficiency, cache transfer, batching, scheduling, or serving-system overhead. Table~\ref{tab:app-cost} reports the full proxy table.
\input{tables/appendix_cost_accounting}

\paragraph{What the proxy captures.}
Patched-token ratio estimates how much of the document portion of the prompt would need recomputation if the system trusted cached states for unpatched tokens. It is directly tied to the semantic repair operation: a lower ratio means the method changes fewer cached document states, while a higher ratio means it recomputes more of the full-prefill document context.

\paragraph{What the proxy does not capture.}
The proxy does not include time to retrieve cache blocks, memory transfer overhead, batching effects, kernel launch costs, or serving-scheduler interactions. It also does not account for model-specific differences in attention kernels. The correct reading is therefore: SAFE-KV reports behavior preservation as a function of recomputation budget, not end-to-end latency. A production system would need to combine this semantic budget analysis with a real serving benchmark.

\paragraph{Why include the proxy anyway.}
Without a cost proxy, document repair could trivially choose full prefill for every example. Patched-token ratio makes the trade-off visible: gates can choose lower budgets with weaker preservation, while oracle/query/entity K2 repair often improves preservation with larger patch ratios. This is the evidence needed to discuss quality-budget trade-offs without overclaiming speed.
""",
        "failure_examples.tex": r"""
\section{Failure Examples}
The result directories include per-run \texttt{answer\_failure\_analysis.md} files. We include representative cases to make the claim boundary concrete. They are not meant as cherry-picked wins; they illustrate why the paper emphasizes behavior preservation, document repair, and random controls.

\paragraph{Conflict drift repaired by semantic selection.}
Example \texttt{conflict\_0018\_noisy} asks: ``According to the official schedule, when does the Mariton observatory open?'' The gold answer is \emph{10 AM}. One distractor document is an old visitor blog saying the observatory opens at \emph{1 PM}; the evidence document is the official schedule saying it opens at \emph{10 AM}. Full prefill answers ``10'', while prefix-conditioned composition answers ``1 PM'' with first-token KL 3.44. Query-similarity repair and the fixed 0.60 gate recover the full-prefill answer, while the random K2 draw in this run does not. This is the cleanest kind of SAFE-KV failure: the composed cache preserves fluent local evidence but changes the source preference that full prefill established.

\paragraph{Multi-hop drift from lost relation structure.}
Example \texttt{multihop\_0015\_noisy} asks: ``Where was the designer of Project Caldrin born?'' One evidence document states that Project Caldrin was designed by Orin Vale; another states that Orin Vale was born in Aster Port. Full prefill answers \emph{Aster Port}. Prefix-conditioned composition instead emits an unrelated distractor sentence about a garden survey, with first-token KL 2.98. Oracle, query, entity, and random document repair recover \emph{Aster Port}, while the 0.60 gate does not repair this example. The case illustrates why multi-hop examples are difficult: neither evidence document alone is the answer unless the relation across documents is preserved.

\paragraph{External natural-data drift.}
In HotpotQA example \texttt{hotpotqa\_7385}, the question asks who founded the fitness magazine for which Elizabeth Austin wrote. The supporting documents connect Elizabeth Austin to \emph{Shape} and \emph{Shape} to founder Christine MacIntyre. Qwen1.5B full prefill answers \emph{Christine MacIntyre}. Prefix-conditioned composition answers \emph{Joe Weider}, with first-token KL 10.16. Oracle, query, entity, gate, and random document repair recover the full-prefill answer. This example shows that answer drift is not purely synthetic.

\paragraph{External random beating semantic selectors.}
In HotpotQA example \texttt{hotpotqa\_4537}, the question asks which adopted name of African-American activist Allen Donaldson co-founded the Black Power movement. The gold answer is \emph{Hakim Abdullah Jamal}; Qwen1.5B full prefill answers \emph{Hakim Jamal}. Prefix-conditioned composition answers \emph{Malcolm X}, with KL 4.52. Oracle repair, the 0.60 gate, and this run's random K2 repair recover the full-prefill answer, but query and entity selectors do not. This motivates the paper's caveat: external natural data supports the existence of drift and partial repair, but not universal semantic-selector superiority.

\paragraph{How to use these examples.}
The examples support the main text in three ways. First, they make clear that non-prefix drift can select the wrong evidence source, not merely change wording. Second, they show why document-level repair is a coherent unit: recomputing a full evidence document can repair source framing or cross-document relation structure. Third, they show why random controls are mandatory. Sometimes coherent document repair itself is the key ingredient, and semantic selectors must be compared against that strong baseline.
""",
        "related_work_comparison.tex": r"""
\section{Related Work Comparison}
\label{sec:app-related-comparison}

Table~\ref{tab:app-related-comparison} summarizes the distinction between SAFE-KV and adjacent cache-reuse work. The table is intentionally coarse: many systems support multiple deployment modes, and SAFE-KV is not a replacement for them. The point is to clarify the paper's evaluation target.

\begin{table*}[h]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{cccccc}
\toprule
Work & Reuse setting & Main goal & Full-prefill safety oracle? & Repair granularity? & Matched random controls? \\
\midrule
vLLM/PagedAttention & serving cache management & throughput/memory efficiency & no & no & no \\
LMCache & cache storage/transfer/reuse layer & system reuse & no & no & no \\
Prompt Cache & modular prompt reuse & latency reduction & limited & no & no \\
CacheBlend & non-prefix chunk fusion & serving efficiency + quality & partially, systems-focused & selective token recompute & not this framing \\
KVLink & independent document cache reuse & speed + QA with adjustment/training & limited & no & no \\
SAFE-KV & non-prefix RAG document composition & semantic safety analysis & yes & yes, span vs document & yes \\
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Positioning against adjacent cache-reuse work. SAFE-KV's novelty is the semantic-safety framing: full-prefill behavior preservation, repair-granularity analysis, answer-level drift, and matched random controls.}
\label{tab:app-related-comparison}
\end{table*}
""",
        "artifact_checklist.tex": r"""
\section{Citation and Artifact Checklist}
The main artifact sources are the SAFE-KV configs, answer-eval CSVs, budget-gate CSVs, and paper-table CSVs under \texttt{results\_paper/}. The primary entrypoints are \path{scripts/make_paper_tables.py}, \path{scripts/make_cost_accounting_tables.py}, and \path{scripts/build_arr_quality_draft.py}.
The bibliography was checked against arXiv or official project pages where possible; see \texttt{paper/CITATION\_VERIFICATION.md}.

\paragraph{Key configs.}
The main synthetic runs use \texttt{configs/v0\_qwen05\_100.yaml}, \texttt{configs/v0\_qwen05\_100\_noisy.yaml}, \texttt{configs/v0\_qwen15\_100.yaml}, and \texttt{configs/v0\_qwen15\_100\_noisy.yaml}. External runs use \texttt{configs/v0\_qwen05\_external.yaml}, \texttt{configs/v0\_qwen15\_external.yaml}, and \texttt{configs/v0\_smollm17\_external.yaml}. Cross-family noisy runs use \texttt{configs/v0\_smollm17\_noisy.yaml}.

\paragraph{Key result directories.}
Answer-level results are stored in \texttt{results\_qwen05\_100\_answer}, \texttt{results\_qwen05\_100\_noisy\_answer}, \texttt{results\_qwen15\_100\_answer}, \texttt{results\_qwen15\_100\_noisy\_answer}, \texttt{results\_qwen05\_external\_answer}, \texttt{results\_qwen15\_external\_answer}, \texttt{results\_smollm17\_noisy\_answer}, and \texttt{results\_smollm17\_external\_answer}. Paper-facing consolidated tables are under \texttt{results\_paper/}.

\paragraph{Claim audit.}
The paper intentionally records unsupported claims. It does not claim production latency, time-to-first-token, throughput improvements, SOTA QA, Qwen7B evidence, or universal selector dominance. This audit is part of the artifact because it constrains how the results should be used in later drafts.
""",
    }
    for name, text in appendix.items():
        write_text(PAPER / "appendix" / name, text)


def write_bibliography() -> None:
    existing = PAPER / "references.bib"
    if existing.exists() and existing.read_text(encoding="utf-8").count("\n@") >= 50:
        return
    write_text(
        PAPER / "references.bib",
        r"""
@misc{kwon2023efficientmemorymanagementlarge,
  title={Efficient Memory Management for Large Language Model Serving with PagedAttention},
  author={Kwon, Woosuk and Li, Zhuohan and Zhuang, Siyuan and Sheng, Ying and Zheng, Lianmin and Yu, Cody Hao and Gonzalez, Joseph E. and Zhang, Hao and Stoica, Ion},
  year={2023},
  eprint={2309.06180},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2309.06180}
}

@misc{liu2025lmcacheefficientkvcache,
  title={LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference},
  author={Liu, Yuhan and Cheng, Yihua and Yao, Jiayi and An, Yuwei and Chen, Xiaokun and Feng, Shaoting and Huang, Yuyang and Shen, Samuel and Zhang, Rui and Du, Kuntai and Jiang, Junchen},
  year={2025},
  eprint={2510.09665},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2510.09665}
}

@misc{gim2024promptcachemodularattention,
  title={Prompt Cache: Modular Attention Reuse for Low-Latency Inference},
  author={Gim, In and Chen, Guojun and Lee, Seung-seob and Sarda, Nikhil and Khandelwal, Anurag and Zhong, Lin},
  year={2024},
  eprint={2311.04934},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2311.04934}
}

@misc{yao2025cacheblendfastlargelanguage,
  title={CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusion},
  author={Yao, Jiayi and Li, Hanchen and Liu, Yuhan and Ray, Siddhant and Cheng, Yihua and Zhang, Qizheng and Du, Kuntai and Lu, Shan and Jiang, Junchen},
  year={2025},
  eprint={2405.16444},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2405.16444}
}

@misc{yang2025kvlinkacceleratinglargelanguage,
  title={KVLink: Accelerating Large Language Models via Efficient KV Cache Reuse},
  author={Yang, Jingbo and Hou, Bairu and Wei, Wei and Bao, Yujia and Chang, Shiyu},
  year={2025},
  eprint={2502.16002},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2502.16002}
}

@misc{liu2024kivituningfreeasymmetric2bit,
  title={KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache},
  author={Liu, Zirui and Yuan, Jiayi and Jin, Hongye and Zhong, Shaochen and Xu, Zhaozhuo and Braverman, Vladimir and Chen, Beidi and Hu, Xia},
  year={2024},
  eprint={2402.02750},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2402.02750}
}

@misc{liu2023scissorhandsexploitingpersistenceimportance,
  title={Scissorhands: Exploiting the Persistence of Importance Hypothesis for LLM KV Cache Compression at Test Time},
  author={Liu, Zichang and Desai, Aditya and Liao, Fangshuo and Wang, Weitao and Xie, Victor and Xu, Zhaozhuo and Kyrillidis, Anastasios and Shrivastava, Anshumali},
  year={2023},
  eprint={2305.17118},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2305.17118}
}

@misc{lewis2021retrievalaugmentedgenerationknowledgeintensivenlp,
  title={Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks},
  author={Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and Kuttler, Heinrich and Lewis, Mike and Yih, Wen-tau and Rocktaschel, Tim and Riedel, Sebastian and Kiela, Douwe},
  year={2021},
  eprint={2005.11401},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2005.11401}
}

@misc{yang2018hotpotqadatasetdiverseexplainable,
  title={HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering},
  author={Yang, Zhilin and Qi, Peng and Zhang, Saizheng and Bengio, Yoshua and Cohen, William W. and Salakhutdinov, Ruslan and Manning, Christopher D.},
  year={2018},
  eprint={1809.09600},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/1809.09600}
}

@misc{ho2020constructingmultihopqadataset,
  title={Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps},
  author={Ho, Xanh and Nguyen, Anh-Khoa Duong and Sugawara, Saku and Aizawa, Akiko},
  year={2020},
  eprint={2011.01060},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2011.01060}
}

@misc{qwen2025qwen25technicalreport,
  title={Qwen2.5 Technical Report},
  author={{Qwen Team} and Yang, An and Yang, Baosong and Zhang, Beichen and Hui, Binyuan and Zheng, Bo and Yu, Bowen and Li, Chengyuan and Liu, Dayiheng and Huang, Fei and Wei, Haoran and Lin, Huan and Yang, Jian and Tu, Jianhong and Zhang, Jianwei and Yang, Jianxin and Yang, Jiaxi and Zhou, Jingren and Lin, Junyang and Dang, Kai and Lu, Keming and Bao, Keqin and Yang, Kexin and Yu, Le and Li, Mei and Xue, Mingfeng and Zhang, Pei and Zhu, Qin and Men, Rui and Lin, Runji and Li, Tianhao and Tang, Tianyi and Xia, Tingyu and Ren, Xingzhang and Ren, Xuancheng and Fan, Yang and Su, Yang and Zhang, Yichang and Wan, Yu and Liu, Yuqiong and Cui, Zeyu and Zhang, Zhenru and Qiu, Zihan},
  year={2025},
  eprint={2412.15115},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2412.15115}
}

@misc{allal2025smollm2smolgoesbig,
  title={SmolLM2: When Smol Goes Big -- Data-Centric Training of a Small Language Model},
  author={Allal, Loubna Ben and Lozhkov, Anton and Bakouch, Elie and Blazquez, Gabriel Martin and Penedo, Guilherme and Tunstall, Lewis and Marafioti, Andres and Kydlicek, Hynek and Lajarin, Agustin Piqueres and Srivastav, Vaibhav and Lochner, Joshua and Fahlgren, Caleb and Nguyen, Xuan-Son and Fourrier, Clementine and Burtenshaw, Ben and Larcher, Hugo and Zhao, Haojun and Zakka, Cyril and Morlon, Mathieu and Raffel, Colin and von Werra, Leandro and Wolf, Thomas},
  year={2025},
  eprint={2502.02737},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2502.02737}
}

@misc{wolf2020huggingfacestransformersstateoftheartnatural,
  title={HuggingFace's Transformers: State-of-the-art Natural Language Processing},
  author={Wolf, Thomas and Debut, Lysandre and Sanh, Victor and Chaumond, Julien and Delangue, Clement and Moi, Anthony and Cistac, Pierric and Rault, Tim and Louf, Remi and Funtowicz, Morgan and Davison, Joe and Shleifer, Sam and von Platen, Patrick and Ma, Clara and Jernite, Yacine and Plu, Julien and Xu, Canwen and Scao, Teven Le and Gugger, Sylvain and Drame, Mariama and Lhoest, Quentin and Rush, Alexander M.},
  year={2020},
  eprint={1910.03771},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/1910.03771}
}
""",
    )


def write_citation_verification() -> None:
    csv_path = PAPER / "citation_verification.csv"
    if csv_path.exists():
        try:
            rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
            verified = [row for row in rows if row.get("status") == "verified"]
            if len(verified) >= 50:
                return
        except Exception:
            pass
    rows = [
        ("kwon2023efficientmemorymanagementlarge", "PagedAttention/vLLM", "arXiv:2309.06180", "verified via arXiv BibTeX"),
        ("liu2025lmcacheefficientkvcache", "LMCache", "arXiv:2510.09665", "verified via arXiv BibTeX"),
        ("gim2024promptcachemodularattention", "Prompt Cache", "arXiv:2311.04934", "verified via arXiv BibTeX"),
        ("yao2025cacheblendfastlargelanguage", "CacheBlend", "arXiv:2405.16444", "verified via arXiv BibTeX"),
        ("yang2025kvlinkacceleratinglargelanguage", "KVLink", "arXiv:2502.16002", "verified via arXiv BibTeX"),
        ("liu2024kivituningfreeasymmetric2bit", "KIVI", "arXiv:2402.02750", "verified via arXiv BibTeX"),
        ("liu2023scissorhandsexploitingpersistenceimportance", "Scissorhands", "arXiv:2305.17118", "verified via arXiv BibTeX"),
        ("lewis2021retrievalaugmentedgenerationknowledgeintensivenlp", "RAG", "arXiv:2005.11401", "verified via arXiv BibTeX"),
        ("yang2018hotpotqadatasetdiverseexplainable", "HotpotQA", "arXiv:1809.09600", "verified via arXiv BibTeX"),
        ("ho2020constructingmultihopqadataset", "2WikiMultihopQA", "arXiv:2011.01060", "verified via arXiv BibTeX"),
        ("qwen2025qwen25technicalreport", "Qwen2.5", "arXiv:2412.15115", "verified via arXiv BibTeX; long author list normalized"),
        ("allal2025smollm2smolgoesbig", "SmolLM2", "arXiv:2502.02737", "verified via arXiv BibTeX; accents normalized for LaTeX robustness"),
        ("wolf2020huggingfacestransformersstateoftheartnatural", "Transformers", "arXiv:1910.03771", "verified via arXiv BibTeX"),
    ]
    lines = ["# Citation Verification", "", "| key | topic | source | status |", "|---|---|---|---|"]
    lines += [f"| `{k}` | {topic} | {source} | {status} |" for k, topic, source, status in rows]
    lines += ["", "No unresolved citation-verification markers are intentionally left in `references.bib`."]
    write_text(PAPER / "CITATION_VERIFICATION.md", "\n".join(lines))


def write_figures() -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        plt.rcParams["pdf.fonttype"] = 42
        plt.rcParams["ps.fonttype"] = 42
    except Exception as exc:  # pragma: no cover
        write_text(PAPER / "FIGURE_STATUS.md", f"# Figure Status\n\nFigure generation failed: `{exc}`")
        return

    fig_dir = PAPER / "figures"
    fig_dir.mkdir(exist_ok=True)

    # Figure 1: conceptual setup.
    fig, ax = plt.subplots(figsize=(10.5, 3.65))
    ax.axis("off")
    boxes = [
        (0.04, 0.64, 0.24, 0.22, "Full prefill\nprefix + docs + query", "#dcecff", "#2f5f9f"),
        (0.39, 0.64, 0.24, 0.22, "Coherent full\nKV cache", "#dcecff", "#2f5f9f"),
        (0.04, 0.18, 0.24, 0.22, "Prefix-conditioned\ndocument caches", "#fff0d8", "#a65e00"),
        (0.39, 0.18, 0.24, 0.22, "Composed non-prefix\ncache", "#ffe2d9", "#b4492d"),
        (0.72, 0.18, 0.22, 0.22, "Document repair\nor budget gate", "#ddf2df", "#3f8b45"),
    ]
    for x, y, w, h, text, face, edge in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=True, facecolor=face, edgecolor=edge, lw=1.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)
    arrow = dict(arrowstyle="->", lw=1.8, color="#333333")
    ax.annotate("", xy=(0.39, 0.75), xytext=(0.28, 0.75), arrowprops=arrow)
    ax.annotate("", xy=(0.39, 0.29), xytext=(0.28, 0.29), arrowprops=arrow)
    ax.annotate("", xy=(0.72, 0.29), xytext=(0.63, 0.29), arrowprops=arrow)
    ax.annotate("compare behavior\nto full prefill", xy=(0.51, 0.55), xytext=(0.51, 0.48), ha="center", fontsize=10.5, color="#8a3a00")
    ax.annotate("", xy=(0.51, 0.64), xytext=(0.51, 0.40), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#8a3a00"))
    ax.text(0.16, 0.90, "coherent state", ha="center", fontsize=10, color="#2f5f9f", weight="bold")
    ax.text(0.16, 0.10, "reused/stale state", ha="center", fontsize=10, color="#a65e00", weight="bold")
    ax.text(0.83, 0.10, "repaired state", ha="center", fontsize=10, color="#3f8b45", weight="bold")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure1_setup.pdf")
    plt.close(fig)

    # Figure 2: category drift.
    drift = [r for r in read_csv(fig_dir / "figure2_category_drift.csv") if r["split"] == "noisy" and r["model"] in {"qwen05", "qwen15"}]
    categories = ["single_evidence", "multi_hop", "conflict", "boundary_sensitive", "distractor_heavy"]
    label_map = {"single_evidence": "single", "multi_hop": "multi-hop", "conflict": "conflict", "boundary_sensitive": "boundary", "distractor_heavy": "distractor"}
    vals = {model: [] for model in ["qwen05", "qwen15"]}
    for model in vals:
        by_cat = {r["category"]: float(r["changed_rate"]) for r in drift if r["model"] == model}
        vals[model] = [by_cat.get(c, 0.0) for c in categories]
    x = np.arange(len(categories))
    fig, ax = plt.subplots(figsize=(7.2, 2.75))
    y = np.arange(len(categories))
    ax.barh(y + 0.18, vals["qwen05"], height=0.34, label="Qwen0.5B", color="#4c78a8")
    ax.barh(y - 0.18, vals["qwen15"], height=0.34, label="Qwen1.5B", color="#f58518")
    ax.set_yticks(y, [label_map[c] for c in categories])
    ax.invert_yaxis()
    ax.set_xlabel("Answer changed from full prefill")
    ax.set_xlim(0, max(max(vals["qwen05"]), max(vals["qwen15"]), 0.1) + 0.12)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure2_category_drift.pdf")
    plt.close(fig)

    # Figure 3: repair granularity.
    gran = {r["method"]: r for r in read_csv(RESULTS / "table2_repair_granularity.csv")}
    base = {r["method"]: r for r in read_csv(RESULTS / "table1_composition_ablation.csv")}["prefix_conditioned_naive_global"]
    patch = aggregate_patch_rows(ROOT / "results_qwen05_100/patch_recompute_metrics.csv")
    repair_items = [
        ("base", base),
        ("span", gran["oracle_evidence_span_window_0"]),
        ("span+16", gran["oracle_evidence_span_window_16"]),
        ("suffix", gran["oracle_support_and_conflict_suffix_patch"]),
        ("random", gran["random_patch_same_budget::oracle_support_and_conflict_suffix_patch"]),
        ("doc", gran["oracle_evidence_doc_patch"]),
        ("full-doc", patch["full_doc_cache_patch_sanity"]),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 2.75))
    ax.bar([x[0] for x in repair_items], [float(x[1]["avg_kl"]) for x in repair_items], color=["#777777", "#72b7b2", "#72b7b2", "#72b7b2", "#b279a2", "#54a24b", "#2f9e44"])
    ax.set_ylabel("First-token KL")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure3_repair_granularity.pdf")
    plt.close(fig)

    # Figure 4: budget gate pareto.
    budget = [r for r in read_csv(RESULTS / "table6_budget_gate_pareto.csv") if r["run"] in {"qwen05_noisy", "qwen15_noisy"}]
    fig, ax = plt.subplots(figsize=(7, 2.85))
    run_labels = {"qwen05_noisy": "Qwen0.5B", "qwen15_noisy": "Qwen1.5B"}
    for run, color in [("qwen05_noisy", "#4c78a8"), ("qwen15_noisy", "#f58518")]:
        rows = sorted([r for r in budget if r["run"] == run], key=lambda r: float(r["actual_budget"]))
        ax.plot([float(r["actual_budget"]) for r in rows], [float(r["answer_equivalence"]) for r in rows], marker="o", color=color, label=f"{run_labels[run]} gate")
        ax.plot([float(r["actual_budget"]) for r in rows], [float(r["random_mean"]) for r in rows], marker="x", ls="--", color=color, alpha=0.7, label=f"{run_labels[run]} random")
    ax.set_xlabel("Patched-token ratio")
    ax.set_ylabel("Answer equivalence")
    ax.set_ylim(0.6, 1.0)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure4_budget_gate_pareto.pdf")
    plt.close(fig)

    # Figure 5: external appendix sanity.
    ext = read_csv(RESULTS / "table4_answer_level_external.csv")
    models = ["qwen05", "qwen15", "smollm17"]
    model_names = {"qwen05": "Qwen0.5B", "qwen15": "Qwen1.5B", "smollm17": "SmolLM2"}
    methods = ["prefix_conditioned_naive_global", "oracle_evidence_doc_patch", "query_similarity_doc_patch_k2", "entity_overlap_doc_patch_k2", "random_doc_patch_k2_seeded"]
    labels = ["base", "oracle", "query", "entity", "random"]
    by = {(r["model"], r["method"]): float(r["answer_equivalence"]) for r in ext}
    x = np.arange(len(models))
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    width = 0.15
    colors = ["#777777", "#54a24b", "#4c78a8", "#72b7b2", "#b279a2"]
    for i, method in enumerate(methods):
        ax.bar(x + (i - 2) * width, [by.get((m, method), 0.0) for m in models], width=width, label=labels[i], color=colors[i])
    ax.set_xticks(x, [model_names[m] for m in models])
    ax.set_ylabel("Answer equivalence")
    ax.set_ylim(0.0, 0.75)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.17))
    fig.tight_layout()
    fig.savefig(fig_dir / "figure5_external_sanity.pdf")
    plt.close(fig)

    write_text(
        PAPER / "FIGURE_STATUS.md",
        """# Figure Status

Generated real PDF figures:

- `figures/figure1_setup.pdf`
- `figures/figure2_category_drift.pdf`
- `figures/figure3_repair_granularity.pdf`
- `figures/figure4_budget_gate_pareto.pdf`
- `figures/figure5_external_sanity.pdf` (appendix)

All figures are generated from existing result CSVs or conceptual paper content. No new model inference is used.
""",
    )


def write_plans_and_reports() -> None:
    write_text(
        PAPER / "BUILD_REPORT.md",
        """# Build Report

## Compile Status

The 8E draft is generated by `scripts/build_arr_quality_draft.py` and is intended to compile with:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

Output PDF: `paper/main.pdf`

## Page Count

- Exact counts should be refreshed after compilation with `pdfinfo main.pdf`.
- The `page:mainend` label is intentionally placed before Limitations so the main-content count excludes the required Limitations section.

## Warnings

- Expected unresolved citations: 0.
- Expected missing figures: 0.
- Remaining layout risks are appendix tables, long paths, and ACL review-mode line numbers.

## Typography Pass

All generated LaTeX tables use centered cells and `\\footnotesize`. Tables are wrapped in `adjustbox` with `max width`, so they can shrink if necessary but are never scaled up.

This file is refreshed after final compilation in the 8E workflow.
""",
    )
    write_text(
        PAPER / "FIGURE_PLAN.md",
        """# Figure Plan

The draft includes four main-paper figures: problem setup, category drift, repair granularity, and budget-quality Pareto. It also includes an appendix external-sanity figure. Final camera-ready polishing may adjust typography, colors, and panel layout, but the data sources and captions are paper-ready.
""",
    )
    write_text(
        PAPER / "APPENDIX_STATUS.md",
        """# Appendix Status

Appendix sections are present:

A. Diagnostic data construction
B. Prompt templates and tokenization
C. Cache mechanics sanity checks
D. Algorithms
E. Full composition ablations
F. Full repair granularity tables
G. Full answer-level tables
H. External HotpotQA/2Wiki sanity
I. Held-out gate calibration
J. Cost accounting
K. Failure examples
L. Related-work comparison
M. Citation and artifact checklist

The appendix is intended as a reviewer-support package. Remaining cleanup is typography, not missing experiments.
""",
    )
    write_text(
        PAPER / "COMPRESSION_REPORT.md",
        """# Compression Report

Milestone 8E moves the draft from an expanded internal manuscript toward an acceptance-oriented submission draft. The `page:mainend` label is placed before Limitations so the main-content estimate follows ARR/ACL convention more closely.

Recommended compression moves:

1. Keep the semantic-state opening and four contributions.
2. Trim repeated caveats where they appear in both Results and Discussion.
3. Move additional budget-gate details to appendix if needed.
4. Preserve random-control and external-data caveats.

The table typography pass reduces visual weight without changing content: all generated LaTeX tables are centered, use `\\footnotesize`, and use `adjustbox` max-width fitting so narrow tables are not enlarged while wide tables still fit.

Do not compress away the limitations, related-work distinction, or no-latency-claim language.
""",
    )
    write_text(
        PAPER / "ARR_QUALITY_REWRITE_STATUS.md",
        """# ARR-Quality Rewrite Status

## Expanded Sections

- Abstract states the semantic-state-reuse problem and the no-latency scope.
- Introduction foregrounds the acceptance-critical thesis: cache reuse is semantic state reuse.
- Related work distinguishes SAFE-KV from CacheBlend, KVLink, LMCache, Prompt Cache, and vLLM/PagedAttention.
- Problem setup defines full, composed, and repaired states.
- Results remain RQ-driven and visibly include random controls.
- Discussion includes explicit does/does-not-claim language.

## Main Tables

The main paper keeps five compact tables. All generated table cells are centered, generated tables use `\\footnotesize`, and tables use max-width fitting rather than full-width scaling, so appendix tables no longer swing between oversized and over-shrunk. Full tables are in the appendix.

## Figures

Five real PDF figures are generated under `paper/figures/`; four are used in the main paper and one in the appendix.

## Compile Status

Run `latexmk -pdf -interaction=nonstopmode main.tex` from `paper/`. The final 8E report records exact page counts and pubcheck status.

## Claim Boundaries

The draft does not claim production latency/TTFT/throughput improvements, SOTA QA, universal selector dominance, span-level repair success, Qwen7B evidence, or serving-system replacement.
""",
    )
    write_text(
        PAPER / "REVIEWER_RISK_AUDIT.md",
        """# Reviewer Risk Audit

## One-Sentence Summary

SAFE-KV shows that non-prefix KV cache reuse is a semantic state-reuse problem: prefix-conditioned composition reduces but does not eliminate answer drift, span repair is unreliable, document-level repair is coherent, and budgeted gates expose quality-risk trade-offs under random controls.

## Checklist

1. Would a CacheBlend/KVLink reviewer understand the difference immediately?  
   Yes. Related Work explicitly distinguishes serving/fusion mechanisms from SAFE-KV's full-prefill behavior-preservation oracle, repair-granularity study, and matched random controls.

2. Does the introduction explain why this is semantic safety, not just efficiency?  
   Yes. It opens with context prefill pressure but quickly argues that document KV states are context-conditioned causal states.

3. Is there a figure in the first 2 pages that explains the setup?  
   Yes. Figure 1 shows full prefill, composed non-prefix caches, and document repair/gating.

4. Is the strongest table result interpretable without the appendix?  
   Yes. Tables 1--5 are compact and have takeaway captions.

5. Are negative results used constructively?  
   Yes. Random K2, mixed external transfer, and non-portable thresholds are framed as claim-calibration evidence.

6. Are external data weaknesses acknowledged before reviewers point them out?  
   Yes. External HotpotQA/2Wiki is framed as sanity evidence, not a benchmark or selector-dominance proof.

7. Are all random baselines visible and respected?  
   Yes. Random K2 and matched random gates appear in main tables and discussion.

8. Are unsupported claims removed?  
   Yes. The draft avoids production speedups, SOTA QA, universal selector dominance, Qwen7B evidence, and serving-system replacement.

9. Does the paper avoid production speedup language?  
   Yes. It reports recomputation-budget proxies only.

10. Can the paper be summarized in one sentence?  
   Yes; see the one-sentence summary above.
""",
    )


if __name__ == "__main__":
    main()
