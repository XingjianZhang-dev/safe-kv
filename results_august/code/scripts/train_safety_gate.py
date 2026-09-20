#!/usr/bin/env python
"""Train and freeze a leakage-controlled full-prefill fallback gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
import sklearn  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)

from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import (  # noqa: E402
    FEATURE_DEFINITIONS,
    FEATURE_NAMES,
    GateRecord,
    choose_max_coverage_threshold,
    dataset_stratified_group_split,
    predict_unsafe_probability,
    runtime_feature_vector,
)


EXPECTED_METHODS = {"full_prefill", "prefix_conditioned_naive_global"}
FORBIDDEN_FEATURE_FIELDS = (
    "gold_answer",
    "normalized_gold_answer",
    "evidence",
    "role",
    "is_supporting",
    "conflicting_docs",
    "sampled_mismatch_mask",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        metavar=("RUN_DIR", "DATA_JSONL"),
        required=True,
        help="Repeat once per completed full-prefill/naive calibration run.",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit-rows", type=Path, required=True)
    parser.add_argument("--validation-fraction", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--minimum-dataset-lower-bound", type=float, default=0.95)
    parser.add_argument("--regularization-c", type=float, default=1.0)
    parser.add_argument("--required-datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--required-conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--expected-examples-per-source", type=int, default=300)
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


def _load_source(run_dir: Path, data_path: Path) -> tuple[list[GateRecord], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    output_path = run_dir / "answer_eval_outputs.jsonl"
    manifest_path = run_dir / "run_manifest.json"
    if not output_path.is_file() or not manifest_path.is_file() or not data_path.is_file():
        raise FileNotFoundError(f"incomplete declared source: {run_dir} / {data_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        raise ValueError(f"source run is not completed successfully: {run_dir}")

    data_rows = _read_jsonl(data_path)
    data_by_id = {str(row["id"]): row for row in data_rows}
    if len(data_by_id) != len(data_rows):
        raise ValueError(f"duplicate example ids in {data_path}")
    evaluations = _read_jsonl(output_path)
    by_id: dict[str, dict[str, dict[str, Any]]] = {}
    for row in evaluations:
        example_id = str(row.get("example_id", ""))
        method = str(row.get("method", ""))
        if method not in EXPECTED_METHODS:
            raise ValueError(f"unexpected method {method!r} in {output_path}")
        if method in by_id.setdefault(example_id, {}):
            raise ValueError(f"duplicate method {method} for {example_id}")
        by_id[example_id][method] = row
    if set(by_id) != set(data_by_id):
        missing = sorted(set(data_by_id) - set(by_id))[:3]
        extra = sorted(set(by_id) - set(data_by_id))[:3]
        raise ValueError(f"data/output id mismatch; missing={missing}, extra={extra}")

    records: list[GateRecord] = []
    for example_id in sorted(data_by_id):
        methods = by_id[example_id]
        if set(methods) != EXPECTED_METHODS:
            raise ValueError(f"incomplete method pair for {example_id}: {sorted(methods)}")
        full = methods["full_prefill"]
        naive = methods["prefix_conditioned_naive_global"]
        if not bool(full.get("answer_equivalence_to_full_prefill")):
            raise ValueError(f"full-prefill self-equivalence failed for {example_id}")
        if int(full["prompt_length"]) != int(naive["prompt_length"]):
            raise ValueError(f"prompt length differs within pair for {example_id}")
        example = data_by_id[example_id]
        metadata = example.get("source_metadata", {})
        dataset = str(metadata.get("dataset", ""))
        condition = str(metadata.get("retrieval_condition", ""))
        source_id = str(metadata.get("source_id", ""))
        split = str(metadata.get("split", ""))
        if not dataset or not condition or not source_id:
            raise ValueError(f"missing source metadata for {example_id}")
        if split != "calibration":
            raise ValueError(
                f"refusing non-calibration data for gate training: {example_id} has split={split!r}"
            )
        records.append(
            GateRecord(
                example_id=example_id,
                group_id=f"{dataset}:{source_id}",
                dataset=dataset,
                condition=condition,
                unsafe=not bool(naive["answer_equivalence_to_full_prefill"]),
                changed_and_gold_wrong=bool(naive["answer_changed_and_gold_wrong"]),
                features=runtime_feature_vector(example, prompt_length=int(naive["prompt_length"])),
            )
        )
    source = {
        "run_dir": str(run_dir),
        "run_manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)},
        "answer_outputs": {"path": str(output_path), "sha256": sha256_file(output_path)},
        "data": {"path": str(data_path), "sha256": sha256_file(data_path)},
        "n_examples": len(records),
    }
    return records, source


def _classification_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    if set(labels.tolist()) != {0, 1}:
        raise ValueError("classification metrics require both safe and unsafe examples")
    bins = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    for index in range(10):
        if index == 9:
            selected = (probabilities >= bins[index]) & (probabilities <= bins[index + 1])
        else:
            selected = (probabilities >= bins[index]) & (probabilities < bins[index + 1])
        if selected.any():
            ece += float(selected.mean()) * abs(
                float(probabilities[selected].mean()) - float(labels[selected].mean())
            )
    return {
        "unsafe_prevalence": float(labels.mean()),
        "auroc": float(roc_auc_score(labels, probabilities)),
        "auprc": float(average_precision_score(labels, probabilities)),
        "brier": float(brier_score_loss(labels, probabilities)),
        "ece_10_equal_width": ece,
    }


def _hash_groups(groups: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(groups)).encode("utf-8")).hexdigest()


def train(args: argparse.Namespace) -> dict[str, Any]:
    if args.regularization_c <= 0:
        raise ValueError("regularization C must be positive")
    all_records: list[GateRecord] = []
    sources = []
    for run_text, data_text in args.source:
        records, source = _load_source(Path(run_text), Path(data_text))
        if len(records) != args.expected_examples_per_source:
            raise ValueError(
                f"expected {args.expected_examples_per_source} examples in {data_text}, "
                f"found {len(records)}"
            )
        all_records.extend(records)
        sources.append(source)
    unique_keys = {(record.example_id, record.condition) for record in all_records}
    if len(unique_keys) != len(all_records):
        raise ValueError("duplicate example/condition records across declared sources")
    required_datasets = {
        item.strip() for item in args.required_datasets.split(",") if item.strip()
    }
    required_conditions = {
        item.strip() for item in args.required_conditions.split(",") if item.strip()
    }
    observed_pairs = {(record.dataset, record.condition) for record in all_records}
    required_pairs = {
        (dataset, condition)
        for dataset in required_datasets
        for condition in required_conditions
    }
    if observed_pairs != required_pairs:
        raise ValueError(
            "calibration grid is incomplete or has unexpected cells; "
            f"missing={sorted(required_pairs - observed_pairs)}, "
            f"unexpected={sorted(observed_pairs - required_pairs)}"
        )
    conditions_by_group: dict[str, set[str]] = {}
    for record in all_records:
        conditions_by_group.setdefault(record.group_id, set()).add(record.condition)
    incomplete_groups = {
        group: sorted(required_conditions - conditions)
        for group, conditions in conditions_by_group.items()
        if conditions != required_conditions
    }
    if incomplete_groups:
        sample = dict(list(sorted(incomplete_groups.items()))[:3])
        raise ValueError(f"source questions lack retrieval conditions: {sample}")

    assignments = dataset_stratified_group_split(
        all_records,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
    )
    train_records = [record for record in all_records if assignments[record.group_id] == "train"]
    validation_records = [
        record for record in all_records if assignments[record.group_id] == "validation"
    ]
    train_x = np.asarray([record.features for record in train_records], dtype=np.float64)
    train_y = np.asarray([record.unsafe for record in train_records], dtype=np.int64)
    validation_x = np.asarray([record.features for record in validation_records], dtype=np.float64)
    validation_y = np.asarray([record.unsafe for record in validation_records], dtype=np.int64)
    if set(train_y.tolist()) != {0, 1}:
        raise ValueError("training split must contain safe and unsafe examples")

    means = train_x.mean(axis=0)
    scales = train_x.std(axis=0)
    scales[scales < 1e-12] = 1.0
    classifier = LogisticRegression(
        C=args.regularization_c,
        class_weight="balanced",
        solver="lbfgs",
        max_iter=5000,
        random_state=args.seed,
    )
    classifier.fit((train_x - means) / scales, train_y)
    coefficients = classifier.coef_[0]
    intercept = float(classifier.intercept_[0])
    train_probabilities = predict_unsafe_probability(
        train_x,
        means=means,
        scales=scales,
        coefficients=coefficients,
        intercept=intercept,
    )
    validation_probabilities = predict_unsafe_probability(
        validation_x,
        means=means,
        scales=scales,
        coefficients=coefficients,
        intercept=intercept,
    )
    threshold, validation_policy = choose_max_coverage_threshold(
        validation_records,
        validation_probabilities,
        minimum_dataset_lower_bound=args.minimum_dataset_lower_bound,
    )

    train_groups = sorted(group for group, split in assignments.items() if split == "train")
    validation_groups = sorted(
        group for group, split in assignments.items() if split == "validation"
    )
    artifact: dict[str, Any] = {
        "schema_version": 1,
        "type": "linear_logistic_unsafe_reuse_gate",
        "decision_rule": "reuse naive non-prefix cache iff predicted_unsafe_probability <= threshold; otherwise full prefill",
        "feature_contract": {
            "names": list(FEATURE_NAMES),
            "definitions": [
                {"name": name, "definition": definition}
                for name, definition in FEATURE_DEFINITIONS
            ],
            "allowed_inputs": [
                "question text",
                "document title/text",
                "retrieval scores",
                "pre-generation prompt length",
            ],
            "forbidden_inputs": list(FORBIDDEN_FEATURE_FIELDS),
        },
        "model": {
            "implementation": "sklearn.linear_model.LogisticRegression",
            "sklearn_version": sklearn.__version__,
            "python_version": platform.python_version(),
            "regularization_c": args.regularization_c,
            "class_weight": "balanced",
            "solver": "lbfgs",
            "max_iter": 5000,
            "means": means.tolist(),
            "scales": scales.tolist(),
            "coefficients": coefficients.tolist(),
            "intercept": intercept,
        },
        "threshold": float(threshold),
        "threshold_selection": {
            "split": "validation only",
            "objective": "maximum reuse coverage",
            "constraint": "two-sided Wilson 95% lower answer-preservation bound on every dataset",
            "minimum_dataset_lower_bound": args.minimum_dataset_lower_bound,
        },
        "split": {
            "seed": args.seed,
            "validation_fraction": args.validation_fraction,
            "group_key": "dataset:source_id shared across retrieval conditions",
            "n_train_groups": len(train_groups),
            "n_validation_groups": len(validation_groups),
            "train_groups_sha256": _hash_groups(train_groups),
            "validation_groups_sha256": _hash_groups(validation_groups),
            "train_groups": train_groups,
            "validation_groups": validation_groups,
        },
        "sources": sources,
        "report": {
            "n_records": len(all_records),
            "n_train_records": len(train_records),
            "n_validation_records": len(validation_records),
            "train_classifier": _classification_metrics(train_y, train_probabilities),
            "validation_classifier": _classification_metrics(
                validation_y, validation_probabilities
            ),
            "validation_policy": validation_policy,
        },
        "integrity": {
            "test_set_used": False,
            "gold_or_evidence_feature_used": False,
            "retrieval_conditions_grouped_by_source_question": True,
            "expected_eval_methods": sorted(EXPECTED_METHODS),
        },
    }

    audit_rows = []
    all_x = np.asarray([record.features for record in all_records], dtype=np.float64)
    all_probabilities = predict_unsafe_probability(
        all_x,
        means=means,
        scales=scales,
        coefficients=coefficients,
        intercept=intercept,
    )
    for record, probability in zip(all_records, all_probabilities):
        split = assignments[record.group_id]
        audit_rows.append(
            {
                "example_id": record.example_id,
                "group_id": record.group_id,
                "dataset": record.dataset,
                "condition": record.condition,
                "split": split,
                "unsafe_label": record.unsafe,
                "changed_and_gold_wrong_label": record.changed_and_gold_wrong,
                "predicted_unsafe_probability": float(probability),
                "reuse_at_frozen_threshold": bool(probability <= threshold),
                "features": dict(zip(FEATURE_NAMES, record.features)),
            }
        )
    args.audit_rows.parent.mkdir(parents=True, exist_ok=True)
    with args.audit_rows.open("w", encoding="utf-8", newline="\n") as handle:
        for row in audit_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    artifact["audit_rows"] = {
        "path": str(args.audit_rows.resolve()),
        "sha256": sha256_file(args.audit_rows),
        "n_rows": len(audit_rows),
    }
    return artifact


def main() -> None:
    args = parse_args()
    artifact = train(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(artifact["report"], ensure_ascii=False, indent=2, sort_keys=True))
    print(f"Wrote frozen gate artifact to {args.out}")


if __name__ == "__main__":
    main()
