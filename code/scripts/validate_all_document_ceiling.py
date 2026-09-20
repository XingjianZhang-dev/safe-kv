#!/usr/bin/env python
"""Validate donor and actual all-document positive controls for answer evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


METHODS = ("all_document_patch", "actual_recompute::all_document_patch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = read_json(args.results_dir / "answer_eval_manifest.json")
    runner_summary = read_json(args.results_dir / "answer_eval_summary.json")
    rows = read_jsonl(args.results_dir / "answer_eval_outputs.jsonl")
    data_path = Path(manifest["data_path"])
    examples = read_jsonl(data_path)[: args.expected_examples]
    examples_by_id = {str(example["id"]): example for example in examples}
    failures: list[str] = []

    if len(examples) != args.expected_examples:
        failures.append(
            f"data example count {len(examples)} != expected {args.expected_examples}"
        )
    if len(examples_by_id) != len(examples):
        failures.append("duplicate example ids in input data")
    if file_sha256(data_path) != manifest.get("data_sha256"):
        failures.append("data hash does not match manifest")
    if tuple(manifest.get("methods", [])) != METHODS:
        failures.append("manifest method order/set mismatch")
    if runner_summary.get("failed_rows") or int(
        runner_summary.get("num_failed_rows", -1)
    ) != 0:
        failures.append("answer runner reported failed rows")

    expected_rows = args.expected_examples * len(METHODS)
    if len(rows) != expected_rows:
        failures.append(f"row count {len(rows)} != expected {expected_rows}")
    keys = [(str(row["example_id"]), str(row["method"])) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append("duplicate example/method keys")
    if {str(row["method"]) for row in rows} != set(METHODS):
        failures.append("output method set mismatch")
    if {str(row["example_id"]) for row in rows} != set(examples_by_id):
        failures.append("output example ids do not match the evaluated data prefix")

    rows_by_key = {
        (str(row["example_id"]), str(row["method"])): row for row in rows
    }
    paired_flags: list[dict[str, bool]] = []
    for example_id, example in examples_by_id.items():
        pair = [rows_by_key.get((example_id, method)) for method in METHODS]
        if any(row is None for row in pair):
            failures.append(f"missing method pair for {example_id}")
            continue
        donor, actual = pair
        assert donor is not None and actual is not None
        expected_doc_ids = [int(doc["doc_id"]) for doc in example["documents"]]
        expected_doc_set = set(expected_doc_ids)
        for row in pair:
            method = str(row["method"])
            selected_ids = [int(doc_id) for doc_id in row["selected_doc_ids"]]
            if len(selected_ids) != len(set(selected_ids)):
                failures.append(f"duplicate selected document id for {example_id}/{method}")
            if set(selected_ids) != expected_doc_set:
                failures.append(f"not all documents selected for {example_id}/{method}")
            if int(row["patched_doc_count"]) != len(expected_doc_ids):
                failures.append(f"patched document count mismatch for {example_id}/{method}")
            context_length = int(row["prompt_length"]) - int(row["query_length"])
            patched_count = int(row["patched_token_count"])
            ratio = float(row["patched_token_ratio"])
            if context_length <= 0 or patched_count <= 0 or patched_count > context_length:
                failures.append(f"invalid context/patch count for {example_id}/{method}")
            elif not math.isclose(
                ratio, patched_count / context_length, rel_tol=0.0, abs_tol=1e-12
            ):
                failures.append(f"patch ratio/count mismatch for {example_id}/{method}")
            kl = float(row["first_token_kl_full_to_method"])
            if not math.isfinite(kl) or kl < -1e-12:
                failures.append(f"invalid first-token KL for {example_id}/{method}")
            normalized_exact = (
                row["normalized_generated_answer"]
                == row["normalized_full_prefill_answer"]
            )
            if bool(row["answer_equivalence_to_full_prefill"]) != normalized_exact:
                failures.append(f"normalized exact flag mismatch for {example_id}/{method}")
            if bool(row["answer_changed_from_full"]) == normalized_exact:
                failures.append(f"answer-changed flag mismatch for {example_id}/{method}")
            token_exact = row["generated_token_ids"] == row["full_prefill_token_ids"]
            if token_exact and row["generated_answer"] != row["full_prefill_answer"]:
                failures.append(
                    f"token-identical outputs decode differently for {example_id}/{method}"
                )
        reference_fields = (
            "full_prefill_answer",
            "normalized_full_prefill_answer",
            "full_prefill_token_ids",
            "prompt_length",
            "query_length",
        )
        if any(donor[field] != actual[field] for field in reference_fields):
            failures.append(f"full reference mismatch within pair for {example_id}")
        if donor["selected_doc_ids"] != actual["selected_doc_ids"]:
            failures.append(f"selected-document order mismatch within pair for {example_id}")
        if donor["patched_token_count"] != actual["patched_token_count"]:
            failures.append(f"patch count mismatch within pair for {example_id}")
        paired_flags.append(
            {
                "same_generated_tokens": donor["generated_token_ids"]
                == actual["generated_token_ids"],
                "same_postprocessed_string": donor["generated_answer"]
                == actual["generated_answer"],
                "same_normalized_flag": donor["answer_equivalence_to_full_prefill"]
                == actual["answer_equivalence_to_full_prefill"],
            }
        )

    method_summaries = []
    for method in METHODS:
        items = [row for row in rows if row["method"] == method]
        method_summaries.append(
            {
                "method": method,
                "num_examples": len(items),
                "normalized_answer_exact_rate": mean_bool(
                    bool(row["answer_equivalence_to_full_prefill"]) for row in items
                ),
                "postprocessed_string_exact_rate": mean_bool(
                    row["generated_answer"] == row["full_prefill_answer"]
                    for row in items
                ),
                "generated_token_exact_rate": mean_bool(
                    row["generated_token_ids"] == row["full_prefill_token_ids"]
                    for row in items
                ),
                "mean_first_token_kl": statistics.fmean(
                    float(row["first_token_kl_full_to_method"]) for row in items
                )
                if items
                else 0.0,
                "max_first_token_kl": max(
                    (float(row["first_token_kl_full_to_method"]) for row in items),
                    default=0.0,
                ),
                "mean_patched_token_ratio": statistics.fmean(
                    float(row["patched_token_ratio"]) for row in items
                )
                if items
                else 0.0,
            }
        )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "interpretation": (
            "all-document execution-partition positive control; not a mathematical "
            "upper bound on exact-answer preservation"
        ),
        "num_rows": len(rows),
        "expected_rows": expected_rows,
        "num_examples": len(examples_by_id),
        "num_failures": len(failures),
        "failures": failures,
        "method_summaries": method_summaries,
        "paired_donor_actual": {
            "num_examples": len(paired_flags),
            "same_generated_tokens_rate": mean_bool(
                item["same_generated_tokens"] for item in paired_flags
            ),
            "same_postprocessed_string_rate": mean_bool(
                item["same_postprocessed_string"] for item in paired_flags
            ),
            "same_normalized_flag_rate": mean_bool(
                item["same_normalized_flag"] for item in paired_flags
            ),
        },
    }
    output_path = args.results_dir / "all_document_ceiling_validation.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def mean_bool(values: Any) -> float:
    materialized = [float(value) for value in values]
    return statistics.fmean(materialized) if materialized else 0.0


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
