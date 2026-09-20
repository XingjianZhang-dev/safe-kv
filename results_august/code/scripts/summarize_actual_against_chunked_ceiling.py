#!/usr/bin/env python
"""Compare partial suffix repair with a chunked all-document positive control.

The all-document path is not a mathematical upper bound: finite-precision
execution partitioning and greedy near-ties can make exact-answer curves
non-monotonic.  This script therefore reports both references without adjusting
or normalizing one by the other.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


ACTUAL_PREFIX = "actual_recompute::"
CEILING_METHOD = "actual_recompute::all_document_patch"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partial-results-dir", type=Path, required=True)
    parser.add_argument("--ceiling-results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    partial_rows = read_jsonl(args.partial_results_dir / "answer_eval_outputs.jsonl")
    ceiling_rows = read_jsonl(args.ceiling_results_dir / "answer_eval_outputs.jsonl")
    ceiling_validation = json.loads(
        (args.ceiling_results_dir / "all_document_ceiling_validation.json").read_text(
            encoding="utf-8"
        )
    )
    failures: list[str] = []
    if ceiling_validation.get("status") != "PASS":
        failures.append("all-document ceiling validation is not PASS")

    actual_partial = [
        row
        for row in partial_rows
        if str(row["method"]).startswith(ACTUAL_PREFIX)
        and str(row["method"]) != CEILING_METHOD
    ]
    ceiling_by_example = {
        str(row["example_id"]): row
        for row in ceiling_rows
        if row["method"] == CEILING_METHOD
    }
    if len(ceiling_by_example) != args.expected_examples:
        failures.append("ceiling example coverage mismatch")
    method_names = sorted({str(row["method"]) for row in actual_partial})
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    reference_mismatch_examples: set[str] = set()
    for row in actual_partial:
        example_id = str(row["example_id"])
        ceiling = ceiling_by_example.get(example_id)
        if ceiling is None:
            failures.append(f"missing ceiling row for {example_id}")
            continue
        if (
            row["full_prefill_answer"] != ceiling["full_prefill_answer"]
            or row["normalized_full_prefill_answer"]
            != ceiling["normalized_full_prefill_answer"]
            or row["full_prefill_token_ids"] != ceiling["full_prefill_token_ids"]
        ):
            reference_mismatch_examples.add(example_id)
        by_method[str(row["method"])].append(
            {
                "normalized_exact_to_one_shot": bool(
                    row["answer_equivalence_to_full_prefill"]
                ),
                "postprocessed_string_exact_to_one_shot": (
                    row["generated_answer"] == row["full_prefill_answer"]
                ),
                "generated_token_exact_to_one_shot": (
                    row["generated_token_ids"] == row["full_prefill_token_ids"]
                ),
                "normalized_exact_to_chunked_all_document": (
                    row["normalized_generated_answer"]
                    == ceiling["normalized_generated_answer"]
                ),
                "postprocessed_string_exact_to_chunked_all_document": (
                    row["generated_answer"] == ceiling["generated_answer"]
                ),
                "generated_token_exact_to_chunked_all_document": (
                    row["generated_token_ids"] == ceiling["generated_token_ids"]
                ),
                "patched_token_ratio": float(row["patched_token_ratio"]),
            }
        )

    if reference_mismatch_examples:
        failures.append(
            f"one-shot full reference differs across runs for "
            f"{len(reference_mismatch_examples)} examples"
        )
    summaries = []
    metric_fields = [
        "normalized_exact_to_one_shot",
        "postprocessed_string_exact_to_one_shot",
        "generated_token_exact_to_one_shot",
        "normalized_exact_to_chunked_all_document",
        "postprocessed_string_exact_to_chunked_all_document",
        "generated_token_exact_to_chunked_all_document",
    ]
    for method in method_names:
        items = by_method[method]
        if len(items) != args.expected_examples:
            failures.append(f"partial method coverage mismatch for {method}: {len(items)}")
        summaries.append(
            {
                "method": method,
                "num_examples": len(items),
                **{
                    f"{field}_rate": mean(float(item[field]) for item in items)
                    for field in metric_fields
                },
                "mean_patched_token_ratio": mean(
                    item["patched_token_ratio"] for item in items
                ),
            }
        )

    ceiling_items = list(ceiling_by_example.values())
    report = {
        "status": "PASS" if not failures else "FAIL",
        "num_examples": args.expected_examples,
        "num_partial_methods": len(method_names),
        "num_failures": len(failures),
        "failures": failures,
        "one_shot_reference_mismatch_count": len(reference_mismatch_examples),
        "chunked_all_document_positive_control": {
            "normalized_exact_to_one_shot_rate": mean(
                float(row["answer_equivalence_to_full_prefill"])
                for row in ceiling_items
            ),
            "postprocessed_string_exact_to_one_shot_rate": mean(
                float(row["generated_answer"] == row["full_prefill_answer"])
                for row in ceiling_items
            ),
            "generated_token_exact_to_one_shot_rate": mean(
                float(row["generated_token_ids"] == row["full_prefill_token_ids"])
                for row in ceiling_items
            ),
            "mean_patched_token_ratio": mean(
                float(row["patched_token_ratio"]) for row in ceiling_items
            ),
        },
        "partial_method_summaries": summaries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def mean(values: Any) -> float:
    materialized = list(values)
    return statistics.fmean(materialized) if materialized else 0.0


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
