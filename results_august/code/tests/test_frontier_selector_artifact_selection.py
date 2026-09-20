import json
from pathlib import Path

import pytest

from scripts.select_frontier_selector_artifact import _candidate_row, _signature, selection_key


def artifact(c: float, saving: float, unsafe_rate: float = 0.0) -> dict:
    return {
        "type": "linear_logistic_executable_suffix_frontier_selector",
        "feature_contract": {"names": ["x"]},
        "threshold_selection": {"minimum_dataset_lower_bound": 0.95},
        "split": {"seed": 1},
        "sources": [{"dataset": "d"}],
        "model": {"regularization_c": c},
        "threshold": 0.1,
        "report": {
            "n_candidates": 10,
            "n_train_candidates": 7,
            "n_validation_candidates": 3,
            "validation_candidate_classifier": {"auroc": 0.7},
            "validation_policy": {
                "overall": {
                    "mean_saved_context_ratio": saving,
                    "answer_preservation": 1.0 - unsafe_rate,
                    "unsafe_selected_rate": unsafe_rate,
                    "full_prefill_fallback_rate": 0.5,
                },
                "by_dataset": {
                    "d": {"answer_preservation_wilson95_low": 0.96}
                },
            },
        },
        "integrity": {"test_set_used": False},
    }


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_selection_prioritizes_utility_then_safety_then_stronger_regularization(tmp_path):
    paths = [tmp_path / name for name in ("a.json", "b.json", "c.json")]
    values = [artifact(0.1, 0.2), artifact(1.0, 0.3, 0.01), artifact(10.0, 0.3, 0.02)]
    for path, value in zip(paths, values):
        write(path, value)
    rows = [_candidate_row(path, value) for path, value in zip(paths, values)]
    assert max(rows, key=selection_key)["regularization_c"] == 1.0

    tied = [artifact(0.1, 0.3), artifact(1.0, 0.3)]
    tied_paths = [tmp_path / "d.json", tmp_path / "e.json"]
    for path, value in zip(tied_paths, tied):
        write(path, value)
    tied_rows = [
        _candidate_row(path, value) for path, value in zip(tied_paths, tied)
    ]
    assert max(tied_rows, key=selection_key)["regularization_c"] == 0.1


def test_candidate_rejects_test_use_or_failed_gate(tmp_path):
    path = tmp_path / "candidate.json"
    value = artifact(1.0, 0.2)
    write(path, value)
    value["integrity"]["test_set_used"] = True
    with pytest.raises(ValueError, match="calibration-only"):
        _candidate_row(path, value)

    value = artifact(1.0, 0.2)
    value["report"]["validation_policy"]["by_dataset"]["d"][
        "answer_preservation_wilson95_low"
    ] = 0.94
    with pytest.raises(ValueError, match="quality gate"):
        _candidate_row(path, value)


def test_signature_detects_protocol_drift():
    left = artifact(0.1, 0.2)
    right = artifact(1.0, 0.2)
    assert _signature(left) == _signature(right)
    right["split"] = {"seed": 2}
    assert _signature(left) != _signature(right)
