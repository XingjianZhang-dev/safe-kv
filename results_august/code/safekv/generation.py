"""Generation and answer-metric helpers for Milestone 2."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Any, Sequence


def normalize_answer(text: str) -> str:
    """Normalize free-form answers for deterministic exact/F1 checks."""

    text = text.lower()
    text = "".join(ch if ch not in string.punctuation else " " for ch in text)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def token_f1(prediction: str, gold: str) -> float:
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    overlap = Counter(pred_tokens) & Counter(gold_tokens)
    common = sum(overlap.values())
    if common == 0:
        return 0.0
    precision = common / len(pred_tokens)
    recall = common / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def exact_match(prediction: str, gold: str) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def compute_task_metrics(answer: str, gold_answer: str) -> dict[str, float | bool]:
    normalized_answer = normalize_answer(answer)
    normalized_gold = normalize_answer(gold_answer)
    return {
        "gold_exact_match": normalized_answer == normalized_gold,
        "gold_f1": token_f1(answer, gold_answer),
        "answer_contains_gold": bool(normalized_gold and normalized_gold in normalized_answer),
        "gold_contains_answer": bool(normalized_answer and normalized_answer in normalized_gold),
    }


def topk_from_logits(logits: Any, tokenizer: Any, k: int = 10) -> list[dict[str, Any]]:
    """Extract top-k token ids, decoded strings, and logits.

    Accepts a 1D torch tensor, a single-row tensor, or a plain sequence of
    numeric logits so tests do not need model downloads.
    """

    if k <= 0:
        raise ValueError("k must be positive")

    if hasattr(logits, "detach"):
        import torch

        tensor = logits.detach()
        if tensor.ndim == 2:
            if tensor.shape[0] != 1:
                raise ValueError("topk_from_logits expects one row of logits")
            tensor = tensor[0]
        values, indices = torch.topk(tensor.float().cpu(), k=min(k, tensor.numel()))
        pairs = [(int(index), float(value)) for index, value in zip(indices.tolist(), values.tolist())]
    else:
        values = _flatten_sequence(logits)
        pairs = sorted(enumerate(values), key=lambda item: item[1], reverse=True)[:k]
        pairs = [(int(index), float(value)) for index, value in pairs]

    return [
        {
            "token_id": token_id,
            "token": _decode_token(tokenizer, token_id),
            "logit": logit,
        }
        for token_id, logit in pairs
    ]


def trim_answer_on_newline(answer: str) -> str:
    return answer.split("\n", 1)[0].strip()


def should_stop_generated_text(
    decoded_text: str,
    stop_on_newline: bool,
    stop_strings: list[str] | None,
) -> bool:
    if stop_on_newline and "\n" in decoded_text:
        return True
    return any(stop and stop in decoded_text for stop in (stop_strings or []))


def trim_generated_answer(
    answer: str,
    stop_on_newline: bool,
    stop_strings: list[str] | None,
) -> str:
    cut_points: list[int] = []
    if stop_on_newline and "\n" in answer:
        cut_points.append(answer.index("\n"))
    for stop in stop_strings or []:
        if stop and stop in answer:
            cut_points.append(answer.index(stop))
    if cut_points:
        answer = answer[: min(cut_points)]
    return answer.strip()


def _flatten_sequence(values: Any) -> list[float]:
    if isinstance(values, Sequence) and values and isinstance(values[0], Sequence):
        if len(values) != 1:
            raise ValueError("topk_from_logits expects one row of logits")
        values = values[0]
    return [float(value) for value in values]


def _decode_token(tokenizer: Any, token_id: int) -> str:
    if hasattr(tokenizer, "decode"):
        return str(tokenizer.decode([token_id], skip_special_tokens=False))
    return str(token_id)
