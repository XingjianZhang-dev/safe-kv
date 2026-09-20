import torch
import pytest

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.cache_ops import cache_seq_len
from safekv.data_schema import TokenRange
from safekv.naive_composition import summarize_rows
from safekv.patch_granularity import (
    build_ranges_for_methods,
    random_method_name,
    summarize_patch_granularity_rows,
)
from safekv.patch_recompute import (
    clip_token_range,
    expand_and_clip_token_range,
    merge_token_ranges,
    oracle_evidence_suffix_patch_ranges,
    oracle_evidence_span_window_patch_ranges,
    oracle_evidence_span_patch_ranges,
    oracle_support_and_conflict_span_patch_ranges,
    random_span_patch_ranges_same_budget,
    replace_cache_slices,
    stable_example_seed,
    support_and_conflict_spans,
    token_count,
)
from safekv.prompting import build_rag_prompt
from safekv.token_spans import RegexTokenizer


def _fake_cache(seq_len: int):
    key = torch.arange(seq_len, dtype=torch.float32).reshape(1, 1, seq_len, 1)
    value = key + 100
    return tuple((key.clone(), value.clone()) for _ in range(2))


def test_merge_token_ranges_merges_overlaps_but_preserves_adjacency() -> None:
    ranges = [
        TokenRange(10, 12),
        TokenRange(1, 4),
        TokenRange(3, 7),
        TokenRange(8, 10),
    ]

    assert merge_token_ranges(ranges) == [TokenRange(1, 7), TokenRange(8, 10), TokenRange(10, 12)]


def test_replace_cache_slices_on_fake_cache() -> None:
    base = _fake_cache(8)
    donor = _fake_cache(8)
    donor = tuple((key + 1000, value + 1000) for key, value in donor)

    patched = replace_cache_slices(base, donor, [TokenRange(2, 5)])

    assert cache_seq_len(patched) == 8
    assert patched[0][0][0, 0, :, 0].tolist() == [0, 1, 1002, 1003, 1004, 5, 6, 7]
    assert base[0][0][0, 0, :, 0].tolist() == list(range(8))


def test_replace_cache_slices_accepts_short_donor_covering_patch() -> None:
    base = _fake_cache(8)
    donor = tuple((key + 1000, value + 1000) for key, value in _fake_cache(5))

    patched = replace_cache_slices(base, donor, [TokenRange(2, 5)])

    assert cache_seq_len(patched) == 8
    assert patched[0][0][0, 0, :, 0].tolist() == [0, 1, 1002, 1003, 1004, 5, 6, 7]


def test_replace_cache_slices_rejects_nonsequence_shape_mismatch() -> None:
    base = ((torch.zeros(1, 2, 8, 4), torch.zeros(1, 2, 8, 4)),)
    donor = ((torch.ones(1, 3, 5, 4), torch.ones(1, 3, 5, 4)),)

    with pytest.raises(ValueError, match="non-sequence shape mismatch"):
        replace_cache_slices(base, donor, [TokenRange(2, 5)])


def test_clip_and_expand_span_ranges_to_document_text() -> None:
    bounds = TokenRange(10, 20)

    assert clip_token_range(TokenRange(5, 12), bounds) == TokenRange(10, 12)
    assert expand_and_clip_token_range(TokenRange(12, 15), 10, bounds) == TokenRange(10, 20)
    assert clip_token_range(TokenRange(1, 5), bounds) is None


def test_deterministic_random_span_selection_matches_budget() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")
    seed = stable_example_seed(13, example.id, "random")

    first = random_span_patch_ranges_same_budget(pack, target_token_count=12, seed=seed)
    second = random_span_patch_ranges_same_budget(pack, target_token_count=12, seed=seed)

    assert first == second
    assert token_count(first) == 12


def test_oracle_evidence_span_ranges_clip_to_doc_text() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")

    ranges = oracle_evidence_span_patch_ranges(pack, expand_window_tokens=4)

    assert ranges
    for token_range in ranges:
        assert any(
            doc_text.start <= token_range.start and token_range.end <= doc_text.end
            for doc_text in pack.doc_text_ranges
        )


def test_oracle_evidence_span_window_expands_within_doc_text() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")

    window_0 = oracle_evidence_span_window_patch_ranges(pack, expand_window_tokens=0)
    window_16 = oracle_evidence_span_window_patch_ranges(pack, expand_window_tokens=16)

    assert token_count(window_16) >= token_count(window_0)
    for token_range in window_16:
        assert any(
            doc_text.start <= token_range.start and token_range.end <= doc_text.end
            for doc_text in pack.doc_text_ranges
        )


