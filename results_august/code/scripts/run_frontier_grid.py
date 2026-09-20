#!/usr/bin/env python
"""Launch an auditable suffix-frontier scan across datasets and retrieval orders."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--split", choices=("calibration", "test"), required=True)
    parser.add_argument("--max-examples", type=int, required=True)
    parser.add_argument("--datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--version", default="v1")
    parser.add_argument("--random-seed", type=int, default=20260821)
    parser.add_argument("--model-manifest", type=Path, default=None)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_source(
    path: Path, *, dataset: str, condition: str, split: str, max_examples: int
) -> None:
    rows = read_jsonl(path)
    if len(rows) < max_examples:
        raise ValueError(f"{path}: only {len(rows)} rows, need {max_examples}")
    for row in rows[:max_examples]:
        metadata = row.get("source_metadata", {})
        observed = (
            metadata.get("dataset"),
            metadata.get("retrieval_condition"),
            metadata.get("split"),
        )
        expected = (dataset, condition, split)
        if observed != expected:
            raise ValueError(f"{path}: source metadata {observed} != {expected}")


def completed_run_is_valid(run_dir: Path, *, expected_examples: int) -> bool:
    manifest_path = run_dir / "run_manifest.json"
    outputs_path = run_dir / "frontier_outputs.jsonl"
    frontier_manifest = run_dir / "frontier_manifest.json"
    if not all(path.is_file() for path in (manifest_path, outputs_path, frontier_manifest)):
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        return False
    rows = read_jsonl(outputs_path)
    if len(rows) != expected_examples:
        return False
    for row in rows:
        count = int(row["num_documents"])
        starts = list(row["suffix_starts"]) + [row["no_repair"]]
        if sorted(int(item["start"]) for item in starts) != list(range(count + 1)):
            return False
    return True


def main() -> None:
    args = parse_args()
    datasets = [item for item in args.datasets.split(",") if item]
    conditions = [item for item in args.conditions.split(",") if item]
    if args.max_examples <= 0 or not datasets or not conditions:
        raise ValueError("positive max-examples and non-empty grid are required")
    config = args.config.resolve()
    data_root = args.data_root.resolve()
    registry = args.registry_dir.resolve()
    code_root = args.code_root.resolve()
    tracked = code_root / "scripts" / "run_tracked.py"
    evaluator = code_root / "scripts" / "run_rebuttal_frontier_eval.py"
    if not all(path.is_file() for path in (config, tracked, evaluator)):
        raise FileNotFoundError("config or launcher/evaluator script is missing")
    if args.model_manifest is not None and not args.model_manifest.resolve().is_file():
        raise FileNotFoundError(args.model_manifest)

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    completed = []
    skipped = []
    for dataset in datasets:
        for condition in conditions:
            data_path = data_root / f"{dataset}_{condition}_{args.split}.jsonl"
            validate_source(
                data_path,
                dataset=dataset,
                condition=condition,
                split=args.split,
                max_examples=args.max_examples,
            )
            run_id = (
                f"{args.model_label}_frontier_{dataset}_{condition}_{args.split}_"
                f"n{args.max_examples}_{args.version}"
            )
            run_dir = registry / run_id
            if run_dir.exists():
                if completed_run_is_valid(run_dir, expected_examples=args.max_examples):
                    skipped.append(run_id)
                    continue
                raise FileExistsError(
                    f"run exists but is not a complete frontier cell: {run_dir}; "
                    "preserve it and launch a new --version"
                )
            command = [
                sys.executable,
                str(tracked),
                "--registry-dir",
                str(registry),
                "--run-id",
                run_id,
                "--label",
                f"{args.model_label} {dataset}/{condition} {args.split} suffix frontier",
                "--code-root",
                str(code_root),
                "--working-directory",
                str(code_root),
                "--input",
                str(config),
                "--input",
                str(data_path),
            ]
            if args.model_manifest is not None:
                command.extend(["--input", str(args.model_manifest.resolve())])
            command.extend(
                [
                    "--",
                    sys.executable,
                    str(evaluator),
                    "--config",
                    str(config),
                    "--data-path",
                    str(data_path),
                    "--results-dir",
                    str(run_dir),
                    "--max-examples",
                    str(args.max_examples),
                    "--random-seed",
                    str(args.random_seed),
                ]
            )
            subprocess.run(command, check=True, env=env, cwd=code_root)
            if not completed_run_is_valid(run_dir, expected_examples=args.max_examples):
                raise RuntimeError(f"frontier output validation failed: {run_id}")
            completed.append(run_id)
            print(json.dumps({"completed": run_id}), flush=True)
    print(json.dumps({"completed_runs": completed, "skipped_runs": skipped}, indent=2))


if __name__ == "__main__":
    main()
