#!/usr/bin/env python
"""Evaluate a frozen suffix-frontier selector on untouched frontier scans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sklearn.metrics import average_precision_score, roc_auc_score  # noqa: E402

from safekv_ipm.frontier_selector import (  # noqa: E402
    FRONTIER_FEATURE_NAMES,
    FrontierCandidate,
    choose_frontier_actions,
    frontier_feature_vector,
    frontier_policy_summary,
)
from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import predict_unsafe_probability, wilson_interval  # noqa: E402


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
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--required-datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--required-conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--expected-examples-per-source", type=int, default=100)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def verify_declared_input(manifest: dict[str, Any], path: Path) -> None:
    expected = sha256_file(path)
    declared = [
        item
        for item in manifest.get("inputs", [])
        if Path(str(item.get("path", ""))).resolve() == path.resolve()
    ]
    if len(declared) != 1 or declared[0].get("sha256") != expected:
        raise ValueError(f"run manifest does not freeze current input hash: {path}")


def load_source(
    run_dir: Path,
    data_path: Path,
) -> tuple[list[FrontierCandidate], dict[str, dict[str, Any]], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    output_path = run_dir / "frontier_outputs.jsonl"
    run_manifest_path = run_dir / "run_manifest.json"
    frontier_manifest_path = run_dir / "frontier_manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    if run_manifest.get("status") != "completed" or run_manifest.get("exit_code") != 0:
        raise ValueError(f"test frontier source is incomplete: {run_dir}")
    verify_declared_input(run_manifest, data_path)
    data_rows = read_jsonl(data_path)
    data_by_id = {str(row["id"]): row for row in data_rows}
    frontier_rows = read_jsonl(output_path)
    frontier_by_id = {str(row["example_id"]): row for row in frontier_rows}
    if len(data_by_id) != len(data_rows) or len(frontier_by_id) != len(frontier_rows):
        raise ValueError("duplicate data/frontier example ids")
    unknown_frontier_ids = set(frontier_by_id) - set(data_by_id)
    if unknown_frontier_ids:
        raise ValueError(
            f"frontier IDs absent from data for {run_dir}: "
            f"{sorted(unknown_frontier_ids)[:5]}"
        )
    # Test scans may intentionally cover a frozen prefix of a larger sealed
    # test file.  Evaluate exactly the IDs materialized by the scan.
    data_by_id = {example_id: data_by_id[example_id] for example_id in frontier_by_id}

    candidates: list[FrontierCandidate] = []
    metadata_by_record: dict[str, dict[str, Any]] = {}
    cell: tuple[str, str] | None = None
    for original_id in sorted(data_by_id):
        example = data_by_id[original_id]
        row = frontier_by_id[original_id]
        metadata = example["source_metadata"]
        if metadata.get("split") != "test":
            raise ValueError(f"refusing non-test frontier input: {original_id}")
        dataset = str(metadata["dataset"])
        condition = str(metadata["retrieval_condition"])
        source_id = str(metadata["source_id"])
        current_cell = (dataset, condition)
        if cell is None:
            cell = current_cell
        if cell != current_cell:
            raise ValueError(f"mixed test cell in {data_path}")
        count = len(example["documents"])
        record_id = f"{dataset}:{source_id}:{condition}"
        group_id = f"{dataset}:{source_id}"
        items = list(row["suffix_starts"]) + [row["no_repair"]]
        if sorted(int(item["start"]) for item in items) != list(range(count + 1)):
            raise ValueError(f"incomplete frontier starts for {original_id}")
        safe_items = [item for item in items if item.get("normalized_qa_equivalent") is True]
        no_repair = next(item for item in items if int(item["start"]) == count)
        latest_safe = max((int(item["start"]) for item in safe_items), default=None)
        minimum_patch = min(
            (float(item["patch_ratio"]) for item in safe_items), default=None
        )
        metadata_by_record[record_id] = {
            "original_example_id": original_id,
            "source_id": source_id,
            "dataset": dataset,
            "condition": condition,
            "group_id": group_id,
            "latest_safe_start": latest_safe,
            "minimum_safe_patch_ratio": minimum_patch,
            "no_repair_answer_preserved": bool(
                no_repair.get("normalized_qa_equivalent") is True
            ),
            "num_documents": count,
        }
        for item in items:
            start = int(item["start"])
            candidates.append(
                FrontierCandidate(
                    example_id=record_id,
                    group_id=group_id,
                    dataset=dataset,
                    condition=condition,
                    start=start,
                    num_documents=count,
                    unsafe=not bool(item["normalized_qa_equivalent"]),
                    patch_ratio=float(item["patch_ratio"]),
                    features=frontier_feature_vector(
                        example,
                        start=start,
                        prompt_length=int(row["prompt_length"]),
                    ),
                )
            )
    if cell is None:
        raise ValueError(f"empty source: {run_dir}")
    source = {
        "dataset": cell[0],
        "condition": cell[1],
        "run_dir": str(run_dir),
        "run_manifest_sha256": sha256_file(run_manifest_path),
        "frontier_manifest_sha256": sha256_file(frontier_manifest_path),
        "frontier_outputs_sha256": sha256_file(output_path),
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "n_examples": len(frontier_rows),
        "n_examples_in_data_file": len(data_rows),
    }
    return candidates, metadata_by_record, source


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    preserved = sum(row["answer_preserved"] for row in rows)
    low, high = wilson_interval(preserved, len(rows))
    naive_preserved = sum(row["no_repair_answer_preserved"] for row in rows)
    safe_minimums = [
        row["minimum_safe_patch_ratio"]
        for row in rows
        if row["minimum_safe_patch_ratio"] is not None
    ]
    excess_values = [
        row["excess_recompute_vs_observed_min"]
        for row in rows
        if row["excess_recompute_vs_observed_min"] is not None
    ]
    return {
        "n": len(rows),
        "answer_preservation": preserved / len(rows),
        "answer_preservation_wilson95_low": low,
        "answer_preservation_wilson95_high": high,
        "no_repair_answer_preservation": naive_preserved / len(rows),
        "answer_preservation_delta_vs_no_repair": (
            preserved - naive_preserved
        )
        / len(rows),
        "full_prefill_fallback_rate": sum(row["full_prefill_fallback"] for row in rows)
        / len(rows),
        "unsafe_selected_rate": sum(row["unsafe_selected"] for row in rows) / len(rows),
        "frontier_exact_accuracy": sum(row["frontier_exact"] for row in rows) / len(rows),
        "frontier_within_one_conservative_accuracy": sum(
            row["frontier_within_one_conservative"] for row in rows
        )
        / len(rows),
        "mean_recomputed_context_ratio": float(
            np.mean([row["selected_recomputed_context_ratio"] for row in rows])
        ),
        "mean_excess_recompute_vs_observed_min": float(
            np.mean(excess_values)
        ) if excess_values else None,
        "observed_safe_frontier_available_rate": len(safe_minimums) / len(rows),
        "mean_observed_minimum_safe_recompute_ratio": (
            float(np.mean(safe_minimums)) if safe_minimums else None
        ),
    }


def main() -> None:
    args = parse_args()
    artifact_path = args.artifact.resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact.get("type") != "linear_logistic_executable_suffix_frontier_selector":
        raise ValueError("unexpected frontier selector artifact type")
    if artifact["feature_contract"]["names"] != list(FRONTIER_FEATURE_NAMES):
        raise ValueError("frontier feature contract mismatch")
    if artifact["integrity"]["test_set_used"] is not False:
        raise ValueError("artifact does not certify calibration-only fitting")
    calibration_groups = set(artifact["split"]["train_groups"]) | set(
        artifact["split"]["validation_groups"]
    )
    required_cells = {
        (dataset, condition)
        for dataset in filter(None, args.required_datasets.split(","))
        for condition in filter(None, args.required_conditions.split(","))
    }

    candidates: list[FrontierCandidate] = []
    metadata_by_record: dict[str, dict[str, Any]] = {}
    sources = []
    cells = set()
    for run_text, data_text in args.source:
        current, metadata, source = load_source(Path(run_text), Path(data_text))
        if source["n_examples"] != args.expected_examples_per_source:
            raise ValueError(
                f"expected {args.expected_examples_per_source} examples in {data_text}, "
                f"found {source['n_examples']}"
            )
        cell = (source["dataset"], source["condition"])
        if cell in cells:
            raise ValueError(f"duplicate test cell: {cell}")
        cells.add(cell)
        if any(item["group_id"] in calibration_groups for item in metadata.values()):
            raise ValueError(f"calibration/test source-question leakage in {cell}")
        candidates.extend(current)
        metadata_by_record.update(metadata)
        sources.append(source)
    if cells != required_cells:
        raise ValueError(
            f"test frontier grid mismatch; missing={sorted(required_cells-cells)}, "
            f"unexpected={sorted(cells-required_cells)}"
        )

    model = artifact["model"]
    feature_matrix = np.asarray(
        [candidate.features for candidate in candidates], dtype=np.float64
    )
    probabilities = predict_unsafe_probability(
        feature_matrix,
        means=model["means"],
        scales=model["scales"],
        coefficients=model["coefficients"],
        intercept=model["intercept"],
    )
    threshold = float(artifact["threshold"])
    actions = choose_frontier_actions(candidates, probabilities, threshold=threshold)
    rows = []
    for record_id, metadata in sorted(metadata_by_record.items()):
        action = actions[record_id]
        latest = metadata["latest_safe_start"]
        minimum_patch = metadata["minimum_safe_patch_ratio"]
        fallback = action is None
        selected_start = None if fallback else action.start
        selected_patch = 1.0 if fallback else action.patch_ratio
        safe = fallback or not action.unsafe
        exact = bool(not fallback and latest is not None and selected_start == latest)
        within_one = bool(
            not fallback
            and latest is not None
            and safe
            and selected_start <= latest
            and latest - selected_start <= 1
        )
        rows.append(
            {
                **metadata,
                "selected_start": selected_start,
                "full_prefill_fallback": fallback,
                "unsafe_selected": bool(not fallback and action.unsafe),
                "answer_preserved": safe,
                "selected_recomputed_context_ratio": selected_patch,
                "frontier_exact": exact,
                "frontier_within_one_conservative": within_one,
                "excess_recompute_vs_observed_min": (
                    selected_patch - minimum_patch if minimum_patch is not None else None
                ),
                "frozen_threshold": threshold,
            }
        )

    labels = np.asarray([candidate.unsafe for candidate in candidates], dtype=np.int64)
    policy = frontier_policy_summary(candidates, probabilities, threshold=threshold)
    by_cell = {}
    for dataset, condition in sorted(required_cells):
        subset = [
            row
            for row in rows
            if row["dataset"] == dataset and row["condition"] == condition
        ]
        by_cell[f"{dataset}/{condition}"] = summarize_rows(subset)
    overall = summarize_rows(rows)
    by_dataset = {
        dataset: summarize_rows([row for row in rows if row["dataset"] == dataset])
        for dataset in sorted({row["dataset"] for row in rows})
    }
    minimum = float(
        artifact["threshold_selection"]["minimum_dataset_lower_bound"]
    )
    report = {
        "schema_version": 1,
        "artifact": {"path": str(artifact_path), "sha256": sha256_file(artifact_path)},
        "threshold_frozen_from_calibration": threshold,
        "threshold_reoptimized_on_test": False,
        "sources": sources,
        "n_test_condition_examples": len(rows),
        "n_test_candidates": len(candidates),
        "candidate_classifier": {
            "unsafe_prevalence": float(labels.mean()),
            "auroc": float(roc_auc_score(labels, probabilities)),
            "auprc": float(average_precision_score(labels, probabilities)),
        },
        "policy_crosscheck": policy,
        "overall": overall,
        "by_dataset": by_dataset,
        "by_dataset_and_condition": by_cell,
        "quality_gate": {
            "required_dataset_wilson95_lower_bound": minimum,
            "passed": all(
                values["answer_preservation_wilson95_low"] >= minimum
                for values in by_dataset.values()
            ),
        },
        "integrity": {
            "all_inputs_are_test_split": True,
            "calibration_test_group_overlap_count": 0,
            "complete_required_grid": True,
        },
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.out_dir / "frozen_frontier_selector_test_outputs.jsonl"
    report_path = args.out_dir / "frozen_frontier_selector_test_report.json"
    if output_path.exists() or report_path.exists():
        raise FileExistsError("refusing to overwrite frontier test outputs")
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    report["outputs"] = {
        "path": str(output_path.resolve()),
        "sha256": sha256_file(output_path),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"overall": overall, "quality_gate": report["quality_gate"]}, indent=2))


if __name__ == "__main__":
    main()
