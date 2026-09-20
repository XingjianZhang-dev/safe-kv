#!/usr/bin/env python
"""Paired example bootstrap for the oracle token-local diagnostic."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.results_dir / "oracle_kv_drift_outputs.jsonl")
    by_example: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_example[str(row["example_id"])][str(row["method"])] = row
    example_ids = sorted(by_example)
    methods = set(next(iter(by_example.values())))
    if any(set(items) != methods for items in by_example.values()):
        raise ValueError("method coverage differs across examples")

    contrasts = [
        (
            "oracle_local_same_budget_minus_actual_risk_suffix_k1",
            "oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1",
            "risk_suffix_k1_actual_recompute",
        ),
        (
            "donor_risk_suffix_k1_minus_actual_risk_suffix_k1",
            "risk_suffix_k1_oracle_donor_copy",
            "risk_suffix_k1_actual_recompute",
        ),
        (
            "oracle_local_same_budget_minus_donor_risk_suffix_k1",
            "oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1",
            "risk_suffix_k1_oracle_donor_copy",
        ),
    ]
    for method in sorted(methods):
        if not method.startswith("oracle_kv_drift_token_local_p"):
            continue
        label = method.removeprefix("oracle_kv_drift_token_local_p")
        random_method = f"random_positions_oracle_full_kv_donor_p{label}"
        if random_method in methods:
            contrasts.append(
                (f"oracle_drift_minus_random_positions_p{label}", method, random_method)
            )

    rng = np.random.default_rng(args.seed)
    indices = rng.integers(
        0,
        len(example_ids),
        size=(args.bootstrap_samples, len(example_ids)),
    )
    fields = {
        "normalized_answer_exact": "qa_answer_equivalence_to_fresh_reference",
        "postprocessed_string_exact": "raw_answer_exact_to_fresh_reference",
        "generated_token_exact": (
            "generated_token_sequence_equivalent_to_fresh_reference"
        ),
    }
    results: list[dict[str, Any]] = []
    for name, method_a, method_b in contrasts:
        item: dict[str, Any] = {
            "contrast": name,
            "method_a": method_a,
            "method_b": method_b,
            "num_paired_examples": len(example_ids),
            "method_a_mean_patched_context_ratio": mean_field(
                by_example, example_ids, method_a, "patched_context_ratio"
            ),
            "method_b_mean_patched_context_ratio": mean_field(
                by_example, example_ids, method_b, "patched_context_ratio"
            ),
        }
        for label, field in fields.items():
            left = metric_array(by_example, example_ids, method_a, field)
            right = metric_array(by_example, example_ids, method_b, field)
            delta = left - right
            boot = delta[indices].mean(axis=1)
            item[f"{label}_delta"] = float(delta.mean())
            item[f"{label}_delta_ci95_low"] = float(np.percentile(boot, 2.5))
            item[f"{label}_delta_ci95_high"] = float(np.percentile(boot, 97.5))
        results.append(item)

    output = {
        "bootstrap_unit": "example ID",
        "bootstrap_samples": args.bootstrap_samples,
        "bootstrap_seed": args.seed,
        "interval": "percentile 95% paired bootstrap",
        "contrasts": results,
    }
    output_path = args.results_dir / "oracle_paired_bootstrap_summary.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


def metric_array(
    by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    method: str,
    field: str,
) -> np.ndarray:
    return np.asarray(
        [float(by_example[example_id][method][field]) for example_id in example_ids],
        dtype=np.float64,
    )


def mean_field(
    by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    method: str,
    field: str,
) -> float:
    return float(metric_array(by_example, example_ids, method, field).mean())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
