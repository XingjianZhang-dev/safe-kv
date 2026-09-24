#!/usr/bin/env python3
"""Generate every NEW camera-ready table from the raw result files.

Reads only the files listed in NUMBERS.md; writes LaTeX into paper/tables/ and a
machine-readable dump (scratch/generated_numbers.json) that check_numbers.py uses.
Submitted tables (table1..table5, appendix_*) are NOT regenerated; they stay as reviewed.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUB = Path(__file__).resolve().parents[2]
REB = Path(__file__).resolve().parents[2] / "results_rebuttal"
AUG = Path(__file__).resolve().parents[2] / "results_august"
OUT = ROOT / "paper_reference" / "camera_ready_tables"
DUMP: dict[str, object] = {}


def jload(p: Path):
    with open(p) as f:
        return json.load(f)


def cload(p: Path):
    with open(p) as f:
        return list(csv.DictReader(f))


def pct(x: float, nd: int = 1) -> str:
    return f"{100 * x:.{nd}f}"


def f3(x: float) -> str:
    return f"{x:.3f}"


def write(name: str, body: str) -> None:
    (OUT / name).write_text(body)
    print("wrote", name)


# ---------------------------------------------------------------- T-ACTUAL
def t_actual() -> None:
    """Table 2: one row per method, HotpotQA and 2Wiki side by side (Ans. eq. / Tok. exact / Recomp. each)."""
    a = {}
    cellsA = {}
    for ds, lab in [("hotpot", "HotpotQA-500"), ("2wiki", "2Wiki-500")]:
        s = jload(REB / f"actual_recompute_{ds}_500" / "answer_eval_summary.json")["method_level"]
        rc = {m["method"]: m for m in jload(REB / f"actual_vs_copy_{ds}_500_l40s_v2" / "donor_actual_reconciliation.json")["method_summaries"]}
        for k, mlab in [("k1", "Risk suffix K1"), ("k2", "Risk suffix K2")]:
            v = s[f"actual_recompute::risk_guided_suffix_closure_{k}"]
            tok = rc[f"risk_guided_suffix_closure_{k}"]["actual_generated_token_exact_rate"]
            a[f"{lab}|{mlab}"] = dict(eq=v["answer_equivalence_to_full_prefill"], tok=tok,
                                      cw=v["answer_changed_and_gold_wrong_count"], ratio=v["avg_patched_token_ratio"],
                                      em=v["gold_exact_match"], f1=v["gold_token_f1"], n=v["num_rows"])
            cellsA[(mlab, lab)] = f"{f3(v['answer_equivalence_to_full_prefill'])} & {f3(tok)} & {f3(v['avg_patched_token_ratio'])}"
    DUMP["T-ACTUAL(a)"] = a
    rows = [f"{m.replace(' suffix', '')} & {cellsA[(m, 'HotpotQA-500')]} & {cellsA[(m, '2Wiki-500')]} \\\\" for m in ["Risk suffix K1", "Risk suffix K2"]]
    b = {}
    across = cload(REB / "neutral_selector_actual_3seed_validation" / "neutral_selector_across_seed.csv")
    order = ["actual_recompute::risk_guided_suffix_closure_k1", "actual_recompute::hybrid_query_risk_union_suffix_k1",
             "actual_recompute::query_similarity_suffix_closure_k2", "actual_recompute::risk_guided_suffix_closure_k2"]
    names = {"actual_recompute::risk_guided_suffix_closure_k1": "Risk suffix K1",
             "actual_recompute::hybrid_query_risk_union_suffix_k1": "Hybrid suffix K1",
             "actual_recompute::query_similarity_suffix_closure_k2": "Query suffix K2",
             "actual_recompute::risk_guided_suffix_closure_k2": "Risk suffix K2"}
    cellsB = {}
    for ds, lab in [("hotpotqa", "HotpotQA 3$\\times$100"), ("2wiki", "2Wiki 3$\\times$100")]:
        for m in order:
            r = next(x for x in across if x["dataset"] == ds and x["method"] == m)
            mean = float(r["normalized_answer_exact_mean_across_seeds"]); lo = float(r["normalized_answer_exact_min_seed"]); hi = float(r["normalized_answer_exact_max_seed"])
            tok = float(r["generated_token_exact_mean_across_seeds"]); ratio = float(r["mean_recomputed_context_token_ratio_mean_across_seeds"])
            b[f"{lab}|{names[m]}"] = dict(eq=mean, lo=lo, hi=hi, tok=tok, ratio=ratio)
            cellsB[(names[m], ds)] = f"{f3(mean)} & {f3(tok)} & {f3(ratio)}"
    DUMP["T-ACTUAL(b)"] = b
    brows = [f"{names[m].replace(' suffix', '')} & {cellsB[(names[m], 'hotpotqa')]} & {cellsB[(names[m], '2wiki')]} \\\\" for m in order]
    body = r"""\begin{table}[t]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{adjustbox}{max width=\linewidth}
