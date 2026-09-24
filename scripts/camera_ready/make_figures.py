#!/usr/bin/env python3
"""Regenerate every figure of the camera-ready from the raw result files.

Step 1 (this file) reads the result files and writes the plotted values of each data figure to
paper_reference/final_figures/<name>.data.csv, with the source file and the NUMBERS id of every value.
Step 2 (draw_figures.py, called at the end) draws the five PDFs from those CSVs only.

  figure1_setup.pdf              Figure 1 (Section 1)    schematic; no data
  figure_local_vs_suffix.pdf     Figure 2 (Section 6.2)  NUMBERS W1-W6                 + .data.csv
  figure_position_sweep.pdf      Figure 3 (Section 6.3)  NUMBERS P1-P3, P5             + .data.csv
  figure5_external_sanity.pdf    Figure 4 (Appendix H)   NUMBERS C1-C2, X1-X3, X5, X7  + .data.csv
  figure4_budget_gate_pareto.pdf Figure 5 (Appendix K)   NUMBERS M7-M12, L1-L5         + .data.csv

The CSVs are byte-identical to the shipped ones. `--csv-only` skips drawing (no matplotlib needed).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT                         # results/ (main donor-copy runs)
REB = ROOT / "results_rebuttal"    # actual-forwarding, staleness and latency runs
FIG = ROOT / "paper_reference/final_figures"


def budget_data() -> None:
    """Figure 5 (Appendix K): quality-budget points (2Wiki-500, donor copy) and L40S first-logit medians."""
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
    out = FIG / "figure4_budget_gate_pareto.data.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "label", "x", "y", "source", "numbers_id"])
        for (lab, x, y), nid in zip(lpts, ["M7", "M9", "M10", "M11", "M12"]):
            w.writerow(["left", lab, f"{x:.4f}", f"{y:.3f}", "SUB/results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json", nid])
        for (lab, fm, km, ratio, sp), (wd, _), nid in zip(rpts, work, ["L1", "L2", "L3", "L4", "L5"]):
            w.writerow(["right", lab.replace("\n", " "), f"full_median_ms={fm:.1f}", f"riskk1_median_ms={km:.1f};repair_ratio={ratio:.4f};paired_speedup={sp:.3f}", f"REB/{wd}/latency_trace_summary.json", nid])
    print("wrote", out)


def mechanism_data() -> None:
    """Figure 2 (Section 6.2, 2Wiki-100 local-vs-suffix curve, NUMBERS W1-W6) and
    Figure 3 (Section 6.3, position sweep, NUMBERS P1-P3, P5)."""
    w = json.load(open(SUB / "results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json"))["method_level"]
    pts = [("Prefix", "prefix_conditioned_naive_global", "W1"), ("Doc K1", "risk_guided_doc_patch_k1", "W2"),
           ("w2", "risk_guided_downstream_w2_k1", "W3"), ("w3", "risk_guided_downstream_w3_k1", "W4"),
           ("w4", "risk_guided_downstream_w4_k1", "W5"), ("Suffix K1", "risk_guided_suffix_closure_k1", "W6")]
    xs = [w[k]["avg_patched_token_ratio"] for _, k, _ in pts]; ys = [w[k]["answer_equivalence_to_full_prefill"] for _, k, _ in pts]
    out = FIG / "figure_local_vs_suffix.data.csv"
    with open(out, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["label", "method_key", "recomputed_context_ratio", "answer_preservation", "source", "numbers_id"])
        for (lab, k, nid), x, y in zip(pts, xs, ys):
            cw.writerow([lab, k, f"{x:.4f}", f"{y:.3f}", "SUB/results/acl_qwen25_7b_2wiki_downstream_window_100/answer_eval_summary.json", nid])
    print("wrote", out)
    # position sweep
    rows = list(csv.DictReader(open(SUB / "results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv")))
    positions = ["first", "early", "middle", "late", "last"]
    series = [("prefix comp.", "prefix_conditioned_naive_global", "P1"), ("oracle doc patch", "oracle_evidence_doc_patch", "P2"),
              ("oracle suffix repair", "oracle_evidence_doc_suffix_closure_patch", "P3"), ("random suffix K1", "random_suffix_closure_k1_seeded", "P5")]
    data = {}
    for lab, k, nid in series:
        ys = [float(next(r for r in rows if r["method"] == k and r["position"] == p)["answer_equivalence"]) for p in positions]
        data[lab] = (k, ys, nid)
    out = FIG / "figure_position_sweep.data.csv"
    with open(out, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["series", "method_key", "position", "answer_preservation", "source", "numbers_id"])
        for lab, (k, ys, nid) in data.items():
            for p, y in zip(positions, ys):
                cw.writerow([lab, k, p, f"{y:.3f}", "SUB/results/acl_qwen25_7b_position_noise16_50x5_suffix/position_summary.csv", nid])
    print("wrote", out)


def external_sanity_data() -> None:
    """Figure 4 (Appendix H, donor copy): full-prefill-correct subsets (NUMBERS C1-C2, recomputed from the per-example
    rows) and the Mistral-7B noisy diagnostic (NUMBERS X1-X3, X5, X7)."""
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
    out = FIG / "figure5_external_sanity.data.csv"
    with open(out, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(["panel", "label", "method_key", "answer_preservation", "n", "source", "numbers_id"])
        for (lab, k, v, n, ds), nid in zip(left, ["C1", "C1", "C2", "C2"]):
            cw.writerow(["left", lab.replace("\n", " "), k, f"{v:.3f}", n, f"SUB/results/acl_qwen25_7b_{ds}_suffix_main_500/answer_eval_metrics.csv (full_prefill gold_exact_match == True)", nid])
        for (lab, k, nid), v in zip(right, rvals):
            cw.writerow(["right", lab, k, f"{v:.3f}", mis[k]["num_rows"], "SUB/results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json", nid])
    print("wrote", out)


if __name__ == "__main__":
    budget_data()
    mechanism_data()
    external_sanity_data()
    if "--csv-only" not in sys.argv[1:]:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import draw_figures
        draw_figures.main(FIG)
