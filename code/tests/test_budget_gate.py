import pytest

from safekv.budget_gate import (
    BudgetExampleInfo,
    budget_method_name,
    random_budget_order,
    safe_budget_order,
    select_examples_for_budget,
    summarize_random_against_safe,
)


def test_budget_target_selection_uses_risk_order_and_computes_actual_budget() -> None:
    infos = [
        BudgetExampleInfo("low", risk_score=0.1, patch_cost=5, denominator=100),
        BudgetExampleInfo("high", risk_score=0.9, patch_cost=20, denominator=100),
        BudgetExampleInfo("mid", risk_score=0.5, patch_cost=10, denominator=100),
    ]

    order = safe_budget_order(infos)
    selected, actual = select_examples_for_budget(
        infos,
        target_budget=0.10,
        order=order,
    )

    assert order == ["high", "mid", "low"]
    assert selected == {"high", "mid"}
    assert actual == pytest.approx(0.10)


def test_zero_budget_and_zero_denominator_return_empty_selection() -> None:
    infos = [BudgetExampleInfo("ex0", risk_score=1.0, patch_cost=5, denominator=0)]

    selected, actual = select_examples_for_budget(infos, target_budget=0.25, order=["ex0"])
    assert selected == set()
    assert actual == 0.0

    infos = [BudgetExampleInfo("ex0", risk_score=1.0, patch_cost=5, denominator=10)]
    selected, actual = select_examples_for_budget(infos, target_budget=0.0, order=["ex0"])
    assert selected == set()
    assert actual == 0.0


def test_random_gate_order_is_deterministic_for_seed() -> None:
    infos = [
        BudgetExampleInfo("a", risk_score=0.1, patch_cost=1, denominator=10),
        BudgetExampleInfo("b", risk_score=0.2, patch_cost=1, denominator=10),
        BudgetExampleInfo("c", risk_score=0.3, patch_cost=1, denominator=10),
    ]

    assert random_budget_order(infos, seed=7) == random_budget_order(infos, seed=7)
    assert random_budget_order(infos, seed=7) != random_budget_order(infos, seed=8)


def test_random_comparison_summary_and_method_name() -> None:
    summary = summarize_random_against_safe(
        safe_value=0.75,
        random_values=[0.50, 0.75, 1.00],
    )

    assert budget_method_name("safe_gate_budget", 0.25) == "safe_gate_budget_0.25"
    assert summary["random_mean"] == pytest.approx(0.75)
    assert summary["random_std"] > 0.0
    assert summary["percentile_vs_random"] == pytest.approx(2 / 3)
