"""Cache utilities for SAFE-KV smoke experiments.

The canonical representation in this repository is the HuggingFace legacy
tuple format: one ``(key, value)`` pair per layer.
"""

from __future__ import annotations

from typing import Any


LegacyCache = tuple[tuple[Any, Any], ...]


def to_legacy_cache(past_key_values: Any) -> LegacyCache:
    if hasattr(past_key_values, "to_legacy_cache"):
        past_key_values = past_key_values.to_legacy_cache()
    elif hasattr(past_key_values, "layers"):
        layers_from_cache: list[tuple[Any, Any]] = []
        for layer in past_key_values.layers:
            if not hasattr(layer, "keys") or not hasattr(layer, "values"):
                raise TypeError("cache layers must expose keys and values")
            layers_from_cache.append((layer.keys, layer.values))
        past_key_values = layers_from_cache
    if not isinstance(past_key_values, (tuple, list)):
        raise TypeError("past_key_values must be a legacy tuple/list or expose to_legacy_cache()")

    layers: list[tuple[Any, Any]] = []
    for layer in past_key_values:
        if not isinstance(layer, (tuple, list)) or len(layer) != 2:
            raise TypeError("each cache layer must be a (key, value) pair")
        key, value = layer
        layers.append((key, value))
    return tuple(layers)


def cache_num_layers(cache: Any) -> int:
    return len(to_legacy_cache(cache))


def cache_seq_len(cache: Any) -> int:
    legacy = to_legacy_cache(cache)
    if not legacy:
        return 0
    return int(legacy[0][0].shape[-2])


def cache_device_dtype_summary(cache: Any) -> dict[str, str | int]:
    legacy = to_legacy_cache(cache)
    if not legacy:
        return {"num_layers": 0, "seq_len": 0, "device": "unknown", "dtype": "unknown"}
    key = legacy[0][0]
    return {
        "num_layers": len(legacy),
        "seq_len": cache_seq_len(legacy),
        "device": str(key.device),
        "dtype": str(key.dtype).replace("torch.", ""),
    }


def validate_cache_compatible(caches: list[Any]) -> None:
    if not caches:
        raise ValueError("at least one cache is required")

    legacy_caches = [to_legacy_cache(cache) for cache in caches]
    expected_layers = len(legacy_caches[0])
    for cache_index, cache in enumerate(legacy_caches):
        if len(cache) != expected_layers:
            raise ValueError(
                f"cache {cache_index} has {len(cache)} layers; expected {expected_layers}"
            )

    for layer_index in range(expected_layers):
        ref_key, ref_value = legacy_caches[0][layer_index]
        for cache_index, cache in enumerate(legacy_caches[1:], start=1):
            key, value = cache[layer_index]
            _validate_tensor_compatible(
                key,
                ref_key,
                cache_index=cache_index,
                layer_index=layer_index,
                tensor_name="key",
            )
            _validate_tensor_compatible(
                value,
                ref_value,
                cache_index=cache_index,
                layer_index=layer_index,
                tensor_name="value",
            )


def concat_legacy_caches(caches: list[Any], dim: int = -2) -> LegacyCache:
    import torch

    validate_cache_compatible(caches)
    legacy_caches = [to_legacy_cache(cache) for cache in caches]
    num_layers = len(legacy_caches[0])
    concatenated: list[tuple[Any, Any]] = []
    for layer_index in range(num_layers):
        keys = [cache[layer_index][0] for cache in legacy_caches]
        values = [cache[layer_index][1] for cache in legacy_caches]
        concatenated.append((torch.cat(keys, dim=dim), torch.cat(values, dim=dim)))
    return tuple(concatenated)


def slice_legacy_cache(cache: Any, start: int, end: int, dim: int = -2) -> LegacyCache:
    legacy = to_legacy_cache(cache)
    if start < 0:
        raise ValueError("cache slice start must be non-negative")
    if end < start:
        raise ValueError("cache slice end must be >= start")
    if legacy:
        seq_len = int(legacy[0][0].shape[dim])
        if end > seq_len:
            raise ValueError(f"cache slice end {end} exceeds seq_len {seq_len}")

    sliced: list[tuple[Any, Any]] = []
    for key, value in legacy:
        index = [slice(None)] * key.ndim
        index[dim] = slice(start, end)
        sliced.append((key[tuple(index)], value[tuple(index)]))
    return tuple(sliced)


def clone_legacy_cache(cache: Any, detach: bool = True) -> LegacyCache:
    cloned: list[tuple[Any, Any]] = []
    for key, value in to_legacy_cache(cache):
        key_copy = key.detach() if detach and hasattr(key, "detach") else key
        value_copy = value.detach() if detach and hasattr(value, "detach") else value
        key_copy = key_copy.clone() if hasattr(key_copy, "clone") else key_copy
        value_copy = value_copy.clone() if hasattr(value_copy, "clone") else value_copy
        cloned.append((key_copy, value_copy))
    return tuple(cloned)


def legacy_cache_to_model_cache(cache: Any) -> Any:
    """Convert a legacy cache to a Transformers Cache object when available."""

    legacy = to_legacy_cache(cache)
    try:
        from transformers.cache_utils import DynamicCache

        if hasattr(DynamicCache, "from_legacy_cache"):
            return DynamicCache.from_legacy_cache(legacy)
        return DynamicCache(ddp_cache_data=legacy)
    except Exception:
        return legacy
    return legacy


def _validate_tensor_compatible(
    tensor: Any,
    reference: Any,
    cache_index: int,
    layer_index: int,
    tensor_name: str,
) -> None:
    if tensor.ndim != reference.ndim:
        raise ValueError(
            f"cache {cache_index} layer {layer_index} {tensor_name} ndim "
            f"{tensor.ndim} != {reference.ndim}"
        )
    if tensor.dtype != reference.dtype:
        raise ValueError(
            f"cache {cache_index} layer {layer_index} {tensor_name} dtype "
            f"{tensor.dtype} != {reference.dtype}"
        )
    if tensor.device != reference.device:
        raise ValueError(
            f"cache {cache_index} layer {layer_index} {tensor_name} device "
            f"{tensor.device} != {reference.device}"
        )
    comparable_shape = tensor.shape[:-2] + tensor.shape[-1:]
    reference_shape = reference.shape[:-2] + reference.shape[-1:]
    if comparable_shape != reference_shape:
        raise ValueError(
            f"cache {cache_index} layer {layer_index} {tensor_name} incompatible shape "
            f"{tuple(tensor.shape)} vs {tuple(reference.shape)}"
        )
