from collections import Counter

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.full_prefill import (
    prompt_pack_metadata,
    select_examples_per_category,
    select_generation_sanity_examples,
    validate_full_prefill_output_row,
)
from safekv.prompting import build_plain_rag_prompt
from safekv.token_spans import RegexTokenizer


def test_full_prefill_output_schema_validator_accepts_expected_row() -> None:
    row = {
        "example_id": "single_0000",
        "category": "single_evidence",
        "gold_answer": "Mira Solen",
        "full_text": "Question: x\nAnswer:",
        "prompt_token_counts": {"full": 5, "context": 3, "query": 2},
        "context_token_range": {"start": 0, "end": 3},
        "query_token_range": {"start": 3, "end": 5},
        "logits_path": "results/logits/full_prefill/single_0000.pt",
        "logits_dtype": "float16",
        "logits_shape": [2],
        "prompt_pack_path": "results/prompt_packs/single_0000.json",
        "top10_next_tokens": [
            {"token_id": 1, "token": "Mira", "logit": 0.2},
            {"token_id": 0, "token": "Other", "logit": 0.1},
        ],
        "generated_answer": "Mira Solen",
        "task_metrics": {
            "gold_exact_match": True,
            "gold_f1": 1.0,
            "answer_contains_gold": True,
            "gold_contains_answer": True,
        },
    }

    validate_full_prefill_output_row(row)


def test_select_examples_per_category_is_stratified() -> None:
    examples = build_diagnostic_examples(n_per_category=4, seed=13)

    selected = select_examples_per_category(examples, max_examples_per_category=2)
    counts = Counter(example.category for example in selected)

    assert len(selected) == 10
    assert set(counts.values()) == {2}


def test_generation_sanity_selection_covers_all_categories() -> None:
    examples = build_diagnostic_examples(n_per_category=3, seed=13)

    selected = select_generation_sanity_examples(examples)
    counts = Counter(example.category for example in selected)

    assert len(selected) == 5
    assert set(counts.values()) == {1}


def test_prompt_pack_metadata_is_complete() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    pack = build_plain_rag_prompt(example, RegexTokenizer())

    metadata = prompt_pack_metadata(pack)

    for key in (
        "full_text",
        "full_input_ids",
        "context_input_ids",
        "query_input_ids",
        "offset_mapping",
        "doc_ranges",
        "doc_text_ranges",
        "span_ranges",
        "evidence_span_ids",
        "conflict_doc_ids",
    ):
        assert key in metadata
    assert metadata["full_text"] == pack.full_text
    assert metadata["full_input_ids"] == pack.full_input_ids
    assert metadata["context_input_ids"] == pack.context_input_ids
    assert metadata["query_input_ids"] == pack.query_input_ids
    assert len(metadata["offset_mapping"]) == len(pack.full_input_ids)
    assert "effective_boundary_window_tokens" in metadata["span_ranges"][0]
