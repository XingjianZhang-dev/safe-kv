from __future__ import annotations

import json
from pathlib import Path

import pytest


pytest.importorskip("sklearn")

from scripts.evaluate_frozen_frontier_selector import load_source as load_test_source
from scripts.train_frontier_selector import load_source as load_calibration_source
from safekv_ipm.run_registry import sha256_file


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def example(example_id: str, split: str) -> dict:
    return {
        "id": example_id,
        "question": "Where was the event held?",
        "documents": [
            {
                "title": "Event",
                "text": "The event was held in Paris.",
                "retrieval_score": 0.8,
            }
        ],
        "source_metadata": {
            "split": split,
            "dataset": "hotpotqa",
            "retrieval_condition": "natural",
            "source_id": example_id,
        },
    }


def frontier_row(example_id: str) -> dict:
    return {
        "example_id": example_id,
        "prompt_length": 64,
        "suffix_starts": [
            {"start": 0, "normalized_qa_equivalent": True, "patch_ratio": 0.8}
        ],
        "no_repair": {
            "start": 1,
            "normalized_qa_equivalent": False,
            "patch_ratio": 0.0,
        },
    }


def source_files(tmp_path: Path, split: str) -> tuple[Path, Path]:
    run_dir = tmp_path / split
    run_dir.mkdir()
    data_path = tmp_path / f"{split}.jsonl"
    # The immutable data file is deliberately larger than the frontier scan.
    write_jsonl(data_path, [example("a", split), example("b", split)])
    write_jsonl(run_dir / "frontier_outputs.jsonl", [frontier_row("a")])
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "exit_code": 0,
                "inputs": [
                    {"path": str(data_path), "sha256": sha256_file(data_path)}
                ],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "frontier_manifest.json").write_text("{}", encoding="utf-8")
    return run_dir, data_path


def test_calibration_loader_accepts_frozen_prefix_scan(tmp_path: Path) -> None:
    run_dir, data_path = source_files(tmp_path, "calibration")
    candidates, source = load_calibration_source(run_dir, data_path)
    assert source["n_examples"] == 1
    assert source["n_examples_in_data_file"] == 2
    assert {candidate.example_id for candidate in candidates} == {
        "hotpotqa:a:natural"
    }
    assert {candidate.start for candidate in candidates} == {0, 1}


def test_test_loader_accepts_frozen_prefix_scan(tmp_path: Path) -> None:
    run_dir, data_path = source_files(tmp_path, "test")
    candidates, metadata, source = load_test_source(run_dir, data_path)
    assert source["n_examples"] == 1
    assert source["n_examples_in_data_file"] == 2
    assert set(metadata) == {"hotpotqa:a:natural"}
    assert {candidate.start for candidate in candidates} == {0, 1}


def test_loader_rejects_frontier_id_absent_from_data(tmp_path: Path) -> None:
    run_dir, data_path = source_files(tmp_path, "calibration")
    write_jsonl(run_dir / "frontier_outputs.jsonl", [frontier_row("unknown")])
    with pytest.raises(ValueError, match="absent from data"):
        load_calibration_source(run_dir, data_path)
