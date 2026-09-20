"""Operational query-attention token ranking for local-repair baselines.

The selector in this module uses only attention produced by forwarding the
current query against the already composed cache.  Full-prefill states and
gold support labels are deliberately absent from the interface so the
selection rule cannot accidentally depend on oracle information.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from safekv.data_schema import TokenRange


def fp32_selection_attention_forward(
    module: Any,
    query: Any,
    key: Any,
    value: Any,
    attention_mask: Any,
    scaling: float,
    dropout: float = 0.0,
    **_kwargs: Any,
) -> tuple[Any, Any]:
    """Numerically stable eager attention used only by the selector pass.

    Transformers' generic eager implementation forms ``QK^T`` in the model
    dtype before its float32 softmax.  FP16 Q/K can therefore overflow before
    the upcast.  This implementation performs QK, masking, softmax, and AV in
    float32, then casts only the attention output back to the model dtype.  It
    returns float32 weights for auditable token ranking.
    """

    import torch

    _ = dropout
    groups = int(getattr(module, "num_key_value_groups", 1))
    if groups < 1:
        raise ValueError("num_key_value_groups must be positive")
    if groups > 1:
        key = key.repeat_interleave(groups, dim=1)
        value = value.repeat_interleave(groups, dim=1)
    weights = torch.matmul(query.float(), key.float().transpose(2, 3)) * float(
        scaling
    )
    if attention_mask is not None:
        weights = weights + attention_mask[:, :, :, : key.shape[-2]].float()
    weights = torch.softmax(weights, dim=-1, dtype=torch.float32)
    output = torch.matmul(weights, value.float())
    output = output.transpose(1, 2).contiguous().to(query.dtype)
    return output, weights


def aggregate_query_attention(
    attentions: Iterable[Any],
    *,
    context_length: int,
    query_length: int,
) -> list[float]:
    """Average attention to each cached context token over layers/heads/query.

    Expected tensors have shape ``[batch, heads, query, key]``.  Only cached
    context keys are scored; attention to query tokens is excluded.
    """

    import torch

    layers = list(attentions)
    if not layers:
        raise ValueError("model returned no attention tensors")
    if context_length < 0 or query_length <= 0:
        raise ValueError("context_length must be nonnegative and query_length positive")

    scores = torch.zeros(context_length, dtype=torch.float64)
    for layer_index, attention in enumerate(layers):
        if attention is None or not hasattr(attention, "shape"):
            raise ValueError(f"attention layer {layer_index} is missing")
        if attention.ndim != 4:
            raise ValueError(
                f"attention layer {layer_index} must be rank 4, got {attention.ndim}"
            )
        if int(attention.shape[0]) != 1:
            raise ValueError("attention baseline requires batch size 1")
        if int(attention.shape[-2]) != query_length:
            raise ValueError(
                "attention query axis does not match the forwarded query length"
            )
        if int(attention.shape[-1]) < context_length:
            raise ValueError("attention key axis is shorter than the cached context")
        context_attention = attention[..., :context_length]
        if not torch.isfinite(context_attention).all():
            nonfinite = int((~torch.isfinite(context_attention)).sum().item())
            raise ValueError(
                f"attention layer {layer_index} contains {nonfinite} non-finite "
                "context weights"
            )
        scores += (
            context_attention.detach()
            .float()
            .mean(dim=(0, 1, 2))
            .double()
            .cpu()
        )
    scores /= len(layers)
    if not torch.isfinite(scores).all():
        raise ValueError("attention scores contain non-finite values")
    return scores.tolist()


def candidate_positions_from_ranges(
    ranges: Iterable[TokenRange],
    *,
    context_length: int,
) -> list[int]:
    positions = sorted(
        position
        for token_range in ranges
        for position in range(token_range.start, token_range.end)
    )
    if len(positions) != len(set(positions)):
        raise ValueError("candidate token ranges overlap")
    if positions and (positions[0] < 0 or positions[-1] >= context_length):
        raise ValueError("candidate token position lies outside cached context")
    return positions


def rank_candidate_positions(
    scores: list[float],
    candidate_positions: Iterable[int],
) -> list[int]:
    candidates = list(candidate_positions)
    if any(position < 0 or position >= len(scores) for position in candidates):
        raise ValueError("candidate position has no attention score")
    if any(not math.isfinite(float(scores[position])) for position in candidates):
        raise ValueError("candidate attention score is non-finite")
    return sorted(candidates, key=lambda position: (-float(scores[position]), position))


def selected_count(candidate_count: int, fraction: float) -> int:
    if candidate_count < 0:
        raise ValueError("candidate_count must be nonnegative")
    if not math.isfinite(fraction) or fraction < 0.0 or fraction > 1.0:
        raise ValueError("fraction must be finite and in [0, 1]")
    if candidate_count == 0 or fraction == 0.0:
        return 0
    return min(candidate_count, max(1, int(math.floor(candidate_count * fraction))))


def positions_to_ranges(positions: Iterable[int]) -> list[TokenRange]:
    ordered = sorted(positions)
    if len(ordered) != len(set(ordered)):
        raise ValueError("selected positions contain duplicates")
    if not ordered:
        return []
    ranges: list[TokenRange] = []
    start = ordered[0]
    previous = ordered[0]
    for position in ordered[1:]:
        if position == previous + 1:
            previous = position
            continue
        ranges.append(TokenRange(start, previous + 1))
        start = position
        previous = position
    ranges.append(TokenRange(start, previous + 1))
    return ranges
