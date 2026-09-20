from safekv.build_diagnostic import build_diagnostic_examples
from safekv.data_schema import TokenRange
from safekv.prompting import (
    ANSWER_INSTRUCTION,
    build_plain_rag_prompt,
    build_prompt_text_and_char_ranges,
    build_rag_prompt,
    tokenize_prompt_with_offsets,
)
from safekv.token_spans import RegexTokenizer


class OffsetRegexTokenizer(RegexTokenizer):
    def __call__(
        self,
        text: str,
        add_special_tokens: bool = False,
        return_offsets_mapping: bool = False,
    ) -> dict[str, object]:
        assert add_special_tokens is False
        input_ids, offsets = self.encode_with_offsets(text)
        response: dict[str, object] = {"input_ids": input_ids}
        if return_offsets_mapping:
            response["offset_mapping"] = offsets
        return response


class ChatRegexTokenizer(OffsetRegexTokenizer):
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        assert tokenize is False
        assert add_generation_prompt is True
        assert len(messages) == 1
        return f"<|user|>\n{messages[0]['content']}<|assistant|>\n"


def test_prompt_reconstruction_and_token_concatenation() -> None:
    tokenizer = RegexTokenizer()
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]

    pack = build_plain_rag_prompt(example, tokenizer)

    assert pack.full_text == pack.context_text + pack.query_text
    assert pack.full_input_ids == pack.context_input_ids + pack.query_input_ids
    assert pack.query_text == (
        f"Question: {example.question}\n"
        f"{ANSWER_INSTRUCTION}\n"
        "Answer:"
    )
    assert pack.offset_mapping_source == "fallback"


def test_prompt_text_builder_uses_title_header_format() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]

    prompt = build_prompt_text_and_char_ranges(example)

    for prompt_doc_index, doc in enumerate(example.documents, start=1):
        header = f"[Document {prompt_doc_index} | Title: {doc.title}]\n"
        assert header in prompt.context_text


def test_offset_mapping_path_uses_one_pass_full_text_tokenization() -> None:
    tokenizer = OffsetRegexTokenizer()
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    prompt = build_prompt_text_and_char_ranges(example)

    pack = tokenize_prompt_with_offsets(prompt, tokenizer)
    encoded = tokenizer(prompt.full_text, add_special_tokens=False, return_offsets_mapping=True)

    assert pack.offset_mapping_source == "offset_mapping"
    assert pack.full_input_ids == encoded["input_ids"]
    assert pack.full_text == pack.context_text + pack.query_text
    assert pack.full_input_ids == pack.context_input_ids + pack.query_input_ids


def test_offset_mapping_ranges_map_back_to_character_ranges() -> None:
    tokenizer = OffsetRegexTokenizer()
    examples = build_diagnostic_examples(n_per_category=1, seed=13)

    for example in examples:
        prompt = build_prompt_text_and_char_ranges(example)
        pack = tokenize_prompt_with_offsets(prompt, tokenizer)

        assert _covered_char_range(pack.offset_mapping, pack.context_token_range) == (
            prompt.context_char_range.start,
            prompt.context_char_range.end,
        )
        assert _covered_char_range(pack.offset_mapping, pack.query_token_range) == (
            prompt.query_char_range.start,
            prompt.query_char_range.end,
        )

        for doc_char, doc_token_range in zip(prompt.doc_char_ranges, pack.doc_ranges, strict=True):
            assert _covered_char_range(pack.offset_mapping, doc_token_range) == (
                doc_char.block_char_range.start,
                doc_char.block_char_range.end,
            )

        span_chars = {span.span_id: span for span in prompt.span_char_ranges}
        for span in pack.span_ranges:
            expected = span_chars[span.span_id]
            assert _covered_char_range(pack.offset_mapping, span.token_range) == (
                expected.prompt_char_range.start,
                expected.prompt_char_range.end,
            )
            assert span.prompt_char_range == expected.prompt_char_range
            assert span.token_distance_to_doc_start >= 0
            assert span.token_distance_to_doc_end >= 0
            assert 0.0 <= span.boundary_token_overlap_ratio <= 1.0


def test_chat_rag_preserves_document_span_mapping() -> None:
    tokenizer = ChatRegexTokenizer()
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]

    pack = build_plain_rag_prompt(
        example,
        tokenizer,
    )
    chat_pack = build_rag_prompt(
        example,
        tokenizer,
        prompt_format="chat_rag",
    )

    assert chat_pack.prompt_format == "chat_rag"
    assert chat_pack.context_token_range.start > pack.context_token_range.start
    assert chat_pack.full_text.startswith("<|user|>")
    assert chat_pack.full_text.endswith("<|assistant|>\n")
    assert chat_pack.span_ranges[0].text == pack.span_ranges[0].text
    assert chat_pack.full_text[
        chat_pack.span_ranges[0].prompt_char_range.start : chat_pack.span_ranges[0].prompt_char_range.end
    ] == chat_pack.span_ranges[0].text


def _covered_char_range(
    offset_mapping: list[tuple[int, int]], token_range: TokenRange
) -> tuple[int, int]:
    offsets = [
        offset
        for offset in offset_mapping[token_range.start : token_range.end]
        if offset[1] > offset[0]
    ]
    assert offsets
    return min(start for start, _ in offsets), max(end for _, end in offsets)
