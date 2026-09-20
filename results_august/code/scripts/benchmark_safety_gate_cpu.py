#!/usr/bin/env python
"""Measure one-request CPU latency of the frozen safety-gate decision path."""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import (  # noqa: E402
    FEATURE_NAMES,
    predict_unsafe_probability,
    runtime_feature_vector,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        metavar=("DATA_JSONL", "ANSWER_OUTPUTS_JSONL"),
        required=True,
    )
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--warmup-examples", type=int, default=50)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "n_calls": len(values),
        "mean_ms": statistics.fmean(values),
        "median_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
        "p99_ms": percentile(values, 99),
        "max_ms": max(values),
    }


def main() -> None:
    args = parse_args()
    if args.repeats < 1 or args.warmup_examples < 0:
        raise ValueError("repeats must be positive and warmup nonnegative")
    artifact_path = args.artifact.resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact["feature_contract"]["names"] != list(FEATURE_NAMES):
        raise ValueError("feature contract differs from frozen artifact")
    model = artifact["model"]

    examples: list[tuple[dict[str, Any], int, str, str]] = []
    sources = []
    for data_text, output_text in args.source:
        data_path = Path(data_text).resolve()
        output_path = Path(output_text).resolve()
        data_rows = read_jsonl(data_path)
        prompt_lengths = {
            str(row["example_id"]): int(row["prompt_length"])
            for row in read_jsonl(output_path)
            if row.get("method") == "prefix_conditioned_naive_global"
        }
        if set(prompt_lengths) != {str(row["id"]) for row in data_rows}:
            raise ValueError(f"prompt-length coverage mismatch for {data_path}")
        for row in data_rows:
            metadata = row["source_metadata"]
            examples.append(
                (
                    row,
                    prompt_lengths[str(row["id"])],
                    str(metadata["dataset"]),
                    str(metadata["retrieval_condition"]),
                )
            )
        sources.append(
            {
                "data": {"path": str(data_path), "sha256": sha256_file(data_path)},
                "answer_outputs": {
                    "path": str(output_path),
                    "sha256": sha256_file(output_path),
                },
                "n_examples": len(data_rows),
            }
        )

    def decide(example: dict[str, Any], prompt_length: int) -> float:
        vector = runtime_feature_vector(example, prompt_length=prompt_length)
        probability = predict_unsafe_probability(
            np.asarray([vector], dtype=np.float64),
            means=model["means"],
            scales=model["scales"],
            coefficients=model["coefficients"],
            intercept=model["intercept"],
        )[0]
        if not math.isfinite(float(probability)):
            raise ValueError("gate probability is non-finite")
        return float(probability)

    for example, prompt_length, _dataset, _condition in examples[: args.warmup_examples]:
        decide(example, prompt_length)

    timings: list[dict[str, Any]] = []
    for repeat in range(args.repeats):
        for example, prompt_length, dataset, condition in examples:
            started = time.perf_counter_ns()
            probability = decide(example, prompt_length)
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
            timings.append(
                {
                    "repeat": repeat,
                    "example_id": str(example["id"]),
                    "dataset": dataset,
                    "condition": condition,
                    "elapsed_ms": elapsed_ms,
                    "predicted_unsafe_probability": probability,
                }
            )

    grouped: dict[str, list[float]] = {"overall": []}
    for row in timings:
        value = float(row["elapsed_ms"])
        grouped["overall"].append(value)
        grouped.setdefault(f"{row['dataset']}/{row['condition']}", []).append(value)
    report = {
        "schema_version": 1,
        "scope": "single-request CPU feature extraction plus logistic decision",
        "timer": "time.perf_counter_ns",
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "processor": platform.processor(),
            "numpy": np.__version__,
        },
        "artifact": {"path": str(artifact_path), "sha256": sha256_file(artifact_path)},
        "parameters": {
            "repeats": args.repeats,
            "warmup_examples": args.warmup_examples,
            "n_unique_examples_condition_rows": len(examples),
        },
        "sources": sources,
        "latency": {key: summarize(values) for key, values in sorted(grouped.items())},
        "raw_timings": timings,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise FileExistsError("refusing to overwrite safety-gate latency output")
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["latency"]["overall"], indent=2))


if __name__ == "__main__":
    main()
