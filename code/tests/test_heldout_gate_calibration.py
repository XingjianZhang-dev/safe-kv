import pytest

from safekv.heldout_gate import (
    HeldoutExample,
    apply_risk_cutoff,
    calibrate_risk_cutoff,
    deterministic_split_ids,
    random_comparison,
    random_gate_rows,
    summarize_rows,
)


def test_deterministic_calibration_split() -> None:
    ids = [f"ex{i}" for i in range(10)]

    first = deterministic_split_ids(ids, seed=13, calibration_fraction=0.3)
    second = deterministic_split_ids(list(reversed(ids)), seed=13, calibration_fraction=0.3)

    assert first == second
    calibration, test = first
    assert len(calibration) == 3
    assert len(test) == 7
    assert calibration.isdisjoint(test)


def test_calibrate_cutoff_and_apply_to_test_examples() -> None:
    examples = [
        _example("a", risk=0.9, patch_cost=20, denominator=100, patch_equiv=True),
        _example("b", risk=0.6, patch_cost=10, denominator=100, patch_equiv=True),
        _example("c", risk=0.1, patch_cost=5, denominator=100, patch_equiv=False),
    ]

    cutoff, actual, selected = calibrate_risk_cutoff(examples, target_budget=0.10)
    test_selected, test_actual = apply_risk_cutoff(examples, risk_cutoff=cutoff)

    assert selected == {"a", "b"}
    assert cutoff == pytest.approx(0.6)
    assert actual == pytest.approx(0.10)
    assert test_selected == {"a", "b"}
    assert test_actual == pytest.approx(0.10)


def test_random_gate_budget_matching_is_deterministic() -> None:
    examples = [
        _example("a", risk=0.9, patch_cost=10, denominator=100, patch_equiv=True),
        _example("b", risk=0.6, patch_cost=10, denominator=100, patch_equiv=False),
        _example("c", risk=0.1, patch_cost=10, denominator=100, patch_equiv=True),
    ]

    rows_a, actual_a, selected_a = random_gate_rows(
        examples,
        target_budget=0.10,
        method_prefix="random",
        seed=7,
    )
    rows_b, actual_b, selected_b = random_gate_rows(
        examples,
        target_budget=0.10,
        method_prefix="random",
        seed=7,
    )

    assert selected_a == selected_b
    assert actual_a == actual_b
    assert rows_a[0]["method"] == "random_seed007"


def test_summary_and_random_comparison() -> None:
    rows = [
        _example("a", risk=0.9, patch_cost=10, denominator=100, patch_equiv=True).patch_row,
        _example("b", risk=0.6, patch_cost=10, denominator=100, patch_equiv=False).base_row,
    ]
    summary = summarize_rows(rows)
    comparison = random_comparison(
        safe_answer_equivalence=0.75,
        random_summaries=[
            {"answer_equivalence_to_full_prefill": 0.5},
            {"answer_equivalence_to_full_prefill": 0.75},
            {"answer_equivalence_to_full_prefill": 1.0},
        ],
    )

    assert summary["n_examples"] == 2
    assert summary["answer_equivalence_to_full_prefill"] == pytest.approx(0.5)
    assert comparison["random_gate_mean_answer_equivalence"] == pytest.approx(0.75)
    assert comparison["percentile_vs_random"] == pytest.approx(2 / 3)


def _example(
    example_id: str,
    *,
    risk: float,
    patch_cost: int,
    denominator: int,
    patch_equiv: bool,
) -> HeldoutExample:
    base = _row(example_id, "prefix_conditioned_naive_global", equiv=False, patch_cost=0, ratio=0.0)
    patch = _row(
        example_id,
        "risk_guided_doc_patch_k2",
        equiv=patch_equiv,
        patch_cost=patch_cost,
        ratio=patch_cost / denominator,
    )
    patch["gate_risk_score"] = risk
    return HeldoutExample(
        example_id=example_id,
        category="conflict",
        risk_score=risk,
        patch_cost=patch_cost,
        denominator=denominator,
        base_row=base,
        patch_row=patch,
    )


def _row(example_id: str, method: str, *, equiv: bool, patch_cost: int, ratio: float):
    return {
        "example_id": example_id,
        "category": "conflict",
        "method": method,
        "answer_equivalence_to_full_prefill": equiv,
        "answer_changed_from_full": not equiv,
        "answer_changed_and_gold_wrong": not equiv,
        "patched_doc_count": 2 if patch_cost else 0,
        "patched_token_count": patch_cost,
        "patched_token_ratio": ratio,
    }