def test_oracle_evidence_suffix_extends_to_doc_text_end() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")

    ranges = oracle_evidence_suffix_patch_ranges(pack)

    assert ranges
    evidence_doc_end = pack.doc_text_ranges[0].end
    assert any(token_range.end == evidence_doc_end for token_range in ranges)


def test_support_and_conflict_span_selection_adds_conflict_doc_span() -> None:
    examples = build_diagnostic_examples(n_per_category=1, seed=13)
    example = next(item for item in examples if item.category == "conflict")
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")

    spans = support_and_conflict_spans(example, pack)
    ranges = oracle_support_and_conflict_span_patch_ranges(example, pack)

    assert any(span.doc_id == 0 for span in spans)
    assert any(span.doc_id == 1 for span in spans)
    assert token_count(ranges) > 0


def test_build_ranges_for_methods_pairs_budget_matched_random() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")
    oracle_method = "oracle_evidence_span_window_8"
    random_method = random_method_name(oracle_method)

    ranges = build_ranges_for_methods(
        example,
        pack,
        methods=[oracle_method, random_method],
        seed=13,
    )

    assert token_count(ranges[oracle_method]) == token_count(ranges[random_method])
    assert ranges[random_method] == build_ranges_for_methods(
        example,
        pack,
        methods=[random_method],
        seed=13,
    )[random_method]


def test_patch_summary_aggregation() -> None:
    rows = [
        {
            "example_id": "ex0",
            "category": "conflict",
            "method": "oracle_evidence_span_patch",
            "first_token_kl_full_to_method": 0.2,
            "first_token_js_divergence": 0.1,
            "top1_match": True,
            "top5_overlap": 0.8,
            "top10_overlap": 0.7,
            "composed_context_length": 20,
            "max_abs_logit_diff": 1.0,
        },
        {
            "example_id": "ex1",
            "category": "multi_hop",
            "method": "random_span_patch_same_budget",
            "first_token_kl_full_to_method": 0.5,
            "first_token_js_divergence": 0.2,
            "top1_match": False,
            "top5_overlap": 0.4,
            "top10_overlap": 0.5,
            "composed_context_length": 20,
            "max_abs_logit_diff": 2.0,
        },
    ]

    summary = summarize_rows(rows, [])

    assert summary["method_level"]["oracle_evidence_span_patch"]["avg_kl"] == 0.2
    assert summary["category_counts"] == {"conflict": 1, "multi_hop": 1}


def test_patch_granularity_summary_pairs_oracle_and_random() -> None:
    oracle_method = "oracle_evidence_span_window_8"
    random_method = random_method_name(oracle_method)
    base_rows = [
        {
            "example_id": "ex0",
            "category": "conflict",
            "method": "prefix_conditioned_naive_global",
            "first_token_kl_full_to_method": 0.4,
            "first_token_js_divergence": 0.2,
            "top1_match": False,
            "top5_overlap": 0.4,
            "top10_overlap": 0.4,
            "composed_context_length": 20,
            "max_abs_logit_diff": 2.0,
        }
    ]
    rows = [
        {
            "example_id": "ex0",
            "category": "conflict",
            "method": oracle_method,
            "first_token_kl_full_to_method": 0.1,
            "first_token_js_divergence": 0.05,
            "top1_match": True,
            "top5_overlap": 0.8,
            "top10_overlap": 0.8,
            "composed_context_length": 20,
            "max_abs_logit_diff": 1.0,
            "patched_token_count": 5,
            "patched_token_ratio": 0.25,
        },
        {
            "example_id": "ex0",
            "category": "conflict",
            "method": random_method,
            "first_token_kl_full_to_method": 0.2,
            "first_token_js_divergence": 0.1,
            "top1_match": True,
            "top5_overlap": 0.6,
            "top10_overlap": 0.7,
            "composed_context_length": 20,
            "max_abs_logit_diff": 1.5,
            "patched_token_count": 5,
            "patched_token_ratio": 0.25,
        },
    ]

    summary = summarize_patch_granularity_rows(rows, base_rows, [])

    method_summary = summary["method_level"][oracle_method]
    assert method_summary["avg_patched_token_ratio"] == 0.25
    assert method_summary["improvement_over_base"]["kl_reduction"] == pytest.approx(0.3)
    assert method_summary["improvement_over_budget_random"]["kl_reduction"] == pytest.approx(0.1)
