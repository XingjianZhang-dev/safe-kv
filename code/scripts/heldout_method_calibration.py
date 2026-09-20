#!/usr/bin/env python
"""Held-out calibration for choosing a repair method under patch budgets.

For each random split, the script chooses the highest-answer-equivalence method
whose calibration patch ratio is within a target budget, breaking ties by lower
patch ratio and lower changed-wrong rate. It then evaluates that preselected
method on held-out examples.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.paper_analysis import truthy  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--candidate-methods", type=str, required=True)
    parser.add_argument("--target-budgets", type=str, default="0.82,0.85,0.90,0.94")
    parser.add_argument("--num-splits", type=int, default=100)
    parser.add_argument("--calibration-fraction", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=13)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = parse_csv(args.candidate_methods)
    target_budgets = [float(item) for item in parse_csv(args.target_budgets)]
    rows_by_example = read_rows_by_example(args.outputs)
    example_ids = [
        example_id
        for example_id, method_rows in sorted(rows_by_example.items())
        if all(method in method_rows for method in candidates)
    ]
    if len(example_ids) < 2:
        raise SystemExit("Need at least two complete examples for calibration/test split.")

    split_rows: list[dict[str, Any]] = []
    for split_index in range(args.num_splits):
        calibration_ids, test_ids = split_ids(
            example_ids,
            seed=args.seed + split_index,
            calibration_fraction=args.calibration_fraction,
        )
        for target_budget in target_budgets:
            selected_method, calibration_summary = choose_method(
                rows_by_example,
                sorted(calibration_ids),
                candidates,
                target_budget=target_budget,
            )
            test_summary = summarize_method(rows_by_example, sorted(test_ids), selected_method)
            split_rows.append(
                {
                    "split_index": split_index,
                    "target_budget": target_budget,
                    "selected_method": selected_method,
                    "n_calibration": len(calibration_ids),
                    "n_test": len(test_ids),
                    "calibration_answer_equivalence": calibration_summary["answer_equivalence"],
                    "calibration_changed_wrong_rate": calibration_summary["changed_wrong_rate"],
                    "calibration_patch_ratio": calibration_summary["patch_ratio"],
                    "test_answer_equivalence": test_summary["answer_equivalence"],
                    "test_changed_wrong_rate": test_summary["changed_wrong_rate"],
                    "test_patch_ratio": test_summary["patch_ratio"],
                    "test_avg_kl": test_summary["avg_kl"],
                }
            )

    aggregate_rows = aggregate(split_rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "heldout_method_calibration_splits.csv", split_rows)
    write_csv(args.out_dir / "heldout_method_calibration_summary.csv", aggregate_rows)
    summary = {
        "source": str(args.outputs),
        "candidate_methods": candidates,
        "target_budgets": target_budgets,
        "num_splits": args.num_splits,
        "calibration_fraction": args.calibration_fraction,
        "seed": args.seed,
        "aggregate": aggregate_rows,
    }
    (args.out_dir / "heldout_method_calibration_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "heldout_method_calibration_report.md").write_text(
        markdown_report(aggregate_rows),
        encoding="utf-8",
    )
    print(json.dumps({"n_examples": len(example_ids), "num_splits": args.num_splits}, indent=2))


def read_rows_by_example(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    rows: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[row["example_id"]][row["method"]] = row
    return rows


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def split_ids(
    example_ids: list[str],
    *,
    seed: int,
    calibration_fraction: float,
) -> tuple[set[str], set[str]]:
    ids = list(example_ids)
    rng = random.Random(seed)
    rng.shuffle(ids)
    n_calibration = max(1, min(len(ids) - 1, round(len(ids) * calibration_fraction)))
    return set(ids[:n_calibration]), set(ids[n_calibration:])


def choose_method(
    rows_by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    candidates: list[str],
    *,
    target_budget: float,
) -> tuple[str, dict[str, float]]:
    summaries = {
        method: summarize_method(rows_by_example, example_ids, method)
        for method in candidates
    }
    feasible = [
        (method, summary)
        for method, summary in summaries.items()
        if summary["patch_ratio"] <= target_budget
    ]
    if not feasible:
        feasible = list(summaries.items())
    selected_method, selected_summary = max(
        feasible,
        key=lambda item: (
            item[1]["answer_equivalence"],
            -item[1]["changed_wrong_rate"],
            -item[1]["patch_ratio"],
            item[0],
        ),
    )
    return selected_method, selected_summary


def summarize_method(
    rows_by_example: dict[str, dict[str, dict[str, Any]]],
    example_ids: list[str],
    method: str,
) -> dict[str, float]:
    rows = [rows_by_example[example_id][method] for example_id in example_ids]
    return {
        "answer_equivalence": mean(
            1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0
            for row in rows
        ),
        "changed_wrong_rate": mean(
            1.0 if truthy(row["answer_changed_and_gold_wrong"]) else 0.0
            for row in rows
        ),
        "patch_ratio": mean(float(row.get("patched_token_ratio") or 0.0) for row in rows),
        "avg_kl": mean(float(row.get("first_token_kl_full_to_method") or 0.0) for row in rows),
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[float(row["target_budget"])].append(row)
    out = []
    for target, items in sorted(grouped.items()):
        counts = Counter(str(item["selected_method"]) for item in items)
        out.append(
            {
                "target_budget": target,
                "num_splits": len(items),
                "selection_counts": json.dumps(dict(sorted(counts.items())), sort_keys=True),
                "mean_test_answer_equivalence": mean(
                    float(item["test_answer_equivalence"]) for item in items
                ),
                "ci_low_test_answer_equivalence": percentile(
                    [float(item["test_answer_equivalence"]) for item in items],
                    0.025,
                ),
                "ci_high_test_answer_equivalence": percentile(
                    [float(item["test_answer_equivalence"]) for item in items],
                    0.975,
                ),
                "mean_test_changed_wrong_rate": mean(
                    float(item["test_changed_wrong_rate"]) for item in items
                ),
                "mean_test_patch_ratio": mean(float(item["test_patch_ratio"]) for item in items),
                "mean_test_avg_kl": mean(float(item["test_avg_kl"]) for item in items),
            }
        )
    return out


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
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


def markdown_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Held-Out Method Calibration",
        "",
        "| target budget | selection counts | test answer eq | 95% split interval | changed+wrong | patch ratio | KL |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {budget:.2f} | `{counts}` | {ans:.4f} | [{low:.4f}, {high:.4f}] | {wrong:.4f} | {patch:.4f} | {kl:.4f} |".format(
                budget=float(row["target_budget"]),
                counts=row["selection_counts"],
                ans=float(row["mean_test_answer_equivalence"]),
                low=float(row["ci_low_test_answer_equivalence"]),
                high=float(row["ci_high_test_answer_equivalence"]),
                wrong=float(row["mean_test_changed_wrong_rate"]),
                patch=float(row["mean_test_patch_ratio"]),
                kl=float(row["mean_test_avg_kl"]),
            )
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
