"""Stress-test helpers for document-level selector validity.

The functions here are intentionally selector-agnostic. They provide random
baseline distributions, repair-oracle subset enumeration, budget-normalized
summaries, and gate baseline matching for Milestone 5B.
"""

from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict
from typing import Any, Iterable

from safekv.data_schema import DiagnosticExample
from safekv.doc_selector import (
    parse_safe_gate_threshold,
    safe_gate_method_name,
)
from safekv.naive_composition import average_metric_summary


SEMANTIC_DOC_SELECTOR_METHODS = [
    "oracle_evidence_doc_patch",
    "top_retrieval_doc_patch_oracle_count",
    "top_retrieval_doc_patch_k1",
    "top_retrieval_doc_patch_k2",
    "query_similarity_doc_patch_oracle_count",
    "query_similarity_doc_patch_k1",
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_oracle_count",
    "entity_overlap_doc_patch_k1",
    "entity_overlap_doc_patch_k2",
    "conflict_aware_doc_patch",
    "risk_guided_doc_patch_oracle_count",
    "risk_guided_doc_patch_k1",
    "risk_guided_doc_patch_k2",
]

SEEDED_RANDOM_DOC_METHODS = [
    "random_doc_patch_same_count_seeded",
    "random_doc_patch_k1_seeded",
    "random_doc_patch_k2_seeded",
]


def random_seed_values(num_random_seeds: int) -> list[int]:
    if num_random_seeds <= 0:
        raise ValueError("num_random_seeds must be positive")
    return list(range(num_random_seeds))


def canonical_doc_subset(doc_ids: Iterable[int]) -> tuple[int, ...]:
    return tuple(sorted({int(doc_id) for doc_id in doc_ids}))


def exhaustive_doc_subsets(
    example: DiagnosticExample,
    *,
    k: int | None = None,
    max_k: int | None = None,
    include_empty: bool = False,
) -> list[tuple[int, ...]]:
    doc_ids = sorted(doc.doc_id for doc in example.documents)
    subsets: list[tuple[int, ...]] = [()] if include_empty else []
    if k is not None:
        if k < 0:
            raise ValueError("k must be non-negative")
        if k == 0:
            return [()] if include_empty else []
        if k <= len(doc_ids):
            subsets.extend(tuple(combo) for combo in itertools.combinations(doc_ids, k))
        return subsets
    if max_k is None:
        raise ValueError("either k or max_k is required")
    if max_k < 1:
        raise ValueError("max_k must be positive")
    for size in range(1, min(max_k, len(doc_ids)) + 1):
        subsets.extend(tuple(combo) for combo in itertools.combinations(doc_ids, size))
    return subsets


def best_subset_by_metric(
    subset_rows: dict[tuple[int, ...], dict[str, Any]],
    candidate_subsets: Iterable[tuple[int, ...]],
    metric_key: str = "first_token_kl_full_to_method",
) -> tuple[tuple[int, ...], dict[str, Any]]:
    candidates = [canonical_doc_subset(subset) for subset in candidate_subsets]
    available = [subset for subset in candidates if subset in subset_rows]
    if not available:
        raise ValueError("no candidate subsets have metric rows")
    best_subset = min(
        available,
        key=lambda subset: (
            float(subset_rows[subset][metric_key]),
            len(subset),
            subset,
        ),
    )
    return best_subset, subset_rows[best_subset]


def repair_oracle_method_names(max_k: int) -> list[str]:
    names = [
        "oracle_best_doc_patch_k1",
        "oracle_best_doc_patch_k2",
        "oracle_best_doc_patch_same_count",
        "oracle_min_kl_doc_subset",
    ]
    if max_k >= 3:
        names.insert(2, "oracle_best_doc_patch_k3")
    return names


def random_gate_ids_same_num_patched_examples(
    example_ids: list[str],
    target_count: int,
    seed: int,
) -> set[str]:
    if target_count <= 0:
        return set()
    rng = random.Random(seed)
    sample_count = min(target_count, len(example_ids))
    return set(rng.sample(example_ids, sample_count))


def random_gate_ids_same_patch_rate(
    candidate_patch_ratios: dict[str, float],
    target_avg_patch_ratio: float,
    seed: int,
) -> set[str]:
    if target_avg_patch_ratio <= 0 or not candidate_patch_ratios:
        return set()
    rng = random.Random(seed)
    example_ids = list(candidate_patch_ratios)
    rng.shuffle(example_ids)
    selected: list[str] = []
    best_selected: list[str] = []
    best_gap = abs(target_avg_patch_ratio)
    total_examples = len(example_ids)
    running_ratio_sum = 0.0
    for example_id in example_ids:
        selected.append(example_id)
        running_ratio_sum += float(candidate_patch_ratios[example_id])
        avg_ratio = running_ratio_sum / total_examples
        gap = abs(avg_ratio - target_avg_patch_ratio)
        if gap < best_gap:
            best_gap = gap
            best_selected = selected[:]
        if avg_ratio >= target_avg_patch_ratio and best_selected:
            break
    return set(best_selected)


