import json
from pathlib import Path

from scripts.evaluate_frozen_safety_gate import _load_test_source
from safekv_ipm.run_registry import sha256_file


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_gate_loader_ignores_declared_additional_answer_methods(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    data_path = tmp_path / "data.jsonl"
    write_jsonl(
        data_path,
        [
            {
                "id": "a",
                "source_metadata": {
                    "split": "test",
                    "dataset": "d",
                    "retrieval_condition": "natural",
                    "source_id": "source-a",
                },
            }
        ],
    )
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
    write_jsonl(
        run_dir / "answer_eval_outputs.jsonl",
        [
            {
                "example_id": "a",
                "method": "full_prefill",
                "answer_equivalence_to_full_prefill": True,
                "prompt_length": 10,
            },
            {
                "example_id": "a",
                "method": "prefix_conditioned_naive_global",
                "answer_equivalence_to_full_prefill": False,
                "prompt_length": 10,
            },
            {
                "example_id": "a",
                "method": "actual_recompute::frozen_frontier_selector",
                "answer_equivalence_to_full_prefill": True,
                "prompt_length": 10,
            },
        ],
    )

    pairs, source = _load_test_source(run_dir, data_path)

    assert len(pairs) == 1
    assert source["evaluated_methods"] == [
        "full_prefill",
        "prefix_conditioned_naive_global",
    ]
    assert source["ignored_additional_methods"] == [
        "actual_recompute::frozen_frontier_selector"
    ]
