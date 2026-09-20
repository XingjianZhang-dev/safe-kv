#!/usr/bin/env python
"""Launch the tracked query-attention local-repair baseline over the IP&M grid."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_DATASETS = "hotpotqa,2wiki,musique"
DEFAULT_CONDITIONS = "natural,shuffle,bm25,dense"
DEFAULT_BUDGETS = "0.05,0.10,0.16,0.20,0.30,0.45,0.60"
DEFAULT_RANDOM_SEEDS = "13,29,47"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--split", choices=("calibration", "test"), required=True)
    parser.add_argument("--max-examples", type=int, required=True)
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--conditions", default=DEFAULT_CONDITIONS)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
    parser.add_argument("--random-seeds", default=DEFAULT_RANDOM_SEEDS)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--model-manifest", type=Path, default=None)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


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


def completed_run_is_valid(
    run_dir: Path,
    *,
    expected_examples: int,
    expected_budgets: int,
    expected_random_seeds: int,
) -> bool:
    manifest_path = run_dir / "run_manifest.json"
    output_path = run_dir / "query_attention_local_outputs.jsonl"
    summary_path = run_dir / "query_attention_local_summary.json"
    if not all(path.is_file() for path in (manifest_path, output_path, summary_path)):
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        return False
    rows = read_jsonl(output_path)
    methods_per_example = 2 + expected_budgets * (1 + expected_random_seeds)
    required = {
        "qa_answer_equivalence_to_fresh_reference",
        "first_token_kl_to_fresh_reference",
        "patched_context_ratio",
        "selection_planning_seconds",
        "selection_source",
    }
    return len(rows) == expected_examples * methods_per_example and all(
        required.issubset(row) for row in rows
    )


def main() -> None:
    args = parse_args()
    datasets = parse_csv(args.datasets)
    conditions = parse_csv(args.conditions)
    budgets = parse_csv(args.budgets)
    random_seeds = parse_csv(args.random_seeds)
    if args.max_examples <= 0:
        raise ValueError("--max-examples must be positive")
    if not datasets or not conditions or not budgets or not random_seeds:
        raise ValueError("grid, budgets, and random seeds must be non-empty")
    if len(budgets) != len(set(budgets)) or len(random_seeds) != len(set(random_seeds)):
        raise ValueError("budgets and random seeds must be unique")

    config = args.config.resolve()
    data_root = args.data_root.resolve()
    registry = args.registry_dir.resolve()
    code_root = args.code_root.resolve()
    tracked = code_root / "scripts" / "run_tracked.py"
    evaluator = code_root / "scripts" / "run_query_attention_local_baseline.py"
    if not all(path.is_file() for path in (config, tracked, evaluator)):
        raise FileNotFoundError("config or launcher/evaluator script is missing")
    if args.model_manifest is not None and not args.model_manifest.resolve().is_file():
        raise FileNotFoundError(args.model_manifest)

    environment = dict(os.environ)
    environment["PYTHONHASHSEED"] = "0"
    completed: list[str] = []
    skipped: list[str] = []
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
                f"{args.model_label}_query_attention_{dataset}_{condition}_{args.split}_"
                f"n{args.max_examples}_{args.version}"
            )
            run_dir = registry / run_id
            if run_dir.exists():
                if completed_run_is_valid(
                    run_dir,
                    expected_examples=args.max_examples,
                    expected_budgets=len(budgets),
                    expected_random_seeds=len(random_seeds),
                ):
                    skipped.append(run_id)
                    continue
                raise FileExistsError(
                    f"run exists but is not a complete attention cell: {run_dir}; "
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
                f"{args.model_label} {dataset}/{condition} {args.split} query-attention local baseline",
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
                    "--budgets",
                    ",".join(budgets),
                    "--random-seeds",
                    ",".join(random_seeds),
                ]
            )
            subprocess.run(command, check=True, env=environment, cwd=code_root)
            if not completed_run_is_valid(
                run_dir,
                expected_examples=args.max_examples,
                expected_budgets=len(budgets),
                expected_random_seeds=len(random_seeds),
            ):
                raise RuntimeError(f"attention output validation failed: {run_id}")
            completed.append(run_id)
            print(json.dumps({"completed": run_id}), flush=True)
    print(json.dumps({"completed_runs": completed, "skipped_runs": skipped}, indent=2))


if __name__ == "__main__":
    main()
