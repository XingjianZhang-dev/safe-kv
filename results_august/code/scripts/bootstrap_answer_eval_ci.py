#!/usr/bin/env python
"""Bootstrap confidence intervals for answer-eval outputs.

The bootstrap samples example ids with replacement, preserving paired method
outputs for each sampled example. This makes method-level CIs and pairwise
delta CIs suitable for reviewer-facing robustness checks.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.paper_analysis import truthy  # noqa: E402


METRICS = [
    "answer_equivalence",
    "gold_em",
    "gold_f1",
    "changed_wrong_rate",
    "patch_ratio",
    "avg_kl",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--methods", type=str, default=None)
    parser.add_argument("--pairs", type=str, default=None)
    parser.add_argument("--num-bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--ci", type=float, default=0.95)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows_by_example = read_rows_by_example(args.outputs)
    requested_methods = parse_csv_arg(args.methods)
    methods = requested_methods or sorted(
        {method for method_rows in rows_by_example.values() for method in method_rows}
    )
    pairs = parse_pairs(args.pairs)
    complete_example_ids = [
        example_id
        for example_id, method_rows in sorted(rows_by_example.items())
        if all(method in method_rows for method in methods)
    ]
    if not complete_example_ids:
        raise SystemExit("No examples contain all requested methods.")

    rng = random.Random(args.seed)
    bootstrap_indices = [
        [rng.randrange(len(complete_example_ids)) for _ in complete_example_ids]
        for _ in range(args.num_bootstrap)
    ]

    method_rows = []
    for method in methods:
        point = summarize_method(rows_by_example, complete_example_ids, method)
        boot = [
            summarize_method(
                rows_by_example,
                [complete_example_ids[index] for index in sample],
                method,
            )
            for sample in bootstrap_indices
        ]
        method_rows.extend(
            {
                "method": method,
                "metric": metric,
                "point": point[metric],
                "ci_low": percentile([item[metric] for item in boot], (1 - args.ci) / 2),
                "ci_high": percentile([item[metric] for item in boot], 1 - (1 - args.ci) / 2),
                "n_examples": len(complete_example_ids),
            }
            for metric in METRICS
        )

    pair_rows = []
    for left, right in pairs:
        if left not in methods or right not in methods:
            continue
        point = summarize_pair_delta(rows_by_example, complete_example_ids, left, right)
        boot = [
            summarize_pair_delta(
                rows_by_example,
                [complete_example_ids[index] for index in sample],
                left,
                right,
            )
            for sample in bootstrap_indices
        ]
        for metric in METRICS:
            values = [item[metric] for item in boot]
            pair_rows.append(
                {
                    "left_method": left,
                    "right_method": right,
                    "metric": metric,
                    "delta_left_minus_right": point[metric],
                    "ci_low": percentile(values, (1 - args.ci) / 2),
                    "ci_high": percentile(values, 1 - (1 - args.ci) / 2),
                    "bootstrap_p_left_le_right": mean(1.0 if value <= 0 else 0.0 for value in values),
                    "n_examples": len(complete_example_ids),
                }
            )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "bootstrap_method_ci.csv", method_rows)
    write_csv(args.out_dir / "bootstrap_pairwise_delta_ci.csv", pair_rows)
    summary = {
        "source": str(args.outputs),
        "n_examples": len(complete_example_ids),
        "num_bootstrap": args.num_bootstrap,
        "seed": args.seed,
        "ci": args.ci,
        "methods": methods,
        "pairs": pairs,
        "method_ci": method_rows,
        "pairwise_delta_ci": pair_rows,
    }
    (args.out_dir / "bootstrap_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "bootstrap_report.md").write_text(
        markdown_report(method_rows, pair_rows),
        encoding="utf-8",
    )
    print(json.dumps({"n_examples": len(complete_example_ids), "methods": methods}, indent=2))


def read_rows_by_example(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    rows: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            rows[row["example_id"]][row["method"]] = row
    return rows


def parse_csv_arg(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_pairs(value: str | None) -> list[tuple[str, str]]:
    pairs = []
    for item in parse_csv_arg(value):
        if ":" not in item:
            raise ValueError(f"pair must be left:right, got {item!r}")
        left, right = item.split(":", 1)
        pairs.append((left, right))
    return pairs


def summarize_method(
    rows_by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    method: str,
) -> dict[str, float]:
    rows = [rows_by_example[example_id][method] for example_id in example_ids]
    return summarize_rows(rows)


def summarize_pair_delta(
    rows_by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    left: str,
    right: str,
) -> dict[str, float]:
    left_summary = summarize_method(rows_by_example, example_ids, left)
    right_summary = summarize_method(rows_by_example, example_ids, right)
    return {
        metric: left_summary[metric] - right_summary[metric]
        for metric in METRICS
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "answer_equivalence": mean(
            1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0
            for row in rows
        ),
        "gold_em": mean(1.0 if truthy(row["gold_exact_match"]) else 0.0 for row in rows),
        "gold_f1": mean(float(row.get("gold_token_f1") or 0.0) for row in rows),
        "changed_wrong_rate": mean(
            1.0 if truthy(row["answer_changed_and_gold_wrong"]) else 0.0
            for row in rows
        ),
        "patch_ratio": mean(float(row.get("patched_token_ratio") or 0.0) for row in rows),
        "avg_kl": mean(float(row.get("first_token_kl_full_to_method") or 0.0) for row in rows),
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def mean(values: Any) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def markdown_report(method_rows: list[dict[str, Any]], pair_rows: list[dict[str, Any]]) -> str:
    lines = ["# Bootstrap Answer-Eval Confidence Intervals", ""]
    lines.extend(
        [
            "## Method-Level 95% CIs",
            "",
            "| method | metric | point | ci low | ci high | n |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in method_rows:
        lines.append(
            "| {method} | {metric} | {point:.4f} | {low:.4f} | {high:.4f} | {n} |".format(
                method=row["method"],
                metric=row["metric"],
                point=float(row["point"]),
                low=float(row["ci_low"]),
                high=float(row["ci_high"]),
                n=row["n_examples"],
            )
        )
    lines.extend(
        [
            "",
            "## Pairwise Delta CIs",
            "",
            "| left - right | metric | delta | ci low | ci high | P(delta<=0) |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in pair_rows:
        lines.append(
            "| {left} - {right} | {metric} | {delta:.4f} | {low:.4f} | {high:.4f} | {p:.4f} |".format(
                left=row["left_method"],
                right=row["right_method"],
                metric=row["metric"],
                delta=float(row["delta_left_minus_right"]),
                low=float(row["ci_low"]),
                high=float(row["ci_high"]),
                p=float(row["bootstrap_p_left_le_right"]),
            )
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
