"""Tokenization and document span helpers for SAFE-KV prompts."""

from __future__ import annotations

import re
from typing import Protocol


class SupportsEncode(Protocol):
    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        ...


class RegexTokenizer:
    """Small deterministic tokenizer for tests and local smoke checks.

    This is not intended to match model tokenization. Production runs should pass
    a HuggingFace tokenizer. The interface mirrors the part of that API used by
    the prompt builder.
    """

    def __init__(self) -> None:
        self._vocab: dict[str, int] = {}

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        del add_special_tokens
        ids: list[int] = []
        for token in _regex_tokens(text):
            if token not in self._vocab:
                self._vocab[token] = len(self._vocab) + 1
            ids.append(self._vocab[token])
        return ids

    def encode_with_offsets(self, text: str) -> tuple[list[int], list[tuple[int, int]]]:
        ids: list[int] = []
        offsets: list[tuple[int, int]] = []
        for token, start, end in _regex_tokens_with_offsets(text):
            if token not in self._vocab:
                self._vocab[token] = len(self._vocab) + 1
            ids.append(self._vocab[token])
            offsets.append((start, end))
        return ids, offsets


def encode_no_special(tokenizer: SupportsEncode, text: str) -> list[int]:
    """Tokenize text without adding BOS/EOS/chat-template tokens."""

    try:
        token_ids = tokenizer.encode(text, add_special_tokens=False)
    except TypeError:
        token_ids = tokenizer.encode(text)
    return list(token_ids)


def _regex_tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]|\s+", text, flags=re.UNICODE)


def _regex_tokens_with_offsets(text: str) -> list[tuple[str, int, int]]:
    return [
        (match.group(0), match.start(), match.end())
        for match in re.finditer(r"\w+|[^\w\s]|\s+", text, flags=re.UNICODE)
    ]


def split_doc_spans(text: str) -> list[tuple[int, int]]:
    """Split a document into inspectable sentence-like spans.

    The returned character ranges point into the original document text and do
    not include leading or trailing whitespace. Text without terminal punctuation
    is returned as one span.
    """

    ranges: list[tuple[int, int]] = []
    span_start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\n":
            _append_trimmed_range(ranges, text, span_start, index)
            span_start = index + 1
        elif char in ".!?" and _is_sentence_boundary(text, index):
            _append_trimmed_range(ranges, text, span_start, index + 1)
            span_start = index + 1
        index += 1

    _append_trimmed_range(ranges, text, span_start, len(text))
    return ranges


def _append_trimmed_range(
    ranges: list[tuple[int, int]], text: str, span_start: int, span_end: int
) -> None:
    while span_start < span_end and text[span_start].isspace():
        span_start += 1
    while span_end > span_start and text[span_end - 1].isspace():
        span_end -= 1
    if span_start < span_end:
        ranges.append((span_start, span_end))


def _is_sentence_boundary(text: str, punctuation_index: int) -> bool:
    abbreviations = ("Dr.", "Mr.", "Ms.", "Mrs.", "Prof.", "Sr.", "Jr.")
    for abbreviation in abbreviations:
        start = punctuation_index + 1 - len(abbreviation)
        if start >= 0 and text[start : punctuation_index + 1] == abbreviation:
            return False

    next_index = punctuation_index + 1
    return next_index == len(text) or text[next_index].isspace()
