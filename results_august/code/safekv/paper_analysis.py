"""Paper-facing analysis helpers for SAFE-KV reviewer-risk checks."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ANSWER_METRICS = [
    "answer_equivalence_to_full_prefill",
    "gold_exact_match",
    "gold_token_f1",
    "answer_contains_gold",
    "answer_changed_from_full",
    "answer_changed_and_gold_wrong",
    "patched_token_ratio",
    "first_token_kl_full_to_method",
    "top1_match",
]


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"missing CSV: {csv_path}")
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def float_or_zero(value: Any) -> float:
    try:
        if value in ("", None):
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def stddev(values: Iterable[float]) -> float:
    vals = list(values)
    if len(vals) < 2:
        return 0.0
    mu = mean(vals)
    return math.sqrt(sum((value - mu) ** 2 for value in vals) / (len(vals) - 1))


def percentile_rank(value: float, samples: list[float]) -> float:
    if not samples:
        return 0.0
    return sum(1 for sample in samples if sample <= value) / len(samples)


def bootstrap_mean_ci(
    values: list[float],
    *,
    seed: int = 13,
    iterations: int = 1000,
    alpha: float = 0.05,
) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in values]
        estimates.append(mean(sample))
    estimates.sort()
    low_index = max(0, int((alpha / 2) * len(estimates)))
    high_index = min(len(estimates) - 1, int((1 - alpha / 2) * len(estimates)))
    return estimates[low_index], estimates[high_index]


def summarize_metric_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n_examples": len({row["example_id"] for row in rows}),
        "answer_equivalence_to_full_prefill": mean(
            1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0 for row in rows
        ),
        "gold_exact_match": mean(1.0 if truthy(row["gold_exact_match"]) else 0.0 for row in rows),
        "gold_token_f1": mean(float_or_zero(row["gold_token_f1"]) for row in rows),
        "answer_contains_gold": mean(
            1.0 if truthy(row["answer_contains_gold"]) else 0.0 for row in rows
        ),
        "answer_changed_from_full": mean(
            1.0 if truthy(row["answer_changed_from_full"]) else 0.0 for row in rows
        ),
        "answer_changed_and_gold_wrong": sum(
            1 for row in rows if truthy(row["answer_changed_and_gold_wrong"])
        ),
        "patched_token_ratio": mean(float_or_zero(row["patched_token_ratio"]) for row in rows),
        "first_token_kl_full_to_method": mean(
            float_or_zero(row["first_token_kl_full_to_method"]) for row in rows
        ),
        "top1_match": mean(1.0 if truthy(row["top1_match"]) else 0.0 for row in rows),
    }


def external_subset_rows(
    *,
    model_label: str,
    metrics_rows: list[dict[str, str]],
    small_n_threshold: int = 10,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_example: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in metrics_rows:
        by_example[row["example_id"]][row["method"]] = row

    dataset_splits = ["all_external"] + sorted(
        {methods["full_prefill"]["category"] for methods in by_example.values()}
    )
    quality_filters = [
        ("all_external", lambda full: True),
        ("full_prefill_gold_exact_match", lambda full: truthy(full["gold_exact_match"])),
        ("full_prefill_answer_contains_gold", lambda full: truthy(full["answer_contains_gold"])),
        ("full_prefill_gold_f1_ge_0.5", lambda full: float_or_zero(full["gold_token_f1"]) >= 0.5),
        ("full_prefill_gold_f1_ge_0.8", lambda full: float_or_zero(full["gold_token_f1"]) >= 0.8),
    ]
    methods = sorted({row["method"] for row in metrics_rows})

    out_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {"model": model_label, "subsets": []}
    for dataset_split in dataset_splits:
        split_examples = [
            example_id
            for example_id, example_methods in by_example.items()
            if dataset_split == "all_external"
            or example_methods["full_prefill"]["category"] == dataset_split
        ]
        for subset_name, predicate in quality_filters:
            subset_examples = [
                example_id
                for example_id in split_examples
                if predicate(by_example[example_id]["full_prefill"])
            ]
            base_changed = [
                example_id
                for example_id in subset_examples
                if truthy(
                    by_example[example_id]["prefix_conditioned_naive_global"][
                        "answer_changed_from_full"
                    ]
                )
            ]
            small_n_warning = len(subset_examples) < small_n_threshold
            summary["subsets"].append(
                {
                    "dataset_split": dataset_split,
                    "quality_subset": subset_name,
                    "n_examples": len(subset_examples),
                    "base_changed_count": len(base_changed),
                    "small_n_warning": small_n_warning,
                }
            )
            for method in methods:
                rows = [
                    by_example[example_id][method]
                    for example_id in subset_examples
                    if method in by_example[example_id]
                ]
                metric_summary = summarize_metric_rows(rows)
                repaired = [
                    example_id
                    for example_id in base_changed
                    if method in by_example[example_id]
                    and truthy(
                        by_example[example_id][method][
                            "answer_equivalence_to_full_prefill"
                        ]
                    )
                ]
                repair_rate = len(repaired) / len(base_changed) if base_changed else 0.0
                out_rows.append(
                    {
                        "model": model_label,
                        "dataset_split": dataset_split,
                        "quality_subset": subset_name,
                        "method": method,
                        **metric_summary,
                        "base_changed_count": len(base_changed),
                        "repaired_base_changes_by_method": len(repaired),
                        "repair_rate_among_base_changes": repair_rate,
                        "small_n_warning": small_n_warning,
                    }
                )
    return out_rows, summary


def markdown_table(rows: list[dict[str, Any]], headers: list[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(headers) - 1)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def write_claim_audit(path: str | Path) -> None:
    text = """# SAFE-KV Claim Audit

## Strongly Supported

- Non-prefix KV composition can cause answer-level drift.
- Prefix-conditioned composition is much stronger than doc-only composition.
- Residual drift is structured and harder under conflict/multi-hop/noisy retrieval.
- Span-level patching is unreliable.
- Document-level repair is a more coherent repair unit.
- First-token KL is correlated with answer-level mismatch.
- Cross-family SmolLM2 sanity shows answer drift is not Qwen-family-only.
- External HotpotQA/2Wiki sanity confirms answer drift is not synthetic-only.

## Supported With Caveat

- Semantic document selectors help under controlled noisy diagnostic.
- External natural data shows drift and partial repair, but selectors do not consistently beat random.
- Safe gating gives quality-budget trade-offs, but fixed thresholds are not portable.
- Budget-targeted gating is more defensible than fixed thresholds, but must be compared to matched random gates.
- Held-out gate calibration helps avoid post-hoc threshold selection, but only beats matched random reliably on controlled noisy/clean diagnostic settings at moderate budgets.
- External natural data shows partial document-level repair, but random K2 remains a very competitive baseline.

## Not Supported / Do Not Claim

- Universal semantic selector dominance.
- System-level latency or throughput improvements.
- vLLM/LMCache replacement.
- Span-level recompute as the final method.
- SOTA QA performance.
- Universal gate superiority over matched random budgets.

## Future Work

- Better external retrieval calibration.
- More robust gate calibration.
- Real serving integration.
- Larger model and real latency evaluation.
- Better held-out calibration protocols for natural external retrieval settings.
"""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def write_json(path: str | Path, payload: Any) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
