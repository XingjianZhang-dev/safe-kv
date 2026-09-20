#!/usr/bin/env python3
"""Build the main external 7B figure from answer-eval summaries.

The main figure uses operating points available for both HotpotQA-500 and
2Wiki-500 after the HotpotQA Hybrid K1 increment was completed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


METHODS = [
    ("Prefix", "prefix_conditioned_naive_global"),
    ("Random K2", "random_suffix_closure_k2_seeded"),
    ("Query K2", "query_similarity_suffix_closure_k2"),
    ("Risk K1", "risk_guided_suffix_closure_k1"),
    ("Hybrid K1", "hybrid_query_risk_union_suffix_k1"),
    ("Risk K2", "risk_guided_suffix_closure_k2"),
]

CHANGE_METHODS = [
    ("Prefix", "prefix_conditioned_naive_global"),
    ("Random K2", "random_suffix_closure_k2_seeded"),
    ("Risk K1", "risk_guided_suffix_closure_k1"),
    ("Hybrid K1", "hybrid_query_risk_union_suffix_k1"),
    ("Risk K2", "risk_guided_suffix_closure_k2"),
]

DATASETS = [
    (
        "HotpotQA-500",
        Path("results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_summary.json"),
        "#2c7fb8",
    ),
    (
        "2Wiki-500",
        Path("results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json"),
        "#2ca25f",
    ),
]


def load_metric(results_root: Path, rel_path: Path, method: str, key: str) -> float:
    data = json.loads((results_root / rel_path).read_text())
    return float(data["method_level"][method][key])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--paper-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "SAFE_KV__Semantic_State_Reuse_and_Document_Level_Repair_for_Non_Prefix_KV_Caches_in_RAG",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paper_dir = args.paper_dir.resolve()
    out_pdf = paper_dir / "figures" / "figure2_category_drift.pdf"
    mirror_pdf = repo_root / "paper_reference" / "final_figures" / "figure2_category_drift.pdf"

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.05), gridspec_kw={"width_ratios": [1.22, 1]})
    fig.suptitle(
        "External 7B RAG: unsafe cache composition changes answers; suffix repair restores behavior",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    ax = axes[0]
    x = np.arange(len(METHODS))
    width = 0.34
    offsets = [-width / 2, width / 2]
    for offset, (label, rel_path, color) in zip(offsets, DATASETS):
        values = [
            load_metric(repo_root, rel_path, method, "answer_equivalence_to_full_prefill")
            for _, method in METHODS
        ]
        bars = ax.bar(
            x + offset,
            values,
            width,
            label=label,
            color=color,
            alpha=0.36 if label.startswith("2Wiki") else 0.72,
            edgecolor=color,
            linewidth=1.2,
        )
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.012,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
                fontweight="bold",
            )
    ax.axhline(1.0, color="#8f8f8f", linestyle="--", linewidth=1.0)
    ax.set_ylabel("answer equivalence to full prefill", fontsize=10)
    ax.set_ylim(0.30, 1.04)
    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _ in METHODS], rotation=22, ha="right")
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False, loc="lower right", fontsize=9)

    ax = axes[1]
    x2 = np.arange(len(CHANGE_METHODS))
    for label, rel_path, color in DATASETS:
        values = [
            load_metric(repo_root, rel_path, method, "answer_changed_and_gold_wrong_count")
            for _, method in CHANGE_METHODS
        ]
        ax.plot(x2, values, marker="o", linewidth=2.3, markersize=5.5, label=label, color=color)
        for xx, value in zip(x2, values):
            ax.text(
                xx,
                value * 1.14,
                f"{int(value)}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=color,
                fontweight="bold",
            )
    ax.set_yscale("log")
    ax.set_ylabel("changed-and-gold-wrong count", fontsize=10)
    ax.set_xticks(x2)
    ax.set_xticklabels([label for label, _ in CHANGE_METHODS], rotation=22, ha="right")
    ax.grid(axis="y", which="both", alpha=0.22)
    ax.legend(frameon=False, loc="upper right", fontsize=9)

    fig.tight_layout()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight")
    mirror_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(mirror_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_pdf}")
    print(f"Wrote {mirror_pdf}")


if __name__ == "__main__":
    main()
