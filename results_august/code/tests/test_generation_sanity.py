from safekv.generation_sanity import (
    category_counts,
    first_failed_check,
    first_token_mismatch,
    format_first_mismatch,
)


def test_first_token_mismatch_reports_index_and_tokens() -> None:
    mismatch = first_token_mismatch([1, 2, 3], [1, 9, 3])

    assert mismatch == {
        "index": 1,
        "manual_token": 2,
        "model_generate_token": 9,
    }


def test_first_token_mismatch_handles_length_difference() -> None:
    mismatch = first_token_mismatch([1, 2], [1, 2, 3])

    assert mismatch == {
        "index": 2,
        "manual_token": None,
        "model_generate_token": 3,
    }


def test_mismatch_formatting_is_actionable() -> None:
    check = {
        "example_id": "multihop_0000",
        "category": "multi_hop",
        "manual_text": "Halden.",
        "model_generate_text": "Halden [Harven moss]",
        "first_mismatch": {
            "index": 3,
            "manual_token": 13,
            "model_generate_token": 508,
        },
    }

    message = format_first_mismatch(check)

    assert "multihop_0000" in message
    assert "multi_hop" in message
    assert "token_index=3" in message
    assert "manual_token=13" in message
    assert "model_generate_token=508" in message


def test_category_counts_and_first_failed_check() -> None:
    checks = [
        {"category": "single_evidence", "match": True},
        {"category": "multi_hop", "match": False},
        {"category": "single_evidence", "match": True},
    ]

    assert category_counts(checks) == {"multi_hop": 1, "single_evidence": 2}
    assert first_failed_check(checks) == checks[1]
