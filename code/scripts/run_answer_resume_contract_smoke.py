#!/usr/bin/env python
"""Exercise fresh, matching-resume, and mismatched-resume answer-eval paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--hf-home", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.results_dir.exists():
        raise ValueError("resume contract smoke requires a brand-new results directory")
    runner = Path(__file__).with_name("run_answer_eval.py").resolve()
    base_command = [
        sys.executable,
        str(runner),
        "--config",
        str(args.config.resolve()),
        "--data-path",
        str(args.data_path.resolve()),
        "--results-dir",
        str(args.results_dir.resolve()),
        "--max-examples",
        "1",
        "--methods",
        "actual_recompute::risk_guided_suffix_closure_k1",
    ]
    environment = dict(os.environ)
    environment["HF_HOME"] = str(args.hf_home.resolve())
    environment["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

    fresh = run(base_command, environment)
    if fresh.returncode != 0:
        raise RuntimeError(f"fresh run failed:\n{fresh.stderr}\n{fresh.stdout}")
    outputs_path = args.results_dir / "answer_eval_outputs.jsonl"
    manifest_path = args.results_dir / "answer_eval_manifest.json"
    fresh_outputs_hash = file_sha256(outputs_path)
    fresh_manifest_hash = file_sha256(manifest_path)

    matching_resume = run([*base_command, "--resume"], environment)
    if matching_resume.returncode != 0:
        raise RuntimeError(
            "matching resume failed:\n"
            f"{matching_resume.stderr}\n{matching_resume.stdout}"
        )
    matching_outputs_hash = file_sha256(outputs_path)

    mismatched_command = list(base_command)
    max_examples_index = mismatched_command.index("--max-examples") + 1
    mismatched_command[max_examples_index] = "2"
    mismatched_resume = run([*mismatched_command, "--resume"], environment)
    mismatched_outputs_hash = file_sha256(outputs_path)
    mismatch_rejected = (
        mismatched_resume.returncode != 0
        and "resume manifest mismatch" in (
            mismatched_resume.stderr + mismatched_resume.stdout
        )
    )

    rows = read_jsonl(outputs_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = {
        "fresh_exit_zero": fresh.returncode == 0,
        "matching_resume_exit_zero": matching_resume.returncode == 0,
        "mismatched_resume_rejected": mismatch_rejected,
        "matching_resume_preserved_output_bytes": (
            matching_outputs_hash == fresh_outputs_hash
        ),
        "mismatched_resume_preserved_output_bytes": (
            mismatched_outputs_hash == fresh_outputs_hash
        ),
        "one_unique_output_row": len(rows) == 1
        and len({(row["example_id"], row["method"]) for row in rows}) == 1,
        "schema_v2_or_newer": int(manifest.get("schema_version", 0)) >= 2,
        "implementation_hashes_present": bool(manifest.get("implementation_sha256")),
        "model_commit_present": bool(manifest.get("model_commit_hash")),
        "tokenizer_fingerprint_present": bool(manifest.get("tokenizer_sha256")),
    }
    report: dict[str, Any] = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "fresh_outputs_sha256": fresh_outputs_hash,
        "matching_resume_outputs_sha256": matching_outputs_hash,
        "mismatched_resume_outputs_sha256": mismatched_outputs_hash,
        "manifest_sha256": fresh_manifest_hash,
        "fresh_returncode": fresh.returncode,
        "matching_resume_returncode": matching_resume.returncode,
        "mismatched_resume_returncode": mismatched_resume.returncode,
    }
    (args.results_dir / "resume_contract_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


def run(command: list[str], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
