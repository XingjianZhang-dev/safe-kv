#!/usr/bin/env python
"""Create paired example-cluster bootstrap summaries for the ARR sweep."""

from __future__ import annotations

import argparse
import csv
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
    rows = read_jsonl(args.results_dir / "staleness_doccount_outputs.jsonl")
    example_ids = sorted({str(row["example_id"]) for row in rows})
    methods = sorted({str(row["method"]) for row in rows})
    cells = sorted(
        {
            (int(row["num_documents"]), float(row["stale_probability"]))
            for row in rows
        }
    )
    values: dict[tuple[str, int, float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        values[
            (
                str(row["example_id"]),
                int(row["num_documents"]),
                float(row["stale_probability"]),
                str(row["method"]),
            )
        ].append(row)

    expected_seeds = sorted({int(row["mask_seed"]) for row in rows})
    for key, items in values.items():
        observed = sorted(int(item["mask_seed"]) for item in items)
        if observed != expected_seeds:
            raise ValueError(f"seed coverage mismatch for {key}: {observed}")

    rng = np.random.default_rng(args.seed)
    bootstrap_indices = rng.integers(
        0,
        len(example_ids),
        size=(args.bootstrap_samples, len(example_ids)),
    )
    output: list[dict[str, Any]] = []
    for num_documents, probability in cells:
        base_token = metric_array(
            values,
            example_ids,
            num_documents,
            probability,
            "mixed_no_repair",
            "generated_token_sequence_equivalent_to_fresh_reference",
        )
        base_norm = metric_array(
            values,
            example_ids,
            num_documents,
            probability,
            "mixed_no_repair",
            "answer_equivalence_to_fresh_reference",
        )
        for method in methods:
            token = metric_array(
                values,
                example_ids,
                num_documents,
                probability,
                method,
                "generated_token_sequence_equivalent_to_fresh_reference",
            )
            norm = metric_array(
                values,
                example_ids,
                num_documents,
                probability,
                method,
                "answer_equivalence_to_fresh_reference",
            )
            raw = metric_array(
                values,
                example_ids,
                num_documents,
                probability,
                method,
                "raw_answer_exact_to_fresh_reference",
            )
            patch = metric_array(
                values,
                example_ids,
                num_documents,
                probability,
                method,
                "recomputed_token_ratio",
            )
            token_bootstrap = token[bootstrap_indices].mean(axis=1)
            norm_bootstrap = norm[bootstrap_indices].mean(axis=1)
            token_delta_bootstrap = (token - base_token)[bootstrap_indices].mean(axis=1)
            norm_delta_bootstrap = (norm - base_norm)[bootstrap_indices].mean(axis=1)
            output.append(
                {
                    "num_documents": num_documents,
                    "stale_probability": probability,
                    "method": method,
                    "num_example_clusters": len(example_ids),
                    "num_mask_seeds": len(expected_seeds),
                    "normalized_answer_exact": float(norm.mean()),
                    "normalized_answer_ci95_low": percentile(norm_bootstrap, 2.5),
                    "normalized_answer_ci95_high": percentile(norm_bootstrap, 97.5),
                    "postprocessed_string_exact": float(raw.mean()),
                    "generated_token_exact": float(token.mean()),
                    "generated_token_ci95_low": percentile(token_bootstrap, 2.5),
                    "generated_token_ci95_high": percentile(token_bootstrap, 97.5),
                    "generated_token_delta_vs_no_repair": float(
                        (token - base_token).mean()
                    ),
                    "generated_token_delta_ci95_low": percentile(
                        token_delta_bootstrap, 2.5
                    ),
                    "generated_token_delta_ci95_high": percentile(
                        token_delta_bootstrap, 97.5
                    ),
                    "normalized_answer_delta_vs_no_repair": float(
                        (norm - base_norm).mean()
                    ),
                    "normalized_answer_delta_ci95_low": percentile(
                        norm_delta_bootstrap, 2.5
                    ),
                    "normalized_answer_delta_ci95_high": percentile(
                        norm_delta_bootstrap, 97.5
                    ),
                    "mean_recomputed_context_token_ratio": float(patch.mean()),
                }
            )

    json_path = args.results_dir / "staleness_paired_bootstrap_summary.json"
    csv_path = args.results_dir / "staleness_paired_bootstrap_summary.csv"
    json_path.write_text(
        json.dumps(
            {
                "bootstrap_unit": "example ID; all three mask seeds remain within cluster",
                "bootstrap_samples": args.bootstrap_samples,
                "bootstrap_seed": args.seed,
                "interval": "percentile 95% cluster bootstrap",
                "num_example_clusters": len(example_ids),
                "num_mask_seeds": len(expected_seeds),
                "rows": output,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(json.dumps({"json": str(json_path), "csv": str(csv_path), "rows": len(output)}))


def metric_array(
    values: dict[tuple[str, int, float, str], list[dict[str, Any]]],
    example_ids: list[str],
    num_documents: int,
    probability: float,
    method: str,
    field: str,
) -> np.ndarray:
    return np.asarray(
        [
            np.mean(
                [
                    float(row[field])
                    for row in values[(example_id, num_documents, probability, method)]
                ]
            )
            for example_id in example_ids
        ],
        dtype=np.float64,
    )


def percentile(values: np.ndarray, quantile: float) -> float:
    return float(np.percentile(values, quantile))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
