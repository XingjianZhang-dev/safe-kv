#!/usr/bin/env python
"""Calibration-only leave-one-feature-out analysis for the frozen safety gate."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import (  # noqa: E402
    FEATURE_NAMES,
    GateRecord,
    choose_max_coverage_threshold,
    predict_unsafe_probability,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--audit-rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def classification_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    return {
        "auroc": float(roc_auc_score(labels, probabilities)),
        "auprc": float(average_precision_score(labels, probabilities)),
        "brier": float(brier_score_loss(labels, probabilities)),
    }


def fit_probabilities(
    train_x: np.ndarray,
    train_y: np.ndarray,
    validation_x: np.ndarray,
    *,
    indices: list[int],
    artifact: dict[str, Any],
) -> np.ndarray:
    selected_train = train_x[:, indices]
    selected_validation = validation_x[:, indices]
    means = selected_train.mean(axis=0)
    scales = selected_train.std(axis=0)
    scales[scales < 1e-12] = 1.0
    frozen = artifact["model"]
    classifier = LogisticRegression(
        C=float(frozen["regularization_c"]),
        class_weight=frozen["class_weight"],
        solver=frozen["solver"],
        max_iter=int(frozen["max_iter"]),
        random_state=int(artifact["split"]["seed"]),
    )
    classifier.fit((selected_train - means) / scales, train_y)
    return predict_unsafe_probability(
        selected_validation,
        means=means,
        scales=scales,
        coefficients=classifier.coef_[0],
        intercept=float(classifier.intercept_[0]),
    )


def main() -> None:
    args = parse_args()
    artifact_path = args.artifact.resolve()
    audit_path = args.audit_rows.resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact["feature_contract"]["names"] != list(FEATURE_NAMES):
        raise ValueError("frozen artifact feature order differs from executable contract")
    if artifact["audit_rows"]["sha256"] != sha256_file(audit_path):
        raise ValueError("calibration audit rows do not match frozen artifact")
    if artifact["integrity"]["test_set_used"] is not False:
        raise ValueError("feature ablation must not use test data")

    rows = read_jsonl(audit_path)
    records = [
        GateRecord(
            example_id=str(row["example_id"]),
            group_id=str(row["group_id"]),
            dataset=str(row["dataset"]),
            condition=str(row["condition"]),
            unsafe=bool(row["unsafe_label"]),
            changed_and_gold_wrong=bool(row["changed_and_gold_wrong_label"]),
            features=tuple(float(row["features"][name]) for name in FEATURE_NAMES),
        )
        for row in rows
    ]
    train_indices = [index for index, row in enumerate(rows) if row["split"] == "train"]
    validation_indices = [
        index for index, row in enumerate(rows) if row["split"] == "validation"
    ]
    if len(train_indices) != artifact["report"]["n_train_records"]:
        raise ValueError("training split size differs from frozen artifact")
    if len(validation_indices) != artifact["report"]["n_validation_records"]:
        raise ValueError("validation split size differs from frozen artifact")
    all_x = np.asarray([record.features for record in records], dtype=np.float64)
    all_y = np.asarray([record.unsafe for record in records], dtype=np.int64)
    train_x = all_x[train_indices]
    train_y = all_y[train_indices]
    validation_x = all_x[validation_indices]
    validation_y = all_y[validation_indices]
    validation_records = [records[index] for index in validation_indices]
    minimum = float(
        artifact["threshold_selection"]["minimum_dataset_lower_bound"]
    )

    frozen = artifact["model"]
    full_probabilities = predict_unsafe_probability(
        validation_x,
        means=frozen["means"],
        scales=frozen["scales"],
        coefficients=frozen["coefficients"],
        intercept=frozen["intercept"],
    )
    full_threshold, full_policy = choose_max_coverage_threshold(
        validation_records,
        full_probabilities,
        minimum_dataset_lower_bound=minimum,
    )
    if abs(full_threshold - float(artifact["threshold"])) > 1e-12:
        raise ValueError("recomputed full-feature threshold differs from frozen artifact")
    full_metrics = classification_metrics(validation_y, full_probabilities)
    full_reuse = float(full_policy["overall"]["reuse_rate"])

    output_rows: list[dict[str, Any]] = []
    all_feature_indices = list(range(len(FEATURE_NAMES)))
    variants = [("full", None, all_feature_indices)] + [
        (
            "leave_one_feature_out",
            omitted,
            [index for index in all_feature_indices if index != omitted_index],
        )
        for omitted_index, omitted in enumerate(FEATURE_NAMES)
    ]
    for variant, omitted, feature_indices in variants:
        if variant == "full":
            probabilities = full_probabilities
            threshold = full_threshold
            policy = full_policy
        else:
            probabilities = fit_probabilities(
                train_x,
                train_y,
                validation_x,
                indices=feature_indices,
                artifact=artifact,
            )
            threshold, policy = choose_max_coverage_threshold(
                validation_records,
                probabilities,
                minimum_dataset_lower_bound=minimum,
            )
        metrics = classification_metrics(validation_y, probabilities)
        dataset_lows = {
            dataset: values["answer_preservation_wilson95_low"]
            for dataset, values in policy["by_dataset"].items()
        }
        output_rows.append(
            {
                "variant": variant,
                "omitted_feature": omitted or "",
                "n_features": len(feature_indices),
                "validation_auroc": metrics["auroc"],
                "validation_auprc": metrics["auprc"],
                "validation_brier": metrics["brier"],
                "delta_auroc_vs_full": metrics["auroc"] - full_metrics["auroc"],
                "delta_auprc_vs_full": metrics["auprc"] - full_metrics["auprc"],
                "threshold": float(threshold),
                "reuse_rate": float(policy["overall"]["reuse_rate"]),
                "delta_reuse_rate_vs_full": float(policy["overall"]["reuse_rate"])
                - full_reuse,
                "overall_answer_preservation": float(
                    policy["overall"]["answer_preservation"]
                ),
                "minimum_dataset_wilson95_low": float(min(dataset_lows.values())),
                "unsafe_reuse_count": int(policy["overall"]["unsafe_reuse_count"]),
                "changed_and_gold_wrong_count": int(
                    policy["overall"]["changed_and_gold_wrong_count"]
                ),
            }
        )

    report = {
        "schema_version": 1,
        "scope": "calibration train/validation only; final test set unused",
        "ablation": "one logistic model refit after omitting each feature",
        "artifact": {"path": str(artifact_path), "sha256": sha256_file(artifact_path)},
        "audit_rows": {"path": str(audit_path), "sha256": sha256_file(audit_path)},
        "split_reused_exactly_from_frozen_artifact": True,
        "quality_constraint": {
            "metric": "per-dataset two-sided Wilson 95% lower answer-preservation bound",
            "minimum": minimum,
        },
        "rows": output_rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists() or args.csv.exists():
        raise FileExistsError("refusing to overwrite safety-gate ablation outputs")
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with args.csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    print(json.dumps({"rows": len(output_rows), "json": str(args.out), "csv": str(args.csv)}))


if __name__ == "__main__":
    main()
