#!/usr/bin/env python
"""Validate same-run donor-copy versus actual-suffix recomputation pairs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


ACTUAL_PREFIX = "actual_recompute::"
REFERENCE_METHODS = {"full_prefill"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.results_dir / "answer_eval_outputs.jsonl")
    manifest = json.loads(
        (args.results_dir / "answer_eval_manifest.json").read_text(encoding="utf-8")
    )
    summary = json.loads(
        (args.results_dir / "answer_eval_summary.json").read_text(encoding="utf-8")
    )
    failures: list[str] = []
    data_path = Path(manifest["data_path"])
    examples = read_jsonl(data_path)[: args.expected_examples]
    examples_by_id = {str(example["id"]): example for example in examples}
    if len(examples) != args.expected_examples or len(examples_by_id) != len(examples):
        failures.append("input data prefix does not contain the expected unique examples")
    if file_sha256(data_path) != manifest.get("data_sha256"):
        failures.append("data hash does not match manifest")
    config_path = Path(manifest["config_path"])
    if file_sha256(config_path) != manifest.get("config_sha256"):
        failures.append("config hash does not match manifest")
    if int(manifest.get("max_examples", -1)) != args.expected_examples:
        failures.append("manifest max_examples mismatch")
    manifest_methods = [str(method) for method in manifest.get("methods", [])]
    manifest_method_set = set(manifest_methods)
    reference_manifest_methods = manifest_method_set & REFERENCE_METHODS
    paired_manifest_methods = manifest_method_set - reference_manifest_methods
    plain_manifest_methods = {
        method.removeprefix(ACTUAL_PREFIX) for method in paired_manifest_methods
    }
    expected_manifest_methods = reference_manifest_methods | plain_manifest_methods | {
        f"{ACTUAL_PREFIX}{method}" for method in plain_manifest_methods
    }
    if not plain_manifest_methods or manifest_method_set != expected_manifest_methods:
        failures.append("manifest does not contain exact donor/actual method pairs")
    if int(manifest.get("schema_version", 0)) >= 2:
        if not manifest.get("implementation_sha256") or not manifest.get(
            "model_commit_hash"
        ):
            failures.append("schema-v2 manifest lacks implementation/model provenance")
    else:
        provenance_path = args.results_dir / "execution_provenance.json"
        if not provenance_path.exists():
            failures.append("legacy manifest lacks supplemental execution provenance")
        else:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            if provenance.get("resume_used") is not False or not provenance.get(
                "implementation_sha256"
            ):
                failures.append("supplemental execution provenance is incomplete")
    keys = [(str(row["example_id"]), str(row["method"])) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append("duplicate example/method keys")
    if int(summary.get("num_failed_rows", -1)) != 0 or summary.get("failed_rows"):
        failures.append("answer runner reported failures")
    if int(summary.get("num_rows", -1)) != len(rows):
        failures.append("runner summary row count mismatch")
    if {str(row["method"]) for row in rows} != manifest_method_set:
        failures.append("output method set does not match manifest")
    if {str(row["example_id"]) for row in rows} != set(examples_by_id):
        failures.append("output example ids do not match input data prefix")

    for row in rows:
        example_id = str(row["example_id"])
        method = str(row["method"])
        example = examples_by_id.get(example_id)
        if example is None:
            continue
        document_ids = [int(doc["doc_id"]) for doc in example["documents"]]
        selected_ids = [int(doc_id) for doc_id in row["selected_doc_ids"]]
        if len(selected_ids) != len(set(selected_ids)) or not set(selected_ids).issubset(
            document_ids
        ):
            failures.append(f"invalid selected document ids for {example_id}/{method}")
        if "suffix_closure" in method and selected_ids:
            earliest = min(document_ids.index(doc_id) for doc_id in selected_ids)
            if selected_ids != document_ids[earliest:]:
                failures.append(f"selected ids are not an ordered suffix for {example_id}/{method}")
        if int(row["patched_doc_count"]) != len(selected_ids):
            failures.append(f"patched document count mismatch for {example_id}/{method}")
        context_length = int(row["prompt_length"]) - int(row["query_length"])
        patched_count = int(row["patched_token_count"])
        ratio = float(row["patched_token_ratio"])
        if context_length <= 0 or patched_count < 0 or patched_count > context_length:
            failures.append(f"invalid context/patch count for {example_id}/{method}")
        elif not math.isclose(
            ratio, patched_count / context_length, rel_tol=0.0, abs_tol=1e-12
        ):
            failures.append(f"patch ratio/count mismatch for {example_id}/{method}")
        normalized_exact = (
            row["normalized_generated_answer"]
            == row["normalized_full_prefill_answer"]
        )
        if bool(row["answer_equivalence_to_full_prefill"]) != normalized_exact:
            failures.append(f"normalized exact flag mismatch for {example_id}/{method}")
        kl = float(row["first_token_kl_full_to_method"])
        if not math.isfinite(kl) or kl < -1e-12:
            failures.append(f"invalid first-token KL for {example_id}/{method}")

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        method = str(row["method"])
        if method in REFERENCE_METHODS:
            continue
        plain_method = method.removeprefix(ACTUAL_PREFIX)
        groups[(str(row["example_id"]), plain_method)].append(row)
    plain_methods = sorted(plain_manifest_methods)
    expected_rows = args.expected_examples * (
        len(reference_manifest_methods) + len(plain_methods) * 2
    )
    if len(rows) != expected_rows:
        failures.append(f"row count {len(rows)} != expected {expected_rows}")

    pairs_by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    full_reference_by_example: dict[str, tuple[Any, Any, Any]] = {}
    if "full_prefill" in reference_manifest_methods:
        full_rows = [row for row in rows if str(row["method"]) == "full_prefill"]
        if len(full_rows) != args.expected_examples:
            failures.append("full-prefill reference row count mismatch")
        for row in full_rows:
            example_id = str(row["example_id"])
            reference = (
                row["full_prefill_answer"],
                row["normalized_full_prefill_answer"],
                row["full_prefill_token_ids"],
            )
            if reference != (
                row["generated_answer"],
                row["normalized_generated_answer"],
                row["generated_token_ids"],
            ):
                failures.append(f"full-prefill row is not self-identical for {example_id}")
            if example_id in full_reference_by_example:
                failures.append(f"duplicate full-prefill reference for {example_id}")
            full_reference_by_example[example_id] = reference
    for (example_id, plain_method), items in groups.items():
        donor = [item for item in items if not str(item["method"]).startswith(ACTUAL_PREFIX)]
        actual = [item for item in items if str(item["method"]).startswith(ACTUAL_PREFIX)]
        if len(donor) != 1 or len(actual) != 1:
            failures.append(f"pair coverage mismatch for {example_id}/{plain_method}")
            continue
        donor_row, actual_row = donor[0], actual[0]
        reference = (
            donor_row["full_prefill_answer"],
            donor_row["normalized_full_prefill_answer"],
            donor_row["full_prefill_token_ids"],
        )
        if reference != (
            actual_row["full_prefill_answer"],
            actual_row["normalized_full_prefill_answer"],
            actual_row["full_prefill_token_ids"],
        ):
            failures.append(f"within-pair full reference mismatch for {example_id}/{plain_method}")
        prior = full_reference_by_example.setdefault(example_id, reference)
        if prior != reference:
            failures.append(f"full reference changed across methods for {example_id}")
        pairs_by_method[plain_method].append(
            {
                "same_generated_answer": donor_row["generated_answer"]
                == actual_row["generated_answer"],
                "same_generated_tokens": donor_row["generated_token_ids"]
                == actual_row["generated_token_ids"],
                "same_normalized_preservation_flag": donor_row[
                    "answer_equivalence_to_full_prefill"
                ]
                == actual_row["answer_equivalence_to_full_prefill"],
                "same_patch_ratio": donor_row["patched_token_ratio"]
                == actual_row["patched_token_ratio"],
                "same_patch_count": donor_row["patched_token_count"]
                == actual_row["patched_token_count"],
                "same_selected_docs": donor_row["selected_doc_ids"]
                == actual_row["selected_doc_ids"],
                "donor_normalized_exact": donor_row[
                    "answer_equivalence_to_full_prefill"
                ],
                "actual_normalized_exact": actual_row[
                    "answer_equivalence_to_full_prefill"
                ],
                "donor_postprocessed_string_exact": str(
                    donor_row["generated_answer"]
                ).strip()
                == str(donor_row["full_prefill_answer"]).strip(),
                "actual_postprocessed_string_exact": str(
                    actual_row["generated_answer"]
                ).strip()
                == str(actual_row["full_prefill_answer"]).strip(),
                "donor_generated_token_exact": donor_row["generated_token_ids"]
                == donor_row["full_prefill_token_ids"],
                "actual_generated_token_exact": actual_row["generated_token_ids"]
                == actual_row["full_prefill_token_ids"],
            }
        )

    method_summaries = []
    fields = [
        "same_generated_answer",
        "same_generated_tokens",
        "same_normalized_preservation_flag",
        "same_patch_ratio",
        "same_patch_count",
        "same_selected_docs",
        "donor_normalized_exact",
        "actual_normalized_exact",
        "donor_postprocessed_string_exact",
        "actual_postprocessed_string_exact",
        "donor_generated_token_exact",
        "actual_generated_token_exact",
    ]
    for method, items in sorted(pairs_by_method.items()):
        if len(items) != args.expected_examples:
            failures.append(f"pair count mismatch for {method}: {len(items)}")
        method_summaries.append(
            {
                "method": method,
                "num_examples": len(items),
                **{
                    f"{field}_rate": statistics.fmean(float(item[field]) for item in items)
                    for field in fields
                },
            }
        )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "num_rows": len(rows),
        "expected_rows": expected_rows,
        "num_examples": len(full_reference_by_example),
        "reference_methods": sorted(reference_manifest_methods),
        "num_failures": len(failures),
        "failures": failures,
        "method_summaries": method_summaries,
    }
    output_path = args.results_dir / "donor_actual_reconciliation.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