def clone_metric_row_for_method(
    row: dict[str, Any],
    *,
    method: str,
    base_row: dict[str, Any],
    selected_doc_ids: Iterable[int],
    selector_reason: dict[str, Any] | None = None,
    random_seed: int | None = None,
) -> dict[str, Any]:
    copied = dict(row)
    selected = list(canonical_doc_subset(selected_doc_ids))
    copied["method"] = method
    copied["selected_doc_ids"] = selected
    copied["patched_doc_count"] = len(selected)
    copied["selector_reason"] = selector_reason or {}
    copied["random_seed"] = random_seed
    copied["base_first_token_kl_full_to_method"] = base_row[
        "first_token_kl_full_to_method"
    ]
    copied["kl_reduction_from_base"] = float(
        base_row["first_token_kl_full_to_method"]
        - copied["first_token_kl_full_to_method"]
    )
    copied["kl_reduction_per_patched_token_ratio"] = _safe_divide(
        copied["kl_reduction_from_base"],
        copied.get("patched_token_ratio", 0.0),
    )
    copied["kl_reduction_per_doc"] = _safe_divide(
        copied["kl_reduction_from_base"],
        copied.get("patched_doc_count", 0.0),
    )
    return copied


def summarize_doc_selector_stress_rows(
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    failed_examples: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    failed_examples = failed_examples or []
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts_by_id: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        method_groups[row["method"]].append(row)
        category_groups[f"{row['method']}::{row['category']}"].append(row)
        category_counts_by_id[row["category"]].add(row["example_id"])

    base_summary = _summary_with_budget_stats(base_rows, None)
    method_level = {
        method: _summary_with_budget_stats(group, base_summary)
        for method, group in sorted(method_groups.items())
    }
    category_level = {
        key: _summary_with_budget_stats(group, base_summary)
        for key, group in sorted(category_groups.items())
    }

    evidence_oracle = method_level.get("oracle_evidence_doc_patch")
    repair_oracle = method_level.get("oracle_min_kl_doc_subset")
    for method, summary in method_level.items():
        if evidence_oracle is not None and method != "oracle_evidence_doc_patch":
            summary["gap_to_evidence_oracle"] = _gap_to_reference(summary, evidence_oracle)
        if repair_oracle is not None and method != "oracle_min_kl_doc_subset":
            summary["gap_to_repair_oracle"] = _gap_to_reference(summary, repair_oracle)

    random_distribution = random_baseline_distribution(rows, base_summary)
    semantic_percentiles = semantic_selector_percentiles(method_level, random_distribution)
    gate_pareto = stress_gate_pareto_rows(method_level)
    ranking = _method_ranking(method_level)

    return {
        "num_rows": len(rows),
        "num_failed_examples": len(failed_examples),
        "failed_examples": failed_examples,
        "category_counts": {
            category: len(example_ids)
            for category, example_ids in sorted(category_counts_by_id.items())
        },
        "base_method_level": base_summary,
        "method_level": method_level,
        "category_level": category_level,
        "random_baseline_distribution": random_distribution,
        "semantic_selector_percentiles": semantic_percentiles,
        "budget_warnings": budget_warnings(method_level),
        "gate_pareto": gate_pareto,
        "method_ranking_by_avg_kl": ranking,
        "best_method_by_avg_kl": ranking[0]["method"] if ranking else None,
    }


def random_baseline_distribution(
    rows: list[dict[str, Any]],
    base_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    seed_groups: dict[str, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        seed = row.get("random_seed")
        if seed is None:
            continue
        seed_groups[row["method"]][int(seed)].append(row)

    result: dict[str, Any] = {}
    for method, groups in sorted(seed_groups.items()):
        seed_summaries = {
            str(seed): _summary_with_budget_stats(group, base_summary)
            for seed, group in sorted(groups.items())
        }
        result[method] = {
            "num_seeds": len(seed_summaries),
            "seed_summaries": seed_summaries,
            "aggregate_over_seeds": _aggregate_seed_summaries(seed_summaries),
        }
    return result


def semantic_selector_percentiles(
    method_level: dict[str, dict[str, Any]],
    random_distribution: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for method, summary in method_level.items():
        baseline = matching_random_baseline_for_method(method)
        if baseline is None or baseline not in random_distribution:
            continue
        random_kls = [
            float(seed_summary["avg_kl"])
            for seed_summary in random_distribution[baseline]["seed_summaries"].values()
        ]
        if not random_kls:
            continue
        avg_kl = float(summary["avg_kl"])
        result[method] = {
            "matched_random_baseline": baseline,
            "semantic_avg_kl": avg_kl,
            "random_avg_kl_mean": _mean(random_kls),
            "percent_random_seeds_worse_or_equal": 100.0
            * sum(1 for value in random_kls if value >= avg_kl)
            / len(random_kls),
            "percent_random_seeds_better": 100.0
            * sum(1 for value in random_kls if value < avg_kl)
            / len(random_kls),
        }
    return result


def matching_random_baseline_for_method(method: str) -> str | None:
    if method.endswith("_k1") or method == "oracle_best_doc_patch_k1":
        return "random_doc_patch_k1_seeded"
    if method.endswith("_k2") or method == "oracle_best_doc_patch_k2":
        return "random_doc_patch_k2_seeded"
    if method.endswith("_oracle_count") or method in {
        "oracle_evidence_doc_patch",
        "oracle_best_doc_patch_same_count",
        "conflict_aware_doc_patch",
    }:
        return "random_doc_patch_same_count_seeded"
    threshold = parse_safe_gate_threshold(method)
    if threshold is not None:
        suffix = _gate_threshold_label(threshold)
        return f"random_gate_same_patch_rate_t{suffix}"
    return None


def stress_gate_pareto_rows(
    method_level: dict[str, dict[str, Any]]
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for method, summary in method_level.items():
        threshold = parse_safe_gate_threshold(method)
        if threshold is None and not method.startswith("random_gate_"):
            continue
        rows.append(
            {
                "method": method,
                "threshold": threshold if threshold is not None else _parse_gate_baseline_threshold(method),
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                "avg_kl": summary["avg_kl"],
                "top1_mismatch_rate": 1.0 - summary["top1_match_rate"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
            }
        )
    return sorted(rows, key=lambda row: (float(row["threshold"] or 0.0), str(row["method"])))


def budget_warnings(method_level: dict[str, dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for method, summary in method_level.items():
        baseline = matching_random_baseline_for_method(method)
        if baseline is None or baseline not in method_level:
            continue
        method_kl = float(summary["avg_kl"])
        random_kl = float(method_level[baseline]["avg_kl"])
        method_ratio = float(summary.get("avg_patched_token_ratio", 0.0))
        random_ratio = float(method_level[baseline].get("avg_patched_token_ratio", 0.0))
        if method_kl < random_kl and random_ratio > 0 and method_ratio > 1.10 * random_ratio:
            warnings.append(
                f"{method} has lower KL than {baseline}, but patches "
                f"{method_ratio:.3f} vs {random_ratio:.3f} average token ratio."
            )
    return warnings


def flatten_random_distribution_for_csv(
    random_distribution: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method, data in sorted(random_distribution.items()):
        for seed, summary in sorted(
            data["seed_summaries"].items(),
            key=lambda item: int(item[0]),
        ):
            rows.append(
                {
                    "method": method,
                    "random_seed": int(seed),
                    "avg_kl": summary["avg_kl"],
                    "avg_js": summary["avg_js"],
                    "top1_match_rate": summary["top1_match_rate"],
                    "avg_top5_overlap": summary["avg_top5_overlap"],
                    "avg_top10_overlap": summary["avg_top10_overlap"],
                    "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                    "avg_patched_doc_count": summary["avg_patched_doc_count"],
                    "kl_reduction_per_patched_token_ratio": summary[
                        "kl_reduction_per_patched_token_ratio"
                    ],
                    "kl_reduction_per_doc": summary["kl_reduction_per_doc"],
                }
            )
    return rows


def _summary_with_budget_stats(
    rows: list[dict[str, Any]],
    base_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    summary = dict(average_metric_summary(rows))
    example_ids = {row["example_id"] for row in rows}
    summary["num_distinct_examples"] = len(example_ids)
    summary["avg_patched_doc_count"] = _mean(
        row.get("patched_doc_count", 0.0) for row in rows
    )
    summary["avg_patched_token_count"] = _mean(
        row.get("patched_token_count", 0.0) for row in rows
    )
    summary["avg_patched_token_ratio"] = _mean(
        row.get("patched_token_ratio", 0.0) for row in rows
    )
    if base_summary is not None:
        kl_reduction = float(base_summary["avg_kl"] - summary["avg_kl"])
        summary["improvement_over_base"] = {
            "kl_reduction": kl_reduction,
            "js_reduction": float(base_summary["avg_js"] - summary["avg_js"]),
            "top1_gain": float(
                summary["top1_match_rate"] - base_summary["top1_match_rate"]
            ),
            "top10_gain": float(
                summary["avg_top10_overlap"] - base_summary["avg_top10_overlap"]
            ),
        }
        summary["kl_reduction_per_patched_token_ratio"] = _safe_divide(
            kl_reduction,
            summary["avg_patched_token_ratio"],
        )
        summary["kl_reduction_per_doc"] = _safe_divide(
            kl_reduction,
            summary["avg_patched_doc_count"],
        )
    else:
        summary["kl_reduction_per_patched_token_ratio"] = 0.0
        summary["kl_reduction_per_doc"] = 0.0
    return summary


def _aggregate_seed_summaries(seed_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = [
        "avg_kl",
        "avg_js",
        "top1_match_rate",
        "avg_top5_overlap",
        "avg_top10_overlap",
        "avg_patched_token_ratio",
        "avg_patched_doc_count",
        "kl_reduction_per_patched_token_ratio",
        "kl_reduction_per_doc",
    ]
    summaries = list(seed_summaries.values())
    aggregate: dict[str, Any] = {}
    for metric in metrics:
        values = [float(summary[metric]) for summary in summaries]
        aggregate[f"{metric}_mean"] = _mean(values)
        aggregate[f"{metric}_std"] = _std(values)
        aggregate[f"{metric}_bootstrap_95_ci"] = _bootstrap_ci(values)
    return aggregate


def _gap_to_reference(
    method_summary: dict[str, Any],
    reference_summary: dict[str, Any],
) -> dict[str, float]:
    return {
        "kl_gap": float(method_summary["avg_kl"] - reference_summary["avg_kl"]),
        "js_gap": float(method_summary["avg_js"] - reference_summary["avg_js"]),
        "top1_gap": float(
            method_summary["top1_match_rate"] - reference_summary["top1_match_rate"]
        ),
        "top10_gap": float(
            method_summary["avg_top10_overlap"] - reference_summary["avg_top10_overlap"]
        ),
    }


def _method_ranking(method_level: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                "method": method,
                "avg_kl": summary["avg_kl"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                "avg_patched_doc_count": summary["avg_patched_doc_count"],
            }
            for method, summary in method_level.items()
        ),
        key=lambda row: row["avg_kl"],
    )


def _parse_gate_baseline_threshold(method: str) -> float | None:
    marker = "_t"
    if marker not in method:
        return None
    suffix = method.rsplit(marker, 1)[1]
    try:
        return float(suffix.replace("_", "."))
    except ValueError:
        return None


def _gate_threshold_label(threshold: float) -> str:
    return safe_gate_method_name(threshold).removeprefix("safe_composition_gate_t")


def _bootstrap_ci(
    values: list[float],
    n_resamples: int = 1000,
    seed: int = 13,
) -> dict[str, float]:
    if not values:
        return {"low": 0.0, "high": 0.0}
    rng = random.Random(seed)
    estimates = []
    n = len(values)
    for _ in range(n_resamples):
        estimates.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    estimates.sort()
    return {"low": _percentile(estimates, 0.025), "high": _percentile(estimates, 0.975)}


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    position = q * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(values[int(position)])
    weight = position - lower
    return float(values[lower] * (1.0 - weight) + values[upper] * weight)


def _mean(values: Iterable[float]) -> float:
    values = [float(value) for value in values]
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _std(values: Iterable[float]) -> float:
    values = [float(value) for value in values]
    if len(values) <= 1:
        return 0.0
    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return float(math.sqrt(variance))


def _safe_divide(numerator: float, denominator: float) -> float:
    denominator = float(denominator)
    if denominator == 0.0:
        return 0.0
    return float(numerator) / denominator


__all__ = [
    "SEEDED_RANDOM_DOC_METHODS",
    "SEMANTIC_DOC_SELECTOR_METHODS",
    "best_subset_by_metric",
    "budget_warnings",
    "canonical_doc_subset",
    "clone_metric_row_for_method",
    "exhaustive_doc_subsets",
    "flatten_random_distribution_for_csv",
    "matching_random_baseline_for_method",
    "random_gate_ids_same_num_patched_examples",
    "random_gate_ids_same_patch_rate",
    "random_seed_values",
    "repair_oracle_method_names",
    "semantic_selector_percentiles",
    "summarize_doc_selector_stress_rows",
]
