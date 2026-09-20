import json

import pytest
import torch

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.naive_composition import (
    bootstrap_metric_cis,
    canonical_composition_method,
    compact_csv_row,
    composition_failure_analysis_markdown,
    composition_length_metadata,
    composition_method_specs,
    make_metric_row,
    prefix_token_range,
    reference_logits_for_example,
    select_composition_method_specs,
    summarize_rows,
)
from safekv.prompting import build_rag_prompt
from safekv.token_spans import RegexTokenizer


class ChatRegexTokenizer(RegexTokenizer):
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        assert tokenize is False
        assert add_generation_prompt is True
        assert len(messages) == 1
        return f"<|user|>\n{messages[0]['content']}<|assistant|>\n"


class TinyTokenizer:
    def decode(self, token_ids, skip_special_tokens=False):
        del skip_special_tokens
        return f"tok{token_ids[0]}"


def test_prefix_range_extraction_for_chat_prompt() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")

    prefix = prefix_token_range(pack)

    assert prefix.start == 0
    assert prefix.end == pack.doc_ranges[0].start
    assert prefix.length > 0


def test_composed_cache_length_accounting() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")
    prefix_len = prefix_token_range(pack).length
    doc_len = sum(doc_range.length for doc_range in pack.doc_ranges)

    with_prefix = composition_length_metadata(pack, includes_prefix_cache=True)
    doc_only = composition_length_metadata(pack, includes_prefix_cache=False)

    assert with_prefix["composed_context_length"] == prefix_len + doc_len
    assert with_prefix["prefix_cache_length"] == prefix_len
    assert with_prefix["missing_prefix_length"] == 0
    assert doc_only["composed_context_length"] == doc_len
    assert doc_only["prefix_cache_length"] == 0
    assert doc_only["missing_prefix_length"] == prefix_len


def test_output_row_metadata_fields() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")
    metadata = composition_length_metadata(pack, includes_prefix_cache=True)
    row = make_metric_row(
        example=example,
        method="prefix_plus_naive_global",
        pack=pack,
        full_logits=torch.tensor([4.0, 1.0, 0.0]),
        method_logits=torch.tensor([3.5, 1.0, 0.2]),
        tokenizer=TinyTokenizer(),
        composed_context_length=int(metadata["composed_context_length"]),
    )
    row.update(metadata)
    row["position_mode"] = "global"
    row["composition_mode"] = "prefix_plus_unconditioned_doc"
    row["doc_conditioning"] = "none"

    for key in (
        "prompt_length",
        "prefix_length",
        "prefix_cache_length",
        "doc_cache_length",
        "query_length",
        "composed_context_length",
        "missing_prefix_length",
        "includes_prefix_cache",
        "position_mode",
        "composition_mode",
        "doc_conditioning",
    ):
        assert key in row


def test_naive_method_aliases_and_specs() -> None:
    assert canonical_composition_method("naive_global") == "doc_only_naive_global"
    assert canonical_composition_method("naive_local") == "doc_only_naive_local"
    assert {
        str(spec["method"])
        for spec in composition_method_specs()
    } == {
        "doc_only_naive_global",
        "doc_only_naive_local",
        "prefix_plus_naive_global",
        "prefix_plus_naive_local",
        "prefix_conditioned_naive_global",
        "prefix_conditioned_naive_local",
    }
    conditioned = [
        spec for spec in composition_method_specs()
        if str(spec["method"]).startswith("prefix_conditioned")
    ]
    assert conditioned
    assert all(spec["doc_conditioning"] == "prefix" for spec in conditioned)
    assert all(spec["includes_prefix_cache"] is True for spec in conditioned)


def test_config_method_selection_with_aliases() -> None:
    specs = select_composition_method_specs(["naive_global", "prefix_conditioned_naive_global"])

    assert [spec["method"] for spec in specs] == [
        "doc_only_naive_global",
        "prefix_conditioned_naive_global",
    ]


def test_config_method_selection_defaults_to_all() -> None:
    assert select_composition_method_specs(None) == composition_method_specs()
    assert select_composition_method_specs([]) == composition_method_specs()


def test_config_method_selection_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unsupported composition method"):
        select_composition_method_specs(["random"])


def test_prefix_conditioned_length_metadata() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")
    prefix_len = prefix_token_range(pack).length
    doc_len = sum(doc_range.length for doc_range in pack.doc_ranges)

    metadata = composition_length_metadata(pack, includes_prefix_cache=True)

    assert metadata["composed_context_length"] == prefix_len + doc_len
    assert metadata["prefix_cache_length"] == prefix_len
    assert metadata["doc_cache_length"] == doc_len