\begin{tabular}{lrrrrrr}
\toprule
 & \multicolumn{3}{c}{HotpotQA} & \multicolumn{3}{c}{2Wiki} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Method & Eq. & Tok. & Rec. & Eq. & Tok. & Rec. \\
\midrule
\multicolumn{7}{l}{\emph{(a) Gold-evidence-first construction, $N=500$}} \\
""" + "\n".join(rows) + r"""
\midrule
\multicolumn{7}{l}{\emph{(b) Score-neutral shuffled order, 3 seeds $\times$ 100 (means)}} \\
""" + "\n".join(brows) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Actual suffix forwarding with Qwen2.5-7B-Instruct (the selected contiguous suffix is re-run through the model from the retained composed prefix; no donor-cache copying). All rows are suffix repair (``Risk K1'' = risk suffix K1, etc.). Eq.\ is normalized answer preservation relative to full prefill; Tok.\ is generated-token-sequence equality; Rec.\ is the mean fraction of context tokens re-forwarded. Panel (a) uses the same gold-evidence-first inputs as Table~\ref{tab:external-main}, so the two tables differ only in protocol (changed-wrong counts: 1/0 on HotpotQA, 12/5 on 2Wiki for K1/K2). Panel (b) removes the construction cues: every retrieval score is zero and documents are shuffled with order seeds 101/202/303 (100 examples each); values are means over seeds, per-seed values in Table~\ref{tab:app-neutral-seed}. Random suffix and query suffix K1 were not run under shuffled order. One NVIDIA L40S, PyTorch~2.8.0.}
\label{tab:actual-forwarding}
\end{table}
"""
    write("table_actual_forwarding.tex", body)


