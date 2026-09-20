#!/usr/bin/env python
"""Apply a frozen calibration-only safety gate to untouched test outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import (  # noqa: E402
    FEATURE_NAMES,
    GateRecord,
    policy_summary,
    predict_unsafe_probability,
    runtime_feature_vector,
)


EXPECTED_METHODS = {"full_prefill", "prefix_conditioned_naive_global"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        metavar=("RUN_DIR", "DATA_JSONL"),
        required=True,
    )
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--required-datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--required-conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--expected-examples-per-source", type=int, default=500)
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {error}") from error
            if not isinstance(row, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(row)
    return rows


def _verify_declared_input(manifest: dict[str, Any], path: Path) -> None:
    expected = sha256_file(path)
    declared = [
        item
        for item in manifest.get("inputs", [])
        if Path(str(item.get("path", ""))).resolve() == path.resolve()
    ]
    if len(declared) != 1 or declared[0].get("sha256") != expected:
        raise ValueError(f"run manifest does not freeze current input hash: {path}")


def _load_test_source(
    run_dir: Path,
    data_path: Path,
) -> tuple[list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    output_path = run_dir / "answer_eval_outputs.jsonl"
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        raise ValueError(f"source run is not completed successfully: {run_dir}")
    _verify_declared_input(manifest, data_path)
    data_rows = _read_jsonl(data_path)
    data_by_id = {str(row["id"]): row for row in data_rows}
    if len(data_by_id) != len(data_rows):
        raise ValueError(f"duplicate ids in {data_path}")
    evaluations = _read_jsonl(output_path)
    eval_by_id: dict[str, dict[str, dict[str, Any]]] = {}
    ignored_methods = set()
    for row in evaluations:
        example_id = str(row.get("example_id", ""))
        method = str(row.get("method", ""))
        if method not in EXPECTED_METHODS:
            ignored_methods.add(method)
            continue
        if method in eval_by_id.setdefault(example_id, {}):
            raise ValueError(f"duplicate {method} row for {example_id}")
        eval_by_id[example_id][method] = row
    if set(eval_by_id) != set(data_by_id):
        raise ValueError(f"data/output id mismatch for {run_dir}")

    pairs = []
    for example_id in sorted(data_by_id):
        example = data_by_id[example_id]
        methods = eval_by_id[example_id]
        if set(methods) != EXPECTED_METHODS:
            raise ValueError(f"incomplete method pair for {example_id}")
        metadata = example.get("source_metadata", {})
        if metadata.get("split") != "test":
            raise ValueError(f"refusing non-test input during frozen gate evaluation: {example_id}")
        full = methods["full_prefill"]
        naive = methods["prefix_conditioned_naive_global"]
        if not full.get("answer_equivalence_to_full_prefill"):
            raise ValueError(f"full-prefill self-equivalence failed for {example_id}")
        if int(full["prompt_length"]) != int(naive["prompt_length"]):
            raise ValueError(f"prompt length differs within pair for {example_id}")
        pairs.append((example, full, naive))
    source = {
        "run_dir": str(run_dir),
        "run_manifest_sha256": sha256_file(manifest_path),
        "answer_outputs_sha256": sha256_file(output_path),
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "n_examples": len(pairs),
        "evaluated_methods": sorted(EXPECTED_METHODS),
        "ignored_additional_methods": sorted(ignored_methods),
    }
    return pairs, source


def evaluate(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    artifact_path = args.artifact.resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact.get("type") != "linear_logistic_unsafe_reuse_gate":
        raise ValueError("unexpected gate artifact type")
    if artifact.get("feature_contract", {}).get("names") != list(FEATURE_NAMES):
        raise ValueError("feature contract differs from the frozen artifact")
    if artifact.get("integrity", {}).get("test_set_used") is not False:
        raise ValueError("artifact does not certify calibration-only fitting")
    threshold = float(artifact["threshold"])
    model = artifact["model"]

    required_datasets = {
        item.strip() for item in args.required_datasets.split(",") if item.strip()
    }
    required_conditions = {
        item.strip() for item in args.required_conditions.split(",") if item.strip()
    }
    required_pairs = {
        (dataset, condition)
        for dataset in required_datasets
        for condition in required_conditions
    }
    calibration_groups = set(artifact.get("split", {}).get("train_groups", [])) | set(
        artifact.get("split", {}).get("validation_groups", [])
    )

    source_reports = []
    source_cells = set()
    raw: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for run_text, data_text in args.source:
        pairs, source = _load_test_source(Path(run_text), Path(data_text))
        if len(pairs) != args.expected_examples_per_source:
            raise ValueError(
                f"expected {args.expected_examples_per_source} examples in {data_text}, "
                f"found {len(pairs)}"
            )
        metadata = pairs[0][0]["source_metadata"]
        cell = (str(metadata["dataset"]), str(metadata["retrieval_condition"]))
        if cell in source_cells:
            raise ValueError(f"duplicate test cell: {cell}")
        source_cells.add(cell)
        source["dataset"] = cell[0]
        source["condition"] = cell[1]
        source_reports.append(source)
        for example, full, naive in pairs:
            current = example["source_metadata"]
            if (str(current["dataset"]), str(current["retrieval_condition"])) != cell:
                raise ValueError(f"mixed cells within source {data_text}")
            group_id = f"{current['dataset']}:{current['source_id']}"
            if group_id in calibration_groups:
                raise ValueError(f"calibration/test source-question leakage: {group_id}")
        raw.extend(pairs)
    if source_cells != required_pairs:
        raise ValueError(
            f"test grid mismatch; missing={sorted(required_pairs-source_cells)}, "
            f"unexpected={sorted(source_cells-required_pairs)}"
        )

    features = np.asarray(
        [
            runtime_feature_vector(example, prompt_length=int(naive["prompt_length"]))
            for example, _full, naive in raw
        ],
        dtype=np.float64,
    )
    probabilities = predict_unsafe_probability(
        features,
        means=model["means"],
        scales=model["scales"],
        coefficients=model["coefficients"],
        intercept=model["intercept"],
    )

    gate_records = []
    output_rows = []
    for (example, full, naive), probability in zip(raw, probabilities):
        metadata = example["source_metadata"]
        reuse = bool(probability <= threshold)
        selected = naive if reuse else full
        record = GateRecord(
            example_id=str(example["id"]),
            group_id=f"{metadata['dataset']}:{metadata['source_id']}",
            dataset=str(metadata["dataset"]),
            condition=str(metadata["retrieval_condition"]),
            unsafe=not bool(naive["answer_equivalence_to_full_prefill"]),
            changed_and_gold_wrong=bool(naive["answer_changed_and_gold_wrong"]),
            features=tuple(float(value) for value in runtime_feature_vector(
                example, prompt_length=int(naive["prompt_length"])
            )),
        )
        gate_records.append(record)
        row = dict(selected)
        row.update(
            {
                "method": "frozen_safety_gate_naive_or_full",
                "dataset": record.dataset,
                "retrieval_condition": record.condition,
                "gate_action": "naive_reuse" if reuse else "full_prefill_fallback",
                "gate_predicted_unsafe_probability": float(probability),
                "gate_threshold": threshold,
                "gate_artifact_sha256": sha256_file(artifact_path),
                "document_context_prefill_fraction": 0.0 if reuse else 1.0,
                "underlying_method": selected["method"],
            }
        )
        output_rows.append(row)

    summary = policy_summary(gate_records, probabilities, threshold=threshold)
    by_condition = {}
    for dataset, condition in sorted(required_pairs):
        indices = [
            index
            for index, record in enumerate(gate_records)
            if record.dataset == dataset and record.condition == condition
        ]
        subset_records = [gate_records[index] for index in indices]
        subset_probabilities = [float(probabilities[index]) for index in indices]
        by_condition[f"{dataset}/{condition}"] = policy_summary(
            subset_records,
            subset_probabilities,
            threshold=threshold,
        )["overall"]
    minimum = float(
        artifact["threshold_selection"]["minimum_dataset_lower_bound"]
    )
    quality_gate_passed = all(
        values["answer_preservation_wilson95_low"] >= minimum
        for values in summary["by_dataset"].values()
    )
    report = {
        "schema_version": 1,
        "artifact": {"path": str(artifact_path), "sha256": sha256_file(artifact_path)},
        "threshold_frozen_from_calibration": threshold,
        "threshold_reoptimized_on_test": False,
        "test_sources": source_reports,
        "n_test_records": len(gate_records),
        "policy": summary,
        "by_dataset_and_condition": by_condition,
        "quality_gate": {
            "required_dataset_wilson95_lower_bound": minimum,
            "passed": quality_gate_passed,
        },
        "integrity": {
            "all_inputs_are_test_split": True,
            "calibration_test_group_overlap_count": 0,
            "complete_required_grid": True,
        },
    }
    return output_rows, report


def main() -> None:
    args = parse_args()
    output_rows, report = evaluate(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.out_dir / "frozen_safety_gate_test_outputs.jsonl"
    report_path = args.out_dir / "frozen_safety_gate_test_report.json"
    if output_path.exists() or report_path.exists():
        raise FileExistsError("refusing to overwrite frozen safety-gate test results")
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in output_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    report["outputs"] = {
        "path": str(output_path.resolve()),
        "sha256": sha256_file(output_path),
        "n_rows": len(output_rows),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
