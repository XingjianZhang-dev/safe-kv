#!/usr/bin/env python
"""Analyze external answer-eval subsets where full prefill is a stronger reference."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.paper_analysis import (  # noqa: E402
    external_subset_rows,
    markdown_table,
    read_csv_rows,
    write_csv_rows,
    write_json,
)


FIELDNAMES = [
    "model",
    "dataset_split",
    "quality_subset",
    "method",
    "n_examples",
    "answer_equivalence_to_full_prefill",
    "gold_exact_match",
    "gold_token_f1",
    "answer_contains_gold",
    "answer_changed_from_full",
    "answer_changed_and_gold_wrong",
    "patched_token_ratio",
    "first_token_kl_full_to_method",
    "top1_match",
    "base_changed_count",
    "repaired_base_changes_by_method",
    "repair_rate_among_base_changes",
    "small_n_warning",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qwen05-results", type=Path, required=True)
    parser.add_argument("--qwen15-results", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inputs = [
        ("qwen05_external", args.qwen05_results),
        ("qwen15_external", args.qwen15_results),
    ]
    all_rows = []
    summaries = []
    for model_label, result_dir in inputs:
        metrics_path = result_dir / "answer_eval_metrics.csv"
        if not metrics_path.exists():
            raise SystemExit(
                f"Missing {metrics_path}. Run Milestone 6C external answer eval first."
            )
        rows, summary = external_subset_rows(
            model_label=model_label,
            metrics_rows=read_csv_rows(metrics_path),
        )
        all_rows.extend(rows)
        summaries.append(summary)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_rows(args.out_dir / "external_subset_analysis.csv", all_rows, FIELDNAMES)
    write_json(args.out_dir / "external_subset_analysis_summary.json", summaries)
    (args.out_dir / "external_subset_analysis.md").write_text(
        _markdown_report(all_rows),
        encoding="utf-8",
    )


def _markdown_report(rows):
    focus = [
        row
        for row in rows
        if row["dataset_split"] == "all_external"
        and row["quality_subset"]
        in {
            "all_external",
            "full_prefill_gold_exact_match",
            "full_prefill_gold_f1_ge_0.5",
            "full_prefill_gold_f1_ge_0.8",
        }
        and row["method"]
        in {
            "prefix_conditioned_naive_global",
            "oracle_evidence_doc_patch",
            "query_similarity_doc_patch_k2",
            "entity_overlap_doc_patch_k2",
            "random_doc_patch_k2_seeded",
        }
    ]
    display = []
    for row in focus:
        display.append(
            {
                "model": row["model"],
                "subset": row["quality_subset"],
                "method": row["method"],
                "n": row["n_examples"],
                "ans_eq": f"{float(row['answer_equivalence_to_full_prefill']):.3f}",
                "changed_wrong": row["answer_changed_and_gold_wrong"],
                "repair_rate": f"{float(row['repair_rate_among_base_changes']):.3f}",
                "small_n": row["small_n_warning"],
            }
        )
    return "\n".join(
        [
            "# External Full-Prefill-Quality Subset Analysis",
            "",
            markdown_table(
                display,
                ["model", "subset", "method", "n", "ans_eq", "changed_wrong", "repair_rate", "small_n"],
            ),
            "",
        ]
    )


if __name__ == "__main__":
    main()

