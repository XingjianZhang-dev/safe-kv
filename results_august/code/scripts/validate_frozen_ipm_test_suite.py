#!/usr/bin/env python3
"""Validate every run and artifact declared by a frozen IP&M test protocol."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv_ipm.run_registry import sha256_file, tree_fingerprint  # noqa: E402


DERIVED_OUTPUTS = {
    "answer_grid_bootstrap": "answer_grid_bootstrap.json",
    "safety_gate_evaluation": "frozen_safety_gate_test_report.json",
    "frontier_selector_evaluation": "frozen_frontier_selector_test_report.json",
    "frontier_selector_bootstrap": "frontier_selector_bootstrap.json",
    "query_attention_bootstrap": "query_attention_bootstrap.json",
    "cross_model_answer_grid_bootstrap": "answer_grid_bootstrap.json",
    "cross_model_frontier_selector_evaluation": (
        "frozen_frontier_selector_test_report.json"
    ),
    "cross_model_frontier_selector_bootstrap": "frontier_selector_bootstrap.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def validate_answer(run_dir: Path, expected_examples: int, methods: list[str]) -> dict:
    output = run_dir / "answer_eval_outputs.jsonl"
    summary_path = run_dir / "answer_eval_summary.json"
    require_file(output)
    require_file(summary_path)
    rows = read_jsonl(output)
    keys = {(str(row["example_id"]), str(row["method"])) for row in rows}
    if len(rows) != expected_examples * len(methods) or len(keys) != len(rows):
        raise ValueError(f"incomplete/duplicate answer grid: {run_dir}")
    if {str(row["method"]) for row in rows} != set(methods):
        raise ValueError(f"answer method contract differs: {run_dir}")
    for row in rows:
        context = int(row["context_token_count"])
        online = int(row["online_context_prefill_token_count"])
        fraction = float(row["online_context_prefill_fraction"])
        if context <= 0 or not 0 <= online <= context or abs(fraction - online / context) > 1e-12:
            raise ValueError(f"invalid online compute accounting: {run_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if int(summary.get("num_failed_rows", -1)) != 0:
        raise ValueError(f"answer evaluator recorded failures: {run_dir}")
    return {"rows": len(rows), "outputs_sha256": sha256_file(output)}


def validate_frontier(run_dir: Path, expected_examples: int) -> dict:
    output = run_dir / "frontier_outputs.jsonl"
    require_file(output)
    rows = read_jsonl(output)
    if len(rows) != expected_examples:
        raise ValueError(f"frontier row count differs: {run_dir}")
    for row in rows:
        count = int(row["num_documents"])
        starts = list(row["suffix_starts"]) + [row["no_repair"]]
        if sorted(int(item["start"]) for item in starts) != list(range(count + 1)):
            raise ValueError(f"incomplete frontier starts: {run_dir}")
    return {"rows": len(rows), "outputs_sha256": sha256_file(output)}


def validate_attention(
    run_dir: Path,
    expected_examples: int,
    budgets: list[float],
    random_seeds: list[int],
) -> dict:
    output = run_dir / "query_attention_local_outputs.jsonl"
    summary_path = run_dir / "query_attention_local_summary.json"
    require_file(output)
    require_file(summary_path)
    rows = read_jsonl(output)
    methods_per_example = 2 + len(budgets) * (1 + len(random_seeds))
    keys = {(str(row["example_id"]), str(row["method"])) for row in rows}
    if len(rows) != expected_examples * methods_per_example or len(keys) != len(rows):
        raise ValueError(f"incomplete/duplicate attention grid: {run_dir}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("official_cache_craft_implementation") is not False:
        raise ValueError(f"attention baseline mislabeled as official: {run_dir}")
    return {"rows": len(rows), "outputs_sha256": sha256_file(output)}


def validate_scaling(run_dir: Path) -> dict:
    summary_path = run_dir / "system_scaling_summary.json"
    trace_path = run_dir / "system_scaling_trace.csv"
    failures_path = run_dir / "system_scaling_failures.jsonl"
    for path in (summary_path, trace_path, failures_path):
        require_file(path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with trace_path.open(encoding="utf-8", newline="") as handle:
        trace_rows = list(csv.DictReader(handle))
    failures = read_jsonl(failures_path)
    if len(trace_rows) != int(summary["num_rows"]):
        raise ValueError("scaling trace count differs from summary")
    if len(failures) != int(summary["num_failures"]):
        raise ValueError("scaling failure count differs from summary")
    if not trace_rows:
        raise ValueError("scaling benchmark produced no successful measurements")
    return {
        "rows": len(trace_rows),
        "failures": len(failures),
        "summary_sha256": sha256_file(summary_path),
    }


def main() -> None:
    args = parse_args()
    protocol_path = args.protocol.resolve()
    registry = args.registry_dir.resolve()
    code_root = args.code_root.resolve()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite validation report: {out}")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    for item in protocol["fixed_inputs"]:
        path = Path(item["path"])
        require_file(path)
        if sha256_file(path) != item["sha256"]:
            raise ValueError(f"frozen input changed: {path}")
    current_code = tree_fingerprint(code_root)
    if current_code["sha256"] != protocol["code"]["sha256"]:
        raise ValueError("code tree differs from frozen protocol")

    methods = list(protocol["answer_evaluation"]["methods"])
    main_answer_n = int(protocol["answer_evaluation"]["examples_per_cell"])
    transfer_answer_n = int(protocol["cross_model_transfer"]["answer_examples_per_cell"])
    main_frontier_n = int(protocol["frontier_evaluation"]["examples_per_cell"])
    transfer_frontier_n = int(protocol["cross_model_transfer"]["frontier_examples_per_cell"])
    attention = protocol["query_attention_local_baseline"]
    results = []
    for target in protocol["target_runs"]:
        kind = str(target["kind"])
        run_id = str(target["run_id"])
        run_dir = registry / run_id
        manifest_path = run_dir / "run_manifest.json"
        require_file(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
            raise ValueError(f"target run is not successful: {run_id}")
        if manifest.get("code", {}).get("sha256") != protocol["code"]["sha256"]:
            raise ValueError(f"target used another code snapshot: {run_id}")
        if kind == "answer":
            detail = validate_answer(run_dir, main_answer_n, methods)
        elif kind == "cross_model_answer":
            detail = validate_answer(run_dir, transfer_answer_n, methods)
        elif kind == "frontier":
            detail = validate_frontier(run_dir, main_frontier_n)
        elif kind == "cross_model_frontier":
            detail = validate_frontier(run_dir, transfer_frontier_n)
        elif kind == "attention":
            detail = validate_attention(
                run_dir,
                int(attention["examples_per_cell"]),
                list(attention["budgets"]),
                list(attention["random_seeds"]),
            )
        elif kind == "system_scaling":
            detail = validate_scaling(run_dir)
        elif kind in DERIVED_OUTPUTS:
            output = run_dir / DERIVED_OUTPUTS[kind]
            require_file(output)
            json.loads(output.read_text(encoding="utf-8"))
            detail = {"output": str(output), "output_sha256": sha256_file(output)}
        else:
            raise ValueError(f"unknown frozen target kind: {kind}")
        results.append(
            {
                "kind": kind,
                "run_id": run_id,
                "run_manifest_sha256": sha256_file(manifest_path),
                **detail,
            }
        )
    report = {
        "schema_version": 1,
        "status": "PASS",
        "protocol": {"path": str(protocol_path), "sha256": sha256_file(protocol_path)},
        "code_sha256": current_code["sha256"],
        "target_runs": results,
        "integrity": {
            "all_fixed_inputs_unchanged": True,
            "all_runs_used_frozen_code": True,
            "all_target_runs_completed": True,
            "all_outputs_complete": True,
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "target_runs": len(results)}, indent=2))


if __name__ == "__main__":
    main()