# ---------------------------------------------------------------- T-LOCAL / T-LOCALFULL
def t_local() -> None:
    budgets = ["0.05", "0.1", "0.16", "0.2", "0.3", "0.45", "0.6"]
    bkey = {"0.05": "p0p05", "0.1": "p0p1", "0.16": "p0p16", "0.2": "p0p2", "0.3": "p0p3", "0.45": "p0p45", "0.6": "p0p6"}
    data = {}
    for o, lab in [("natural", "natural"), ("shuffle", "shuffled"), ("bm25", "BM25")]:
        rows = cload(AUG / "run_registry" / f"qwen25_query_attention_hotpotqa_{o}_test_n100_v1" / "query_attention_local_summary.csv")
        get = lambda m: next(r for r in rows if r["method"] == m)
        d = {"prefix": float(get("prefix_conditioned_composition")["qa_answer_equivalence_to_fresh_reference"]),
             "ref": float(get("all_fresh_context_chunked_reference")["qa_answer_equivalence_to_fresh_reference"]),
             "qa": {}, "rand": {}, "ctx": {}, "doc": {}, "qa_tok": {}}
        for b in budgets:
            q = get(f"query_attention_local_actual_{bkey[b]}")
            d["qa"][b] = float(q["qa_answer_equivalence_to_fresh_reference"])
            d["qa_tok"][b] = float(q["token_sequence_equivalence_to_fresh_reference"])
            d["ctx"][b] = float(q["avg_patched_context_ratio"])
            d["doc"][b] = float(q["avg_patched_document_token_ratio"])
            d["rand"][b] = [float(get(f"random_local_actual_{bkey[b]}_seed{s}")["qa_answer_equivalence_to_fresh_reference"]) for s in (13, 29, 47)]
        data[lab] = d
    DUMP["T-LOCAL"] = data
    # compact main-text table at b = 0.6
    rows = []
    qsum = 0.0; rsum = 0.0; psum = 0.0
    for lab in ["natural", "shuffled", "BM25"]:
        d = data[lab]
        rmean = statistics.fmean(d["rand"]["0.6"])
        rows.append(f"{lab} & {f3(d['prefix'])} & {f3(statistics.fmean(d['rand']['0.6']))} & {f3(d['qa']['0.6'])} \\\\")
        qsum += d["qa"]["0.6"]; rsum += rmean; psum += d["prefix"]
    pooled_q = qsum / 3; pooled_r = rsum / 3; pooled_p = psum / 3
    DUMP["T-LOCAL-pooled"] = dict(query_attention=pooled_q, random=pooled_r, prefix=pooled_p)
    rows.append(r"\midrule")
    rows.append(f"pooled (300) & {f3(pooled_p)} & {f3(pooled_r)} & {f3(pooled_q)} \\\\")
    ctx_vals = {f3(data[lab]["ctx"]["0.6"]) for lab in ["natural", "shuffled", "BM25"]}
    assert len(ctx_vals) == 1, ctx_vals  # the recomputed context fraction is identical across orders; it is stated in the caption
    ctx60 = ctx_vals.pop()
    body = r"""\begin{table}[t]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{adjustbox}{max width=\linewidth}
\begin{tabular}{lrrr}
\toprule
 & Prefix- & Random & Query-attn. \\
Order & comp. & local & local \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Operational token-local repair on HotpotQA (100 examples per order; natural, shuffled, and BM25 document orders built without gold labels), Qwen2.5-7B-Instruct, actual forwarding of the selected token spans from the stale composed cache. Query-attn.\ local ranks context tokens by the query's attention over the stale cache and recomputes the top spans within a 60\% document-token budget; Random local recomputes equal-budget random spans (mean over three seeds). Values are normalized answer preservation relative to the all-fresh reference; the recomputed fraction of context tokens is """ + ctx60 + r""" in every row. Runs: one NVIDIA RTX PRO 6000 Blackwell GPU, PyTorch~2.8.0. Full budget curves: Table~\ref{tab:app-local-full}.}
\label{tab:local-operational}
\end{table}
"""
    write("table_local_operational.tex", body)
    # full appendix table
    lines = []
    for lab in ["natural", "shuffled", "BM25"]:
        d = data[lab]
        lines.append(f"\\multicolumn{{8}}{{l}}{{\\emph{{{lab} order}} (prefix-composition {f3(d['prefix'])}; all-fresh chunked reference {f3(d['ref'])})}} \\\\")
        lines.append("Query-attention local & " + " & ".join(f3(d["qa"][b]) for b in budgets) + " \\\\")
        lines.append("\\quad token exact & " + " & ".join(f3(d["qa_tok"][b]) for b in budgets) + " \\\\")
        for i, s in enumerate((13, 29, 47)):
            lines.append(f"Random local, seed {s} & " + " & ".join(f3(d["rand"][b][i]) for b in budgets) + " \\\\")
        lines.append("Context ratio & " + " & ".join(f3(d["ctx"][b]) for b in budgets) + " \\\\")
        lines.append(r"\midrule")
    lines = lines[:-1]
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{l""" + "r" * len(budgets) + r"""}
\toprule
Method / document-token budget & """ + " & ".join(budgets) + r""" \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Operational query-attention token-local baseline: full budget curves on HotpotQA (100 examples per order), actual forwarding, Qwen2.5-7B-Instruct, one RTX PRO 6000 Blackwell GPU. Values are normalized answer preservation relative to the all-fresh chunked reference (token-sequence exact shown for the query-attention rows); Context ratio is the recomputed context-token fraction at each document-token budget. Random local uses equal-budget random spans with seeds 13/29/47.}
\label{tab:app-local-full}
\end{table*}
"""
    write("appendix_local_full.tex", body)


# ---------------------------------------------------------------- T-STALE / T-STALEFULL
def t_stale() -> None:
    rows = cload(REB / "staleness_doccount_full_50_v3" / "staleness_doccount_summary.csv")
    ps = ["0.0", "0.25", "0.5", "0.75", "1.0"]
    ns = ["N1", "N2", "N4", "N8", "N16"]
    meth = [("mixed_no_repair", "No repair"), ("query_actual_doc_only_k1", "Query doc-only K1"),
            ("query_actual_downstream_w4_k1", "Query window w4 K1"), ("query_actual_suffix_k1", "Query suffix K1"),
            ("risk_actual_suffix_k1", "Risk suffix K1"), ("risk_actual_suffix_k2", "Risk suffix K2"),
            ("earliest_stale_actual_suffix_oracle", "Mask-informed earliest-stale oracle")]
    cell = {}
    for r in rows:
        cell[(r["method"], r["dataset_label"], f"{float(r['stale_probability']):.2f}")] = r
    def g(m, n, p):
        return cell[(m, n, f"{float(p):.2f}")]
    DUMP["T-STALE"] = {f"{m}|{n}|{p}": dict(eq=float(g(m, n, p)["answer_equivalence_to_fresh_reference"]),
                                          lo=float(g(m, n, p)["clustered_example_ci95_low"]),
                                          hi=float(g(m, n, p)["clustered_example_ci95_high"]),
                                          ratio=float(g(m, n, p)["avg_recomputed_token_ratio"]),
                                          tok=float(g(m, n, p)["token_sequence_equivalence_to_fresh_reference"]),
                                          n=int(g(m, n, p)["num_rows"]))
                      for m, _ in meth for n in ns for p in ps}
    # compact
    lines = []
    for n in ns:
        lines.append(f"{n[1:]} & " + " & ".join(pct(float(g('mixed_no_repair', n, p)['answer_equivalence_to_fresh_reference'])) for p in ps) + " \\\\")
    rep = []
    short = {"Query doc-only K1": "Query doc K1", "Query window w4 K1": "Query w4 K1"}
    for m, lab in meth[1:6]:
        r1 = g(m, "N16", "1.0")
        rep.append(f"{short.get(lab, lab)} & " + " & ".join(pct(float(g(m, 'N16', p)['answer_equivalence_to_fresh_reference'])) for p in ps) + f" & {pct(float(r1['avg_recomputed_token_ratio']))} \\\\")
    body = r"""\begin{table}[t]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{adjustbox}{max width=\linewidth}
