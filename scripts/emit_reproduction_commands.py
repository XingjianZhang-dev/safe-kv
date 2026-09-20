#!/usr/bin/env python
"""Emit or execute reproduction commands from packaged result summaries."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = Path("reproduction_runs/recomputed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=["answer", "latency", "all"],
        default="all",
        help="Which command family to emit.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run commands instead of only printing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands: list[list[str]] = []
    if args.kind in {"answer", "all"}:
        commands.extend(answer_commands())
    if args.kind in {"latency", "all"}:
        commands.extend(latency_commands())

    for command in commands:
        print(shell_join(with_env(command)))
        if args.execute:
            subprocess.run(with_env(command), cwd=ROOT, check=True)
    print(f"# commands: {len(commands)}", file=sys.stderr)
    return 0


def answer_commands() -> list[list[str]]:
    commands = []
    for summary_path in sorted((ROOT / "results").glob("*/answer_eval_summary.json")):
        summary = read_json(summary_path)
        result_name = summary_path.parent.name
        methods = list(summary.get("method_level", {}).keys())
        if not methods:
            continue
        command = [
            "python",
            "code/scripts/run_answer_eval.py",
            "--config",
            summary["config_path"],
            "--data-path",
            summary["dataset_path"],
            "--results-dir",
            str(OUT_ROOT / result_name),
            "--methods",
            ",".join(methods),
            "--resume",
        ]
        command.extend(selection_args(summary))
        selector = summary.get("selector_artifact")
        if selector:
            command.extend(["--selector-artifact", selector])
        commands.append(command)
    return commands


def latency_commands() -> list[list[str]]:
    commands = []
    for summary_path in sorted((ROOT / "results").glob("*/latency_summary.json")):
        summary = read_json(summary_path)
        result_name = summary_path.parent.name
        command = [
            "python",
            "code/scripts/run_latency_eval.py",
            "--config",
            summary["config_path"],
            "--data-path",
            summary["dataset_path"],
            "--results-dir",
            str(OUT_ROOT / result_name),
        ]
        if summary.get("num_examples") is not None:
            command.extend(["--max-examples", str(summary["num_examples"])])
        commands.append(command)
    return commands


def selection_args(summary: dict) -> list[str]:
    counts = summary.get("category_counts") or {}
    if not counts:
        return []
    values = list(counts.values())
    total = sum(values)
    if len(values) > 1 and len(set(values)) == 1:
        return ["--max-examples-per-category", str(values[0])]
    return ["--max-examples", str(total)]


def with_env(command: list[str]) -> list[str]:
    return ["env", "PYTHONPATH=code", *command]


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
