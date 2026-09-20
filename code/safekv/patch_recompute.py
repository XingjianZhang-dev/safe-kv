"""Oracle cache patching helpers for Milestone 4A."""

from __future__ import annotations

import hashlib
import re
import random
from typing import Any

from safekv.cache_ops import cache_seq_len, clone_legacy_cache, to_legacy_cache
from safekv.data_schema import DiagnosticExample, PromptPack, SpanInfo, TokenRange


def merge_token_ranges(ranges: list[TokenRange]) -> list[TokenRange]:
    if not ranges:
        return []
    sorted_ranges = sorted(ranges, key=lambda token_range: (token_range.start, token_range.end))
    merged = [sorted_ranges[0]]
    for token_range in sorted_ranges[1:]:
        previous = merged[-1]
        if token_range.start < previous.end:
            merged[-1] = TokenRange(previous.start, max(previous.end, token_range.end))
        else:
            merged.append(token_range)
    return merged


def token_range_intersection(left: TokenRange, right: TokenRange) -> TokenRange | None:
    start = max(left.start, right.start)
    end = min(left.end, right.end)
    if end <= start:
        return None
    return TokenRange(start, end)


def clip_token_range(token_range: TokenRange, bounds: TokenRange) -> TokenRange | None:
    return token_range_intersection(token_range, bounds)


def expand_and_clip_token_range(
    token_range: TokenRange,
    expand_window_tokens: int,
    bounds: TokenRange,
) -> TokenRange | None:
    if expand_window_tokens < 0:
        raise ValueError("expand_window_tokens must be non-negative")
    expanded = TokenRange(
        max(0, token_range.start - expand_window_tokens),
        token_range.end + expand_window_tokens,
    )
    return clip_token_range(expanded, bounds)


def token_count(ranges: list[TokenRange]) -> int:
    return sum(token_range.length for token_range in merge_token_ranges(ranges))


def full_doc_patch_ranges(pack: PromptPack) -> list[TokenRange]:
    return merge_token_ranges(list(pack.doc_ranges))


def oracle_evidence_doc_patch_ranges(
    example: DiagnosticExample,
    pack: PromptPack,
) -> list[TokenRange]:
    doc_ids = {evidence.doc_id for evidence in example.evidence}
    if example.category == "conflict":
        doc_ids.update(example.conflicting_docs)
    doc_ranges_by_id = {
        doc.doc_id: token_range
        for doc, token_range in zip(example.documents, pack.doc_ranges, strict=True)
    }
    return merge_token_ranges(
        [doc_ranges_by_id[doc_id] for doc_id in sorted(doc_ids) if doc_id in doc_ranges_by_id]
    )


def oracle_evidence_span_patch_ranges(
    pack: PromptPack,
    expand_window_tokens: int = 0,
) -> list[TokenRange]:
    return oracle_evidence_span_window_patch_ranges(
        pack,
        expand_window_tokens=expand_window_tokens,
    )


def oracle_evidence_span_window_patch_ranges(
    pack: PromptPack,
    expand_window_tokens: int = 0,
) -> list[TokenRange]:
    doc_text_ranges_by_id = _doc_text_ranges_by_id(pack)
    ranges: list[TokenRange] = []
    for span in evidence_spans(pack):
        bounds = doc_text_ranges_by_id[span.doc_id]
        clipped = expand_and_clip_token_range(
            span.token_range,
            expand_window_tokens=expand_window_tokens,
            bounds=bounds,
        )
        if clipped is not None:
            ranges.append(clipped)
    return merge_token_ranges(ranges)


def oracle_evidence_suffix_patch_ranges(pack: PromptPack) -> list[TokenRange]:
    return suffix_ranges_for_spans(pack, evidence_spans(pack))


def oracle_evidence_sentence_to_doc_end_patch_ranges(pack: PromptPack) -> list[TokenRange]:
    # SpanInfo is sentence-like in the current diagnostic builder. Keeping this
    # separate makes the intended causal-closure ablation explicit.
    return suffix_ranges_for_spans(pack, evidence_spans(pack))


def oracle_support_and_conflict_span_patch_ranges(
    example: DiagnosticExample,
    pack: PromptPack,
) -> list[TokenRange]:
    spans = support_and_conflict_spans(example, pack)
    return merge_token_ranges([span.token_range for span in spans])


def oracle_support_and_conflict_suffix_patch_ranges(
    example: DiagnosticExample,
    pack: PromptPack,
) -> list[TokenRange]:
    return suffix_ranges_for_spans(pack, support_and_conflict_spans(example, pack))


