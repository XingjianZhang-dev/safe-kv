"""Budget-targeted safe gate utilities for SAFE-KV Milestone 7A."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from safekv.paper_analysis import mean, percentile_rank, stddev


@dataclass(frozen=True)
class BudgetExampleInfo:
    example_id: str
    risk_score: float
    patch_cost: int
    denominator: int


def budget_method_name(prefix: str, target_budget: float) -> str:
    return f"{prefix}_{target_budget:.2f}"


def select_examples_for_budget(
    infos: list[BudgetExampleInfo],
    *,
    target_budget: float,
    order: list[str],
) -> tuple[set[str], float]:
    info_by_id = {info.example_id: info for info in infos}
    total_denominator = sum(info.denominator for info in infos)
    if total_denominator <= 0 or target_budget <= 0:
        return set(), 0.0

    selected: set[str] = set()
    current_cost = 0
    best_selected: set[str] = set()
    best_budget = 0.0
    best_gap = abs(target_budget)
    for example_id in order:
        info = info_by_id[example_id]
        if info.patch_cost <= 0:
            continue
        selected.add(example_id)
        current_cost += info.patch_cost
        actual_budget = current_cost / total_denominator
        gap = abs(actual_budget - target_budget)
        if gap < best_gap or (gap == best_gap and actual_budget <= target_budget):
            best_gap = gap
            best_budget = actual_budget
            best_selected = set(selected)
    return best_selected, best_budget


def safe_budget_order(infos: list[BudgetExampleInfo]) -> list[str]:
    ordered = sorted(infos, key=lambda info: (-info.risk_score, info.example_id))
    return [info.example_id for info in ordered]


def random_budget_order(infos: list[BudgetExampleInfo], *, seed: int) -> list[str]:
    ids = [info.example_id for info in infos]
    rng = random.Random(seed)
    rng.shuffle(ids)
    return ids


def summarize_random_against_safe(
    *,
    safe_value: float,
    random_values: list[float],
) -> dict[str, Any]:
    sigma = stddev(random_values)
    mu = mean(random_values)
    return {
        "random_mean": mu,
        "random_std": sigma,
        "random_95ci_low": mu - 1.96 * sigma,
        "random_95ci_high": mu + 1.96 * sigma,
        "percentile_vs_random": percentile_rank(safe_value, random_values),
    }