\begin{tabular}{lrrrrrr}
\toprule
 & \multicolumn{5}{c}{mismatch probability $p$} & \\
\cmidrule(lr){2-6}
 & 0 & 0.25 & 0.5 & 0.75 & 1 & Recomp. \\
\midrule
\multicolumn{7}{l}{\emph{No repair, by document count $N$}} \\
""" + "\n".join(lines) + r"""
\midrule
\multicolumn{7}{l}{\emph{Repair policies at $N=16$ (actual forwarding)}} \\
""" + "\n".join(rep) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Staleness probability $\times$ document count: normalized answer preservation (\%) relative to the all-fresh reference on a controlled single-evidence benchmark with $N$ documents (nested from the Noise16 pool, layout seed 101, retrieval scores zero), 50 paired examples, three mismatch-mask seeds. $p$ is the probability that an eligible slice (position $\geq 2$) was encoded from the static prefix instead of its exact preceding history; the query is always recomputed and no selector sees the mask. ``Query doc K1'' and ``Query w4 K1'' are the query doc-only and query window-w4 policies; Recomp.\ is the mean recomputed context fraction at $N{=}16$. Actual forwarding, Qwen2.5-7B-Instruct, one NVIDIA L40S; full grid with clustered intervals in Table~\ref{tab:app-stale-full}.}
\label{tab:staleness}
\end{table}
"""
    write("table_staleness_compact.tex", body)
    # full grid
    lines = []
    for m, lab in meth:
        lines.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{lab}}}}} \\\\")
        for n in ns:
            cells = []
            for p in ps:
                r = g(m, n, p)
                eq = float(r["answer_equivalence_to_fresh_reference"]); lo = float(r["clustered_example_ci95_low"]); hi = float(r["clustered_example_ci95_high"]); ra = float(r["avg_recomputed_token_ratio"])
                cells.append(f"{f3(eq)} [{lo:.2f}, {hi:.2f}] @{ra:.3f}")
            lines.append(f"{n[1:]} & " + " & ".join(cells) + " \\\\")
        lines.append(r"\midrule")
    lines = lines[:-1]
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lrrrrr}
\toprule
$N$ & $p=0$ & $p=0.25$ & $p=0.5$ & $p=0.75$ & $p=1$ \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Full staleness-probability $\times$ document-count grid (26{,}250 rows; validator passed with zero invariant failures). Each cell reports normalized answer preservation relative to the all-fresh reference, its example-clustered 95\% interval, and the mean recomputed context-token fraction (@). Fifty paired examples per $N$, mask seeds 13/29/47. The mask-informed oracle recomputes from the earliest truly mismatched slice and is a sanity check of the intervention, not a deployable policy. Actual forwarding; Qwen2.5-7B-Instruct; one NVIDIA L40S.}
\label{tab:app-stale-full}
\end{table*}
"""
    write("appendix_staleness_full.tex", body)


# ---------------------------------------------------------------- T-LAT / T-LATFULL / T-PLAN / Noise64 gate
WORKLOADS = [("latency_hotpot_original_50_v1", "HotpotQA, original order", "gold-evidence-first"),
             ("latency_2wiki_original_50_v1", "2Wiki, original order", "gold-evidence-first"),
             ("latency_2wiki_neutral_shuffle101_50_v1", "2Wiki, score-neutral shuffled", "shuffled seed 101"),
             ("latency_n16_neutral_layout101_50_v1", "$N{=}16$ nested, $p{=}1$", "synthetic"),
             ("latency_noise64_50_v1", "Noise64 (67 documents)", "synthetic")]
METHODS = [("full_prefill", "Full prefill"), ("prefix_query", "Prefix query only (no repair; diagnostic)"),
           ("query_suffix_k1", "Query suffix K1"), ("risk_suffix_k1", "Risk suffix K1"),
           ("hybrid_query_risk_union_suffix_k1", "Hybrid suffix K1"), ("risk_suffix_k2", "Risk suffix K2")]


def t_latency() -> None:
    lat = {}
    for w, lab, _ in WORKLOADS:
        s = jload(REB / w / "latency_trace_summary.json")
        ms = {m["method"]: m for m in s["method_summary"]}
        pb = {r["method"]: r for r in cload(REB / w / "latency_paired_bootstrap_summary.csv")}
        sel = {m["method"]: m for m in s["selector_summary"]}
        assert s["gpu"] == "NVIDIA L40S" and s["num_examples"] == 50 and s["repeats"] == 5
        lat[w] = dict(label=lab, prompt=ms["full_prefill"]["avg_prompt_length"], methods={}, selectors=sel,
                      cache_build_median_ms=s["cache_build_summary"]["median_s"] * 1000)
        for m, _ in METHODS:
            v = ms[m]
            lat[w]["methods"][m] = dict(median_ms=v["median_of_example_median_time_to_first_logit_s"] * 1000,
                                       p95_ms=v["p95_time_to_first_logit_s"] * 1000,
                                       ratio=v["avg_context_recomputed_token_ratio"],
                                       mem=v["avg_incremental_peak_cuda_memory_mb"],
                                       speed=float(pb[m]["paired_example_speedup_median"]),
                                       lo=float(pb[m]["paired_example_speedup_median_ci95_low"]),
                                       hi=float(pb[m]["paired_example_speedup_median_ci95_high"]),
                                       faster=float(pb[m]["fraction_examples_faster_than_full"]))
    DUMP["T-LAT"] = lat
    # noise64 gate
    q = jload(REB / "quality_noise64_actual_riskk1_50_v1" / "answer_eval_summary.json")["method_level"]
    ci = {(r["method"], r["metric"]): r for r in cload(REB / "quality_noise64_actual_riskk1_50_v1" / "bootstrap" / "bootstrap_method_ci.csv")}
    dl = next(r for r in cload(REB / "quality_noise64_actual_riskk1_50_v1" / "bootstrap" / "bootstrap_pairwise_delta_ci.csv") if r["metric"] == "answer_equivalence")
    rc = jload(REB / "quality_noise64_actual_riskk1_50_v1" / "donor_actual_reconciliation.json")["method_summaries"][0]
    gate = dict(full_em=q["full_prefill"]["gold_exact_match"],
                donor_eq=q["risk_guided_suffix_closure_k1"]["answer_equivalence_to_full_prefill"],
                donor_lo=float(ci[("risk_guided_suffix_closure_k1", "answer_equivalence")]["ci_low"]),
                donor_hi=float(ci[("risk_guided_suffix_closure_k1", "answer_equivalence")]["ci_high"]),
                actual_eq=q["actual_recompute::risk_guided_suffix_closure_k1"]["answer_equivalence_to_full_prefill"],
                actual_lo=float(ci[("actual_recompute::risk_guided_suffix_closure_k1", "answer_equivalence")]["ci_low"]),
                actual_hi=float(ci[("actual_recompute::risk_guided_suffix_closure_k1", "answer_equivalence")]["ci_high"]),
                actual_em=q["actual_recompute::risk_guided_suffix_closure_k1"]["gold_exact_match"],
                donor_em=q["risk_guided_suffix_closure_k1"]["gold_exact_match"],
                actual_tok=rc["actual_generated_token_exact_rate"], donor_tok=rc["donor_generated_token_exact_rate"],
                actual_cw=q["actual_recompute::risk_guided_suffix_closure_k1"]["answer_changed_and_gold_wrong_count"],
                donor_cw=q["risk_guided_suffix_closure_k1"]["answer_changed_and_gold_wrong_count"],
                ratio=q["actual_recompute::risk_guided_suffix_closure_k1"]["avg_patched_token_ratio"],
                delta=float(dl["delta_left_minus_right"]), dlo=float(dl["ci_low"]), dhi=float(dl["ci_high"]))
    DUMP["NOISE64-GATE"] = gate
    # main table
    rows = []
    for w, lab, _ in WORKLOADS:
        L = lat[w]; f = L["methods"]["full_prefill"]; r = L["methods"]["risk_suffix_k1"]
        rows.append(f"{lab} & {L['prompt']:.0f} & {f['median_ms']:.1f} & {r['median_ms']:.1f} & {pct(r['ratio'])} & "
                    f"{r['speed']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}] & {pct(r['faster'], 0)}\\% & {f['p95_ms']:.1f} / {r['p95_ms']:.1f} \\\\")
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lrrrrrrr}
\toprule
Workload (order) & Prompt tok. & Full (ms) & Risk K1 (ms) & Repair (\%) & Paired speedup [95\% CI] & Faster & p95 full / K1 (ms) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Time to first logit (ms) with actual suffix forwarding, selector scoring and suffix-start planning included, on one NVIDIA L40S (Qwen2.5-7B-Instruct, FP16, SDPA, batch size 1, composed cache resident; cache construction, lookup, transfer, scheduling, token emission, and concurrency excluded). Fifty examples per workload, five timed repeats; medians over per-example medians, p95 over all 250 calls; paired speedup is full/Risk-K1 per example with an example bootstrap; ``Faster'' is the fraction of examples improved. Orders: original = inputs of Table~\ref{tab:external-main}; shuffled = score-neutral seed 101; $N{=}16$ and Noise64 synthetic. On Noise64, actual forwarding preserves only """ + pct(gate["actual_eq"], 0) + r"""\% of answers on the same examples (Table~\ref{tab:app-noise64-gate}). All methods: Tables~\ref{tab:app-lat-full}--\ref{tab:app-plan}.}
\label{tab:latency-main}
\end{table*}
"""
    write("table_latency_main.tex", body)
    # appendix full
    lines = []
    for w, lab, _ in WORKLOADS:
        L = lat[w]
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\emph{{{lab}}} (mean prompt {L['prompt']:.1f} tokens)}} \\\\")
        for m, mlab in METHODS:
            v = L["methods"][m]
            sp = "---" if m == "full_prefill" else f"{v['speed']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}]"
            lines.append(f"{mlab} & {v['median_ms']:.1f} & {v['p95_ms']:.1f} & {f3(v['ratio'])} & {v['mem']:.0f} & {sp} & {pct(v['faster'], 0)}\\% \\\\")
        lines.append(r"\midrule")
    lines = lines[:-1]
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lrrrrrr}
\toprule
Method & Median (ms) & p95 (ms) & Repair ratio & Incr.\ peak MB & Paired speedup [95\% CI] & Faster \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{All timed methods for the five L40S workloads of Table~\ref{tab:latency-main} (actual forwarding; selector scoring and suffix-start planning inside the timed region for the four SAFE-KV rows). ``Prefix query only'' evaluates the query against the unrepaired composed cache and is shown only to separate query evaluation from repair work; it is not an operating point. Incr.\ peak MB is the incremental peak CUDA memory of the request above the resident model and cache pool. Each run passed the independent validator (1{,}500 latency rows, 200 selector rows, 50 cache-build rows, zero failures). One-shot composed-cache construction, outside the request path, had median 201.5 / 204.4 / 203.1 / 532.3 / 2174.0~ms for the five workloads.}
\label{tab:app-lat-full}
\end{table*}
"""
    write("appendix_latency_full.tex", body)
    # planning cost table: L40S runs + CPU audit
    audit = cload(REB / "cpu_selector_audit_l40s_host" / "latency.csv")
    DUMP["T-PLAN-audit"] = {f"{r['workload']}|{r['method']}": dict(median=float(r["median_ms"]), p95=float(r["p95_ms"]), calls=int(r["num_calls"])) for r in audit}
    lines = []
    selm = [("query_similarity_doc_patch_k1", "Query K1"), ("risk_guided_doc_patch_k1", "Risk K1"),
            ("risk_guided_doc_patch_k2", "Risk K2"), ("hybrid_query_risk_union_suffix_k1", "Hybrid K1")]
    for w, lab, _ in WORKLOADS:
        S = lat[w]["selectors"]
        lines.append(f"{lab} (50 ex.\\ $\\times$ 25) & " + " & ".join(f"{S[m]['median_of_example_medians_ms']:.3f} / {S[m]['p95_of_example_medians_ms']:.3f}" for m, _ in selm) + " \\\\")
    lines.append(r"\midrule")
    for wl, lab in [("external_hotpotqa", "HotpotQA-500, gold-first (500 $\\times$ 20)"), ("external_2wiki", "2Wiki-500, gold-first (500 $\\times$ 20)"), ("synthetic_docs67", "Noise64, 67 docs (40 $\\times$ 20)")]:
        a = {r["method"]: r for r in audit if r["workload"] == wl}
        lines.append(f"{lab} & " + " & ".join((f"{float(a[m]['median_ms']):.3f} / {float(a[m]['p95_ms']):.3f}" if m in a else "---") for m, _ in selm) + " \\\\")
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lrrrr}
\toprule
Workload (examples $\times$ repeats) & Query K1 & Risk K1 & Risk K2 & Hybrid K1 \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{CPU cost of the paper's selectors in milliseconds (median / p95). The timed region is feature computation, weighted scoring and top-$K$ selection for one selector call on the host CPU (x86\_64; CPU model not recorded); the suffix start is a single minimum over the selected positions and is timed only inside the end-to-end measurements of Table~\ref{tab:app-lat-full}, which include it. Upper block: inside the five L40S latency runs, median and p95 over the 50 per-example medians of 25 repeats. Lower block: the separate selector-only audit on the same host, median and p95 over all calls (Hybrid K1 was not timed there).}
\label{tab:app-plan}
\end{table*}
"""
    write("appendix_selector_planning.tex", body)
    # noise64 gate table
    g = gate
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{tabular}{lrrrr}
\toprule
Path & Ans. eq. [95\% CI] & Token exact & Gold EM & Changed-wrong \\
\midrule
Full prefill & 1.000 & 1.000 & """ + f3(g["full_em"]) + r""" & 0 \\
Donor-copy Risk K1 (diagnostic) & """ + f"{f3(g['donor_eq'])} [{g['donor_lo']:.2f}, {g['donor_hi']:.2f}] & {f3(g['donor_tok'])} & {f3(g['donor_em'])} & {g['donor_cw']}" + r""" \\
Actual-forwarding Risk K1 & """ + f"{f3(g['actual_eq'])} [{g['actual_lo']:.2f}, {g['actual_hi']:.2f}] & {f3(g['actual_tok'])} & {f3(g['actual_em'])} & {g['actual_cw']}" + r""" \\
\bottomrule
\end{tabular}
\caption{Noise64 quality gate on the exact 50 examples and suffixes timed in Table~\ref{tab:latency-main} (mean repair ratio """ + f3(g["ratio"]) + r""" for both paths; identical selected documents). Donor-copy and actual forwarding differ by """ + f"{g['delta']:+.2f}" + r""" [""" + f"{g['dlo']:.2f}, {g['dhi']:.2f}" + r"""] in normalized answer preservation (paired bootstrap). The mechanical median speed-up of Risk K1 on this workload therefore does not correspond to a behavior-preserving operating point.}
\label{tab:app-noise64-gate}
\end{table*}
"""
    write("appendix_noise64_gate.tex", body)


# ---------------------------------------------------------------- neutral per-seed + reconciliation
def t_neutral_seed() -> None:
    by = cload(REB / "neutral_selector_actual_3seed_validation" / "neutral_selector_by_seed.csv")
    names = {"actual_recompute::risk_guided_suffix_closure_k1": "Risk suffix K1",
             "actual_recompute::hybrid_query_risk_union_suffix_k1": "Hybrid suffix K1",
             "actual_recompute::query_similarity_suffix_closure_k2": "Query suffix K2",
             "actual_recompute::risk_guided_suffix_closure_k2": "Risk suffix K2"}
    order = list(names)
    DUMP["T-NEUTRALSEED"] = {f"{r['dataset']}|{r['order_seed']}|{names[r['method']]}": dict(eq=float(r["normalized_answer_exact"]), tok=float(r["generated_token_exact"]), ratio=float(r["mean_recomputed_context_token_ratio"]), n=int(r["num_examples"])) for r in by}
    lines = []
    for ds, lab in [("hotpotqa", "HotpotQA"), ("2wiki", "2Wiki")]:
        for m in order:
            cells = []
            for seed in ("101", "202", "303"):
                r = next(x for x in by if x["dataset"] == ds and x["method"] == m and x["order_seed"] == seed)
                cells.append(f"{float(r['normalized_answer_exact']):.2f} / {float(r['generated_token_exact']):.2f} / {float(r['mean_recomputed_context_token_ratio']):.3f}")
            lines.append(f"{lab} & {names[m]} & " + " & ".join(cells) + " \\\\")
        lines.append(r"\midrule")
    lines = lines[:-1]
    rc = {}
    for ds, lab in [("hotpot", "HotpotQA-500"), ("2wiki", "2Wiki-500")]:
        for m in jload(REB / f"actual_vs_copy_{ds}_500_l40s_v2" / "donor_actual_reconciliation.json")["method_summaries"]:
            rc[f"{lab}|{m['method']}"] = m
    DUMP["T-RECON"] = {k: dict(donor=v["donor_normalized_exact_rate"], actual=v["actual_normalized_exact_rate"], same=v["same_generated_answer_rate"], donor_tok=v["donor_generated_token_exact_rate"], actual_tok=v["actual_generated_token_exact_rate"]) for k, v in rc.items()}
    rlines = []
    for k, v in rc.items():
        lab, m = k.split("|"); mlab = "Risk suffix K1" if m.endswith("k1") else "Risk suffix K2"
        rlines.append(f"{lab} & {mlab} & {f3(v['donor_normalized_exact_rate'])} & {f3(v['actual_normalized_exact_rate'])} & {f3(v['same_generated_answer_rate'])} & {f3(v['donor_generated_token_exact_rate'])} & {f3(v['actual_generated_token_exact_rate'])} \\\\")
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{llrrr}
\toprule
Data & Method & seed 101 & seed 202 & seed 303 \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Per-seed values behind Table~\ref{tab:actual-forwarding}(b): normalized answer preservation / generated-token exact / mean recomputed context fraction for each score-neutral shuffled order seed (100 examples each, actual forwarding, one NVIDIA L40S).}
\label{tab:app-neutral-seed}
\end{table*}

\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{llrrrrr}
\toprule
Data & Method & Donor ans.\ eq. & Actual ans.\ eq. & Same generated answer & Donor token exact & Actual token exact \\
\midrule
""" + "\n".join(rlines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Same-run donor-copy versus actual-forwarding reconciliation on the original gold-evidence-first inputs (500 examples each; identical selected documents and patch ratios in every row; validator passed). This rerun used PyTorch~2.8.0+cu128 on one NVIDIA L40S, whereas Table~\ref{tab:external-main} was produced under PyTorch~2.4.1+cu124; the donor-copy 2Wiki values here (0.978/0.992) therefore differ slightly from the 0.970/0.984 of Table~\ref{tab:external-main} although inputs, selections and patch counts are byte-identical. The difference traces to FP16/SDPA near-tie sensitivity across runtime versions; code, data, and selections are unchanged.}
\label{tab:app-recon}
\end{table*}
"""
    write("appendix_neutral_seed_recon.tex", body)


# ---------------------------------------------------------------- oracle local
def t_oracle_local() -> None:
    s = jload(REB / "oracle_kv_drift_2wiki_neutral_shuffle101_100_v3" / "oracle_kv_drift_summary.json")
    ms = {m["method"]: m for m in s["method_summary"]}
    pb = {c["contrast"]: c for c in jload(REB / "oracle_kv_drift_2wiki_neutral_shuffle101_100_v3" / "oracle_paired_bootstrap_summary.json")["contrasts"]}
    DUMP["T-ORACLELOCAL"] = {k: dict(eq=v["qa_answer_equivalence_to_fresh_reference"], tok=v["token_sequence_equivalence_to_fresh_reference"], ctx=v["avg_patched_context_ratio"]) for k, v in ms.items()}
    DUMP["T-ORACLELOCAL-contrasts"] = {k: dict(d=v["normalized_answer_exact_delta"], lo=v["normalized_answer_exact_delta_ci95_low"], hi=v["normalized_answer_exact_delta_ci95_high"], td=v["generated_token_exact_delta"], tlo=v["generated_token_exact_delta_ci95_low"], thi=v["generated_token_exact_delta_ci95_high"]) for k, v in pb.items()}
    b = ["p0p2", "p0p3", "p0p45", "p0p6"]
    q = lambda m: ms[m]
    lines = [
        "Prefix-comp. & " + " & ".join([f3(q("prefix_conditioned_composition")["qa_answer_equivalence_to_fresh_reference"])] * 4) + " & --- \\\\",
        "Oracle KV-drift token-local (donor copy) & " + " & ".join(f3(q(f"oracle_kv_drift_token_local_{x}")["qa_answer_equivalence_to_fresh_reference"]) for x in b) + f" & {f3(q('oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1')['qa_answer_equivalence_to_fresh_reference'])} \\\\",
        "Random positions, oracle full-KV donor & " + " & ".join(f3(q(f"random_positions_oracle_full_kv_donor_{x}")["qa_answer_equivalence_to_fresh_reference"]) for x in b) + f" & {f3(q('random_positions_oracle_full_kv_donor_same_budget_as_risk_suffix_k1')['qa_answer_equivalence_to_fresh_reference'])} \\\\",
        f"Risk suffix K1, actual forwarding & --- & --- & --- & --- & {f3(q('risk_suffix_k1_actual_recompute')['qa_answer_equivalence_to_fresh_reference'])} \\\\",
        f"Risk suffix K1, donor copy & --- & --- & --- & --- & {f3(q('risk_suffix_k1_oracle_donor_copy')['qa_answer_equivalence_to_fresh_reference'])} \\\\",
        "Context ratio & " + " & ".join(f3(q(f"oracle_kv_drift_token_local_{x}")["avg_patched_context_ratio"]) for x in b) + f" & {f3(q('oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1')['avg_patched_context_ratio'])} \\\\",
    ]
    c = pb["oracle_local_same_budget_minus_actual_risk_suffix_k1"]
    body = r"""\begin{table*}[t]
