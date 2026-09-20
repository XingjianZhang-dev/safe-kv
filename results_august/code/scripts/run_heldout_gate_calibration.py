#!/usr/bin/env python
"""Run held-out budget-gate calibration from existing budget-gate outputs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.heldout_gate import (  # noqa: E402
    apply_risk_cutoff,
    calibrate_risk_cutoff,
    deterministic_split_ids,
    materialize_gate_rows,
    random_comparison,
    random_gate_rows,
    read_budget_gate_examples,
    summarize_rows,
)
from safekv.paper_analysis import mean, write_csv_rows  # noqa: E402


DEFAULT_RUNS = [
    ("qwen05", "diagnostic_100_noisy", "results_budget_gate/qwen05_noisy/budget_gate_outputs.jsonl"),
    ("qwen15", "diagnostic_100_noisy", "results_budget_gate/qwen15_noisy/budget_gate_outputs.jsonl"),
    ("qwen05", "external_multihop_100", "results_budget_gate/qwen05_external/budget_gate_outputs.jsonl"),
    ("qwen15", "external_multihop_100", "results_budget_gate/qwen15_external/budget_gate_outputs.jsonl"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("results_paper"))
    parser.add_argument("--target-budgets", default="0.10,0.25,0.40")
    parser.add_argument("--num-random-seeds", type=int, default=100)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--calibration-fraction", type=float, default=0.30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_budgets = [
        float(item.strip()) for item in args.target_budgets.split(",") if item.strip()
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    all_output_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "seed": args.seed,
        "calibration_fraction": args.calibration_fraction,
        "target_budgets": target_budgets,
        "runs": [],
    }

    for model, dataset, path_text in DEFAULT_RUNS:
        path = Path(path_text)
        if not path.exists():
            raise FileNotFoundError(
                f"Missing budget-gate outputs for {model}/{dataset}: {path}. "
                "Run scripts/run_budget_gate_eval.py first."
            )
        examples = read_budget_gate_examples(path)
        calibration_ids, test_ids = deterministic_split_ids(
            [example.example_id for example in examples],
            seed=args.seed,
            calibration_fraction=args.calibration_fraction,
        )
        calibration_examples = [
            example for example in examples if example.example_id in calibration_ids
        ]
        test_examples = [example for example in examples if example.example_id in test_ids]
        run_summary = {
            "model": model,
            "dataset": dataset,
            "source": str(path),
            "n_calibration": len(calibration_examples),
            "n_test": len(test_examples),
            "budgets": [],
        }

        for target in target_budgets:
            safe_method = f"heldout_budget_gate_{target:.2f}"
            risk_cutoff, calibration_budget, calibration_selected = calibrate_risk_cutoff(
                calibration_examples,
                target_budget=target,
            )
            safe_selected, safe_actual = apply_risk_cutoff(
                test_examples,
                risk_cutoff=risk_cutoff,
            )
            safe_rows = materialize_gate_rows(
                test_examples,
                method=safe_method,
                selected=safe_selected,
                target_budget=target,
                actual_test_budget=safe_actual,
            )
            for row in safe_rows:
                row["model"] = model
                row["dataset"] = dataset
                row["calibrated_risk_cutoff"] = risk_cutoff
                row["calibration_actual_budget"] = calibration_budget
            all_output_rows.extend(safe_rows)
            safe_summary = summarize_rows(safe_rows)

            random_summaries = []
            random_actual_budgets = []
            random_target = safe_actual
            random_prefix = f"heldout_random_gate_{target:.2f}"
            for seed in range(args.num_random_seeds):
                rows, actual, _selected = random_gate_rows(
                    test_examples,
                    target_budget=random_target,
                    method_prefix=random_prefix,
                    seed=seed,
                )
                for row in rows:
                    row["model"] = model
                    row["dataset"] = dataset
                    row["declared_target_budget"] = target
                    row["matched_safe_actual_budget"] = safe_actual
                all_output_rows.extend(rows)
                random_summaries.append(summarize_rows(rows))
                random_actual_budgets.append(actual)

            random_stats = random_comparison(
                safe_answer_equivalence=safe_summary["answer_equivalence_to_full_prefill"],
                random_summaries=random_summaries,
            )
            metric = {
                "model": model,
                "dataset": dataset,
                "target_budget": target,
                "calibration_actual_budget": calibration_budget,
                "test_actual_budget": safe_actual,
                "calibrated_risk_cutoff": risk_cutoff,
                "n_calibration": len(calibration_examples),
                "n_test": len(test_examples),
                "method": safe_method,
                **safe_summary,
                "random_gate_mean_actual_budget": mean(random_actual_budgets),
                **random_stats,
            }
            metric_rows.append(metric)
            run_summary["budgets"].append(metric)

        summary["runs"].append(run_summary)

    _write_jsonl(args.out_dir / "heldout_gate_calibration_outputs.jsonl", all_output_rows)
    _write_metrics(args.out_dir / "heldout_gate_calibration_metrics.csv", metric_rows)
    (args.out_dir / "heldout_gate_calibration_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "heldout_gate_calibration_report.md").write_text(
        _markdown_report(metric_rows),
        encoding="utf-8",
    )
    print(json.dumps({"num_metric_rows": len(metric_rows), "runs": summary["runs"]}, indent=2))


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_metrics(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "model",
        "dataset",
        "target_budget",
        "calibration_actual_budget",
        "test_actual_budget",
        "calibrated_risk_cutoff",
        "n_calibration",
        "n_test",
        "method",
        "answer_equivalence_to_full_prefill",
        "answer_changed_from_full_rate",
        "answer_changed_and_gold_wrong_rate",
        "answer_changed_and_gold_wrong_count",
        "patched_token_ratio",
        "patched_doc_count",
        "random_gate_mean_actual_budget",
        "random_gate_mean_answer_equivalence",
        "random_gate_95ci_low",
        "random_gate_95ci_high",
        "percentile_vs_random",
    ]
    write_csv_rows(path, rows, fields)


def _markdown_report(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Held-Out Gate Calibration",
        "",
        "| model | dataset | target | test budget | answer eq | random mean | percentile | changed+wrong |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {dataset} | {target:.2f} | {actual:.3f} | {ans:.3f} | {rand:.3f} | {pct:.3f} | {wrong:.3f} |".format(
                model=row["model"],
                dataset=row["dataset"],
                target=float(row["target_budget"]),
                actual=float(row["test_actual_budget"]),
                ans=float(row["answer_equivalence_to_full_prefill"]),
                rand=float(row["random_gate_mean_answer_equivalence"]),
                pct=float(row["percentile_vs_random"]),
                wrong=float(row["answer_changed_and_gold_wrong_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "Calibration uses 30% of example ids to derive a risk cutoff from the predeclared budget.",
            "Final quality metrics are computed only on the held-out 70% test examples.",
            "Matched random gates select on the same held-out examples to match the safe gate's actual test budget.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
