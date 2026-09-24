#!/usr/bin/env python3
"""Draw the five camera-ready figures of SAFE-KV (Findings of AACL-IJCNLP 2026) from the plotted-value CSVs.

Every data figure is drawn only from the CSV shipped next to it in paper_reference/final_figures/ (written from the raw
result files by make_figures.py, which calls this script); no value is recomputed here. Figures are drawn at the
physical size at which the paper includes them (no \includegraphics scaling), with TrueType (Type 42) fonts and no
text below 7.5 pt.

  figure1_setup.pdf              Figure 1 (figure*, 0.92\linewidth = 5.80 in)  schematic, no data
  figure_local_vs_suffix.pdf     Figure 2 (column, 0.86\linewidth = 2.61 in)   figure_local_vs_suffix.data.csv
  figure_position_sweep.pdf      Figure 3 (column, 0.86\linewidth = 2.61 in)   figure_position_sweep.data.csv
  figure5_external_sanity.pdf    Figure 4 (figure*, 0.95\linewidth = 5.99 in)  figure5_external_sanity.data.csv
  figure4_budget_gate_pareto.pdf Figure 5 (figure*, 0.98\linewidth = 6.17 in)  figure4_budget_gate_pareto.data.csv

Usage: python -B scripts/camera_ready/draw_figures.py [OUTPUT_DIR]   (default: paper_reference/final_figures)

Fonts: the paper PDFs use Liberation Serif (metric-compatible with Times, matching the body text); Times New Roman or
Nimbus Roman is used when it is not installed, which changes glyph shapes but no value or layout.
Palette (colour-vision-deficiency safe): suffix repair / SAFE-KV = blue #2a78d6, local (document/window) repair =
orange #eb6834, query selector = aqua #1baf7a, hybrid selector = violet #4a3aa7, no repair / full prefill = neutral
gray. Identity is never carried by colour alone: every series is also direct-labelled or distinguished by marker shape.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

FIG = Path(__file__).resolve().parents[2] / "paper_reference" / "final_figures"

plt.rcParams.update({
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8.0,
    "axes.linewidth": 0.6, "axes.edgecolor": "#3d3d3a", "axes.labelcolor": "#1f1f1d",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 8.5, "axes.titleweight": "normal", "axes.titlepad": 4.0,
    "xtick.color": "#3d3d3a", "ytick.color": "#3d3d3a", "xtick.labelcolor": "#1f1f1d", "ytick.labelcolor": "#1f1f1d",
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "grid.color": "#e4e3de", "grid.linewidth": 0.5,
    "legend.fontsize": 7.5, "legend.frameon": False,
    "savefig.dpi": 300,
    "hatch.linewidth": 0.6,
})
META = {"CreationDate": None, "Creator": None, "Producer": None}

COL, TEXT = 3.03, 6.30          # ACL column / text width (in)
FS, FS_S = 8.0, 7.5             # label size, smallest size used anywhere
INK, INK2, MUTED = "#1f1f1d", "#52514e", "#8a8984"
BLUE, BLUE_D, BLUE_L = "#2a78d6", "#1c5cab", "#cde2fb"
ORANGE, ORANGE_L, ORANGE_D = "#eb6834", "#fbd9c9", "#b8491c"
AQUA, VIOLET = "#1baf7a", "#4a3aa7"
GRAY, GRAY_L = "#9b9a94", "#d9d8d2"


def read(name):
    with open(FIG / name, newline="") as f:
        return list(csv.DictReader(f))


def save(fig, name):
    fig.savefig(FIG / name, metadata=META)
    plt.close(fig)
    print("wrote", FIG / name)


# --------------------------------------------------------------------------- Figure 1 (schematic)
def fig1_setup():
    W, H = 0.92 * TEXT, 1.50
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

    # cell states: exact (computed under its true history), stale (mismatched history), fresh (re-encoded)
    STY = {
        "prefix": dict(fc="#ecebe6", ec="#8a8984", hatch=None, tc=INK),
        "exact": dict(fc=BLUE_L, ec=BLUE, hatch=None, tc=INK),
        "stale": dict(fc=ORANGE_L, ec=ORANGE, hatch="////", tc=INK),
        "fresh": dict(fc=BLUE, ec=BLUE_D, hatch=None, tc="white"),
    }
    cw, ch, gap = 0.232, 0.25, 0.022          # cell width/height/gap (in)
    panels = [
        ("(a) Full prefill", "reference behavior",
         [("p", "prefix"), ("d₁", "exact"), ("d₂", "exact"), ("d₃", "exact"), ("q", "exact")],
         None, "reference answer\n(one causal pass)", INK),
        ("(b) Composed cache", "each dᵢ encoded after p only",
         [("p", "prefix"), ("d₁", "exact"), ("d₂", "stale"), ("d₃", "stale"), ("q", "stale")],
         None, "mismatched histories:\nanswer can drift", ORANGE_D),
        ("(c) Document-only repair", "re-encode d₂ alone",
         [("p", "prefix"), ("d₁", "exact"), ("d₂", "fresh"), ("d₃", "stale"), ("q", "stale")],
         (2, 2), "d₃ still misses d₂:\ndrift persists", ORANGE_D),
        ("(d) SAFE-KV suffix repair", "re-encode Suffix($s$), $s{=}2$",
         [("p", "prefix"), ("d₁", "exact"), ("d₂", "fresh"), ("d₃", "fresh"), ("q", "fresh")],
         (2, 4), "consistent from $s$ on:\nanswer restored", BLUE_D),
    ]
    pw = W / 4
    y_strip = 0.62
    for k, (title, sub, cells, rep, outcome, ocol) in enumerate(panels):
        x_mid = pw * (k + 0.5)
        strip_w = 5 * cw + 4 * gap
        x0 = x_mid - strip_w / 2
        ax.text(x_mid, H - 0.07, title, ha="center", va="top", fontsize=FS, color=INK, weight="bold")
        ax.text(x_mid, H - 0.215, sub, ha="center", va="top", fontsize=FS_S, color=INK2)
        for i, (lab, st) in enumerate(cells):
            s = STY[st]
            xi = x0 + i * (cw + gap)
            if s["hatch"]:  # light hatch underneath, crisp border on top, so the label stays legible
                ax.add_patch(FancyBboxPatch((xi, y_strip), cw, ch, boxstyle="round,pad=0,rounding_size=0.03",
                                            fc=s["fc"], ec="#f4b89c", lw=0.0, hatch=s["hatch"], zorder=2))
                ax.add_patch(FancyBboxPatch((xi, y_strip), cw, ch, boxstyle="round,pad=0,rounding_size=0.03",
                                            fc="none", ec=s["ec"], lw=0.8, zorder=2.5))
            else:
                ax.add_patch(FancyBboxPatch((xi, y_strip), cw, ch, boxstyle="round,pad=0,rounding_size=0.03",
                                            fc=s["fc"], ec=s["ec"], lw=0.8, zorder=2))
            ax.text(xi + cw / 2, y_strip + ch / 2, lab, ha="center", va="center", fontsize=FS, color=s["tc"], zorder=3)
        if rep is not None:  # bracket over the re-encoded region
            a, b = rep
            xa = x0 + a * (cw + gap) - 0.004; xb = x0 + b * (cw + gap) + cw + 0.004
            yb = y_strip + ch + 0.05
            ax.plot([xa, xa, xb, xb], [yb - 0.03, yb, yb, yb - 0.03], color=BLUE_D, lw=0.8)
            ax.text((xa + xb) / 2, yb + 0.015, "re-encoded", ha="center", va="bottom", fontsize=FS_S, color=BLUE_D)
        if k == 2:  # stale dependency d3 -> d2 that document-only repair leaves in place
            xs = x0 + 3 * (cw + gap) + cw / 2; xt = x0 + 2 * (cw + gap) + cw / 2
            ax.annotate("", xy=(xt, y_strip - 0.015), xytext=(xs, y_strip - 0.015),
                        arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.9, mutation_scale=7,
                                        connectionstyle="arc3,rad=0.55", linestyle=(0, (2, 1.2))))
        ax.text(x_mid, 0.50, outcome, ha="center", va="top", fontsize=FS_S, color=ocol, linespacing=1.15,
                weight="bold" if k in (0, 3) else "normal")
        if k > 0:
            ax.plot([pw * k, pw * k], [0.26, H - 0.05], color="#e4e3de", lw=0.6)
    # legend (identity also carried by hatch and text colour)
    ly = 0.09
    items = [("exact history", "exact"), ("mismatched history", "stale"), ("re-encoded", "fresh"), ("static prefix", "prefix")]
    xs = [W * 0.20, W * 0.38, W * 0.58, W * 0.74]
    for (lab, st), xl in zip(items, xs):
        s = STY[st]
        if s["hatch"]:
            ax.add_patch(Rectangle((xl, ly - 0.055), 0.16, 0.11, fc=s["fc"], ec="#f4b89c", lw=0.0, hatch=s["hatch"]))
            ax.add_patch(Rectangle((xl, ly - 0.055), 0.16, 0.11, fc="none", ec=s["ec"], lw=0.7))
        else:
            ax.add_patch(Rectangle((xl, ly - 0.055), 0.16, 0.11, fc=s["fc"], ec=s["ec"], lw=0.7))
        ax.text(xl + 0.21, ly, lab, ha="left", va="center", fontsize=FS_S, color=INK2)
    save(fig, "figure1_setup.pdf")


# --------------------------------------------------------------------------- Figure 2 (local vs suffix)
def fig2_local_vs_suffix():
    rows = read("figure_local_vs_suffix.data.csv")
    P = {r["label"]: (float(r["recomputed_context_ratio"]), float(r["answer_preservation"])) for r in rows}
    fig, ax = plt.subplots(figsize=(0.86 * COL, 1.75))
    loc = ["Prefix", "Doc K1", "w2", "w3", "w4"]
    xs = [P[k][0] for k in loc]; ys = [P[k][1] for k in loc]
    ax.plot(xs, ys, color=ORANGE, lw=1.4, zorder=2)
    ax.scatter(xs[1:], ys[1:], s=22, marker="s", color=ORANGE, edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter([xs[0]], [ys[0]], s=24, color=GRAY, edgecolor="white", linewidth=0.6, zorder=3)
    sx, sy = P["Suffix K1"]
    ax.plot([xs[-1], sx], [ys[-1], sy], color=BLUE, lw=0.8, ls=(0, (2, 1.5)), zorder=1)
    ax.scatter([sx], [sy], s=46, marker="D", color=BLUE, edgecolor="white", linewidth=0.7, zorder=4)
    lab = {"Prefix": (0.0, -0.055, "center"), "Doc K1": (0.0, 0.045, "center"), "w2": (0.0, 0.045, "center"),
           "w3": (0.035, -0.035, "left"), "w4": (0.035, -0.035, "left")}
    for k in loc:
        dx, dy, ha = lab[k]
        ax.text(P[k][0] + dx, P[k][1] + dy, k, fontsize=FS_S, color=INK2, ha=ha, va="center")
    ax.text(sx - 0.035, sy + 0.005, "Suffix K1", fontsize=FS_S, color=BLUE_D, ha="right", va="center", weight="bold")
    ax.text(0.97, 0.05, "local repair\n(document, window)", transform=ax.transAxes, fontsize=FS_S, color=ORANGE_D,
            ha="right", va="bottom", linespacing=1.1)
    ax.set_xlim(-0.05, 0.9); ax.set_ylim(0.24, 1.04)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8]); ax.set_yticks([0.4, 0.6, 0.8, 1.0])
    ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_xlabel("recomputed context ratio", fontsize=FS); ax.set_ylabel("answer preservation", fontsize=FS)
    fig.tight_layout(pad=0.25)
    save(fig, "figure_local_vs_suffix.pdf")


# --------------------------------------------------------------------------- Figure 4 (robustness, Appendix H)
def bar_labels(ax, xs, vals, fmt="{:.3f}", dy=0.012):
    for x, v in zip(xs, vals):
        ax.text(x, v + dy, fmt.format(v), ha="center", va="bottom", fontsize=FS_S, color=INK)


def fig4_robustness():
    rows = read("figure5_external_sanity.data.csv")
    L = {r["label"]: float(r["answer_preservation"]) for r in rows if r["panel"] == "left"}
    R = [(r["label"], float(r["answer_preservation"])) for r in rows if r["panel"] == "right"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(0.95 * TEXT, 2.21), gridspec_kw={"width_ratios": [1, 1.25]})
    # (a) grouped by dataset, bars direct-labelled
    xs = [0, 0.8, 2.15, 2.95]; w = 0.64
    keys = ["Hotpot prefix", "Hotpot risk K2", "2Wiki prefix", "2Wiki risk K2"]
    vals = [L[k] for k in keys]
    a1.bar(xs, vals, w, color=[GRAY_L, BLUE, GRAY_L, BLUE], edgecolor=[GRAY, "none", GRAY, "none"], linewidth=0.6)
    bar_labels(a1, xs, vals, dy=0.015)
    a1.set_xticks(xs); a1.set_xticklabels(["Prefix", "Risk K2"] * 2, fontsize=FS_S)
    for xc, name in [(0.4, "HotpotQA (272 examples)"), (2.55, "2Wiki (226 examples)")]:
        a1.text(xc, -0.115, name, transform=a1.get_xaxis_transform(), ha="center", va="top", fontsize=FS, color=INK)
    a1.set_xlim(-0.5, 3.45)
    a1.set_ylim(0, 1.12); a1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a1.set_ylabel("answer preservation", fontsize=FS)
    a1.set_title("(a) Full-prefill-correct subsets, Qwen2.5-7B", fontsize=FS, loc="left")
    # (b) Mistral
    cols = {"Prefix": GRAY_L, "Query K1": AQUA, "Risk K1": BLUE, "Hybrid K1": VIOLET, "Risk K2": BLUE_D}
    x = np.arange(len(R)); vals = [v for _, v in R]
    a2.bar(x, vals, 0.62, color=[cols[k] for k, _ in R],
           edgecolor=[GRAY if k == "Prefix" else "none" for k, _ in R], linewidth=0.6)
    bar_labels(a2, x, vals, dy=0.015)
    a2.set_xticks(x); a2.set_xticklabels(["Prefix-comp." if k == "Prefix" else k for k, _ in R], fontsize=FS_S)
    a2.set_ylim(0, 1.12); a2.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a2.set_ylabel("answer preservation", fontsize=FS)
    a2.set_title("(b) Mistral-7B noisy diagnostic (250 examples)", fontsize=FS, loc="left")
    for a in (a1, a2):
        a.grid(axis="y"); a.set_axisbelow(True); a.tick_params(axis="x", length=0)
    fig.tight_layout(pad=0.3, w_pad=1.6)
    save(fig, "figure5_external_sanity.pdf")


# --------------------------------------------------------------------------- Figure 5 (budget + latency, Appendix K)
def fig5_budget_latency():
    rows = read("figure4_budget_gate_pareto.data.csv")
    left = {r["label"]: (float(r["x"]), float(r["y"])) for r in rows if r["panel"] == "left"}
    right = []
    for r in rows:
        if r["panel"] != "right":
            continue
        full = float(r["x"].split("=")[1])
        kv = dict(t.split("=") for t in r["y"].split(";"))
        right.append((r["label"], full, float(kv["riskk1_median_ms"]), float(kv["repair_ratio"])))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(0.98 * TEXT, 2.55), gridspec_kw={"width_ratios": [1, 1.3]})
    # (a) operating points
    sty = {"Prefix": (GRAY, "o"), "Random K2": ("#c98500", "v"), "Risk K1": (BLUE, "D"),
           "Hybrid K1": (VIOLET, "s"), "Risk K2": (BLUE_D, "D")}
    order = ["Random K2", "Risk K1", "Hybrid K1", "Risk K2"]
    a1.plot([left[k][0] for k in order], [left[k][1] for k in order], color=GRAY_L, lw=1.0, zorder=1)
    for k, (c, m) in sty.items():
        a1.scatter(*left[k], s=34, marker=m, color=c, edgecolor="white", linewidth=0.7, zorder=3)
    a1.annotate("Prefix", left["Prefix"], xytext=(0.06, left["Prefix"][1]), fontsize=FS_S, color=INK, va="center")
    a1.annotate("Random K2", left["Random K2"], xytext=(left["Random K2"][0] - 0.04, left["Random K2"][1]),
                fontsize=FS_S, color=INK, ha="right", va="center")
    # inset: the high-fidelity cluster
    ins = a1.inset_axes([0.37, 0.22, 0.57, 0.36])
    ins.plot([left[k][0] for k in order[1:]], [left[k][1] for k in order[1:]], color=GRAY_L, lw=1.0, zorder=1)
    for k in order[1:]:
        c, m = sty[k]
        ins.scatter(*left[k], s=34, marker=m, color=c, edgecolor="white", linewidth=0.7, zorder=3)
    for k, (dx, dy, ha) in {"Risk K1": (0.0, -0.0042, "center"), "Hybrid K1": (0.0, 0.0034, "center"),
                            "Risk K2": (-0.004, 0.0036, "center")}.items():
        ins.text(left[k][0] + dx, left[k][1] + dy, k, fontsize=FS_S, color=INK, ha=ha, va="center")
    ins.set_xlim(0.79, 0.96); ins.set_ylim(0.962, 0.992)
    ins.set_xticks([0.8, 0.85, 0.9, 0.95]); ins.set_yticks([0.97, 0.98, 0.99])
    ins.tick_params(labelsize=FS_S, length=2)
    for sp in ins.spines.values():
        sp.set_visible(True); sp.set_color(MUTED); sp.set_linewidth(0.5)
    ins.grid(True); ins.set_axisbelow(True)
    a1.indicate_inset_zoom(ins, edgecolor=MUTED, alpha=0.9, linewidth=0.5)
    a1.set_xlim(-0.03, 1.02); a1.set_ylim(0.3, 1.06)
    a1.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); a1.set_yticks([0.4, 0.6, 0.8, 1.0])
    a1.grid(True); a1.set_axisbelow(True)
    a1.set_xlabel("recomputed context ratio (donor copy)", fontsize=FS)
    a1.set_ylabel("answer preservation (2Wiki-500)", fontsize=FS)
    a1.set_title("(a) Quality\u2013budget operating points", fontsize=FS, loc="left")
    # (b) latency
    idx = np.arange(len(right)); w = 0.36
    full = [r[1] for r in right]; k1 = [r[2] for r in right]
    a2.bar(idx - w / 2 - 0.01, full, w, color=GRAY_L, edgecolor=GRAY, linewidth=0.6, label="Full prefill")
    a2.bar(idx + w / 2 + 0.01, k1, w, color=BLUE, label="Risk suffix K1 (actual forwarding + planning)")
    for i, r in enumerate(right):
        a2.text(i - w / 2 - 0.01, r[1] + 3, f"{r[1]:.1f}", ha="center", va="bottom", fontsize=FS_S, color=INK)
        a2.text(i + w / 2 + 0.01, r[2] + 3, f"{r[2]:.1f}", ha="center", va="bottom", fontsize=FS_S, color=INK)
    names = {"HotpotQA original": "HotpotQA\noriginal", "2Wiki original": "2Wiki\noriginal",
             "2Wiki shuffled": "2Wiki\nshuffled", "N=16 nested": "$N{=}16$\nnested", "Noise64 (67 docs)": "Noise64\n(67 docs)"}
    a2.set_xticks(idx)
    a2.set_xticklabels([f"{names[r[0]]}\n{100 * r[3]:.0f}% re-enc." for r in right], fontsize=FS_S, linespacing=1.1)
    a2.tick_params(axis="x", length=0)
    a2.set_ylim(0, 262); a2.set_yticks([0, 50, 100, 150, 200, 250])
    a2.set_ylabel("median time to first logit (ms)", fontsize=FS)
    a2.set_title("(b) Latency on one L40S (batch 1)", fontsize=FS, loc="left")
    a2.legend(loc="upper left", handlelength=1.0, handletextpad=0.4)
    a2.grid(axis="y"); a2.set_axisbelow(True)
    fig.tight_layout(pad=0.3, w_pad=1.6)
    save(fig, "figure4_budget_gate_pareto.pdf")


# --------------------------------------------------------------------------- Figure 3 (position sweep, Section 6.3)
def fig3_position_sweep():
    rows = read("figure_position_sweep.data.csv")
    pos = ["first", "early", "middle", "late", "last"]
    series = [("prefix comp.", GRAY, "o", "-"), ("oracle doc patch", ORANGE, "s", "-"),
              ("oracle suffix repair", BLUE, "^", "-"), ("random suffix K1", VIOLET, "D", (0, (3, 1.5)))]
    fig, ax = plt.subplots(figsize=(0.86 * COL, 2.00))
    x = np.arange(5)
    for lab, c, m, ls in series:
        ys = [float(next(r for r in rows if r["series"] == lab and r["position"] == p)["answer_preservation"]) for p in pos]
        ax.plot(x, ys, color=c, marker=m, lw=1.3, ls=ls, markersize=4.2, markeredgecolor="white",
                markeredgewidth=0.6, label=lab, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(pos, fontsize=FS_S)
    ax.set_xlim(-0.25, 4.25); ax.set_ylim(0.2, 1.04); ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(axis="y"); ax.set_axisbelow(True)
    ax.set_xlabel("position of the evidence document", fontsize=FS); ax.set_ylabel("answer preservation", fontsize=FS)
    ax.legend(loc="lower right", handlelength=1.8, handletextpad=0.5, borderaxespad=0.2)
    fig.tight_layout(pad=0.25)
    save(fig, "figure_position_sweep.pdf")


def main(out_dir=None):
    global FIG
    if out_dir is not None:
        FIG = Path(out_dir)
    fig1_setup(); fig2_local_vs_suffix(); fig3_position_sweep(); fig4_robustness(); fig5_budget_latency()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