\centering
\footnotesize
\begin{adjustbox}{max width=\textwidth}
\begin{tabular}{lrrrrr}
\toprule
Method / document-token budget & 0.20 & 0.30 & 0.45 & 0.60 & Risk-K1-matched \\
\midrule
""" + "\n".join(lines) + r"""
\bottomrule
\end{tabular}
\end{adjustbox}
\caption{Full-reference-informed token-local diagnostic on 2Wiki, score-neutral shuffled order (seed 101), 100 examples. Token positions are ranked by the K/V drift between the composed cache and the full-prefill cache, and the selected K/V states are donor-copied from the full-prefill cache; both steps use the reference, so this diagnostic is an analysis tool rather than a deployable method. Values are normalized answer preservation. At the Risk-K1-matched context cost the oracle-local minus actual-Risk-K1 paired difference is """ + f"{c['normalized_answer_exact_delta']:+.2f} [{c['normalized_answer_exact_delta_ci95_low']:.2f}, {c['normalized_answer_exact_delta_ci95_high']:.2f}]" + r""" (generated-token exact: """ + f"{c['generated_token_exact_delta']:+.2f} [{c['generated_token_exact_delta_ci95_low']:.2f}, {c['generated_token_exact_delta_ci95_high']:.2f}]" + r"""), a descriptive interval without multiple-comparison correction.}
\label{tab:app-oracle-local}
\end{table*}
"""
    write("appendix_oracle_local.tex", body)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    t_actual(); t_local(); t_stale(); t_latency(); t_neutral_seed(); t_oracle_local()
    (ROOT / "paper_reference" / "camera_ready_tables" / "generated_numbers.json").write_text(json.dumps(DUMP, indent=1, default=float))
    print("dumped", len(DUMP), "blocks")
