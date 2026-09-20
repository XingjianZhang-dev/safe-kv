#!/usr/bin/env python
"""Benchmark complete frozen frontier selection on calibration examples."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.frontier_selector import (  # noqa: E402
    FRONTIER_FEATURE_NAMES,
    FrontierCandidate,
    choose_frontier_actions,
    frontier_feature_vector,
)
from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import predict_unsafe_probability  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        metavar=("FRONTIER_RUN_DIR", "DATA_JSONL"),
        required=True,
    )
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--warmup-passes", type=int, default=2)
    parser.add_argument("--measured-passes", type=int, default=10)
    parser.add_argument("--expected-examples-per-source", type=int, default=100)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("percentile requires data")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def load_examples(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict]]:
    examples = []
    sources = []
    seen_cells = set()
    for run_text, data_text in args.source:
        run_dir = Path(run_text).resolve()
        data_path = Path(data_text).resolve()
        outputs_path = run_dir / "frontier_outputs.jsonl"
        run_manifest_path = run_dir / "run_manifest.json"
        frontier_manifest_path = run_dir / "frontier_manifest.json"
        run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        if run_manifest.get("status") != "completed" or run_manifest.get("exit_code") != 0:
            raise ValueError(f"frontier source did not complete: {run_dir}")
        data_rows = read_jsonl(data_path)
        data_by_id = {str(row["id"]): row for row in data_rows}
        output_rows = read_jsonl(outputs_path)
        if len(output_rows) != args.expected_examples_per_source:
            raise ValueError(f"unexpected frontier row count: {run_dir}")
        cell = None
        for output in output_rows:
            example_id = str(output["example_id"])
            row = data_by_id[example_id]
            metadata = row["source_metadata"]
            if metadata.get("split") != "calibration":
                raise ValueError("CPU benchmark may use calibration inputs only")
            current = (str(metadata["dataset"]), str(metadata["retrieval_condition"]))
            if cell is None:
                cell = current
            if current != cell:
                raise ValueError(f"mixed source cell: {data_path}")
            examples.append(
                {
                    "record_id": f"{current[0]}:{metadata['source_id']}:{current[1]}",
                    "row": row,
                    "prompt_length": int(output["prompt_length"]),
                }
            )
        if cell in seen_cells:
            raise ValueError(f"duplicate source cell: {cell}")
        seen_cells.add(cell)
        sources.append(
            {
                "dataset": cell[0],
                "condition": cell[1],
                "run_dir": str(run_dir),
                "frontier_outputs_sha256": sha256_file(outputs_path),
                "run_manifest_sha256": sha256_file(run_manifest_path),
                "frontier_manifest_sha256": sha256_file(frontier_manifest_path),
                "data_path": str(data_path),
                "data_sha256": sha256_file(data_path),
            }
        )
    return examples, sources


def select_one(example: dict[str, Any], artifact: dict[str, Any]) -> int | None:
    row = example["row"]
    count = len(row["documents"])
    candidates = [
        FrontierCandidate(
            example_id=example["record_id"],
            group_id=example["record_id"],
            dataset="calibration",
            condition="calibration",
            start=start,
            num_documents=count,
            unsafe=False,
            patch_ratio=(count - start) / count,
            features=frontier_feature_vector(
                row,
                start=start,
                prompt_length=example["prompt_length"],
            ),
        )
        for start in range(count + 1)
    ]
    model = artifact["model"]
    probabilities = predict_unsafe_probability(
        np.asarray([candidate.features for candidate in candidates], dtype=np.float64),
        means=model["means"],
        scales=model["scales"],
        coefficients=model["coefficients"],
        intercept=model["intercept"],
    )
    action = choose_frontier_actions(
        candidates,
        probabilities,
        threshold=float(artifact["threshold"]),
    )[example["record_id"]]
    return None if action is None else int(action.start)


def main() -> None:
    args = parse_args()
    if args.warmup_passes < 0 or args.measured_passes <= 0:
        raise ValueError("invalid benchmark pass counts")
    artifact_path = args.artifact.resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact["feature_contract"]["names"] != list(FRONTIER_FEATURE_NAMES):
        raise ValueError("frontier feature contract mismatch")
    if artifact["integrity"].get("test_set_used") is not False:
        raise ValueError("CPU benchmark requires a calibration-only artifact")
    examples, sources = load_examples(args)

    checksum = 0
    for _ in range(args.warmup_passes):
        for example in examples:
            start = select_one(example, artifact)
            checksum += -1 if start is None else start

    timings_us = []
    for _ in range(args.measured_passes):
        for example in examples:
            started = time.perf_counter_ns()
            start = select_one(example, artifact)
            elapsed = time.perf_counter_ns() - started
            timings_us.append(elapsed / 1000.0)
            checksum += -1 if start is None else start

    report = {
        "schema_version": 1,
        "scope": (
            "single-process CPU wall time for feature extraction over all candidate "
            "starts, logistic scoring, and latest-safe/fallback decision"
        ),
        "artifact": {"path": str(artifact_path), "sha256": sha256_file(artifact_path)},
        "sources": sources,
        "n_examples_per_pass": len(examples),
        "warmup_passes": args.warmup_passes,
        "measured_passes": args.measured_passes,
        "n_measurements": len(timings_us),
        "latency_microseconds_per_example": {
            "mean": statistics.fmean(timings_us),
            "median": statistics.median(timings_us),
            "p95": percentile(timings_us, 0.95),
            "p99": percentile(timings_us, 0.99),
            "min": min(timings_us),
            "max": max(timings_us),
        },
        "checksum": checksum,
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "integrity": {"test_set_used": False, "gold_or_oracle_feature_used": False},
    }
    args.out = args.out.resolve()
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite benchmark: {args.out}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["latency_microseconds_per_example"], indent=2))


if __name__ == "__main__":
    main()
