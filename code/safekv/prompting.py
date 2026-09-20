"""Plain RAG prompt construction with token/span range tracking."""

from __future__ import annotations

from typing import Any, Protocol

from safekv.data_schema import (
    CharRange,
    DiagnosticExample,
    DocCharInfo,
    PromptPack,
    PromptTextAndCharRanges,
    SpanCharInfo,
    SpanInfo,
    TokenRange,
)
from safekv.token_spans import SupportsEncode, split_doc_spans

ANSWER_INSTRUCTION = "Answer with the shortest exact answer phrase from the documents."
DEFAULT_BOUNDARY_WINDOW_TOKENS = 8


class SupportsOffsetFallback(Protocol):
    def encode_with_offsets(self, text: str) -> tuple[list[int], list[tuple[int, int]]]:
        ...


def build_plain_rag_prompt(
    example: DiagnosticExample,
    tokenizer: SupportsEncode,
    boundary_window_tokens: int = DEFAULT_BOUNDARY_WINDOW_TOKENS,
    adaptive_boundary_window: bool = True,
) -> PromptPack:
    """Build and tokenize the fixed SAFE-KV v0 plain RAG prompt."""

    prompt = build_prompt_text_and_char_ranges(example)
    return tokenize_prompt_with_offsets(
        prompt,
        tokenizer=tokenizer,
        boundary_window_tokens=boundary_window_tokens,
        adaptive_boundary_window=adaptive_boundary_window,
    )


def build_rag_prompt(
    example: DiagnosticExample,
    tokenizer: SupportsEncode,
    prompt_format: str = "plain_rag",
    boundary_window_tokens: int = DEFAULT_BOUNDARY_WINDOW_TOKENS,
    adaptive_boundary_window: bool = True,
) -> PromptPack:
    """Build a plain or chat RAG prompt while preserving document span ranges."""

    prompt = build_prompt_text_and_char_ranges(example)
    if prompt_format == "plain_rag":
        rendered_prompt = prompt
    elif prompt_format == "chat_rag":
        rendered_prompt = render_chat_prompt_with_char_ranges(prompt, tokenizer)
    else:
        raise ValueError(f"unsupported prompt_format {prompt_format!r}")

    return tokenize_prompt_with_offsets(
        rendered_prompt,
        tokenizer=tokenizer,
        boundary_window_tokens=boundary_window_tokens,
        adaptive_boundary_window=adaptive_boundary_window,
    )


def build_prompt_text_and_char_ranges(example: DiagnosticExample) -> PromptTextAndCharRanges:
    """Build prompt text and global character ranges before tokenization."""

    example.validate()

    context_parts: list[str] = []
    doc_char_ranges: list[DocCharInfo] = []
    span_char_ranges: list[SpanCharInfo] = []
    evidence_span_ids: list[str] = []

    cursor = 0
    evidence_by_doc = _evidence_by_doc(example)

    for prompt_doc_index, doc in enumerate(example.documents, start=1):
        header = f"[Document {prompt_doc_index} | Title: {doc.title}]\n"
        separator = "\n\n"
        block_start = cursor
        text_start = block_start + len(header)
        text_end = text_start + len(doc.text)
        block_end = text_end + len(separator)

        doc_char_ranges.append(
            DocCharInfo(
                doc_id=doc.doc_id,
                prompt_doc_index=prompt_doc_index,
                title=doc.title,
                block_char_range=CharRange(block_start, block_end),
                text_char_range=CharRange(text_start, text_end),
            )
        )

        for span_index, (char_start, char_end) in enumerate(split_doc_spans(doc.text)):
            span_text = doc.text[char_start:char_end]
            contains_gold_evidence = any(ev_text in span_text for ev_text in evidence_by_doc[doc.doc_id])
            span_id = f"doc{doc.doc_id}_span{span_index}"
            span_info = SpanCharInfo(
                span_id=span_id,
                doc_id=doc.doc_id,
                text=span_text,
                prompt_char_range=CharRange(text_start + char_start, text_start + char_end),
                char_range_in_doc=(char_start, char_end),
                role=doc.role,
                retrieval_score=doc.retrieval_score,
                contains_gold_evidence=contains_gold_evidence,
            )
            span_char_ranges.append(span_info)
            if contains_gold_evidence:
                evidence_span_ids.append(span_id)

        context_parts.append(f"{header}{doc.text}{separator}")
        cursor = block_end

    context_text = "".join(context_parts)
    query_text = (
        f"Question: {example.question}\n"
        f"{ANSWER_INSTRUCTION}\n"
        "Answer:"
    )
    full_text = context_text + query_text
    context_char_range = CharRange(0, len(context_text))
    query_char_range = CharRange(len(context_text), len(full_text))

    return PromptTextAndCharRanges(
        example_id=example.id,
        prompt_format="plain_rag",
        full_text=full_text,
        context_text=context_text,
        query_text=query_text,
        context_char_range=context_char_range,
        query_char_range=query_char_range,
        doc_char_ranges=doc_char_ranges,
        span_char_ranges=span_char_ranges,
        evidence_span_ids=evidence_span_ids,
        conflict_doc_ids=list(example.conflicting_docs),
    )


