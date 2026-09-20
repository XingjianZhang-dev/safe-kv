#!/usr/bin/env python
"""Build virtual adaptive-threshold Pareto curves from answer-eval outputs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import read_answer_rows, summarize_answer_eval_rows  # noqa: E402
from safekv.data_schema import DiagnosticExample  # noqa: E402
from safekv.doc_selector import safe_composition_risk  # noqa: E402


SELECTOR_METHODS = {
    "query": (
        "query_similarity_doc_patch_k2",
        "query_similarity_suffix_closure_k2",
    ),
    "risk": (
        "risk_guided_doc_patch_k2",
        "risk_guided_suffix_closure_k2",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument(
        "--thresholds",
        type=str,
        default="0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85",
    )
    parser.add_argument(
        "--selectors",
        type=str,
        default="query,risk",
        help="Comma-separated selector names: query,risk",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    thresholds = [float(item) for item in args.thresholds.split(",") if item.strip()]
    selectors = [item.strip() for item in args.selectors.split(",") if item.strip()]

    examples = load_examples(args.data_path)
    risks = {example.id: safe_composition_risk(example)[0] for example in examples}
    rows_by_key = {
        (row["example_id"], row["method"]): row
        for row in read_answer_rows(args.outputs)
    }
    result_rows: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for selector in selectors:
        if selector not in SELECTOR_METHODS:
            raise ValueError(f"unknown selector {selector!r}")
        doc_method, suffix_method = SELECTOR_METHODS[selector]
        for threshold in thresholds:
            virtual_rows = []
            for example in examples:
                chosen_method = doc_method if risks[example.id] < threshold else suffix_method
                source = rows_by_key.get((example.id, chosen_method))
                if source is None:
                    continue
                row = dict(source)
                row["method"] = virtual_method_name(selector, threshold)
                row["adaptive_threshold"] = threshold
                row["adaptive_source_method"] = chosen_method
                row["risk_score"] = risks[example.id]
                virtual_rows.append(row)
            summary = summarize_answer_eval_rows(virtual_rows)
            method_summary = summary["method_level"][virtual_method_name(selector, threshold)]
            csv_rows.append(
                {
                    "selector": selector,
                    "threshold": threshold,
                    "num_examples": len(virtual_rows),
                    "answer_equivalence": method_summary[
                        "answer_equivalence_to_full_prefill"
                    ],
                    "gold_em": method_summary["gold_exact_match"],
                    "gold_f1": method_summary["gold_token_f1"],
                    "changed_wrong": method_summary[
                        "answer_changed_and_gold_wrong_count"
                    ]
                    / max(1, method_summary["num_rows"]),
                    "patch_ratio": method_summary["avg_patched_token_ratio"],
                    "avg_kl": method_summary["avg_first_token_kl"],
                }
            )
            result_rows.append(
                {
                    "selector": selector,
                    "threshold": threshold,
                    "summary": method_summary,
                }
            )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "selector",
                "threshold",
                "num_examples",
                "answer_equivalence",
                "gold_em",
                "gold_f1",
                "changed_wrong",
                "patch_ratio",
                "avg_kl",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)
    args.out_json.write_text(
        json.dumps(result_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(csv_rows, indent=2, ensure_ascii=False))


def load_examples(path: Path) -> list[DiagnosticExample]:
    examples = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                examples.append(DiagnosticExample.from_dict(json.loads(line)))
    return examples


def virtual_method_name(selector: str, threshold: float) -> str:
    return f"{selector}_virtual_adaptive_t{threshold:.2f}"


if __name__ == "__main__":
    main()
