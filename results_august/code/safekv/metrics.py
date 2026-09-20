"""Small logit-preservation metrics for Milestone 3A."""

from __future__ import annotations

from typing import Any


def logit_kl_divergence(full_logits: Any, method_logits: Any) -> float:
    import torch

    full = _as_float_tensor(full_logits)
    method = _as_float_tensor(method_logits)
    full_log_probs = torch.log_softmax(full, dim=-1)
    method_log_probs = torch.log_softmax(method, dim=-1)
    full_probs = torch.exp(full_log_probs)
    value = float(torch.sum(full_probs * (full_log_probs - method_log_probs)).item())
    return _clamp_tiny_negative(value)


def logit_js_divergence(full_logits: Any, method_logits: Any) -> float:
    import torch

    full = _as_float_tensor(full_logits)
    method = _as_float_tensor(method_logits)
    p = torch.softmax(full, dim=-1)
    q = torch.softmax(method, dim=-1)
    m = 0.5 * (p + q)
    value = float(
        0.5 * torch.sum(p * (torch.log(p.clamp_min(1e-30)) - torch.log(m.clamp_min(1e-30))))
        + 0.5
        * torch.sum(q * (torch.log(q.clamp_min(1e-30)) - torch.log(m.clamp_min(1e-30))))
    )
    return _clamp_tiny_negative(value)


def max_abs_logit_diff(full_logits: Any, method_logits: Any) -> float:
    import torch

    return float(torch.max(torch.abs(_as_float_tensor(full_logits) - _as_float_tensor(method_logits))).item())


def mean_abs_logit_diff(full_logits: Any, method_logits: Any) -> float:
    import torch

    return float(torch.mean(torch.abs(_as_float_tensor(full_logits) - _as_float_tensor(method_logits))).item())


def topk_token_ids(logits: Any, k: int) -> list[int]:
    import torch

    tensor = _as_float_tensor(logits)
    _, indices = torch.topk(tensor, k=min(k, tensor.numel()))
    return [int(index) for index in indices.tolist()]


def topk_overlap(full_logits: Any, method_logits: Any, k: int) -> float:
    full = set(topk_token_ids(full_logits, k))
    method = set(topk_token_ids(method_logits, k))
    if not full:
        return 0.0
    return len(full & method) / k


def logit_preservation_metrics(
    full_logits: Any,
    method_logits: Any,
    tokenizer: Any | None = None,
) -> dict[str, Any]:
    full_top1 = topk_token_ids(full_logits, 1)[0]
    method_top1 = topk_token_ids(method_logits, 1)[0]
    return {
        "first_token_kl_full_to_method": logit_kl_divergence(full_logits, method_logits),
        "first_token_js_divergence": logit_js_divergence(full_logits, method_logits),
        "max_abs_logit_diff": max_abs_logit_diff(full_logits, method_logits),
        "mean_abs_logit_diff": mean_abs_logit_diff(full_logits, method_logits),
        "top1_match": full_top1 == method_top1,
        "top5_overlap": topk_overlap(full_logits, method_logits, 5),
        "top10_overlap": topk_overlap(full_logits, method_logits, 10),
        "argmax_full_token": full_top1,
        "argmax_method_token": method_top1,
        "argmax_full_decoded": _decode_token(tokenizer, full_top1),
        "argmax_method_decoded": _decode_token(tokenizer, method_top1),
    }


def _as_float_tensor(logits: Any):
    import torch

    if not hasattr(logits, "detach"):
        return torch.tensor(logits, dtype=torch.float32)
    tensor = logits.detach()
    if tensor.ndim == 2:
        if tensor.shape[0] != 1:
            raise ValueError("expected one row of logits")
        tensor = tensor[0]
    return tensor.float().cpu()


def _decode_token(tokenizer: Any | None, token_id: int) -> str:
    if tokenizer is None or not hasattr(tokenizer, "decode"):
        return str(token_id)
    return str(tokenizer.decode([token_id], skip_special_tokens=False))


def _clamp_tiny_negative(value: float, tolerance: float = 1e-6) -> float:
    if value < 0.0 and abs(value) < tolerance:
        return 0.0
    return value
