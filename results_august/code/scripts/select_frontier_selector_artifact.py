#!/usr/bin/env python
"""Select one calibration-only frontier selector using a frozen rule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _signature(artifact: dict[str, Any]) -> dict[str, Any]:
    """Fields that must be identical for a fair candidate comparison."""

    return {
        "type": artifact["type"],
        "feature_contract": artifact["feature_contract"],
        "threshold_selection": artifact["threshold_selection"],
        "split": artifact["split"],
        "sources": artifact["sources"],
        "n_candidates": artifact["report"]["n_candidates"],
        "n_train_candidates": artifact["report"]["n_train_candidates"],
        "n_validation_candidates": artifact["report"]["n_validation_candidates"],
    }


def _candidate_row(path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["integrity"].get("test_set_used") is not False:
        raise ValueError(f"candidate does not certify calibration-only fitting: {path}")
    policy = artifact["report"]["validation_policy"]
    minimum = float(artifact["threshold_selection"]["minimum_dataset_lower_bound"])
    dataset_lows = {
        dataset: float(values["answer_preservation_wilson95_low"])
        for dataset, values in policy["by_dataset"].items()
    }
    passed = bool(dataset_lows) and min(dataset_lows.values()) >= minimum
    if not passed:
        raise ValueError(f"candidate violates its frozen validation quality gate: {path}")
    overall = policy["overall"]
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "regularization_c": float(artifact["model"]["regularization_c"]),
        "threshold": float(artifact["threshold"]),
        "mean_saved_context_ratio": float(overall["mean_saved_context_ratio"]),
        "answer_preservation": float(overall["answer_preservation"]),
        "unsafe_selected_rate": float(overall["unsafe_selected_rate"]),
        "full_prefill_fallback_rate": float(overall["full_prefill_fallback_rate"]),
        "minimum_dataset_wilson95_low": min(dataset_lows.values()),
        "validation_auroc": float(
            artifact["report"]["validation_candidate_classifier"]["auroc"]
        ),
        "quality_gate_passed": True,
    }


def selection_key(row: dict[str, Any]) -> tuple[float, float, float, str]:
    """Frozen order: utility, safety, stronger regularization, stable path."""

    return (
        row["mean_saved_context_ratio"],
        -row["unsafe_selected_rate"],
        -row["regularization_c"],
        row["path"],
    )


def main() -> None:
    args = parse_args()
    paths = [path.resolve() for path in args.candidate]
    if len(paths) < 2:
        raise ValueError("at least two candidate artifacts are required")
    if len(set(paths)) != len(paths):
        raise ValueError("candidate paths must be unique")
    artifacts = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    reference = _signature(artifacts[0])
    for path, artifact in zip(paths[1:], artifacts[1:]):
        if _signature(artifact) != reference:
            raise ValueError(f"candidate does not share the frozen comparison protocol: {path}")
    rows = [_candidate_row(path, artifact) for path, artifact in zip(paths, artifacts)]
    chosen = max(rows, key=selection_key)
    report = {
        "schema_version": 1,
        "scope": "calibration train/validation artifacts only; final test set unused",
        "selection_rule": [
            "require each candidate to pass the frozen per-dataset Wilson-95 quality gate",
            "maximize validation mean saved context ratio",
            "break exact ties by lower unsafe-selected rate",
            "then prefer the smaller C (stronger regularization)",
            "then use the absolute artifact path for deterministic ordering",
        ],
        "candidate_count": len(rows),
        "candidates": sorted(rows, key=lambda row: row["regularization_c"]),
        "selected": chosen,
        "integrity": {
            "test_set_used": False,
            "all_candidates_share_split_sources_features_and_gate": True,
        },
    }
    args.out = args.out.resolve()
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite selection report: {args.out}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
