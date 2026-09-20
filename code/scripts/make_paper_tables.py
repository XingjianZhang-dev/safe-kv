#!/usr/bin/env python
"""Build consolidated paper-facing SAFE-KV result tables."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.paper_analysis import (  # noqa: E402
    bootstrap_mean_ci,
    mean,
    read_csv_rows,
    truthy,
    write_claim_audit,
    write_csv_rows,
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("results_paper"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    _table_composition(args.out_dir / "table1_composition_ablation.csv")
    _table_repair(args.out_dir / "table2_repair_granularity.csv")
    _table_answer_synthetic(args.out_dir / "table3_answer_level_synthetic.csv")
    _table_answer_external(args.out_dir / "table4_answer_level_external.csv")
    _table_external_subset(args.out_dir / "table5_external_full_prefill_correct_subset.csv")
    _table_budget_gate(args.out_dir / "table6_budget_gate_pareto.csv")
    write_claim_audit(args.out_dir / "paper_claim_audit.md")
    (args.out_dir / "paper_result_summary.md").write_text(_result_summary(), encoding="utf-8")


def _aggregate_rows(rows, method_field="method"):
    groups = defaultdict(list)
    for row in rows:
        groups[row[method_field]].append(row)
    out = []
    for method, group in sorted(groups.items()):
        out.append(
            {
                "method": method,
                "n": len(group),
                "avg_kl": mean(float(row["first_token_kl_full_to_method"]) for row in group),
                "top1": mean(1.0 if truthy(row["top1_match"]) else 0.0 for row in group),
                "top10": mean(float(row.get("top10_overlap", 0.0)) for row in group),
                "patch_ratio": mean(float(row.get("patched_token_ratio", 0.0) or 0.0) for row in group),
            }
        )
    return out


def _table_composition(path):
    rows = _aggregate_rows(read_csv_rows("results_qwen05_100/composition_metrics.csv"))
    write_csv_rows(path, rows, ["method", "n", "avg_kl", "top1", "top10", "patch_ratio"])


def _table_repair(path):
    rows = _aggregate_rows(read_csv_rows("results_qwen05_100/patch_granularity_metrics.csv"))
    write_csv_rows(path, rows, ["method", "n", "avg_kl", "top1", "top10", "patch_ratio"])


def _table_answer_synthetic(path):
    runs = [
        ("qwen05", "clean", "results_qwen05_100_answer"),
        ("qwen05", "noisy", "results_qwen05_100_noisy_answer"),
        ("qwen15", "clean", "results_qwen15_100_answer"),
        ("qwen15", "noisy", "results_qwen15_100_noisy_answer"),
    ]
    rows = []
    for model, split, directory in runs:
        rows.extend(_answer_table_rows(model, split, Path(directory)))
    fields = [
        "model",
        "split",
        "method",
        "n",
        "answer_equivalence",
        "answer_equivalence_ci_low",
        "answer_equivalence_ci_high",
        "changed_wrong",
        "patch_ratio",
    ]
    write_csv_rows(path, rows, fields)


def _table_answer_external(path):
    runs = [
        ("qwen05", "external", "results_qwen05_external_answer"),
        ("qwen15", "external", "results_qwen15_external_answer"),
    ]
    rows = []
    for model, split, directory in runs:
        rows.extend(_answer_table_rows(model, split, Path(directory), include_gold=True))
    fields = [
        "model",
        "split",
        "method",
        "n",
        "answer_equivalence",
        "answer_equivalence_ci_low",
        "answer_equivalence_ci_high",
        "gold_em",
        "gold_f1",
        "changed_wrong",
        "patch_ratio",
    ]
    write_csv_rows(path, rows, fields)


def _answer_table_rows(model, split, directory: Path, include_gold=False):
    metrics_path = directory / "answer_eval_metrics.csv"
    if not metrics_path.exists():
        return []
    rows = read_csv_rows(metrics_path)
    groups = defaultdict(list)
    for row in rows:
        groups[row["method"]].append(row)
    out = []
    for method, group in sorted(groups.items()):
        values = [1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0 for row in group]
        low, high = bootstrap_mean_ci(values, iterations=500)
        item = {
            "model": model,
            "split": split,
            "method": method,
            "n": len(group),
            "answer_equivalence": mean(values),
            "answer_equivalence_ci_low": low,
            "answer_equivalence_ci_high": high,
            "changed_wrong": sum(1 for row in group if truthy(row["answer_changed_and_gold_wrong"])),
            "patch_ratio": mean(float(row["patched_token_ratio"]) for row in group),
        }
        if include_gold:
            item["gold_em"] = mean(1.0 if truthy(row["gold_exact_match"]) else 0.0 for row in group)
            item["gold_f1"] = mean(float(row["gold_token_f1"]) for row in group)
        out.append(item)
    return out


def _table_external_subset(path):
    source = Path("results_paper/external_subset_analysis.csv")
    rows = read_csv_rows(source) if source.exists() else []
    write_csv_rows(path, rows, list(rows[0]) if rows else ["missing"])


def _table_budget_gate(path):
    rows = []
    for pareto in Path("results_budget_gate").glob("*/budget_gate_pareto.csv"):
        if pareto.parent.name.endswith("_smoke"):
            continue
        for row in read_csv_rows(pareto):
            item = dict(row)
            item["run"] = pareto.parent.name
            rows.append(item)
    fields = [
        "run",
        "target_budget",
        "method",
        "actual_budget",
        "answer_equivalence",
        "changed_wrong",
        "avg_first_token_kl",
        "random_mean",
        "random_std",
        "random_95ci_low",
        "random_95ci_high",
        "percentile_vs_random",
    ]
    write_csv_rows(path, rows, fields)


def _result_summary() -> str:
    return """# Paper Result Summary

This directory consolidates SAFE-KV paper-facing tables from diagnostic, answer-level,
external, subset, and budget-gate analyses.

Use the claim audit as the boundary for ARR drafting: the strongest claims are semantic
safety analysis, structured answer drift, document-level repair, and calibrated
quality-budget trade-offs. External natural data should be framed as a sanity check.

## 7B Additions

- SmolLM2-1.7B cross-family sanity supports that answer drift and document repair are not Qwen-family-only.
- Held-out gate calibration shows moderate/high budget gates can help on controlled noisy diagnostic data, but external results remain mixed against matched random gates.
- Table 7 reports recomputation-budget proxies only: patched-token ratio, estimated recompute ratio, and estimated prefill-token saving. These are not production latency or throughput measurements.

## Drafting Boundary

The ARR paper should emphasize semantic safety analysis, prefix-conditioned composition,
document-level repair, and calibrated quality-budget trade-offs. It should avoid universal
selector/gate dominance claims and avoid system-level serving speedup claims.
"""


if __name__ == "__main__":
    main()
