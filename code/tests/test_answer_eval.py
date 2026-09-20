import json

import pytest

from safekv.answer_eval import (
    answer_contains_gold,
    answer_equivalent,
    answer_failure_analysis_markdown,
    append_answer_rows,
    completed_output_keys,
    internal_selector_method,
    kl_bin_mismatch_aggregation,
    make_answer_eval_row,
    normalize_answer,
    parse_methods_arg,
    read_answer_rows,
    summarize_answer_eval_rows,
    token_f1,
)


def test_answer_normalization_and_equivalence() -> None:
    assert normalize_answer("The 9 AM.") == "9 am"
    assert answer_equivalent("The Velora Observatory", "velora observatory")
    assert not answer_equivalent("9 AM", "10 AM")


def test_token_f1_and_answer_contains_gold() -> None:
    assert token_f1("Mira Solen", "Mira Solen") == pytest.approx(1.0)
    assert token_f1("Mira", "Mira Solen") == pytest.approx(2 / 3)
    assert answer_contains_gold("The answer is Mira Solen.", "Mira Solen")
    assert not answer_contains_gold("Mira", "Mira Solen")


def test_method_parsing_and_safe_gate_aliases() -> None:
    assert parse_methods_arg("full_prefill, risk_guided_doc_patch_k2") == [
        "full_prefill",
        "risk_guided_doc_patch_k2",
    ]
    assert internal_selector_method("safe_gate_t0.45") == "safe_composition_gate_t0_45"
    assert internal_selector_method("safe_gate_t0.60") == "safe_composition_gate_t0_60"


def test_summary_aggregation_and_kl_bins() -> None:
    rows = [
        _fake_answer_row("full_prefill", "ex0", "Mira Solen", "Mira Solen", 0.0, True, 0.0),
        _fake_answer_row(
            "prefix_conditioned_naive_global",
            "ex0",
            "Mira",
            "Mira Solen",
            0.2,
            False,
            0.0,
        ),
        _fake_answer_row(
            "risk_guided_doc_patch_k2",
            "ex0",
            "Mira Solen",
            "Mira Solen",
            0.01,
            True,
            0.5,
        ),
    ]

    summary = summarize_answer_eval_rows(rows)
    bins = kl_bin_mismatch_aggregation(rows, bins=[0.0, 0.05, 1.0])

    assert summary["method_level"]["full_prefill"]["answer_equivalence_to_full_prefill"] == 1.0
    assert summary["method_level"]["prefix_conditioned_naive_global"][
        "answer_equivalence_to_full_prefill"
    ] == 0.0
    assert summary["method_level"]["risk_guided_doc_patch_k2"]["gold_token_f1"] == 1.0
    assert bins[0]["num_rows"] == 2
    assert bins[1]["answer_mismatch_rate"] == 1.0


def test_failure_analysis_formatting() -> None:
    rows = [
        _fake_answer_row("full_prefill", "ex0", "Norwick", "Norwick", 0.0, True, 0.0),
        _fake_answer_row(
            "prefix_conditioned_naive_global",
            "ex0",
            "Mariton",
            "Norwick",
            0.5,
            False,
            0.0,
        ),
        _fake_answer_row("safe_gate_t0.45", "ex0", "Norwick", "Norwick", 0.01, True, 0.4),
        _fake_answer_row(
            "oracle_evidence_doc_patch",
            "ex0",
            "Norwick",
            "Norwick",
            0.01,
            True,
            0.4,
        ),
    ]
    summary = summarize_answer_eval_rows(rows)

    markdown = answer_failure_analysis_markdown(rows, summary)

    assert "Top 10 Base Answer Changes" in markdown
    assert "Repaired By Safe Gates" in markdown
    assert "ex0" in markdown


def test_resume_output_append_behavior_with_fake_rows(tmp_path) -> None:
    path = tmp_path / "answer_eval_outputs.jsonl"
    first = _fake_answer_row("full_prefill", "ex0", "A", "A", 0.0, True, 0.0)
    second = _fake_answer_row("prefix_conditioned_naive_global", "ex0", "B", "A", 0.2, False, 0.0)

    append_answer_rows(path, [first])
    assert completed_output_keys(path) == {("ex0", "full_prefill")}
    append_answer_rows(path, [second])
    loaded = read_answer_rows(path)

    assert [json.loads(line)["method"] for line in path.read_text().splitlines()] == [
        "full_prefill",
        "prefix_conditioned_naive_global",
    ]
    assert len(loaded) == 2
    assert completed_output_keys(path) == {
        ("ex0", "full_prefill"),
        ("ex0", "prefix_conditioned_naive_global"),
    }


def _fake_answer_row(
    method: str,
    example_id: str,
    generated: str,
    full: str,
    kl: float,
    top1: bool,
    ratio: float,
):
    return make_answer_eval_row(
        example_id=example_id,
        category="multi_hop",
        method=method,
        generated_answer=generated,
        full_prefill_answer=full,
        gold_answer=full,
        patched_doc_count=1 if ratio else 0,
        patched_token_count=int(100 * ratio),
        patched_token_ratio=ratio,
        prompt_length=200,
        query_length=40,
        first_token_kl_full_to_method=kl,
        top1_match=top1,
    )
