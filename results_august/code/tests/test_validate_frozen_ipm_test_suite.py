import json

import pytest

from scripts.validate_frozen_ipm_test_suite import validate_answer


def write_answer_run(path, rows):
    path.mkdir()
    (path / "answer_eval_outputs.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    (path / "answer_eval_summary.json").write_text(
        json.dumps({"num_failed_rows": 0}), encoding="utf-8"
    )


def test_validate_answer_checks_explicit_online_compute_accounting(tmp_path):
    run = tmp_path / "run"
    rows = [
        {
            "example_id": "e1",
            "method": "full_prefill",
            "context_token_count": 10,
            "online_context_prefill_token_count": 10,
            "online_context_prefill_fraction": 1.0,
        },
        {
            "example_id": "e1",
            "method": "exact_prefix_reuse",
            "context_token_count": 10,
            "online_context_prefill_token_count": 0,
            "online_context_prefill_fraction": 0.0,
        },
    ]
    write_answer_run(run, rows)

    result = validate_answer(run, 1, ["full_prefill", "exact_prefix_reuse"])

    assert result["rows"] == 2


def test_validate_answer_rejects_inconsistent_online_fraction(tmp_path):
    run = tmp_path / "run"
    write_answer_run(
        run,
        [
            {
                "example_id": "e1",
                "method": "full_prefill",
                "context_token_count": 10,
                "online_context_prefill_token_count": 10,
                "online_context_prefill_fraction": 0.0,
            }
        ],
    )

    with pytest.raises(ValueError, match="online compute accounting"):
        validate_answer(run, 1, ["full_prefill"])
