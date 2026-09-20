#!/usr/bin/env python3
"""Compare a fresh GPU smoke run with the frozen July reference outputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


EXACT_FIELDS = (
    "category",
    "generated_answer",
    "full_prefill_answer",
    "normalized_generated_answer",
    "normalized_full_prefill_answer",
    "answer_equivalence_to_full_prefill",
    "top1_match",
    "patched_doc_count",
    "patched_token_count",
    "prompt_length",
    "query_length",
    "selected_doc_ids",
    "generated_token_ids",
    "full_prefill_token_ids",
)


def read_rows(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = (str(row["example_id"]), str(row["method"]))
            if key in indexed:
                raise ValueError(f"{path}:{line_number}: duplicate key {key}")
            indexed[key] = row
    return indexed


def compare(reference_path: Path, candidate_path: Path, kl_atol: float) -> dict[str, Any]:
    reference = read_rows(reference_path)
    candidate = read_rows(candidate_path)
    failures: list[dict[str, Any]] = []
    if reference.keys() != candidate.keys():
        failures.append(
            {
                "field": "row_keys",
                "missing": sorted(set(reference) - set(candidate)),
                "extra": sorted(set(candidate) - set(reference)),
            }
        )
    max_kl_delta = 0.0
    max_patch_ratio_delta = 0.0
    for key in sorted(reference.keys() & candidate.keys()):
        expected = reference[key]
        actual = candidate[key]
        for field in EXACT_FIELDS:
            if actual.get(field) != expected.get(field):
                failures.append(
                    {
                        "key": key,
                        "field": field,
                        "expected": expected.get(field),
                        "actual": actual.get(field),
                    }
                )
        patch_delta = abs(
            float(actual["patched_token_ratio"])
            - float(expected["patched_token_ratio"])
        )
        max_patch_ratio_delta = max(max_patch_ratio_delta, patch_delta)
        if patch_delta > 1e-12:
            failures.append(
                {
                    "key": key,
                    "field": "patched_token_ratio",
                    "expected": expected["patched_token_ratio"],
                    "actual": actual["patched_token_ratio"],
                }
            )
        expected_kl = float(expected["first_token_kl_full_to_method"])
        actual_kl = float(actual["first_token_kl_full_to_method"])
        kl_delta = abs(actual_kl - expected_kl)
        max_kl_delta = max(max_kl_delta, kl_delta)
        if not math.isfinite(actual_kl) or kl_delta > kl_atol:
            failures.append(
                {
                    "key": key,
                    "field": "first_token_kl_full_to_method",
                    "expected": expected_kl,
                    "actual": actual_kl,
                    "absolute_delta": kl_delta,
                    "atol": kl_atol,
                }
            )
    return {
        "schema_version": 1,
        "reference": str(reference_path.resolve()),
        "candidate": str(candidate_path.resolve()),
        "num_reference_rows": len(reference),
        "num_candidate_rows": len(candidate),
        "kl_absolute_tolerance": kl_atol,
        "max_kl_absolute_delta": max_kl_delta,
        "max_patch_ratio_absolute_delta": max_patch_ratio_delta,
        "num_failures": len(failures),
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kl-atol", type=float, default=5e-4)
    args = parser.parse_args()
    report = compare(args.reference, args.candidate, args.kl_atol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