def suffix_ranges_for_spans(pack: PromptPack, spans: list[SpanInfo]) -> list[TokenRange]:
    doc_text_ranges_by_id = _doc_text_ranges_by_id(pack)
    ranges: list[TokenRange] = []
    for span in spans:
        bounds = doc_text_ranges_by_id[span.doc_id]
        if bounds.end <= span.token_range.start:
            continue
        ranges.append(TokenRange(max(span.token_range.start, bounds.start), bounds.end))
    return merge_token_ranges(ranges)


def support_and_conflict_spans(
    example: DiagnosticExample,
    pack: PromptPack,
) -> list[SpanInfo]:
    selected = evidence_spans(pack)
    if example.category != "conflict":
        return selected

    selected_ids = {span.span_id for span in selected}
    for doc_id in example.conflicting_docs:
        conflict_span = best_conflict_span(example, pack, doc_id)
        if conflict_span is not None and conflict_span.span_id not in selected_ids:
            selected.append(conflict_span)
            selected_ids.add(conflict_span.span_id)
    return selected


def best_conflict_span(
    example: DiagnosticExample,
    pack: PromptPack,
    doc_id: int,
) -> SpanInfo | None:
    candidates = [span for span in pack.span_ranges if span.doc_id == doc_id]
    if not candidates:
        return None
    question_terms = lexical_terms(example.question)
    gold_terms = lexical_terms(example.gold_answer)

    def score(span: SpanInfo) -> tuple[float, int, int]:
        span_terms = lexical_terms(span.text)
        overlap = len(span_terms & question_terms) / max(1, len(question_terms))
        answerish_terms = {
            term
            for term in span_terms
            if (any(char.isdigit() for char in term) or term in {"am", "pm"})
            and term not in gold_terms
        }
        conflict_role_bonus = 0.25 if span.role == "conflict" else 0.0
        answerish_bonus = 0.5 if answerish_terms else 0.0
        return (
            overlap + answerish_bonus + conflict_role_bonus,
            span.token_range.length,
            -span.token_range.start,
        )

    return max(candidates, key=score)


def evidence_spans(pack: PromptPack) -> list[SpanInfo]:
    evidence_span_ids = set(pack.evidence_span_ids)
    return [
        span
        for span in pack.span_ranges
        if span.span_id in evidence_span_ids or span.contains_gold_evidence
    ]


def lexical_terms(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", text)
        if token and token.lower() not in _STOPWORDS
    }


def random_span_patch_ranges_same_budget(
    pack: PromptPack,
    target_token_count: int,
    seed: int,
) -> list[TokenRange]:
    if target_token_count <= 0:
        return []
    candidate_positions: list[int] = []
    for doc_text_range in pack.doc_text_ranges:
        candidate_positions.extend(range(doc_text_range.start, doc_text_range.end))
    if not candidate_positions:
        return []
    sample_count = min(target_token_count, len(candidate_positions))
    rng = random.Random(seed)
    sampled = sorted(rng.sample(candidate_positions, sample_count))
    return _positions_to_ranges(sampled)


