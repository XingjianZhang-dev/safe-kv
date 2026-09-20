#!/usr/bin/env python
"""Build SAFE-KV recomputation-budget proxy tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.cost_accounting import cost_accounting_rows, cost_markdown_table  # noqa: E402
from safekv.paper_analysis import read_csv_rows, write_csv_rows  # noqa: E402


DEFAULT_RUNS = [
    ("qwen05", "diagnostic_clean", "results_qwen05_100_answer/answer_eval_metrics.csv"),
    ("qwen05", "diagnostic_noisy", "results_qwen05_100_noisy_answer/answer_eval_metrics.csv"),
    ("qwen15", "diagnostic_clean", "results_qwen15_100_answer/answer_eval_metrics.csv"),
    ("qwen15", "diagnostic_noisy", "results_qwen15_100_noisy_answer/answer_eval_metrics.csv"),
    ("qwen05", "external_multihop", "results_qwen05_external_answer/answer_eval_metrics.csv"),
    ("qwen15", "external_multihop", "results_qwen15_external_answer/answer_eval_metrics.csv"),
    ("smollm17", "diagnostic_noisy", "results_smollm17_noisy_answer/answer_eval_metrics.csv"),
    ("smollm17", "external_multihop", "results_smollm17_external_answer/answer_eval_metrics.csv"),
]

DEFAULT_METHODS = {
    "full_prefill",
    "prefix_conditioned_naive_global",
    "oracle_evidence_doc_patch",
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_k2",
    "safe_gate_t0.60",
    "random_doc_patch_k2_seeded",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("results_paper"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    missing = []
    for model, dataset, path_text in DEFAULT_RUNS:
        path = Path(path_text)
        if not path.exists():
            missing.append(path_text)
            continue
        rows.extend(
            cost_accounting_rows(
                model=model,
                dataset=dataset,
                metric_rows=read_csv_rows(path),
                methods=DEFAULT_METHODS,
            )
        )

    fields = [
        "model",
        "dataset",
        "method",
        "n_examples",
        "answer_equivalence_to_full_prefill",
        "changed_wrong_rate",
        "patched_doc_count",
        "patched_token_ratio",
        "estimated_recompute_ratio",
        "estimated_prefill_saving",
    ]
    write_csv_rows(args.out_dir / "table7_cost_accounting.csv", rows, fields)
    md = [
        "# SAFE-KV Cost Accounting",
        "",
        "These are recomputation-budget proxies, not measured serving latency.",
        "`estimated_recompute_ratio = patched_token_ratio`; `estimated_prefill_saving = 1 - patched_token_ratio`.",
        "",
        cost_markdown_table(rows),
    ]
    if missing:
        md.extend(["", "## Missing Optional Inputs", ""])
        md.extend(f"- `{item}`" for item in missing)
    (args.out_dir / "table7_cost_accounting.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} cost-accounting rows to {args.out_dir}")


if __name__ == "__main__":
    main()
