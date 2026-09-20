"""Held-out budget-gate calibration helpers for SAFE-KV Milestone 7B."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from safekv.budget_gate import (
    BudgetExampleInfo,
    random_budget_order,
    safe_budget_order,
    select_examples_for_budget,
)
from safekv.paper_analysis import mean, percentile_rank, truthy


@dataclass(frozen=True)
class HeldoutExample:
    example_id: str
    category: str
    risk_score: float
    patch_cost: int
    denominator: int
    base_row: dict[str, Any]
    patch_row: dict[str, Any]

    def budget_info(self) -> BudgetExampleInfo:
        return BudgetExampleInfo(
            example_id=self.example_id,
            risk_score=self.risk_score,
            patch_cost=self.patch_cost,
            denominator=self.denominator,
        )


def deterministic_split_ids(
    example_ids: list[str],
    *,
    seed: int = 13,
    calibration_fraction: float = 0.30,
) -> tuple[set[str], set[str]]:
    if not 0.0 < calibration_fraction < 1.0:
        raise ValueError("calibration_fraction must be between 0 and 1")
    ids = sorted(example_ids)
    rng = random.Random(seed)
    rng.shuffle(ids)
    calibration_count = max(1, min(len(ids) - 1, round(len(ids) * calibration_fraction)))
    calibration_ids = set(ids[:calibration_count])
    test_ids = set(ids[calibration_count:])
    return calibration_ids, test_ids


def read_budget_gate_examples(path: str | Path) -> list[HeldoutExample]:
    rows_by_example: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            method = row.get("method")
            if method in {"prefix_conditioned_naive_global", "risk_guided_doc_patch_k2"}:
                rows_by_example[row["example_id"]][method] = row

    examples = []
    for example_id, methods in sorted(rows_by_example.items()):
        if "prefix_conditioned_naive_global" not in methods:
            continue
        if "risk_guided_doc_patch_k2" not in methods:
            continue
        base = methods["prefix_conditioned_naive_global"]
        patch = methods["risk_guided_doc_patch_k2"]
        ratio = float(patch.get("patched_token_ratio") or 0.0)
        patch_cost = int(float(patch.get("patched_token_count") or 0.0))
        denominator = int(round(patch_cost / ratio)) if ratio > 0 else int(base.get("prompt_length") or 0)
        examples.append(
            HeldoutExample(
                example_id=example_id,
                category=str(base.get("category", "")),
                risk_score=float(patch.get("gate_risk_score") or 0.0),
                patch_cost=patch_cost,
                denominator=denominator,
                base_row=base,
                patch_row=patch,
            )
        )
    return examples


def calibrate_risk_cutoff(
    calibration_examples: list[HeldoutExample],
    *,
    target_budget: float,
) -> tuple[float, float, set[str]]:
    infos = [example.budget_info() for example in calibration_examples]
    selected, actual_budget = select_examples_for_budget(
        infos,
        target_budget=target_budget,
        order=safe_budget_order(infos),
    )
    if not selected:
        return float("inf"), actual_budget, selected
    selected_risks = [
        example.risk_score for example in calibration_examples if example.example_id in selected
    ]
    return min(selected_risks), actual_budget, selected


def apply_risk_cutoff(
    test_examples: list[HeldoutExample],
    *,
    risk_cutoff: float,
) -> tuple[set[str], float]:
    selected = {
        example.example_id
        for example in test_examples
        if example.patch_cost > 0 and example.risk_score >= risk_cutoff
    }
    return selected, actual_budget(test_examples, selected)


def actual_budget(examples: list[HeldoutExample], selected: set[str]) -> float:
    denominator = sum(example.denominator for example in examples)
    if denominator <= 0:
        return 0.0
    cost = sum(example.patch_cost for example in examples if example.example_id in selected)
    return cost / denominator


def materialize_gate_rows(
    examples: list[HeldoutExample],
    *,
    method: str,
    selected: set[str],
    target_budget: float,
    actual_test_budget: float,
    split: str = "test",
    random_seed: int | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for example in sorted(examples, key=lambda item: item.example_id):
        source = example.patch_row if example.example_id in selected else example.base_row
        row = dict(source)
        row["method"] = method
        row["budget_selected"] = example.example_id in selected
        row["target_budget"] = target_budget
        row["actual_budget"] = actual_test_budget
        row["heldout_split"] = split
        row["gate_risk_score"] = example.risk_score
        if random_seed is not None:
            row["random_seed"] = random_seed
        rows.append(row)
    return rows


def random_gate_rows(
    examples: list[HeldoutExample],
    *,
    target_budget: float,
    method_prefix: str,
    seed: int,
) -> tuple[list[dict[str, Any]], float, set[str]]:
    infos = [example.budget_info() for example in examples]
    selected, actual = select_examples_for_budget(
        infos,
        target_budget=target_budget,
        order=random_budget_order(infos, seed=seed),
    )
    rows = materialize_gate_rows(
        examples,
        method=f"{method_prefix}_seed{seed:03d}",
        selected=selected,
        target_budget=target_budget,
        actual_test_budget=actual,
        random_seed=seed,
    )
    return rows, actual, selected


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "n_examples": n,
        "answer_equivalence_to_full_prefill": mean(
            1.0 if truthy(row["answer_equivalence_to_full_prefill"]) else 0.0
            for row in rows
        ),
        "answer_changed_from_full_rate": mean(
            1.0 if truthy(row["answer_changed_from_full"]) else 0.0 for row in rows
        ),
        "answer_changed_and_gold_wrong_rate": mean(
            1.0 if truthy(row["answer_changed_and_gold_wrong"]) else 0.0 for row in rows
        ),
        "answer_changed_and_gold_wrong_count": sum(
            1 for row in rows if truthy(row["answer_changed_and_gold_wrong"])
        ),
        "patched_token_ratio": mean(float(row.get("patched_token_ratio") or 0.0) for row in rows),
        "patched_doc_count": mean(float(row.get("patched_doc_count") or 0.0) for row in rows),
    }


def percentile_interval(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    ordered = sorted(values)
    low_index = int(0.025 * (len(ordered) - 1))
    high_index = int(0.975 * (len(ordered) - 1))
    return ordered[low_index], ordered[high_index]


def random_comparison(
    *,
    safe_answer_equivalence: float,
    random_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    values = [
        float(summary["answer_equivalence_to_full_prefill"])
        for summary in random_summaries
    ]
    low, high = percentile_interval(values)
    return {
        "random_gate_mean_answer_equivalence": mean(values),
        "random_gate_95ci_low": low,
        "random_gate_95ci_high": high,
        "percentile_vs_random": percentile_rank(safe_answer_equivalence, values),
    }
