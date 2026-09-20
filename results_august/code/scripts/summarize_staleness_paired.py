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


PAIRWISE_METHODS = (
    (
        "query_suffix_vs_query_doc_only_k1",
        "query_actual_suffix_k1",
        "query_actual_doc_only_k1",
    ),
    (
        "query_suffix_vs_query_downstream_w4_k1",
        "query_actual_suffix_k1",
        "query_actual_downstream_w4_k1",
    ),
    (
        "risk_suffix_k2_vs_risk_suffix_k1",
        "risk_actual_suffix_k2",
        "risk_actual_suffix_k1",
    ),
    (
        "oracle_suffix_vs_no_repair",
        "earliest_stale_actual_suffix_oracle",
        "mixed_no_repair",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (defaults to --results-dir for backward compatibility).",
    )
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or args.results_dir
    out_dir.mkdir(parents=True, exist_ok=True)
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

    pairwise_output = pairwise_method_summaries(
        values=values,
        example_ids=example_ids,
        cells=cells,
        bootstrap_indices=bootstrap_indices,
    )
    interaction_output = endpoint_interaction_summaries(
        values=values,
        example_ids=example_ids,
        methods=methods,
        cells=cells,
        bootstrap_indices=bootstrap_indices,
    )

    json_path = out_dir / "staleness_paired_bootstrap_summary.json"
    csv_path = out_dir / "staleness_paired_bootstrap_summary.csv"
    pairwise_json_path = out_dir / "staleness_paired_method_differences.json"
    pairwise_csv_path = out_dir / "staleness_paired_method_differences.csv"
    interaction_json_path = out_dir / "staleness_endpoint_interactions.json"
    interaction_csv_path = out_dir / "staleness_endpoint_interactions.csv"
    json_path.write_text(
        json.dumps(
            {
                "bootstrap_unit": "example ID; all three mask seeds remain within cluster",
                "bootstrap_samples": args.bootstrap_samples,
                "bootstrap_seed": args.seed,
                "interval": "percentile 95% cluster bootstrap",
                "source_results_dir": str(args.results_dir.resolve()),
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
    write_summary_pair(
        json_path=pairwise_json_path,
        csv_path=pairwise_csv_path,
        rows=pairwise_output,
        metadata={
            "estimand": "paired left-minus-right method difference within cell",
            "bootstrap_unit": "example ID; all three mask seeds remain within cluster",
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.seed,
            "interval": "percentile 95% cluster bootstrap",
            "source_results_dir": str(args.results_dir.resolve()),
        },
    )
    write_summary_pair(
        json_path=interaction_json_path,
        csv_path=interaction_csv_path,
        rows=interaction_output,
        metadata={
            "estimand": (
                "[outcome(N_high,p=1)-outcome(N_high,p=0)] - "
                "[outcome(N_low,p=1)-outcome(N_low,p=0)]"
            ),
            "bootstrap_unit": "example ID; all three mask seeds remain within cluster",
            "bootstrap_samples": args.bootstrap_samples,
            "bootstrap_seed": args.seed,
            "interval": "percentile 95% cluster bootstrap",
            "source_results_dir": str(args.results_dir.resolve()),
        },
    )
    print(
        json.dumps(
            {
                "json": str(json_path),
                "csv": str(csv_path),
                "rows": len(output),
                "pairwise_json": str(pairwise_json_path),
                "pairwise_rows": len(pairwise_output),
                "interaction_json": str(interaction_json_path),
                "interaction_rows": len(interaction_output),
            }
        )
    )


def pairwise_method_summaries(
    *,
    values: dict[tuple[str, int, float, str], list[dict[str, Any]]],
    example_ids: list[str],
    cells: list[tuple[int, float]],
    bootstrap_indices: np.ndarray,
) -> list[dict[str, Any]]:
    rows = []
    fields = (
        "answer_equivalence_to_fresh_reference",
        "generated_token_sequence_equivalent_to_fresh_reference",
        "recomputed_token_ratio",
    )
    for num_documents, probability in cells:
        for label, left_method, right_method in PAIRWISE_METHODS:
            row: dict[str, Any] = {
                "comparison": label,
                "left_method": left_method,
                "right_method": right_method,
                "num_documents": num_documents,
                "stale_probability": probability,
                "num_example_clusters": len(example_ids),
            }
            for field in fields:
                left = metric_array(
                    values,
                    example_ids,
                    num_documents,
                    probability,
                    left_method,
                    field,
                )
                right = metric_array(
                    values,
                    example_ids,
                    num_documents,
                    probability,
                    right_method,
                    field,
                )
                difference = left - right
                bootstrap = difference[bootstrap_indices].mean(axis=1)
                prefix = {
                    "answer_equivalence_to_fresh_reference": "normalized_answer_delta",
                    "generated_token_sequence_equivalent_to_fresh_reference": (
                        "generated_token_exact_delta"
                    ),
                    "recomputed_token_ratio": "recomputed_context_ratio_delta",
                }[field]
                row[prefix] = float(difference.mean())
                row[f"{prefix}_ci95_low"] = percentile(bootstrap, 2.5)
                row[f"{prefix}_ci95_high"] = percentile(bootstrap, 97.5)
            rows.append(row)
    return rows


def endpoint_interaction_summaries(
    *,
    values: dict[tuple[str, int, float, str], list[dict[str, Any]]],
    example_ids: list[str],
    methods: list[str],
    cells: list[tuple[int, float]],
    bootstrap_indices: np.ndarray,
) -> list[dict[str, Any]]:
    document_counts = sorted({num_documents for num_documents, _probability in cells})
    probabilities = {probability for _num_documents, probability in cells}
    if not {0.0, 1.0}.issubset(probabilities):
        raise ValueError("endpoint interaction requires p=0 and p=1 cells")
    comparisons = list(zip(document_counts[:-1], document_counts[1:], strict=False))
    if len(document_counts) > 2:
        comparisons.append((document_counts[0], document_counts[-1]))
    rows = []
    fields = (
        "answer_equivalence_to_fresh_reference",
        "generated_token_sequence_equivalent_to_fresh_reference",
        "recomputed_token_ratio",
    )
    for method in methods:
        for low_n, high_n in comparisons:
            row: dict[str, Any] = {
                "method": method,
                "low_num_documents": low_n,
                "high_num_documents": high_n,
                "low_stale_probability": 0.0,
                "high_stale_probability": 1.0,
                "num_example_clusters": len(example_ids),
            }
            for field in fields:
                high_effect = metric_array(
                    values, example_ids, high_n, 1.0, method, field
                ) - metric_array(values, example_ids, high_n, 0.0, method, field)
                low_effect = metric_array(
                    values, example_ids, low_n, 1.0, method, field
                ) - metric_array(values, example_ids, low_n, 0.0, method, field)
                interaction = high_effect - low_effect
                bootstrap = interaction[bootstrap_indices].mean(axis=1)
                prefix = {
                    "answer_equivalence_to_fresh_reference": (
                        "normalized_answer_endpoint_interaction"
                    ),
                    "generated_token_sequence_equivalent_to_fresh_reference": (
                        "generated_token_exact_endpoint_interaction"
                    ),
                    "recomputed_token_ratio": "recomputed_ratio_endpoint_interaction",
                }[field]
                row[prefix] = float(interaction.mean())
                row[f"{prefix}_ci95_low"] = percentile(bootstrap, 2.5)
                row[f"{prefix}_ci95_high"] = percentile(bootstrap, 97.5)
            rows.append(row)
    return rows


def write_summary_pair(
    *,
    json_path: Path,
    csv_path: Path,
    rows: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> None:
    json_path.write_text(
        json.dumps({**metadata, "rows": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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