def stable_example_seed(base_seed: int, example_id: str, method: str = "") -> int:
    digest = hashlib.sha256(f"{base_seed}:{example_id}:{method}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


def validate_patch_ranges_within_documents(
    ranges: list[TokenRange],
    pack: PromptPack,
) -> None:
    for token_range in ranges:
        if token_range.end > pack.query_token_range.start:
            raise ValueError(
                f"patch range {token_range.start}:{token_range.end} crosses into query tokens"
            )
        if not any(_range_contains(doc_range, token_range) for doc_range in pack.doc_ranges):
            raise ValueError(
                f"patch range {token_range.start}:{token_range.end} is not contained in one document"
            )


def replace_cache_slices(
    base_cache: Any,
    donor_cache: Any,
    ranges: list[TokenRange],
    dim: int = -2,
) -> Any:
    base = clone_legacy_cache(base_cache)
    donor = to_legacy_cache(donor_cache)
    base_len = cache_seq_len(base)
    donor_len = cache_seq_len(donor)
    if len(base) != len(donor):
        raise ValueError(f"cache layer count mismatch: base={len(base)} donor={len(donor)}")

    merged_ranges = merge_token_ranges(ranges)
    for token_range in merged_ranges:
        if token_range.end > base_len:
            raise ValueError(
                f"patch range {token_range.start}:{token_range.end} exceeds base length {base_len}"
            )
        if token_range.end > donor_len:
            raise ValueError(
                f"patch range {token_range.start}:{token_range.end} exceeds donor length {donor_len}"
            )

    patched = []
    for layer_index, ((base_key, base_value), (donor_key, donor_value)) in enumerate(zip(base, donor, strict=True)):
        _validate_replacement_tensors(
            base_key,
            donor_key,
            base_len=base_len,
            donor_len=donor_len,
            dim=dim,
            label=f"cache layer {layer_index} key",
        )
        _validate_replacement_tensors(
            base_value,
            donor_value,
            base_len=base_len,
            donor_len=donor_len,
            dim=dim,
            label=f"cache layer {layer_index} value",
        )
        for token_range in merged_ranges:
            _replace_tensor_slice(base_key, donor_key, token_range, dim=dim)
            _replace_tensor_slice(base_value, donor_value, token_range, dim=dim)
        patched.append((base_key, base_value))

    patched_cache = tuple(patched)
    if cache_seq_len(patched_cache) != base_len:
        raise ValueError("patched cache length changed unexpectedly")
    return patched_cache


def _replace_tensor_slice(base_tensor: Any, donor_tensor: Any, token_range: TokenRange, dim: int) -> None:
    base_index = [slice(None)] * base_tensor.ndim
    donor_index = [slice(None)] * donor_tensor.ndim
    base_index[dim] = slice(token_range.start, token_range.end)
    donor_index[dim] = slice(token_range.start, token_range.end)
    base_slice = base_tensor[tuple(base_index)]
    donor_slice = donor_tensor[tuple(donor_index)]
    if base_slice.shape != donor_slice.shape:
        raise ValueError(
            "replacement slice shape mismatch: "
            f"base={tuple(base_slice.shape)} donor={tuple(donor_slice.shape)}"
        )
    base_slice[...] = donor_slice.to(
        device=base_tensor.device,
        dtype=base_tensor.dtype,
    )


def _validate_replacement_tensors(
    base_tensor: Any,
    donor_tensor: Any,
    *,
    base_len: int,
    donor_len: int,
    dim: int,
    label: str,
) -> None:
    if base_tensor.ndim != donor_tensor.ndim:
        raise ValueError(f"{label} ndim mismatch")
    normalized_dim = dim if dim >= 0 else base_tensor.ndim + dim
    if normalized_dim < 0 or normalized_dim >= base_tensor.ndim:
        raise ValueError(f"{label} invalid sequence dimension {dim}")
    if int(base_tensor.shape[normalized_dim]) != base_len:
        raise ValueError(f"{label} base sequence length mismatch")
    if int(donor_tensor.shape[normalized_dim]) != donor_len:
        raise ValueError(f"{label} donor sequence length mismatch")
    base_nonsequence = tuple(
        size for axis, size in enumerate(base_tensor.shape) if axis != normalized_dim
    )
    donor_nonsequence = tuple(
        size for axis, size in enumerate(donor_tensor.shape) if axis != normalized_dim
    )
    if base_nonsequence != donor_nonsequence:
        raise ValueError(
            f"{label} non-sequence shape mismatch: "
            f"base={tuple(base_tensor.shape)} donor={tuple(donor_tensor.shape)}"
        )


def _doc_text_ranges_by_id(pack: PromptPack) -> dict[int, TokenRange]:
    return {
        doc.doc_id: token_range
        for doc, token_range in zip(pack.doc_char_ranges, pack.doc_text_ranges, strict=True)
    }


def _positions_to_ranges(positions: list[int]) -> list[TokenRange]:
    if not positions:
        return []
    ranges: list[TokenRange] = []
    start = positions[0]
    previous = positions[0]
    for position in positions[1:]:
        if position == previous + 1:
            previous = position
            continue
        ranges.append(TokenRange(start, previous + 1))
        start = position
        previous = position
    ranges.append(TokenRange(start, previous + 1))
    return ranges


def _range_contains(container: TokenRange, token_range: TokenRange) -> bool:
    return container.start <= token_range.start and token_range.end <= container.end


_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "does",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "who",
    "with",
}


__all__ = [
    "best_conflict_span",
    "clip_token_range",
    "evidence_spans",
    "expand_and_clip_token_range",
    "full_doc_patch_ranges",
    "lexical_terms",
    "merge_token_ranges",
    "oracle_evidence_doc_patch_ranges",
    "oracle_evidence_sentence_to_doc_end_patch_ranges",
    "oracle_evidence_span_patch_ranges",
    "oracle_evidence_span_window_patch_ranges",
    "oracle_evidence_suffix_patch_ranges",
    "oracle_support_and_conflict_span_patch_ranges",
    "oracle_support_and_conflict_suffix_patch_ranges",
    "random_span_patch_ranges_same_budget",
    "replace_cache_slices",
    "stable_example_seed",
    "suffix_ranges_for_spans",
    "support_and_conflict_spans",
    "token_range_intersection",
    "token_count",
    "validate_patch_ranges_within_documents",
]
