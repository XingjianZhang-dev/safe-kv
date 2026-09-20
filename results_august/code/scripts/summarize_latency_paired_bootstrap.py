#!/usr/bin/env python
"""Paired example-level bootstrap intervals for repeated latency traces."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


FULL_METHOD = "full_prefill"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-replicates", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.bootstrap_replicates <= 0:
        raise ValueError("bootstrap-replicates must be positive")
    validation = json.loads(
        (args.results_dir / "validation_report.json").read_text(encoding="utf-8")
    )
    if validation.get("status") != "PASS":
        raise ValueError("latency validation report must be PASS before bootstrap")
    trace_path = args.results_dir / "latency_trace.csv"
    trace_sha256 = file_sha256(trace_path)
    validated_trace_sha256 = validation.get("input_artifact_sha256", {}).get(
        "latency_trace.csv"
    )
    if trace_sha256 != validated_trace_sha256:
        raise ValueError("latency trace changed after validation; rerun validator")
    validator_path = Path(validation["validator_script_path"])
    if file_sha256(validator_path) != validation.get("validator_script_sha256"):
        raise ValueError("latency validator changed; rerun validator before bootstrap")
    rows = read_csv(trace_path)
    example_medians = example_method_medians(rows)
    methods = sorted({method for _example_id, method in example_medians})
    example_ids = sorted({example_id for example_id, _method in example_medians})
    if any((example_id, FULL_METHOD) not in example_medians for example_id in example_ids):
        raise ValueError("full-prefill median missing for at least one example")

    summary_rows = []
    for method in methods:
        values = paired_values(example_ids, method, example_medians)
        rng = random.Random(stable_seed(args.seed, method))
        bootstrap_speedup_medians = []
        bootstrap_saved_medians = []
        bootstrap_faster_fractions = []
        for _ in range(args.bootstrap_replicates):
            sampled = [values[rng.randrange(len(values))] for _ in values]
            bootstrap_speedup_medians.append(
                statistics.median(item["speedup"] for item in sampled)
            )
            bootstrap_saved_medians.append(
                statistics.median(item["time_saved_s"] for item in sampled)
            )
            bootstrap_faster_fractions.append(
                statistics.fmean(float(item["time_saved_s"] > 0.0) for item in sampled)
            )
        summary_rows.append(
            {
                "method": method,
                "num_examples": len(values),
                "paired_example_speedup_median": statistics.median(
                    item["speedup"] for item in values
                ),
                "paired_example_speedup_median_ci95_low": percentile(
                    bootstrap_speedup_medians, 0.025
                ),
                "paired_example_speedup_median_ci95_high": percentile(
                    bootstrap_speedup_medians, 0.975
                ),
                "paired_example_time_saved_s_median": statistics.median(
                    item["time_saved_s"] for item in values
                ),
                "paired_example_time_saved_s_median_ci95_low": percentile(
                    bootstrap_saved_medians, 0.025
                ),
                "paired_example_time_saved_s_median_ci95_high": percentile(
                    bootstrap_saved_medians, 0.975
                ),
                "fraction_examples_faster_than_full": statistics.fmean(
                    float(item["time_saved_s"] > 0.0) for item in values
                ),
                "fraction_examples_faster_ci95_low": percentile(
                    bootstrap_faster_fractions, 0.025
                ),
                "fraction_examples_faster_ci95_high": percentile(
                    bootstrap_faster_fractions, 0.975
                ),
            }
        )

    output = {
        "scope": (
            "paired nonparametric bootstrap over examples after taking each "
            "example/method median across repeats; repeats are not independent units"
        ),
        "bootstrap_replicates": args.bootstrap_replicates,
        "seed": args.seed,
        "num_examples": len(example_ids),
        "input_latency_trace_sha256": trace_sha256,
        "validation_report_sha256": file_sha256(
            args.results_dir / "validation_report.json"
        ),
        "bootstrap_script_sha256": file_sha256(Path(__file__).resolve()),
        "method_summary": summary_rows,
    }
    (args.results_dir / "latency_paired_bootstrap_summary.json").write_text(
        json.dumps(output, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(
        args.results_dir / "latency_paired_bootstrap_summary.csv", summary_rows
    )
    print(json.dumps(output, indent=2))


def example_method_medians(rows: list[dict[str, str]]) -> dict[tuple[str, str], float]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(row["example_id"], row["method"])].append(
            float(row["time_to_first_logit_s"])
        )
    return {key: statistics.median(values) for key, values in grouped.items()}


def paired_values(
    example_ids: list[str],
    method: str,
    medians: dict[tuple[str, str], float],
) -> list[dict[str, float]]:
    output = []
    for example_id in example_ids:
        full = medians[(example_id, FULL_METHOD)]
        candidate = medians.get((example_id, method))
        if candidate is None or full <= 0.0 or candidate <= 0.0:
            raise ValueError(f"missing/nonpositive paired latency for {example_id}/{method}")
        output.append(
            {
                "speedup": full / candidate,
                "time_saved_s": full - candidate,
            }
        )
    return output


def stable_seed(seed: int, method: str) -> int:
    value = seed
    for character in method.encode("utf-8"):
        value = ((value * 131) + character) % (2**63 - 1)
    return value


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
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
