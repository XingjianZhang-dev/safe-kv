#!/usr/bin/env python
"""Train and freeze a grouped, calibration-only executable suffix selector."""

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
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score  # noqa: E402

from safekv_ipm.frontier_selector import (  # noqa: E402
    FRONTIER_FEATURE_NAMES,
    FrontierCandidate,
    choose_frontier_threshold,
    frontier_feature_vector,
)
from safekv_ipm.run_registry import sha256_file  # noqa: E402
from safekv_ipm.safety_gate import (  # noqa: E402
    dataset_stratified_group_split,
    predict_unsafe_probability,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        metavar=("FRONTIER_RUN_DIR", "DATA_JSONL"),
        required=True,
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit-rows", type=Path, required=True)
    parser.add_argument("--validation-fraction", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--minimum-dataset-lower-bound", type=float, default=0.95)
    parser.add_argument("--regularization-c", type=float, default=1.0)
    parser.add_argument("--required-datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--required-conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--expected-examples-per-source", type=int, default=100)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_source(
    run_dir: Path,
    data_path: Path,
) -> tuple[list[FrontierCandidate], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    output_path = run_dir / "frontier_outputs.jsonl"
    run_manifest_path = run_dir / "run_manifest.json"
    frontier_manifest_path = run_dir / "frontier_manifest.json"
    for path in (output_path, run_manifest_path, frontier_manifest_path, data_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    if run_manifest.get("status") != "completed" or run_manifest.get("exit_code") != 0:
        raise ValueError(f"frontier source is not completed successfully: {run_dir}")
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
    # Frontier runs may intentionally scan a prefix of a larger, immutable
    # calibration file.  Restrict metadata lookup to exactly the persisted
    # frontier IDs while retaining the full data-file hash in provenance.
    data_by_id = {example_id: data_by_id[example_id] for example_id in frontier_by_id}

    candidates: list[FrontierCandidate] = []
    cell: tuple[str, str] | None = None
    for original_id in sorted(data_by_id):
        example = data_by_id[original_id]
        row = frontier_by_id[original_id]
        metadata = example["source_metadata"]
        if metadata.get("split") != "calibration":
            raise ValueError(f"refusing non-calibration frontier source: {original_id}")
        dataset = str(metadata["dataset"])
        condition = str(metadata["retrieval_condition"])
        source_id = str(metadata["source_id"])
        current_cell = (dataset, condition)
        if cell is None:
            cell = current_cell
        if cell != current_cell:
            raise ValueError(f"mixed dataset/condition in {data_path}")
        document_count = len(example["documents"])
        start_items = list(row["suffix_starts"]) + [row["no_repair"]]
        if sorted(int(item["start"]) for item in start_items) != list(
            range(document_count + 1)
        ):
            raise ValueError(f"incomplete frontier starts for {original_id}")
        record_id = f"{dataset}:{source_id}:{condition}"
        group_id = f"{dataset}:{source_id}"
        for item in start_items:
            start = int(item["start"])
            value = item.get("normalized_qa_equivalent")
            if value is None:
                raise ValueError(f"missing normalized frontier label for {original_id}/{start}")
            candidates.append(
                FrontierCandidate(
                    example_id=record_id,
                    group_id=group_id,
                    dataset=dataset,
                    condition=condition,
                    start=start,
                    num_documents=document_count,
                    unsafe=not bool(value),
                    patch_ratio=float(item["patch_ratio"]),
                    features=frontier_feature_vector(
                        example,
                        start=start,
                        prompt_length=int(row["prompt_length"]),
                    ),
                )
            )
    if cell is None:
        raise ValueError(f"empty frontier source: {run_dir}")
    source = {
        "dataset": cell[0],
        "condition": cell[1],
        "run_dir": str(run_dir),
        "run_manifest": {
            "path": str(run_manifest_path),
            "sha256": sha256_file(run_manifest_path),
        },
        "frontier_manifest": {
            "path": str(frontier_manifest_path),
            "sha256": sha256_file(frontier_manifest_path),
        },
        "frontier_outputs": {
            "path": str(output_path),
            "sha256": sha256_file(output_path),
        },
        "data": {"path": str(data_path), "sha256": sha256_file(data_path)},
        "n_examples": len(frontier_rows),
        "n_examples_in_data_file": len(data_rows),
        "n_candidates": len(candidates),
    }
    return candidates, source


def metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    return {
        "unsafe_prevalence": float(labels.mean()),
        "auroc": float(roc_auc_score(labels, probabilities)),
        "auprc": float(average_precision_score(labels, probabilities)),
        "brier": float(brier_score_loss(labels, probabilities)),
    }


def hash_groups(groups: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(groups)).encode()).hexdigest()


def main() -> None:
    args = parse_args()
    required_datasets = {item for item in args.required_datasets.split(",") if item}
    required_conditions = {item for item in args.required_conditions.split(",") if item}
    required_cells = {
        (dataset, condition)
        for dataset in required_datasets
        for condition in required_conditions
    }
    candidates: list[FrontierCandidate] = []
    sources = []
    observed_cells = set()
    for run_text, data_text in args.source:
        current, source = load_source(Path(run_text), Path(data_text))
        if source["n_examples"] != args.expected_examples_per_source:
            raise ValueError(
                f"expected {args.expected_examples_per_source} examples in {data_text}, "
                f"found {source['n_examples']}"
            )
        cell = (source["dataset"], source["condition"])
        if cell in observed_cells:
            raise ValueError(f"duplicate frontier cell: {cell}")
        observed_cells.add(cell)
        candidates.extend(current)
        sources.append(source)
    if observed_cells != required_cells:
        raise ValueError(
            f"frontier grid mismatch; missing={sorted(required_cells-observed_cells)}, "
            f"unexpected={sorted(observed_cells-required_cells)}"
        )

    conditions_by_group: dict[str, set[str]] = {}
    for candidate in candidates:
        conditions_by_group.setdefault(candidate.group_id, set()).add(candidate.condition)
    if any(conditions != required_conditions for conditions in conditions_by_group.values()):
        raise ValueError("source question does not have every retrieval condition")

    assignments = dataset_stratified_group_split(
        candidates,
        validation_fraction=args.validation_fraction,
        seed=args.seed,
    )
    train = [candidate for candidate in candidates if assignments[candidate.group_id] == "train"]
    validation = [
        candidate for candidate in candidates if assignments[candidate.group_id] == "validation"
    ]
    train_x = np.asarray([candidate.features for candidate in train], dtype=np.float64)
    train_y = np.asarray([candidate.unsafe for candidate in train], dtype=np.int64)
    validation_x = np.asarray(
        [candidate.features for candidate in validation], dtype=np.float64
    )
    validation_y = np.asarray(
        [candidate.unsafe for candidate in validation], dtype=np.int64
    )
    if set(train_y.tolist()) != {0, 1} or set(validation_y.tolist()) != {0, 1}:
        raise ValueError("train and validation candidate sets must contain both labels")
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
    threshold, validation_policy = choose_frontier_threshold(
        validation,
        validation_probabilities,
        minimum_dataset_lower_bound=args.minimum_dataset_lower_bound,
    )
    train_groups = sorted(group for group, split in assignments.items() if split == "train")
    validation_groups = sorted(
        group for group, split in assignments.items() if split == "validation"
    )
    artifact = {
        "schema_version": 1,
        "type": "linear_logistic_executable_suffix_frontier_selector",
        "decision_rule": (
            "score every document start and the no-repair start; choose the latest "
            "start whose predicted unsafe probability is at most the frozen threshold; "
            "fall back to full prefill when no start qualifies"
        ),
        "feature_contract": {
            "names": list(FRONTIER_FEATURE_NAMES),
            "allowed_inputs": [
                "question text",
                "document title/text and order",
                "retrieval scores",
                "pre-generation prompt length",
                "candidate suffix start",
            ],
            "forbidden_inputs": [
                "gold answer",
                "gold evidence labels",
                "full-prefill state/logits/answer",
                "observed frontier labels",
                "sampled mismatch mask",
            ],
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
            "split": "grouped validation only",
            "objective": "maximize mean saved context fraction",
            "constraint": "per-dataset two-sided Wilson 95% answer-preservation lower bound",
            "minimum_dataset_lower_bound": args.minimum_dataset_lower_bound,
        },
        "split": {
            "seed": args.seed,
            "validation_fraction": args.validation_fraction,
            "group_key": "dataset:source_id shared across retrieval conditions and starts",
            "n_train_groups": len(train_groups),
            "n_validation_groups": len(validation_groups),
            "train_groups_sha256": hash_groups(train_groups),
            "validation_groups_sha256": hash_groups(validation_groups),
            "train_groups": train_groups,
            "validation_groups": validation_groups,
        },
        "sources": sources,
        "report": {
            "n_candidates": len(candidates),
            "n_train_candidates": len(train),
            "n_validation_candidates": len(validation),
            "n_condition_examples": len({candidate.example_id for candidate in candidates}),
            "train_candidate_classifier": metrics(train_y, train_probabilities),
            "validation_candidate_classifier": metrics(
                validation_y, validation_probabilities
            ),
            "validation_policy": validation_policy,
        },
        "integrity": {
            "test_set_used": False,
            "gold_or_oracle_feature_used": False,
            "retrieval_conditions_and_candidate_starts_grouped_by_source_question": True,
        },
    }

    all_x = np.asarray([candidate.features for candidate in candidates], dtype=np.float64)
    all_probabilities = predict_unsafe_probability(
        all_x,
        means=means,
        scales=scales,
        coefficients=coefficients,
        intercept=intercept,
    )
    args.audit_rows.parent.mkdir(parents=True, exist_ok=True)
    if args.audit_rows.exists() or args.out.exists():
        raise FileExistsError("refusing to overwrite frontier selector artifacts")
    with args.audit_rows.open("w", encoding="utf-8", newline="\n") as handle:
        for candidate, probability in zip(candidates, all_probabilities):
            handle.write(
                json.dumps(
                    {
                        "example_id": candidate.example_id,
                        "group_id": candidate.group_id,
                        "dataset": candidate.dataset,
                        "condition": candidate.condition,
                        "split": assignments[candidate.group_id],
                        "start": candidate.start,
                        "num_documents": candidate.num_documents,
                        "unsafe_label": candidate.unsafe,
                        "patch_ratio": candidate.patch_ratio,
                        "predicted_unsafe_probability": float(probability),
                        "features": dict(zip(FRONTIER_FEATURE_NAMES, candidate.features)),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
    artifact["audit_rows"] = {
        "path": str(args.audit_rows.resolve()),
        "sha256": sha256_file(args.audit_rows),
        "n_rows": len(candidates),
    }
    args.out.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(artifact["report"], ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
