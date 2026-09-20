#!/usr/bin/env python
"""CPU-only selector audit for the SAFE-KV ARR author response.

This script intentionally does not run the language model. It measures:

1. selector quality under document-order shuffling;
2. selector quality after removing the gold-derived retrieval-score signal;
3. deterministic-random selector quality over multiple seeds; and
4. per-example selector latency on the local CPU.

The audit leaves the main SAFE-KV implementation unchanged and writes all
outputs to a separate directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

CODE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_ROOT.parent
sys.path.insert(0, str(CODE_ROOT))

from safekv.build_diagnostic import read_jsonl  # noqa: E402
from safekv.data_schema import DiagnosticExample  # noqa: E402
from safekv.doc_selector import (  # noqa: E402
    random_doc_ids_same_count,
    selected_doc_ids_for_method,
)
from safekv.patch_recompute import stable_example_seed  # noqa: E402


QUALITY_METHODS = [
    "query_similarity_doc_patch_k1",
    "query_similarity_doc_patch_k2",
    "risk_guided_doc_patch_k1",
    "risk_guided_doc_patch_k2",
]
LATENCY_METHODS = QUALITY_METHODS
DEFAULT_SHUFFLE_SEEDS = [101, 202, 303]
DEFAULT_RANDOM_SEEDS = list(range(20))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "results" / "rebuttal_cpu_selector_audit",
    )
    parser.add_argument("--latency-repeats", type=int, default=10)
    parser.add_argument("--latency-max-examples", type=int, default=500)
    parser.add_argument(
        "--shuffle-seeds",
        type=str,
        default=",".join(str(seed) for seed in DEFAULT_SHUFFLE_SEEDS),
    )
    parser.add_argument(
        "--random-seeds",
        type=str,
        default=",".join(str(seed) for seed in DEFAULT_RANDOM_SEEDS),
    )
    return parser.parse_args()


def parse_int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def stable_shuffle_seed(seed: int, example_id: str) -> int:
    digest = hashlib.sha256(f"{seed}:{example_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def transform_example(
    example: DiagnosticExample,
    *,
    neutralize_retrieval: bool,
    shuffle_seed: int | None,
) -> DiagnosticExample:
    """Return a valid example with optional order shuffle and id remapping."""

    documents = list(example.documents)
    if shuffle_seed is not None:
        rng = random.Random(stable_shuffle_seed(shuffle_seed, example.id))
        rng.shuffle(documents)

    old_to_new = {doc.doc_id: new_id for new_id, doc in enumerate(documents)}
    transformed_documents = [
        replace(
            doc,
            doc_id=new_id,
            retrieval_score=0.0 if neutralize_retrieval else doc.retrieval_score,
        )
        for new_id, doc in enumerate(documents)
    ]
    transformed = replace(
        example,
        documents=transformed_documents,
        evidence=[replace(span, doc_id=old_to_new[span.doc_id]) for span in example.evidence],
        conflicting_docs=[old_to_new[doc_id] for doc_id in example.conflicting_docs],
    )
    transformed.validate()
    return transformed


def select_docs(example: DiagnosticExample, method: str, seed: int = 13) -> list[int]:
    selected, _reason = selected_doc_ids_for_method(method, example, seed=seed)
    return selected


def selector_quality(
    examples: Iterable[DiagnosticExample],
    method: str,
    *,
    seed: int = 13,
) -> dict[str, float]:
    recalls: list[float] = []
    precisions: list[float] = []
    any_hits: list[float] = []
    exact_sets: list[float] = []
    suffix_ratios: list[float] = []
    selected_counts: list[float] = []

    for example in examples:
        positives = {span.doc_id for span in example.evidence}
        selected = select_docs(example, method, seed=seed)
        selected_set = set(selected)
        hits = selected_set & positives
        recalls.append(len(hits) / max(1, len(positives)))
        precisions.append(len(hits) / max(1, len(selected_set)))
        any_hits.append(1.0 if hits else 0.0)
        exact_sets.append(1.0 if selected_set == positives else 0.0)
        suffix_ratios.append(suffix_doc_ratio(example, selected))
        selected_counts.append(float(len(selected_set)))

    return {
        "recall": mean(recalls),
        "precision": mean(precisions),
        "any_hit": mean(any_hits),
        "exact_set": mean(exact_sets),
        "avg_selected_docs": mean(selected_counts),
        "avg_suffix_doc_ratio": mean(suffix_ratios),
    }


def random_selector_quality(
    examples: Iterable[DiagnosticExample],
    *,
    k: int,
    seed: int,
) -> dict[str, float]:
    recalls: list[float] = []
    precisions: list[float] = []
    any_hits: list[float] = []
    exact_sets: list[float] = []
    suffix_ratios: list[float] = []

    for example in examples:
        positives = {span.doc_id for span in example.evidence}
        method = f"rebuttal_random_doc_patch_k{k}"
        selected = random_doc_ids_same_count(
            example,
            count=k,
            seed=stable_example_seed(seed, example.id, method),
        )
        selected_set = set(selected)
        hits = selected_set & positives
        recalls.append(len(hits) / max(1, len(positives)))
        precisions.append(len(hits) / max(1, len(selected_set)))
        any_hits.append(1.0 if hits else 0.0)
        exact_sets.append(1.0 if selected_set == positives else 0.0)
        suffix_ratios.append(suffix_doc_ratio(example, selected))

    return {
        "recall": mean(recalls),
        "precision": mean(precisions),
        "any_hit": mean(any_hits),
        "exact_set": mean(exact_sets),
        "avg_suffix_doc_ratio": mean(suffix_ratios),
    }


def suffix_doc_ratio(example: DiagnosticExample, selected_doc_ids: list[int]) -> float:
    if not selected_doc_ids:
        return 0.0
    selected = set(selected_doc_ids)
    positions = [idx for idx, doc in enumerate(example.documents) if doc.doc_id in selected]
    if not positions:
        return 0.0
    return (len(example.documents) - min(positions)) / max(1, len(example.documents))


def run_quality_audit(
    datasets: dict[str, list[DiagnosticExample]],
    shuffle_seeds: list[int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scenario_specs = [
        ("original", False, None),
        ("retrieval_neutral", True, None),
    ]
    scenario_specs.extend(
        ("order_shuffled", False, seed) for seed in shuffle_seeds
    )
    scenario_specs.extend(
        ("retrieval_neutral_order_shuffled", True, seed) for seed in shuffle_seeds
    )

    for dataset_name, examples in datasets.items():
        for scenario, neutralize_retrieval, shuffle_seed in scenario_specs:
            transformed = [
                transform_example(
                    example,
                    neutralize_retrieval=neutralize_retrieval,
                    shuffle_seed=shuffle_seed,
                )
                for example in examples
            ]
            for method in QUALITY_METHODS:
                rows.append(
                    {
                        "dataset": dataset_name,
                        "scenario": scenario,
                        "scenario_seed": "" if shuffle_seed is None else shuffle_seed,
                        "method": method,
                        "num_examples": len(transformed),
                        **selector_quality(transformed, method),
                    }
                )
    return rows


def summarize_quality_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["scenario"], row["method"])].append(row)

    metric_names = [
        "recall",
        "precision",
        "any_hit",
        "exact_set",
        "avg_selected_docs",
        "avg_suffix_doc_ratio",
    ]
    summaries: list[dict[str, Any]] = []
    for (dataset, scenario, method), group in sorted(grouped.items()):
        summary: dict[str, Any] = {
            "dataset": dataset,
            "scenario": scenario,
            "method": method,
            "num_examples": group[0]["num_examples"],
            "num_scenario_seeds": len(group),
        }
        for metric in metric_names:
            values = [float(row[metric]) for row in group]
            summary[f"{metric}_mean"] = mean(values)
            summary[f"{metric}_min"] = min(values)
            summary[f"{metric}_max"] = max(values)
        summaries.append(summary)
    return summaries


def run_random_audit(
    datasets: dict[str, list[DiagnosticExample]],
    random_seeds: list[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    for dataset_name, examples in datasets.items():
        for k in [1, 2]:
            for seed in random_seeds:
                rows.append(
                    {
                        "dataset": dataset_name,
                        "method": f"random_doc_patch_k{k}",
                        "seed": seed,
                        "num_examples": len(examples),
                        **random_selector_quality(examples, k=k, seed=seed),
                    }
                )

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["method"])].append(row)
    summaries: list[dict[str, Any]] = []
    metric_names = ["recall", "precision", "any_hit", "exact_set", "avg_suffix_doc_ratio"]
    for (dataset, method), group in sorted(grouped.items()):
        summary: dict[str, Any] = {
            "dataset": dataset,
            "method": method,
            "num_examples": group[0]["num_examples"],
            "num_seeds": len(group),
        }
        for metric in metric_names:
            values = [float(row[metric]) for row in group]
            summary[f"{metric}_mean"] = mean(values)
            summary[f"{metric}_stdev"] = statistics.pstdev(values)
            summary[f"{metric}_min"] = min(values)
            summary[f"{metric}_max"] = max(values)
        summaries.append(summary)
    return rows, summaries


def run_latency_audit(
    workloads: dict[str, list[DiagnosticExample]],
    *,
    repeats: int,
    max_examples: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workload_name, all_examples in workloads.items():
        examples = all_examples[:max_examples]
        for method in LATENCY_METHODS:
            for example in examples[: min(25, len(examples))]:
                select_docs(example, method)

            elapsed_ms: list[float] = []
            for _repeat in range(repeats):
                for example in examples:
                    started = time.perf_counter_ns()
                    select_docs(example, method)
                    elapsed_ms.append((time.perf_counter_ns() - started) / 1_000_000.0)

            doc_counts = [len(example.documents) for example in examples]
            rows.append(
                {
                    "workload": workload_name,
                    "method": method,
                    "num_examples": len(examples),
                    "num_repeats": repeats,
                    "num_calls": len(elapsed_ms),
                    "min_docs": min(doc_counts),
                    "max_docs": max(doc_counts),
                    "median_ms": percentile(elapsed_ms, 50),
                    "p95_ms": percentile(elapsed_ms, 95),
                    "p99_ms": percentile(elapsed_ms, 99),
                    "mean_ms": mean(elapsed_ms),
                }
            )
    return rows


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def mean(values: Iterable[float]) -> float:
    materialized = list(values)
    return sum(materialized) / len(materialized) if materialized else 0.0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cpu_description() -> str:
    try:
        value = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    return platform.processor() or platform.machine()


def load_latency_workloads(data_dir: Path) -> dict[str, list[DiagnosticExample]]:
    workloads = {
        "external_hotpotqa": read_jsonl(data_dir / "external_hotpotqa_500.jsonl"),
        "external_2wiki": read_jsonl(data_dir / "external_2wiki_500.jsonl"),
    }
    sweep_sources = {
        3: data_dir / "noise_sweep_0_250.jsonl",
        7: data_dir / "noise_sweep_4_250.jsonl",
        19: data_dir / "noise_sweep_16_250.jsonl",
        67: data_dir / "noise_sweep_64_50.jsonl",
    }
    for doc_count, path in sweep_sources.items():
        examples = [example for example in read_jsonl(path) if len(example.documents) == doc_count]
        workloads[f"synthetic_docs{doc_count}"] = examples
    return workloads


def render_report(summary: dict[str, Any]) -> str:
    quality = summary["quality_summary"]
    latency = summary["latency"]
    lines = [
        "# SAFE-KV CPU Selector Audit",
        "",
        "This is a selector-only audit. It does not establish language-model answer quality or end-to-end recomputation correctness.",
        "",
        "## Quality under retrieval-score removal and order shuffling",
        "",
        "| Dataset | Scenario | Method | Recall | Any hit | Exact set | Suffix ratio |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in quality:
        if row["method"] not in {
            "query_similarity_doc_patch_k2",
            "risk_guided_doc_patch_k2",
        }:
            continue
        lines.append(
            "| {dataset} | {scenario} | {method} | {recall:.3f} | {hit:.3f} | {exact:.3f} | {suffix:.3f} |".format(
                dataset=row["dataset"],
                scenario=row["scenario"],
                method=row["method"],
                recall=row["recall_mean"],
                hit=row["any_hit_mean"],
                exact=row["exact_set_mean"],
                suffix=row["avg_suffix_doc_ratio_mean"],
            )
        )

    lines.extend(
        [
            "",
            "## Local CPU latency",
            "",
            f"CPU: {summary['environment']['cpu']}",
            "",
            "| Workload | Method | Calls | Median ms | P95 ms | P99 ms |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in latency:
        lines.append(
            "| {workload} | {method} | {calls} | {median:.3f} | {p95:.3f} | {p99:.3f} |".format(
                workload=row["workload"],
                method=row["method"],
                calls=row["num_calls"],
                median=row["median_ms"],
                p95=row["p95_ms"],
                p99=row["p99_ms"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation guardrail",
            "",
            "These results can support a narrow claim about selector cost and label-free document identification. They cannot support the paper's answer-equivalence or production-latency claims without the GPU recomputation experiment.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    shuffle_seeds = parse_int_list(args.shuffle_seeds)
    random_seeds = parse_int_list(args.random_seeds)
    data_dir = PROJECT_ROOT / "data"
    datasets = {
        "hotpotqa": read_jsonl(data_dir / "external_hotpotqa_500.jsonl"),
        "2wiki": read_jsonl(data_dir / "external_2wiki_500.jsonl"),
    }

    quality_rows = run_quality_audit(datasets, shuffle_seeds)
    quality_summary = summarize_quality_rows(quality_rows)
    random_rows, random_summary = run_random_audit(datasets, random_seeds)
    latency_rows = run_latency_audit(
        load_latency_workloads(data_dir),
        repeats=args.latency_repeats,
        max_examples=args.latency_max_examples,
    )

    output = {
        "environment": {
            "cpu": cpu_description(),
            "platform": platform.platform(),
            "python": sys.version,
        },
        "parameters": {
            "shuffle_seeds": shuffle_seeds,
            "random_seeds": random_seeds,
            "latency_repeats": args.latency_repeats,
            "latency_max_examples": args.latency_max_examples,
        },
        "quality_summary": quality_summary,
        "random_quality_summary": random_summary,
        "latency": latency_rows,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "quality_by_seed.csv", quality_rows)
    write_csv(args.out_dir / "quality_summary.csv", quality_summary)
    write_csv(args.out_dir / "random_quality_by_seed.csv", random_rows)
    write_csv(args.out_dir / "random_quality_summary.csv", random_summary)
    write_csv(args.out_dir / "latency.csv", latency_rows)
    (args.out_dir / "summary.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "REPORT.md").write_text(render_report(output), encoding="utf-8")
    print(f"Wrote CPU selector audit to {args.out_dir}")


if __name__ == "__main__":
    main()
