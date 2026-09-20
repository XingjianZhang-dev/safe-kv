import json

from scripts.run_query_attention_grid import completed_run_is_valid


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_completed_query_attention_grid_cell_validation(tmp_path):
    (tmp_path / "run_manifest.json").write_text(
        json.dumps({"status": "completed", "exit_code": 0}),
        encoding="utf-8",
    )
    (tmp_path / "query_attention_local_summary.json").write_text(
        "{}\n", encoding="utf-8"
    )
    template = {
        "qa_answer_equivalence_to_fresh_reference": True,
        "first_token_kl_to_fresh_reference": 0.0,
        "patched_context_ratio": 0.1,
        "selection_planning_seconds": 0.01,
        "selection_source": "stale_query_attention",
    }
    # Two references plus one attention and two random policies per budget.
    write_jsonl(
        tmp_path / "query_attention_local_outputs.jsonl",
        [dict(template, row=index) for index in range(2 * (2 + 2 * 3))],
    )

    assert completed_run_is_valid(
        tmp_path,
        expected_examples=2,
        expected_budgets=2,
        expected_random_seeds=2,
    )
    assert not completed_run_is_valid(
        tmp_path,
        expected_examples=3,
        expected_budgets=2,
        expected_random_seeds=2,
    )
