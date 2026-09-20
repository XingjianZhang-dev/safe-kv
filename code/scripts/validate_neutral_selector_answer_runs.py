#!/usr/bin/env python
"""Validate and aggregate retrieval-neutral shuffled answer-forward runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, action="append", required=True)
    parser.add_argument("--expected-examples", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    expected_methods: set[str] | None = None
    failures: list[str] = []
    run_summaries: list[dict[str, Any]] = []
    for run_dir in args.run_dir:
        manifest = read_json(run_dir / "answer_eval_manifest.json")
        summary = read_json(run_dir / "answer_eval_summary.json")
        rows = read_jsonl(run_dir / "answer_eval_outputs.jsonl")
        methods = set(str(item) for item in manifest.get("methods", []))
        if expected_methods is None:
            expected_methods = methods
        elif methods != expected_methods:
            failures.append(f"method set mismatch in {run_dir}")
        if int(manifest.get("max_examples", -1)) != args.expected_examples:
            failures.append(f"manifest max_examples mismatch in {run_dir}")
        validate_hash(manifest, "config_path", "config_sha256", failures, run_dir)
        validate_hash(manifest, "data_path", "data_sha256", failures, run_dir)

        expected_rows = args.expected_examples * len(methods)
        if len(rows) != expected_rows:
            failures.append(f"row count {len(rows)} != {expected_rows} in {run_dir}")
        keys = [(str(row["example_id"]), str(row["method"])) for row in rows]
        if len(keys) != len(set(keys)):
            failures.append(f"duplicate example/method keys in {run_dir}")
        if {str(row["method"]) for row in rows} != methods:
            failures.append(f"row method set mismatch in {run_dir}")
        if int(summary.get("num_failed_rows", -1)) != 0 or summary.get("failed_rows"):
            failures.append(f"answer runner reported failures in {run_dir}")

        by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_method[str(row["method"])].append(row)
        data_path = Path(str(manifest["data_path"]))
        dataset = "hotpotqa" if "hotpot" in data_path.name else "2wiki"
        order_seed = parse_order_seed(data_path.name)
        for method in sorted(methods):
            items = by_method[method]
            if len(items) != args.expected_examples:
                failures.append(f"method row count mismatch for {run_dir}/{method}")
            qa = mean_bool(items, "answer_equivalence_to_full_prefill")
            raw = statistics.fmean(
                float(str(item["generated_answer"]).strip() == str(item["full_prefill_answer"]).strip())
                for item in items
            )
            token = statistics.fmean(
                float(item["generated_token_ids"] == item["full_prefill_token_ids"])
                for item in items
            )
            patch = statistics.fmean(float(item["patched_token_ratio"]) for item in items)
            first_kl = statistics.fmean(
                float(item["first_token_kl_full_to_method"]) for item in items
            )
            summary_item = summary.get("method_level", {}).get(method)
            if not isinstance(summary_item, dict):
                failures.append(f"missing summary method for {run_dir}/{method}")
            else:
                compare_float(
                    qa,
                    summary_item.get("answer_equivalence_to_full_prefill"),
                    f"QA equivalence {run_dir}/{method}",
                    failures,
                )
                compare_float(
                    patch,
                    summary_item.get("avg_patched_token_ratio"),
                    f"patch ratio {run_dir}/{method}",
                    failures,
                )
                compare_float(
                    first_kl,
                    summary_item.get("avg_first_token_kl"),
                    f"first-token KL {run_dir}/{method}",
                    failures,
                )
            run_summaries.append(
                {
                    "dataset": dataset,
                    "order_seed": order_seed,
                    "method": method,
                    "num_examples": len(items),
                    "normalized_answer_exact": qa,
                    "postprocessed_string_exact": raw,
                    "generated_token_exact": token,
                    "mean_recomputed_context_token_ratio": patch,
                    "mean_first_token_kl": first_kl,
                    "run_dir": str(run_dir.resolve()),
                }
            )

    aggregate: list[dict[str, Any]] = []
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in run_summaries:
        groups[(item["dataset"], item["method"])].append(item)
    for (dataset, method), items in sorted(groups.items()):
        aggregate.append(
            {
                "dataset": dataset,
                "method": method,
                "num_order_seeds": len(items),
                "order_seeds": [int(item["order_seed"]) for item in items],
                **aggregate_metric(items, "normalized_answer_exact"),
                **aggregate_metric(items, "postprocessed_string_exact"),
                **aggregate_metric(items, "generated_token_exact"),
                **aggregate_metric(items, "mean_recomputed_context_token_ratio"),
                **aggregate_metric(items, "mean_first_token_kl"),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS" if not failures else "FAIL",
        "expected_examples_per_seed": args.expected_examples,
        "num_runs": len(args.run_dir),
        "num_failures": len(failures),
        "failures": failures,
        "run_summaries": run_summaries,
        "across_seed_summary": aggregate,
    }
    (args.output_dir / "neutral_selector_validation.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(args.output_dir / "neutral_selector_by_seed.csv", run_summaries)
    write_csv(args.output_dir / "neutral_selector_across_seed.csv", aggregate)
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


def aggregate_metric(items: list[dict[str, Any]], field: str) -> dict[str, float]:
    values = [float(item[field]) for item in items]
    return {
        f"{field}_mean_across_seeds": statistics.fmean(values),
        f"{field}_min_seed": min(values),
        f"{field}_max_seed": max(values),
    }


def parse_order_seed(name: str) -> int:
    marker = "shuffle"
    if marker not in name:
        raise ValueError(f"cannot parse order seed from {name}")
    return int(name.split(marker, 1)[1].split(".", 1)[0])


def validate_hash(
    manifest: dict[str, Any],
    path_field: str,
    hash_field: str,
    failures: list[str],
    run_dir: Path,
) -> None:
    path = Path(str(manifest.get(path_field, "")))
    if not path.exists():
        failures.append(f"missing manifest path {path} in {run_dir}")
        return
    if file_sha256(path) != manifest.get(hash_field):
        failures.append(f"manifest hash mismatch for {path} in {run_dir}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean_bool(items: list[dict[str, Any]], field: str) -> float:
    return statistics.fmean(float(item[field]) for item in items)


def compare_float(
    observed: float,
    expected: Any,
    label: str,
    failures: list[str],
) -> None:
    if expected is None or not math.isclose(
        observed,
        float(expected),
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        failures.append(f"summary mismatch: {label}")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