def render_chat_prompt_with_char_ranges(
    prompt: PromptTextAndCharRanges,
    tokenizer: SupportsEncode,
) -> PromptTextAndCharRanges:
    """Render a chat-template prompt and shift existing document char ranges.

    This keeps the plain RAG content as a single user message and relies on the
    rendered chat prompt containing that user content verbatim. If a tokenizer's
    chat template transforms or escapes the content, we fail loudly instead of
    producing untrustworthy offsets.
    """

    apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
    if apply_chat_template is None:
        raise ValueError("chat_rag requires tokenizer.apply_chat_template")

    rendered = apply_chat_template(
        [{"role": "user", "content": prompt.full_text}],
        tokenize=False,
        add_generation_prompt=True,
    )
    content_start = rendered.find(prompt.full_text)
    if content_start < 0:
        raise ValueError("chat template did not preserve plain RAG content verbatim")

    def shift_char_range(char_range: CharRange) -> CharRange:
        return CharRange(char_range.start + content_start, char_range.end + content_start)

    doc_char_ranges = [
        DocCharInfo(
            doc_id=doc.doc_id,
            prompt_doc_index=doc.prompt_doc_index,
            title=doc.title,
            block_char_range=shift_char_range(doc.block_char_range),
            text_char_range=shift_char_range(doc.text_char_range),
        )
        for doc in prompt.doc_char_ranges
    ]
    span_char_ranges = [
        SpanCharInfo(
            span_id=span.span_id,
            doc_id=span.doc_id,
            text=span.text,
            prompt_char_range=shift_char_range(span.prompt_char_range),
            char_range_in_doc=span.char_range_in_doc,
            role=span.role,
            retrieval_score=span.retrieval_score,
            contains_gold_evidence=span.contains_gold_evidence,
        )
        for span in prompt.span_char_ranges
    ]

    context_char_range = shift_char_range(prompt.context_char_range)
    query_char_range = CharRange(prompt.query_char_range.start + content_start, len(rendered))

    return PromptTextAndCharRanges(
        example_id=prompt.example_id,
        prompt_format="chat_rag",
        full_text=rendered,
        context_text=rendered[context_char_range.start : context_char_range.end],
        query_text=rendered[query_char_range.start : query_char_range.end],
        context_char_range=context_char_range,
        query_char_range=query_char_range,
        doc_char_ranges=doc_char_ranges,
        span_char_ranges=span_char_ranges,
        evidence_span_ids=list(prompt.evidence_span_ids),
        conflict_doc_ids=list(prompt.conflict_doc_ids),
    )


