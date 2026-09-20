import json
import sys

from scripts import validate_donor_actual_reconciliation as validator


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )


def answer_row(method, *, selected_doc_ids, patched_token_count):
    ratio = patched_token_count / 8
    return {
        "example_id": "example-0",
        "method": method,
        "generated_answer": "answer",
        "full_prefill_answer": "answer",
        "normalized_generated_answer": "answer",
        "normalized_full_prefill_answer": "answer",
        "answer_equivalence_to_full_prefill": True,
        "patched_doc_count": len(selected_doc_ids),
        "patched_token_count": patched_token_count,
        "patched_token_ratio": ratio,
        "first_token_kl_full_to_method": 0.0,
        "prompt_length": 10,
        "query_length": 2,
        "selected_doc_ids": selected_doc_ids,
        "generated_token_ids": [7],
        "full_prefill_token_ids": [7],
    }


def test_validator_allows_explicit_full_prefill_reference_rows(tmp_path, monkeypatch):
    data_path = tmp_path / "data.jsonl"
    config_path = tmp_path / "config.yaml"
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    write_jsonl(
        data_path,
        [
            {
                "id": "example-0",
                "documents": [
                    {"doc_id": 0, "title": "a", "text": "a"},
                    {"doc_id": 1, "title": "b", "text": "b"},
                ],
            }
        ],
    )
    config_path.write_text("seed: 13\n", encoding="utf-8")
    methods = [
        "full_prefill",
        "risk_guided_suffix_closure_k1",
        "actual_recompute::risk_guided_suffix_closure_k1",
    ]
    rows = [
        answer_row("full_prefill", selected_doc_ids=[], patched_token_count=0),
        answer_row(
            "risk_guided_suffix_closure_k1",
            selected_doc_ids=[1],
            patched_token_count=4,
        ),
        answer_row(
            "actual_recompute::risk_guided_suffix_closure_k1",
            selected_doc_ids=[1],
            patched_token_count=4,
        ),
    ]
    write_jsonl(results_dir / "answer_eval_outputs.jsonl", rows)
    (results_dir / "answer_eval_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 4,
                "data_path": str(data_path),
                "data_sha256": validator.file_sha256(data_path),
                "config_path": str(config_path),
                "config_sha256": validator.file_sha256(config_path),
                "max_examples": 1,
                "methods": methods,
                "implementation_sha256": {"runner": "hash"},
                "model_commit_hash": "commit",
            }
        ),
        encoding="utf-8",
    )
    (results_dir / "answer_eval_summary.json").write_text(
        json.dumps({"num_rows": 3, "num_failed_rows": 0, "failed_rows": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_donor_actual_reconciliation.py",
            "--results-dir",
            str(results_dir),
            "--expected-examples",
            "1",
        ],
    )

    validator.main()
    report = json.loads(
        (results_dir / "donor_actual_reconciliation.json").read_text()
    )
    assert report["status"] == "PASS"
    assert report["expected_rows"] == 3
    assert report["reference_methods"] == ["full_prefill"]