def test_summary_handles_prefix_conditioned_method() -> None:
    rows = [
        {
            "example_id": "ex0",
            "category": "multi_hop",
            "method": "prefix_conditioned_naive_global",
            "first_token_kl_full_to_method": 0.2,
            "first_token_js_divergence": 0.1,
            "top1_match": True,
            "top5_overlap": 0.8,
            "top10_overlap": 0.7,
            "composed_context_length": 12,
            "max_abs_logit_diff": 1.5,
        },
        {
            "example_id": "ex1",
            "category": "conflict",
            "method": "doc_only_naive_global",
            "first_token_kl_full_to_method": 0.4,
            "first_token_js_divergence": 0.2,
            "top1_match": False,
            "top5_overlap": 0.4,
            "top10_overlap": 0.5,
            "composed_context_length": 10,
            "max_abs_logit_diff": 2.0,
        },
    ]

    summary = summarize_rows(rows, failed_examples=[])

    assert "prefix_conditioned_naive_global" in summary["method_level"]
    assert summary["best_method_by_avg_kl"] == "prefix_conditioned_naive_global"
    assert "bootstrap_95_ci" in summary["method_level"]["prefix_conditioned_naive_global"]


def test_bootstrap_ci_is_deterministic() -> None:
    rows = [
        {
            "first_token_kl_full_to_method": 0.1,
            "first_token_js_divergence": 0.01,
            "top1_match": True,
            "top5_overlap": 0.8,
            "top10_overlap": 0.7,
        },
        {
            "first_token_kl_full_to_method": 0.4,
            "first_token_js_divergence": 0.02,
            "top1_match": False,
            "top5_overlap": 0.4,
            "top10_overlap": 0.5,
        },
    ]

    first = bootstrap_metric_cis(rows, n_resamples=50, seed=7)
    second = bootstrap_metric_cis(rows, n_resamples=50, seed=7)

    assert first == second
    assert set(first) == {"avg_kl", "avg_js", "top1_match_rate", "avg_top5_overlap", "avg_top10_overlap"}


def test_compact_csv_row_formatting() -> None:
    row = {
        "example_id": "ex0",
        "category": "multi_hop",
        "method": "prefix_conditioned_naive_global",
        "first_token_kl_full_to_method": 0.2,
        "first_token_js_divergence": 0.1,
        "top1_match": True,
        "top5_overlap": 0.8,
        "top10_overlap": 0.7,
        "prompt_length": 100,
        "prefix_length": 10,
        "doc_cache_length": 70,
        "query_length": 20,
        "position_mode": "global",
        "composition_mode": "prefix_conditioned_naive",
        "doc_conditioning": "prefix",
    }

    csv_row = compact_csv_row(row)

    assert csv_row["example_id"] == "ex0"
    assert csv_row["doc_conditioning"] == "prefix"
    assert "cache_summary" not in csv_row


def test_failure_analysis_markdown_with_fake_rows() -> None:
    rows = [
        {
            "example_id": "ex0",
            "category": "conflict",
            "method": "prefix_conditioned_naive_global",
            "first_token_kl_full_to_method": 1.2,
            "top1_match": False,
            "argmax_full_decoded": "9",
            "argmax_method_decoded": "10",
        },
        {
            "example_id": "ex1",
            "category": "single_evidence",
            "method": "prefix_conditioned_naive_global",
            "first_token_kl_full_to_method": 0.01,
            "top1_match": True,
            "argmax_full_decoded": "Mira",
            "argmax_method_decoded": "Mira",
        },
    ]

    markdown = composition_failure_analysis_markdown(rows, top_n=1)

    assert "# Composition Failure Analysis" in markdown
    assert "ex0" in markdown
    assert "Top-1 next-token changed" in markdown


def test_sidecar_reference_is_not_used_by_default(tmp_path) -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")
    current = object()

    result = reference_logits_for_example(
        current_logits=current,
        use_sidecar_reference=False,
        results_dir=tmp_path,
        example_id=example.id,
        pack=pack,
    )

    assert result is current


def test_stale_sidecar_reference_rejected_when_opted_in(tmp_path) -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_rag_prompt(example, ChatRegexTokenizer(), prompt_format="chat_rag")
    prompt_pack_path = tmp_path / "prompt_packs" / f"{example.id}.json"
    prompt_pack_path.parent.mkdir(parents=True)
    prompt_pack_path.write_text(
        json.dumps({"full_input_ids": [999999]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stale sidecar reference"):
        reference_logits_for_example(
            current_logits=torch.tensor([1.0]),
            use_sidecar_reference=True,
            results_dir=tmp_path,
            example_id=example.id,
            pack=pack,
        )
