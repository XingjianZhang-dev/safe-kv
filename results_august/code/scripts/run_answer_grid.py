#!/usr/bin/env python
"""Launch an auditable dataset-by-retrieval-condition answer-evaluation grid."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_DATASETS = "hotpotqa,2wiki,musique"
DEFAULT_CONDITIONS = "natural,shuffle,bm25,dense"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--split", choices=("calibration", "test"), required=True)
    parser.add_argument("--max-examples", type=int, required=True)
    parser.add_argument("--methods", required=True)
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--conditions", default=DEFAULT_CONDITIONS)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--model-manifest", type=Path, default=None)
    parser.add_argument("--selector-artifact", type=Path, default=None)
    parser.add_argument("--frontier-selector-artifact", type=Path, default=None)
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


def completed_run_is_valid(
    run_dir: Path, *, expected_examples: int, expected_methods: int
) -> bool:
    manifest_path = run_dir / "run_manifest.json"
    output_path = run_dir / "answer_eval_outputs.jsonl"
    if not manifest_path.is_file() or not output_path.is_file():
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        return False
    rows = read_jsonl(output_path)
    required_fields = {
        "raw_trimmed_answer_exact_to_full_prefill",
        "response_token_f1_to_full_prefill",
        "response_rouge_l_f1_to_full_prefill",
        "generated_token_sequence_exact_to_full_prefill",
        "first_token_kl_full_to_method",
        "first_token_js_divergence",
        "top1_match",
        "top5_overlap",
        "top10_overlap",
        "online_context_prefill_fraction",
        "online_context_prefill_token_count",
        "context_token_count",
    }
    return len(rows) == expected_examples * expected_methods and all(
        required_fields.issubset(row) for row in rows
    )


def main() -> None:
    args = parse_args()
    if args.max_examples <= 0:
        raise ValueError("--max-examples must be positive")
    datasets = [item for item in args.datasets.split(",") if item]
    conditions = [item for item in args.conditions.split(",") if item]
    methods = [item for item in args.methods.split(",") if item]
    if not datasets or not conditions or not methods:
        raise ValueError("datasets, conditions, and methods must be non-empty")
    config = args.config.resolve()
    data_root = args.data_root.resolve()
    registry = args.registry_dir.resolve()
    code_root = args.code_root.resolve()
    tracked = code_root / "scripts" / "run_tracked.py"
    evaluator = code_root / "scripts" / "run_answer_eval.py"
    if not all(path.is_file() for path in (config, tracked, evaluator)):
        raise FileNotFoundError("config or launcher/evaluator script is missing")
    if args.model_manifest is not None and not args.model_manifest.resolve().is_file():
        raise FileNotFoundError(args.model_manifest)
    if args.selector_artifact is not None and not args.selector_artifact.resolve().is_file():
        raise FileNotFoundError(args.selector_artifact)
    if (
        args.frontier_selector_artifact is not None
        and not args.frontier_selector_artifact.resolve().is_file()
    ):
        raise FileNotFoundError(args.frontier_selector_artifact)

    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    completed = []
    skipped = []
    for dataset in datasets:
        for condition in conditions:
            data_path = data_root / f"{dataset}_{condition}_{args.split}.jsonl"
            if not data_path.is_file():
                raise FileNotFoundError(data_path)
            validate_source(
                data_path,
                dataset=dataset,
                condition=condition,
                split=args.split,
                max_examples=args.max_examples,
            )
            run_id = (
                f"{args.model_label}_answers_{dataset}_{condition}_{args.split}_"
                f"n{args.max_examples}_{args.version}"
            )
            run_dir = registry / run_id
            if run_dir.exists():
                if completed_run_is_valid(
                    run_dir,
                    expected_examples=args.max_examples,
                    expected_methods=len(methods),
                ):
                    skipped.append(run_id)
                    continue
                raise FileExistsError(
                    f"run exists but is not a complete expected grid cell: {run_dir}; "
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
                f"{args.model_label} {dataset}/{condition} {args.split} answer evaluation",
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
            if args.selector_artifact is not None:
                command.extend(["--input", str(args.selector_artifact.resolve())])
            if args.frontier_selector_artifact is not None:
                command.extend(
                    ["--input", str(args.frontier_selector_artifact.resolve())]
                )
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
                    "--methods",
                    ",".join(methods),
                ]
            )
            if args.selector_artifact is not None:
                command.extend(
                    ["--selector-artifact", str(args.selector_artifact.resolve())]
                )
            if args.frontier_selector_artifact is not None:
                command.extend(
                    [
                        "--frontier-selector-artifact",
                        str(args.frontier_selector_artifact.resolve()),
                    ]
                )
            subprocess.run(command, check=True, env=env, cwd=code_root)
            if not completed_run_is_valid(
                run_dir,
                expected_examples=args.max_examples,
                expected_methods=len(methods),
            ):
                raise RuntimeError(f"completed command failed output validation: {run_id}")
            completed.append(run_id)
            print(json.dumps({"completed": run_id}), flush=True)
    print(json.dumps({"completed_runs": completed, "skipped_runs": skipped}, indent=2))


if __name__ == "__main__":
    main()
