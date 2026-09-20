#!/usr/bin/env python3
"""Regenerate every figure of the camera-ready from raw result files, at the physical size used in the PDF
(no \\includegraphics downscaling), with TrueType fonts (pdf.fonttype 42) and no text below 7.5 pt.

  figure1_setup.pdf              (Figure 1, figure*, 6.3 in wide)   schematic; no data
  figure_local_vs_suffix.pdf     (Section 6.2, 2.60 in wide)         NUMBERS W1-W6   + .data.csv
  figure5_external_sanity.pdf    (Appendix H, figure*, 6.0 in wide)  NUMBERS C1-C2, X1-X3, X5, X7 + .data.csv
  figure4_budget_gate_pareto.pdf (Appendix K, figure*, 6.17 in wide) NUMBERS M7-M12, L1-L5 + .data.csv
  figure_position_sweep.pdf      (Appendix M, 2.78 in wide)          NUMBERS P1-P3, P5 + .data.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42   # TrueType, not Type 3, so figure text is extractable/searchable
matplotlib.rcParams["ps.fonttype"] = 42
PDFMETA = {"CreationDate": None}  # no timestamp, so regenerated PDFs are byte-identical on the same platform
matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]  # narrower than DejaVu when available
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SUB = Path(__file__).resolve().parents[2]
REB = Path(__file__).resolve().parents[2] / "results_rebuttal"
FIG = ROOT / "paper_reference/final_figures"

# ACL column geometry: \textwidth 6.3 in, \columnwidth 3.03 in. Figures are drawn at the width they are included at.
COL = 3.03
TEXT = 6.30
FS = 8.0        # axis labels / tick labels
FS_SMALL = 7.5  # annotations, legends, bar labels (never below this)


def budget_figure() -> None:
    """Appendix K: quality-budget points (2Wiki-500, donor copy) and L40S first-logit medians. Included at 0.98\\linewidth."""
    s2 = json.load(open(SUB / "results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json"))["method_level"]
    left = [("Prefix", "prefix_conditioned_naive_global"), ("Random K2", "random_suffix_closure_k2_seeded"),
            ("Risk K1", "risk_guided_suffix_closure_k1"), ("Hybrid K1", "hybrid_query_risk_union_suffix_k1"),
            ("Risk K2", "risk_guided_suffix_closure_k2")]
    lpts = [(lab, s2[k]["avg_patched_token_ratio"], s2[k]["answer_equivalence_to_full_prefill"]) for lab, k in left]
    work = [("latency_hotpot_original_50_v1", "HotpotQA\noriginal"), ("latency_2wiki_original_50_v1", "2Wiki\noriginal"),
            ("latency_2wiki_neutral_shuffle101_50_v1", "2Wiki\nshuffled"), ("latency_n16_neutral_layout101_50_v1", "N=16\nnested"),
            ("latency_noise64_50_v1", "Noise64\n(67 docs)")]
    rpts = []
    for w, lab in work:
        s = json.load(open(REB / w / "latency_trace_summary.json"))
        ms = {m["method"]: m for m in s["method_summary"]}
        pb = {r["method"]: r for r in csv.DictReader(open(REB / w / "latency_paired_bootstrap_summary.csv"))}
        rpts.append((lab, ms["full_prefill"]["median_of_example_median_time_to_first_logit_s"] * 1000,
                     ms["risk_suffix_k1"]["median_of_example_median_time_to_first_logit_s"] * 1000,
                     ms["risk_suffix_k1"]["avg_context_recomputed_token_ratio"],
                     float(pb["risk_suffix_k1"]["paired_example_speedup_median"])))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(0.98 * TEXT, 2.7), gridspec_kw={"width_ratios": [1, 1.25]})
    colors = {"Prefix": "#b8c1cc", "Random K2": "#f28e2b", "Risk K1": "#2ca25f", "Hybrid K1": "#7b6fd0", "Risk K2": "#2ca25f"}
    offsets = {"Prefix": (8, -3), "Random K2": (8, -9), "Risk K1": (-46, 10), "Hybrid K1": (10, -10), "Risk K2": (8, 4)}  # points
    for lab, x, y in lpts:
        ax1.scatter([x], [y], s=48, color=colors[lab], edgecolor="black", zorder=3)
        ax1.annotate(lab, (x, y), xytext=offsets[lab], textcoords="offset points", fontsize=FS_SMALL,
                     arrowprops=dict(arrowstyle="-", lw=0.5, color="#777777") if lab in ("Risk K1", "Hybrid K1") else None)
    xs = [p[1] for p in lpts[1:]]; ys = [p[2] for p in lpts[1:]]
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ax1.plot([xs[i] for i in order], [ys[i] for i in order], color="#cccccc", zorder=2)
    ax1.set_xlabel("recomputed context ratio (donor copy)", fontsize=FS)
    ax1.set_ylabel("2Wiki-500 answer preservation", fontsize=FS)
    ax1.set_xlim(-0.03, 1.08); ax1.set_ylim(0.3, 1.06); ax1.grid(alpha=0.3); ax1.tick_params(labelsize=FS_SMALL)
    ax1.set_title("Quality-budget operating points (2Wiki-500)", fontsize=FS)

    idx = np.arange(len(rpts)); wdt = 0.38
    full = [p[1] for p in rpts]; k1 = [p[2] for p in rpts]
    ax2.bar(idx - wdt / 2, full, wdt, color="#b8c1cc", edgecolor="black", label="Full prefill")
    ax2.bar(idx + wdt / 2, k1, wdt, color="#2ca25f", edgecolor="black", label="Risk K1 (actual forwarding + planning)")
    for i, p in enumerate(rpts):
        ax2.text(i - wdt / 2 - 0.07, p[1] + 4, f"{p[1]:.1f}", ha="center", fontsize=FS_SMALL)
        ax2.text(i + wdt / 2 + 0.07, p[2] + 4, f"{p[2]:.1f}", ha="center", fontsize=FS_SMALL)
    ax2.set_xticks(idx); ax2.set_xticklabels([f"{p[0]}\n({100*p[3]:.0f}%)" for p in rpts], fontsize=FS_SMALL)
    ax2.tick_params(axis="y", labelsize=FS_SMALL)
    ax2.set_ylabel("median time to first logit (ms)", fontsize=FS)
    ax2.set_xlabel("workload (Risk K1 recomputed context fraction)", fontsize=FS)
    ax2.set_ylim(0, max(full + k1) * 1.32)
    ax2.legend(fontsize=FS_SMALL, loc="upper left", frameon=False)
    ax2.set_title("Risk K1 is slower on four workloads; the Noise64\nmedian crossover fails the answer-preservation gate (44%)", fontsize=FS)
    ax2.grid(axis="y", alpha=0.3)
    fig.tight_layout(pad=0.4)
    out = FIG / "figure4_budget_gate_pareto.pdf"
    fig.savefig(out, metadata=PDFMETA); plt.close(fig); print("wrote", out)
    with open(FIG / "figure4_budget_gate_pareto.data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "label", "x", "y", "source", "numbers_id"])
        for (lab, x, y), nid in zip(lpts, ["M7", "M9", "M10", "M11", "M12"]):
            w.writerow(["left", lab, f"{x:.4f}", f"{y:.3f}", "SUB/results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json", nid])
        for (lab, fm, km, ratio, sp), (wd, _), nid in zip(rpts, work, ["L1", "L2", "L3", "L4", "L5"]):
            w.writerow(["right", lab.replace("\n", " "), f"full_median_ms={fm:.1f}", f"riskk1_median_ms={km:.1f};repair_ratio={ratio:.4f};paired_speedup={sp:.3f}", f"REB/{wd}/latency_trace_summary.json", nid])


def mechanism_figures() -> None:
    """Section 6.2 (2Wiki-100 local-vs-suffix curve, NUMBERS W1-W6; included at 0.86\\linewidth) and
    Appendix M (position sweep, NUMBERS P1-P3, P5; included at 0.92\\linewidth)."""
    w = json.load(open(SUB / "results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json"))["method_level"]
    pts = [("Prefix", "prefix_conditioned_naive_global", "W1"), ("Doc K1", "risk_guided_doc_patch_k1", "W2"),
           ("w2", "risk_guided_downstream_w2_k1", "W3"), ("w3", "risk_guided_downstream_w3_k1", "W4"),
           ("w4", "risk_guided_downstream_w4_k1", "W5"), ("Suffix K1", "risk_guided_suffix_closure_k1", "W6")]
    xs = [w[k]["avg_patched_token_ratio"] for _, k, _ in pts]; ys = [w[k]["answer_equivalence_to_full_prefill"] for _, k, _ in pts]
    fig, ax = plt.subplots(figsize=(0.86 * COL, 1.75))
    ax.plot(xs, ys, color="#2ca25f", linewidth=2.0, marker="o", markersize=5, zorder=3)
    offs = {"Prefix": (0.03, 0.02), "Doc K1": (0.0, 0.04), "w2": (0.0, 0.04), "w3": (0.03, -0.04), "w4": (-0.07, 0.04), "Suffix K1": (-0.27, -0.01)}
    for (lab, _, _), x, y in zip(pts, xs, ys):
        dx, dy = offs[lab]
        ax.annotate(lab, (x, y), xytext=(x + dx, y + dy), fontsize=FS_SMALL)
    ax.set_xlabel("recomputed context ratio", fontsize=FS); ax.set_ylabel("answer preservation", fontsize=FS)
    ax.set_xlim(-0.03, 0.92); ax.set_ylim(0.3, 1.02); ax.grid(alpha=0.3); ax.tick_params(labelsize=FS_SMALL)
    fig.tight_layout(pad=0.3)
    out = FIG / "figure_local_vs_suffix.pdf"; fig.savefig(out, metadata=PDFMETA); plt.close(fig); print("wrote", out)
    with open(FIG / "figure_local_vs_suffix.data.csv", "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["label", "method_key", "recomputed_context_ratio", "answer_preservation", "source", "numbers_id"])
        for (lab, k, nid), x, y in zip(pts, xs, ys):
            cw.writerow([lab, k, f"{x:.4f}", f"{y:.3f}", "SUB/results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json", nid])
    # position sweep
    rows = list(csv.DictReader(open(SUB / "results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv")))
    positions = ["first", "early", "middle", "late", "last"]
    series = [("prefix comp.", "prefix_conditioned_naive_global", "#b8c1cc", "o", "P1"), ("oracle doc patch", "oracle_evidence_doc_patch", "#f28e2b", "s", "P2"),
              ("oracle suffix repair", "oracle_evidence_doc_suffix_closure_patch", "#2ca25f", "^", "P3"), ("random suffix K1", "random_suffix_closure_k1_seeded", "#7b6fd0", "D", "P5")]
    fig, ax = plt.subplots(figsize=(0.92 * COL, 2.05))
    data = {}
    for lab, k, col, mk, nid in series:
        ys = [float(next(r for r in rows if r["method"] == k and r["position"] == p)["answer_equivalence"]) for p in positions]
        data[lab] = (k, ys, nid)
        ax.plot(positions, ys, color=col, marker=mk, linewidth=1.8, markersize=4.5, label=lab, zorder=3)
    ax.set_ylabel("answer preservation", fontsize=FS); ax.set_xlabel("evidence position", fontsize=FS)
    ax.set_ylim(0.35, 1.03); ax.grid(alpha=0.3); ax.tick_params(labelsize=FS_SMALL)
    ax.legend(fontsize=FS_SMALL, loc="lower right", frameon=False)
    fig.tight_layout(pad=0.3)
    out = FIG / "figure_position_sweep.pdf"; fig.savefig(out, metadata=PDFMETA); plt.close(fig); print("wrote", out)
    with open(FIG / "figure_position_sweep.data.csv", "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["series", "method_key", "position", "answer_preservation", "source", "numbers_id"])
        for lab, (k, ys, nid) in data.items():
            for p, y in zip(positions, ys):
                cw.writerow([lab, k, p, f"{y:.3f}", "SUB/results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv", nid])


def external_sanity_figure() -> None:
    """Appendix H robustness figure (donor copy): full-prefill-correct subsets (NUMBERS C1-C2) and the Mistral-7B noisy
    diagnostic (NUMBERS X1-X3, X5, X7). Included at 0.95\\linewidth in a figure*."""
    left = []
    for ds, lab in [("hotpotqa", "Hotpot"), ("2wiki", "2Wiki")]:
        rows = list(csv.DictReader(open(SUB / f"results/acl_qwen25_7b_{ds}_suffix_main_500/answer_eval_metrics.csv")))
        full_ok = {r["example_id"] for r in rows if r["method"] == "full_prefill" and r["gold_exact_match"] == "True"}
        def eq(m):
            sub = [r for r in rows if r["method"] == m and r["example_id"] in full_ok]
            return sum(r["answer_equivalence_to_full_prefill"] == "True" for r in sub) / len(sub)
        left.append((f"{lab}\nprefix", "prefix_conditioned_naive_global", eq("prefix_conditioned_naive_global"), len(full_ok), ds))
        left.append((f"{lab}\nrisk K2", "risk_guided_suffix_closure_k2", eq("risk_guided_suffix_closure_k2"), len(full_ok), ds))
    mis = json.load(open(SUB / "results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json"))["method_level"]
    right = [("Prefix", "prefix_conditioned_naive_global", "X7"), ("Query K1", "query_similarity_suffix_closure_k1", "X1"),
             ("Risk K1", "risk_guided_suffix_closure_k1", "X2"), ("Hybrid K1", "hybrid_query_risk_union_suffix_k1", "X3"),
             ("Risk K2", "risk_guided_suffix_closure_k2", "X5")]
    rvals = [mis[k]["answer_equivalence_to_full_prefill"] for _, k, _ in right]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(0.95 * TEXT, 2.3), gridspec_kw={"width_ratios": [1, 1.2]})
    cols = ["#b8c1cc", "#2ca25f", "#b8c1cc", "#2ca25f"]
    x = np.arange(4)
    ax1.bar(x, [p[2] for p in left], 0.7, color=cols, edgecolor="black")
    for i, p in enumerate(left):
        ax1.text(i, p[2] + 0.012, f"{p[2]:.3f}", ha="center", fontsize=FS_SMALL)
    ax1.set_xticks(x); ax1.set_xticklabels([p[0] for p in left], fontsize=FS_SMALL); ax1.tick_params(axis="y", labelsize=FS_SMALL)
    ax1.set_ylim(0.4, 1.06); ax1.set_ylabel("answer preservation,\nfull-prefill-correct subset", fontsize=FS); ax1.grid(axis="y", alpha=0.3)
    ax1.set_title("Gold-correct subsets (Qwen2.5-7B)", fontsize=FS)
    cols2 = ["#b8c1cc", "#2c7fb8", "#2ca25f", "#7b6fd0", "#2ca25f"]
    x2 = np.arange(5)
    ax2.bar(x2, rvals, 0.7, color=cols2, edgecolor="black")
    for i, v in enumerate(rvals):
        ax2.text(i, v + 0.012, f"{v:.3f}", ha="center", fontsize=FS_SMALL)
    ax2.set_xticks(x2); ax2.set_xticklabels([p[0] for p in right], fontsize=FS_SMALL); ax2.tick_params(axis="y", labelsize=FS_SMALL)
    ax2.set_ylim(0.2, 1.08); ax2.set_ylabel("answer preservation", fontsize=FS); ax2.grid(axis="y", alpha=0.3)
    ax2.set_title("Mistral-7B noisy diagnostic (250 examples)", fontsize=FS)
    fig.tight_layout(pad=0.4)
    out = FIG / "figure5_external_sanity.pdf"; fig.savefig(out, metadata=PDFMETA); plt.close(fig); print("wrote", out)
    with open(FIG / "figure5_external_sanity.data.csv", "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["panel", "label", "method_key", "answer_preservation", "n", "source", "numbers_id"])
        for (lab, k, v, n, ds), nid in zip(left, ["C1", "C1", "C2", "C2"]):
            cw.writerow(["left", lab.replace("\n", " "), k, f"{v:.3f}", n, f"SUB/results/acl_qwen25_7b_{ds}_suffix_main_500/answer_eval_metrics.csv (full_prefill gold_exact_match == True)", nid])
        for (lab, k, nid), v in zip(right, rvals):
            cw.writerow(["right", lab, k, f"{v:.3f}", mis[k]["num_rows"], "SUB/results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json", nid])


def setup_figure() -> None:
    """Figure 1 schematic (figure*, included at 0.92\\linewidth = 5.8 in). Conceptual; no data."""
    W = 0.92 * TEXT
    fig, ax = plt.subplots(figsize=(W, 1.85))
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    stages = [
        (0.125, "1. Full prefill (oracle)", "one causal pass over\np, d1, d2, d3, q", "#c9dff2", "#2f5f9f"),
        (0.375, "2. Document caches", "same text, each encoded\nafter the prefix only", "#fbd9a0", "#a65e00"),
        (0.625, "3. Composed state", "fluent, but not\nnecessarily reachable", "#f6a9a0", "#b4492d"),
        (0.875, "4. Suffix repair", "re-encode from the\nselected start document", "#c6e9b8", "#3f8b45"),
    ]
    bw, bh, by = 0.235, 0.15, 0.83
    for cx, title, sub, face, edge in stages:
        ax.add_patch(plt.Rectangle((cx - bw / 2, by), bw, bh, facecolor=face, edgecolor=edge, lw=1.2, zorder=2))
        ax.text(cx, by + bh / 2, title, ha="center", va="center", fontsize=FS, weight="bold", zorder=3)
        ax.text(cx, by - 0.035, sub, ha="center", va="top", fontsize=FS_SMALL, color="#555555", linespacing=1.15)
    # token strips
    PAL = {"p": "#e5e5e5", "d1": "#4a8fd1", "d2": "#2ca25f", "d3": "#4a8fd1", "q": "#8c6bb1", "d2*": "#b5e3a6", "d3*": "#b5e3a6"}
    def strip(x0, y0, cells, width, h=0.075):
        cw = width / len(cells)
        for i, c in enumerate(cells):
            ax.add_patch(plt.Rectangle((x0 + i * cw, y0), cw, h, facecolor=PAL[c], edgecolor="#333333", lw=0.6, zorder=2))
            ax.text(x0 + (i + 0.5) * cw, y0 + h / 2, c, ha="center", va="center", fontsize=FS_SMALL, zorder=3,
                    color="white" if c in ("d1", "d3", "q") else "black")
    sw = 0.20; sy = 0.44
    strip(0.125 - sw / 2, sy, ["p", "d1", "d2", "d3", "q"], sw)
    for j, d in enumerate(["d1", "d2", "d3"]):
        strip(0.375 - sw * 0.3, sy + 0.095 - j * 0.095, ["p", d], sw * 0.6)
    strip(0.625 - sw / 2, sy, ["p", "d1", "d2", "d3", "q"], sw)
    xc = 0.625 - sw / 2 + sw * 0.5
    ax.plot([xc - 0.018, xc + 0.018], [sy - 0.015, sy + 0.09], color="#d62728", lw=1.4, zorder=4)
    ax.plot([xc + 0.018, xc - 0.018], [sy - 0.015, sy + 0.09], color="#d62728", lw=1.4, zorder=4)
    strip(0.875 - sw / 2, sy, ["p", "d1", "d2*", "d3*", "q"], sw)
    arrow = dict(arrowstyle="->", lw=1.0, color="#555555")
    ya = sy + 0.037
    ax.annotate("", xy=(0.625 - sw / 2 - 0.008, ya), xytext=(0.375 + sw * 0.3 + 0.008, ya), arrowprops=arrow)
    ax.text(0.5, ya + 0.03, "compose", ha="center", va="bottom", fontsize=FS_SMALL, color="#555555")
    ax.annotate("", xy=(0.875 - sw / 2 - 0.008, ya), xytext=(0.625 + sw / 2 + 0.008, ya), arrowprops=arrow)
    ax.text(0.75, ya + 0.03, "repair", ha="center", va="bottom", fontsize=FS_SMALL, color="#555555")
    ax.annotate("", xy=(0.375 - sw * 0.3 - 0.008, ya), xytext=(0.125 + sw / 2 + 0.008, ya),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8a3a00", linestyle="--"))
    ax.text(0.25, ya + 0.03, "compare", ha="center", va="bottom", fontsize=FS_SMALL, color="#8a3a00")
    notes = [(0.125, "reachable state,\nreference behavior", "#222222", "bold"),
             (0.375, "locally valid slices,\nmissing neighbors", "#555555", "normal"),
             (0.625, "unreachable causal state,\nanswer drift", "#c0392b", "bold"),
             (0.875, "suffix from d2 recomputed,\nback toward the oracle", "#2e7d32", "bold")]
    for cx, t, c, wgt in notes:
        ax.text(cx, sy - 0.16, t, ha="center", va="top", fontsize=FS_SMALL, color=c, weight=wgt, linespacing=1.15)
    ax.text(0.5, 0.0, "Evaluation target: answer equivalence to full prefill on the exact prompt.\n"
                      "Cost target: recomputed context ratio and measured time to first logit.",
            ha="center", va="bottom", fontsize=FS_SMALL, color="#222222", linespacing=1.15)
    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
    out = FIG / "figure1_setup.pdf"; fig.savefig(out, metadata=PDFMETA); plt.close(fig); print("wrote", out)


if __name__ == "__main__":
    budget_figure()
    mechanism_figures()
    external_sanity_figure()
    setup_figure()