def tokenize_prompt_with_offsets(
    prompt: PromptTextAndCharRanges,
    tokenizer: SupportsEncode,
    boundary_window_tokens: int = DEFAULT_BOUNDARY_WINDOW_TOKENS,
    adaptive_boundary_window: bool = True,
) -> PromptPack:
    """Tokenize full_text once and map prompt char ranges to token ranges.

    HuggingFace fast tokenizers should take the primary path via
    ``return_offsets_mapping=True``. Unit tests use ``RegexTokenizer`` through
    the explicit ``encode_with_offsets`` fallback, still over the full prompt in
    one pass. Tokenizers without either capability are rejected because they
    cannot support trustworthy KV-cache position mapping.
    """

    if boundary_window_tokens <= 0:
        raise ValueError("boundary_window_tokens must be positive")

    token_ids, offset_mapping, offset_source = _tokenize_full_text_with_offsets(
        tokenizer, prompt.full_text
    )
    context_token_range = char_range_to_token_range(offset_mapping, prompt.context_char_range)
    query_token_range = char_range_to_token_range(offset_mapping, prompt.query_char_range)

    if prompt.prompt_format == "plain_rag":
        if context_token_range.start != 0:
            raise ValueError("context token range must start at token 0")
        if context_token_range.end != query_token_range.start:
            raise ValueError(
                "context/query split crosses a tokenizer token; choose a safer prompt boundary"
            )
        if query_token_range.end != len(token_ids):
            raise ValueError("query token range must end at the final full-text token")
    elif query_token_range.end != len(token_ids):
        raise ValueError("chat query token range must include the final rendered prompt token")

    doc_ranges: list[TokenRange] = []
    doc_text_ranges: list[TokenRange] = []
    doc_text_range_by_id: dict[int, TokenRange] = {}
    for doc_char in prompt.doc_char_ranges:
        doc_range = char_range_to_token_range(offset_mapping, doc_char.block_char_range)
        doc_text_range = char_range_to_token_range(offset_mapping, doc_char.text_char_range)
        doc_ranges.append(doc_range)
        doc_text_ranges.append(doc_text_range)
        doc_text_range_by_id[doc_char.doc_id] = doc_text_range

    span_infos: list[SpanInfo] = []
    for span_char in prompt.span_char_ranges:
        span_token_range = char_range_to_token_range(offset_mapping, span_char.prompt_char_range)
        doc_text_range = doc_text_range_by_id[span_char.doc_id]
        effective_window = effective_boundary_window_tokens(
            configured_window_tokens=boundary_window_tokens,
            doc_text_token_len=doc_text_range.length,
            adaptive=adaptive_boundary_window,
        )
        distance_to_doc_start = max(0, span_token_range.start - doc_text_range.start)
        distance_to_doc_end = max(0, doc_text_range.end - span_token_range.end)
        overlap_ratio = boundary_token_overlap_ratio(
            span_token_range=span_token_range,
            doc_text_token_range=doc_text_range,
            boundary_window_tokens=effective_window,
        )
        span_infos.append(
            SpanInfo(
                span_id=span_char.span_id,
                doc_id=span_char.doc_id,
                text=span_char.text,
                token_range=span_token_range,
                prompt_char_range=span_char.prompt_char_range,
                char_range_in_doc=span_char.char_range_in_doc,
                role=span_char.role,
                retrieval_score=span_char.retrieval_score,
                token_distance_to_doc_start=distance_to_doc_start,
                token_distance_to_doc_end=distance_to_doc_end,
                boundary_token_overlap_ratio=overlap_ratio,
                effective_boundary_window_tokens=effective_window,
                contains_gold_evidence=span_char.contains_gold_evidence,
            )
        )

    return PromptPack(
        example_id=prompt.example_id,
        prompt_format=prompt.prompt_format,
        full_text=prompt.full_text,
        context_text=prompt.context_text,
        query_text=prompt.query_text,
        full_input_ids=token_ids,
        context_input_ids=token_ids[context_token_range.start : context_token_range.end],
        query_input_ids=token_ids[query_token_range.start : query_token_range.end],
        doc_ranges=doc_ranges,
        doc_text_ranges=doc_text_ranges,
        context_token_range=context_token_range,
        query_token_range=query_token_range,
        doc_char_ranges=prompt.doc_char_ranges,
        span_ranges=span_infos,
        evidence_span_ids=list(prompt.evidence_span_ids),
        conflict_doc_ids=list(prompt.conflict_doc_ids),
        offset_mapping=offset_mapping,
        offset_mapping_source=offset_source,
        boundary_window_tokens=boundary_window_tokens,
    )


