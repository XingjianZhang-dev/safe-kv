import pytest

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.doc_selector_stress import (
    best_subset_by_metric,
    canonical_doc_subset,
    exhaustive_doc_subsets,
    matching_random_baseline_for_method,
    random_gate_ids_same_num_patched_examples,
    random_gate_ids_same_patch_rate,
    random_seed_values,
    semantic_selector_percentiles,
    summarize_doc_selector_stress_rows,
)


def test_random_seed_generation_is_deterministic() -> None:
    assert random_seed_values(4) == [0, 1, 2, 3]
    with pytest.raises(ValueError):
        random_seed_values(0)


def test_exhaustive_subset_enumeration_and_canonicalization() -> None:
    example = next(
        example
        for example in build_diagnostic_examples(n_per_category=1, seed=13)
        if example.category == "distractor_heavy"
    )

    assert canonical_doc_subset([3, 1, 3]) == (1, 3)
    assert len(exhaustive_doc_subsets(example, k=1)) == 6
    assert len(exhaustive_doc_subsets(example, k=2)) == 15
    assert len(exhaustive_doc_subsets(example, max_k=2)) == 21


def test_repair_oracle_selection_uses_lowest_kl() -> None:
    subset_rows = {
        (0,): _fake_row("subset", "ex0", kl=0.3, ratio=0.2, docs=1),
        (1,): _fake_row("subset", "ex0", kl=0.1, ratio=0.2, docs=1),
        (0, 1): _fake_row("subset", "ex0", kl=0.2, ratio=0.4, docs=2),
    }

    subset, row = best_subset_by_metric(subset_rows, [(0,), (1,), (0, 1)])

    assert subset == (1,)
    assert row["first_token_kl_full_to_method"] == pytest.approx(0.1)


def test_summary_includes_budget_normalized_columns_and_percentiles() -> None:
    base_rows = [_fake_row("prefix_conditioned_naive_global", "ex0", kl=0.4, ratio=0.0, docs=0)]
    rows = [
        _fake_row("risk_guided_doc_patch_k1", "ex0", kl=0.2, ratio=0.25, docs=1),
        _fake_row(
            "random_doc_patch_k1_seeded",
            "ex0",
            kl=0.3,
            ratio=0.25,
            docs=1,
            seed=0,
        ),
        _fake_row(
            "random_doc_patch_k1_seeded",
            "ex0",
            kl=0.1,
            ratio=0.25,
            docs=1,
            seed=1,
        ),
    ]

    summary = summarize_doc_selector_stress_rows(rows, base_rows, [])

    risk_summary = summary["method_level"]["risk_guided_doc_patch_k1"]
    assert risk_summary["kl_reduction_per_patched_token_ratio"] == pytest.approx(0.8)
    assert risk_summary["kl_reduction_per_doc"] == pytest.approx(0.2)
    percentile = summary["semantic_selector_percentiles"]["risk_guided_doc_patch_k1"]
    assert percentile["matched_random_baseline"] == "random_doc_patch_k1_seeded"
    assert percentile["percent_random_seeds_worse_or_equal"] == pytest.approx(50.0)


def test_matching_random_baselines_for_semantic_methods() -> None:
    assert matching_random_baseline_for_method("query_similarity_doc_patch_k1") == (
        "random_doc_patch_k1_seeded"
    )
    assert matching_random_baseline_for_method("risk_guided_doc_patch_k2") == (
        "random_doc_patch_k2_seeded"
    )
    assert matching_random_baseline_for_method("top_retrieval_doc_patch_oracle_count") == (
        "random_doc_patch_same_count_seeded"
    )


def test_random_gate_baseline_matching_is_deterministic() -> None:
    example_ids = ["a", "b", "c", "d"]
    first = random_gate_ids_same_num_patched_examples(example_ids, target_count=2, seed=7)
    second = random_gate_ids_same_num_patched_examples(example_ids, target_count=2, seed=7)
    ratios = {"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1}

    rate_first = random_gate_ids_same_patch_rate(ratios, target_avg_patch_ratio=0.2, seed=9)
    rate_second = random_gate_ids_same_patch_rate(ratios, target_avg_patch_ratio=0.2, seed=9)

    assert first == second
    assert len(first) == 2
    assert rate_first == rate_second
    assert sum(ratios[item] for item in rate_first) / len(ratios) <= 0.25


def test_semantic_selector_percentile_uses_lower_kl_as_better() -> None:
    method_level = {"risk_guided_doc_patch_k1": {"avg_kl": 0.2}}
    random_distribution = {
        "random_doc_patch_k1_seeded": {
            "seed_summaries": {
                "0": {"avg_kl": 0.1},
                "1": {"avg_kl": 0.3},
                "2": {"avg_kl": 0.4},
            }
        }
    }

    percentiles = semantic_selector_percentiles(method_level, random_distribution)

    assert percentiles["risk_guided_doc_patch_k1"][
        "percent_random_seeds_worse_or_equal"
    ] == pytest.approx(200 / 3)


def _fake_row(
    method: str,
    example_id: str,
    *,
    kl: float,
    ratio: float,
    docs: int,
    seed: int | None = None,
):
    return {
        "example_id": example_id,
        "category": "conflict",
        "method": method,
        "first_token_kl_full_to_method": kl,
        "first_token_js_divergence": kl / 2,
        "top1_match": kl < 0.25,
        "top5_overlap": 0.8,
        "top10_overlap": 0.7,
        "composed_context_length": 20,
        "max_abs_logit_diff": 1.0,
        "patched_doc_count": docs,
        "patched_token_count": int(20 * ratio),
        "patched_token_ratio": ratio,
        "random_seed": seed,
    }
