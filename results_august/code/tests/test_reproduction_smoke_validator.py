from __future__ import annotations

import json

from scripts.validate_reproduction_smoke import compare


def write_rows(path, rows):
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def row():
    return {
        "example_id": "example",
        "method": "method",
        "category": "test",
        "generated_answer": "a",
        "full_prefill_answer": "a",
        "normalized_generated_answer": "a",
        "normalized_full_prefill_answer": "a",
        "answer_equivalence_to_full_prefill": True,
        "top1_match": True,
        "patched_doc_count": 1,
        "patched_token_count": 2,
        "patched_token_ratio": 0.25,
        "prompt_length": 10,
        "query_length": 2,
        "selected_doc_ids": [1],
        "generated_token_ids": [3],
        "full_prefill_token_ids": [3],
        "first_token_kl_full_to_method": 0.001,
    }


def test_reproduction_validator_accepts_small_kl_drift(tmp_path):
    reference = tmp_path / "reference.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    expected = row()
    actual = row()
    actual["first_token_kl_full_to_method"] = 0.0011
    write_rows(reference, [expected])
    write_rows(candidate, [actual])

    assert compare(reference, candidate, kl_atol=0.0002)["status"] == "PASS"


def test_reproduction_validator_rejects_token_drift(tmp_path):
    reference = tmp_path / "reference.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    expected = row()
    actual = row()
    actual["generated_token_ids"] = [4]
    write_rows(reference, [expected])
    write_rows(candidate, [actual])

    report = compare(reference, candidate, kl_atol=0.0002)
    assert report["status"] == "FAIL"
    assert report["failures"][0]["field"] == "generated_token_ids"
