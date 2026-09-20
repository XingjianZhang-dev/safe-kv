#!/usr/bin/env python
"""Cluster-bootstrap frozen frontier-selector test metrics by source question."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402


METRICS = (
    "answer_preservation",
    "no_repair_answer_preservation",
    "answer_preservation_delta_vs_no_repair",
    "full_prefill_fallback_rate",
    "mean_recomputed_context_ratio",
    "frontier_exact_accuracy",
    "frontier_within_one_conservative_accuracy",
    "mean_excess_recompute_vs_observed_min",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--evaluation-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260821)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def summarize(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    if not rows:
        raise ValueError("cannot summarize an empty bootstrap sample")
    preservation = np.asarray([row["answer_preserved"] for row in rows], dtype=float)
    naive = np.asarray([row["no_repair_answer_preserved"] for row in rows], dtype=float)
    excess = [
        float(row["excess_recompute_vs_observed_min"])
        for row in rows
        if row["excess_recompute_vs_observed_min"] is not None
    ]
    return {
        "answer_preservation": float(preservation.mean()),
        "no_repair_answer_preservation": float(naive.mean()),
        "answer_preservation_delta_vs_no_repair": float(
            (preservation - naive).mean()
        ),
        "full_prefill_fallback_rate": float(
            np.mean([row["full_prefill_fallback"] for row in rows])
        ),
        "mean_recomputed_context_ratio": float(
            np.mean([row["selected_recomputed_context_ratio"] for row in rows])
        ),
        "frontier_exact_accuracy": float(
            np.mean([row["frontier_exact"] for row in rows])
        ),
        "frontier_within_one_conservative_accuracy": float(
            np.mean([row["frontier_within_one_conservative"] for row in rows])
        ),
        "mean_excess_recompute_vs_observed_min": (
            float(np.mean(excess)) if excess else None
        ),
    }


def interval(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "bootstrap_mean": float(array.mean()),
        "ci95_low": float(np.quantile(array, 0.025)),
        "ci95_high": float(np.quantile(array, 0.975)),
    }


def main() -> None:
    args = parse_args()
    if args.iterations <= 0:
        raise ValueError("bootstrap iterations must be positive")
    outputs_path = args.outputs.resolve()
    evaluation_path = args.evaluation_report.resolve()
    rows = read_jsonl(outputs_path)
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("threshold_reoptimized_on_test") is not False:
        raise ValueError("evaluation report does not certify frozen test threshold")
    if len(rows) != int(evaluation["n_test_condition_examples"]):
        raise ValueError("output row count differs from evaluation report")

    groups_by_dataset: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    conditions = set()
    for row in rows:
        groups_by_dataset[str(row["dataset"])][str(row["group_id"])].append(row)
        conditions.add(str(row["condition"]))
    for dataset, groups in groups_by_dataset.items():
        expected = len(conditions)
        if any(len(group_rows) != expected for group_rows in groups.values()):
            raise ValueError(
                f"source-question group in {dataset} does not contain every condition"
            )

    scopes: dict[str, list[dict[str, Any]]] = {"overall": rows}
    for dataset in sorted(groups_by_dataset):
        scopes[f"dataset:{dataset}"] = [
            row
            for group_rows in groups_by_dataset[dataset].values()
            for row in group_rows
        ]
        for condition in sorted(conditions):
            scopes[f"cell:{dataset}/{condition}"] = [
                row
                for group_rows in groups_by_dataset[dataset].values()
                for row in group_rows
                if row["condition"] == condition
            ]

    rng = np.random.default_rng(args.seed)
    draws: dict[str, dict[str, list[float]]] = {
        scope: {metric: [] for metric in METRICS} for scope in scopes
    }
    group_ids_by_dataset = {
        dataset: sorted(groups) for dataset, groups in groups_by_dataset.items()
    }
    for _ in range(args.iterations):
        sampled_by_dataset = {}
        for dataset, group_ids in group_ids_by_dataset.items():
            sampled_ids = rng.choice(group_ids, size=len(group_ids), replace=True)
            sampled_by_dataset[dataset] = [
                row
                for group_id in sampled_ids
                for row in groups_by_dataset[dataset][str(group_id)]
            ]
        bootstrap_scopes = {
            "overall": [
                row
                for dataset in sorted(sampled_by_dataset)
                for row in sampled_by_dataset[dataset]
            ]
        }
        for dataset, sampled_rows in sampled_by_dataset.items():
            bootstrap_scopes[f"dataset:{dataset}"] = sampled_rows
            for condition in conditions:
                bootstrap_scopes[f"cell:{dataset}/{condition}"] = [
                    row for row in sampled_rows if row["condition"] == condition
                ]
        for scope, sampled_rows in bootstrap_scopes.items():
            values = summarize(sampled_rows)
            for metric, value in values.items():
                if value is not None:
                    draws[scope][metric].append(float(value))

    report_scopes = {}
    for scope, point_rows in scopes.items():
        points = summarize(point_rows)
        report_scopes[scope] = {
            "n_condition_rows": len(point_rows),
            "n_source_groups": len({row["group_id"] for row in point_rows}),
            "metrics": {
                metric: {
                    "estimate": points[metric],
                    **(interval(draws[scope][metric]) if draws[scope][metric] else {}),
                }
                for metric in METRICS
            },
        }
    report = {
        "schema_version": 1,
        "method": (
            "dataset-stratified nonparametric bootstrap over source-question groups; "
            "all retrieval conditions for a source question are resampled together"
        ),
        "iterations": args.iterations,
        "seed": args.seed,
        "outputs": {"path": str(outputs_path), "sha256": sha256_file(outputs_path)},
        "evaluation_report": {
            "path": str(evaluation_path),
            "sha256": sha256_file(evaluation_path),
        },
        "scopes": report_scopes,
        "integrity": {
            "threshold_reoptimized_on_test": False,
            "retrieval_conditions_clustered_by_source_question": True,
        },
    }
    args.out = args.out.resolve()
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite bootstrap report: {args.out}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"out": str(args.out), "scopes": len(report_scopes)}, indent=2))


if __name__ == "__main__":
    main()