def effective_boundary_window_tokens(
    configured_window_tokens: int,
    doc_text_token_len: int,
    adaptive: bool = True,
) -> int:
    if configured_window_tokens <= 0:
        raise ValueError("configured_window_tokens must be positive")
    if not adaptive:
        return configured_window_tokens
    return min(configured_window_tokens, max(4, doc_text_token_len // 6))


def char_range_to_token_range(
    offset_mapping: list[tuple[int, int]], char_range: CharRange
) -> TokenRange:
    """Return the contiguous token range whose offsets overlap a char range."""

    overlapping_indices = [
        index
        for index, (token_start, token_end) in enumerate(offset_mapping)
        if token_end > token_start
        and token_start < char_range.end
        and token_end > char_range.start
    ]
    if overlapping_indices:
        return TokenRange(overlapping_indices[0], overlapping_indices[-1] + 1)

    insertion = 0
    for index, (_, token_end) in enumerate(offset_mapping):
        if token_end <= char_range.start:
            insertion = index + 1
        else:
            break
    return TokenRange(insertion, insertion)


def boundary_token_overlap_ratio(
    span_token_range: TokenRange,
    doc_text_token_range: TokenRange,
    boundary_window_tokens: int,
) -> float:
    if span_token_range.length == 0 or doc_text_token_range.length == 0:
        return 0.0

    left_window = TokenRange(
        doc_text_token_range.start,
        min(doc_text_token_range.end, doc_text_token_range.start + boundary_window_tokens),
    )
    right_window = TokenRange(
        max(doc_text_token_range.start, doc_text_token_range.end - boundary_window_tokens),
        doc_text_token_range.end,
    )
    boundary_tokens = set(range(left_window.start, left_window.end))
    boundary_tokens.update(range(right_window.start, right_window.end))
    span_tokens = set(range(span_token_range.start, span_token_range.end))
    return len(span_tokens & boundary_tokens) / span_token_range.length


def _tokenize_full_text_with_offsets(
    tokenizer: SupportsEncode, text: str
) -> tuple[list[int], list[tuple[int, int]], str]:
    try:
        encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
        token_ids = _extract_input_ids(encoded)
        offsets = _extract_offset_mapping(encoded)
        if offsets is None:
            raise ValueError("tokenizer response did not include offset_mapping")
        if len(token_ids) != len(offsets):
            raise ValueError("tokenizer returned different input_ids and offset_mapping lengths")
        return token_ids, offsets, "offset_mapping"
    except (AttributeError, TypeError, ValueError, NotImplementedError):
        fallback = getattr(tokenizer, "encode_with_offsets", None)
        if fallback is None:
            raise ValueError(
                "tokenizer must support return_offsets_mapping=True or encode_with_offsets(text)"
            )
        token_ids, offsets = fallback(text)
        if len(token_ids) != len(offsets):
            raise ValueError("fallback tokenizer returned different ids and offsets lengths")
        return list(token_ids), [(int(start), int(end)) for start, end in offsets], "fallback"


def _extract_input_ids(encoded: Any) -> list[int]:
    input_ids = _get_encoded_value(encoded, "input_ids")
    if input_ids is None:
        raise ValueError("tokenizer response did not include input_ids")
    if input_ids and isinstance(input_ids[0], list):
        if len(input_ids) != 1:
            raise ValueError("batched tokenization is not supported for prompt packs")
        input_ids = input_ids[0]
    return [int(token_id) for token_id in input_ids]


def _extract_offset_mapping(encoded: Any) -> list[tuple[int, int]] | None:
    offsets = _get_encoded_value(encoded, "offset_mapping")
    if offsets is None:
        return None
    if (
        offsets
        and isinstance(offsets[0], list)
        and offsets[0]
        and isinstance(offsets[0][0], (tuple, list))
    ):
        if len(offsets) != 1:
            raise ValueError("batched offset mappings are not supported for prompt packs")
        offsets = offsets[0]
    return [(int(start), int(end)) for start, end in offsets]


def _get_encoded_value(encoded: Any, key: str) -> Any:
    if isinstance(encoded, dict):
        return encoded.get(key)
    return getattr(encoded, key, None)


def _evidence_by_doc(example: DiagnosticExample) -> dict[int, list[str]]:
    evidence: dict[int, list[str]] = {doc.doc_id: [] for doc in example.documents}
    for item in example.evidence:
        evidence[item.doc_id].append(item.text)
    return evidence
