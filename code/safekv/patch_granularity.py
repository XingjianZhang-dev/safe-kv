"""Patch granularity method definitions and summaries for Milestone 4B."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from safekv.data_schema import DiagnosticExample, PromptPack, TokenRange
from safekv.naive_composition import average_metric_summary
from safekv.patch_recompute import (
    oracle_evidence_doc_patch_ranges,
    oracle_evidence_sentence_to_doc_end_patch_ranges,
    oracle_evidence_span_window_patch_ranges,
    oracle_evidence_suffix_patch_ranges,
    oracle_support_and_conflict_span_patch_ranges,
    oracle_support_and_conflict_suffix_patch_ranges,
    random_span_patch_ranges_same_budget,
    stable_example_seed,
    token_count,
)


DEFAULT_SPAN_WINDOWS = [0, 4, 8, 16, 32]
REFERENCE_METHODS = ["oracle_evidence_doc_patch"]
SUFFIX_METHODS = [
    "oracle_evidence_suffix_patch",
    "oracle_evidence_sentence_to_doc_end_patch",
    "oracle_support_and_conflict_span_patch",
    "oracle_support_and_conflict_suffix_patch",
]


def oracle_span_window_method(window: int) -> str:
    return f"oracle_evidence_span_window_{window}"


def random_method_name(oracle_method: str) -> str:
    return f"random_patch_same_budget::{oracle_method}"


def oracle_methods(windows: list[int] | None = None) -> list[str]:
    resolved_windows = DEFAULT_SPAN_WINDOWS if windows is None else windows
    return (
        REFERENCE_METHODS
        + [oracle_span_window_method(window) for window in resolved_windows]
        + SUFFIX_METHODS
    )


def default_patch_granularity_methods(windows: list[int] | None = None) -> list[str]:
    methods: list[str] = []
    for method in oracle_methods(windows):
        methods.append(method)
        if method not in REFERENCE_METHODS:
            methods.append(random_method_name(method))
    return methods


def is_random_budget_method(method: str) -> bool:
    return method.startswith("random_patch_same_budget::")


def paired_oracle_method(method: str) -> str:
    if not is_random_budget_method(method):
        return method
    return method.split("::", 1)[1]


def build_oracle_ranges_by_method(
    example: DiagnosticExample,
    pack: PromptPack,
    windows: list[int] | None = None,
) -> dict[str, list[TokenRange]]:
    ranges: dict[str, list[TokenRange]] = {
        "oracle_evidence_doc_patch": oracle_evidence_doc_patch_ranges(example, pack),
        "oracle_evidence_suffix_patch": oracle_evidence_suffix_patch_ranges(pack),
        "oracle_evidence_sentence_to_doc_end_patch": (
            oracle_evidence_sentence_to_doc_end_patch_ranges(pack)
        ),
        "oracle_support_and_conflict_span_patch": (
            oracle_support_and_conflict_span_patch_ranges(example, pack)
        ),
        "oracle_support_and_conflict_suffix_patch": (
            oracle_support_and_conflict_suffix_patch_ranges(example, pack)
        ),
    }
    for window in DEFAULT_SPAN_WINDOWS if windows is None else windows:
        ranges[oracle_span_window_method(window)] = oracle_evidence_span_window_patch_ranges(
            pack,
            expand_window_tokens=window,
        )
    return ranges


def build_ranges_for_methods(
    example: DiagnosticExample,
    pack: PromptPack,
    methods: list[str],
    seed: int,
    windows: list[int] | None = None,
) -> dict[str, list[TokenRange]]:
    oracle_ranges = build_oracle_ranges_by_method(example, pack, windows=windows)
    ranges: dict[str, list[TokenRange]] = {}
    for method in methods:
        if is_random_budget_method(method):
            oracle_method = paired_oracle_method(method)
            if oracle_method not in oracle_ranges:
                raise ValueError(f"random baseline references unsupported method {oracle_method!r}")
            ranges[method] = random_span_patch_ranges_same_budget(
                pack,
                target_token_count=token_count(oracle_ranges[oracle_method]),
                seed=stable_example_seed(seed, example.id, method),
            )
        else:
            if method not in oracle_ranges:
                raise ValueError(f"unsupported patch granularity method {method!r}")
            ranges[method] = oracle_ranges[method]
    return ranges


def summarize_patch_granularity_rows(
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    failed_examples: list[dict[str, str]],
) -> dict[str, Any]:
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts_by_id: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        method_groups[row["method"]].append(row)
        category_groups[f"{row['method']}::{row['category']}"].append(row)
        category_counts_by_id[row["category"]].add(row["example_id"])

    base_summary = average_metric_summary(base_rows)
    method_level = {
        method: _with_patch_and_delta_summary(
            average_metric_summary(group),
            group,
            base_summary=base_summary,
            random_summary=None,
        )
        for method, group in sorted(method_groups.items())
    }

    for method, summary in method_level.items():
        if is_random_budget_method(method):
            continue
        random_name = random_method_name(method)
        random_summary = method_level.get(random_name)
        if random_summary is not None:
            summary["improvement_over_budget_random"] = _improvement_delta(
                summary,
                random_summary,
            )

    category_level = {
        key: _with_patch_and_delta_summary(
            average_metric_summary(group),
            group,
            base_summary=None,
            random_summary=None,
        )
        for key, group in sorted(category_groups.items())
    }
    method_ranking = sorted(
        (
            {
                "method": method,
                "avg_kl": summary["avg_kl"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
            }
            for method, summary in method_level.items()
        ),
        key=lambda row: row["avg_kl"],
    )
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
        "method_ranking_by_avg_kl": method_ranking,
        "best_method_by_avg_kl": method_ranking[0]["method"] if method_ranking else None,
    }


def _with_patch_and_delta_summary(
    summary: dict[str, Any],
    rows: list[dict[str, Any]],
    base_summary: dict[str, Any] | None,
    random_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    result = dict(summary)
    result["avg_patched_token_count"] = _mean(row.get("patched_token_count", 0.0) for row in rows)
    result["avg_patched_token_ratio"] = _mean(row.get("patched_token_ratio", 0.0) for row in rows)
    if base_summary is not None:
        result["improvement_over_base"] = _improvement_delta(result, base_summary)
    if random_summary is not None:
        result["improvement_over_budget_random"] = _improvement_delta(result, random_summary)
    return result


def _improvement_delta(
    method_summary: dict[str, Any],
    reference_summary: dict[str, Any],
) -> dict[str, float]:
    return {
        "kl_reduction": float(reference_summary["avg_kl"] - method_summary["avg_kl"]),
        "js_reduction": float(reference_summary["avg_js"] - method_summary["avg_js"]),
        "top1_gain": float(
            method_summary["top1_match_rate"] - reference_summary["top1_match_rate"]
        ),
        "top5_gain": float(
            method_summary["avg_top5_overlap"] - reference_summary["avg_top5_overlap"]
        ),
        "top10_gain": float(
            method_summary["avg_top10_overlap"] - reference_summary["avg_top10_overlap"]
        ),
    }


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(sum(float(value) for value in values) / len(values))


__all__ = [
    "DEFAULT_SPAN_WINDOWS",
    "build_oracle_ranges_by_method",
    "build_ranges_for_methods",
    "default_patch_granularity_methods",
    "is_random_budget_method",
    "oracle_methods",
    "oracle_span_window_method",
    "paired_oracle_method",
    "random_method_name",
    "summarize_patch_granularity_rows",
]
