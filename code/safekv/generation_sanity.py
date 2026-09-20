"""Pure helpers for generation sanity checks."""

from __future__ import annotations

from collections import Counter
from typing import Any


def first_token_mismatch(
    manual_tokens: list[int], model_tokens: list[int]
) -> dict[str, int | None] | None:
    max_len = max(len(manual_tokens), len(model_tokens))
    for index in range(max_len):
        manual_token = manual_tokens[index] if index < len(manual_tokens) else None
        model_token = model_tokens[index] if index < len(model_tokens) else None
        if manual_token != model_token:
            return {
                "index": index,
                "manual_token": manual_token,
                "model_generate_token": model_token,
            }
    return None


def category_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row["category"]) for row in rows)
    return dict(sorted(counts.items()))


def first_failed_check(checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    for check in checks:
        if not check.get("match", False):
            return check
    return None


def format_first_mismatch(check: dict[str, Any]) -> str:
    mismatch = check.get("first_mismatch") or {}
    return (
        "First generation mismatch: "
        f"example_id={check.get('example_id')} "
        f"category={check.get('category')} "
        f"token_index={mismatch.get('index')} "
        f"manual_token={mismatch.get('manual_token')} "
        f"model_generate_token={mismatch.get('model_generate_token')} "
        f"manual_text={check.get('manual_text')!r} "
        f"model_generate_text={check.get('model_generate_text')!r}"
    )
