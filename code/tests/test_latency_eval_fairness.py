from types import SimpleNamespace

import torch

from safekv.cache_ops import cache_seq_len
from safekv.data_schema import TokenRange
from scripts.run_latency_eval import (
    full_prefill_first_token,
    query_first_token,
    recompute_contiguous_range,
)


class RecordingCacheModel:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        input_length = int(kwargs["input_ids"].shape[1])
        past = kwargs.get("past_key_values")
        past_length = cache_seq_len(past) if past is not None else 0
        total_length = past_length + input_length
        key = torch.zeros((1, 1, total_length, 2), dtype=torch.float32)
        value = torch.zeros_like(key)
        kept = int(kwargs.get("logits_to_keep", input_length))
        logits = torch.zeros((1, kept, 11), dtype=torch.float32)
        return SimpleNamespace(logits=logits, past_key_values=((key, value),))


def make_pack():
    return SimpleNamespace(
        full_input_ids=[10, 11, 12, 13, 14],
        query_token_range=TokenRange(3, 5),
    )


def make_cache(length: int):
    key = torch.zeros((1, 1, length, 2), dtype=torch.float32)
    value = torch.zeros_like(key)
    return ((key, value),)


def test_full_and_query_ttft_keep_only_final_logits_and_return_equal_lifetime_cache():
    model = RecordingCacheModel()
    loaded = SimpleNamespace(model=model, device="cpu")
    pack = make_pack()

    full = full_prefill_first_token(None, pack, loaded)
    query = query_first_token(pack, loaded, make_cache(3))

    assert model.calls[0]["logits_to_keep"] == 1
    assert model.calls[1]["logits_to_keep"] == 1
    assert set(full) == {"first_logits", "full_cache"}
    assert set(query) == {"first_logits", "full_cache"}
    assert full["first_logits"].shape == query["first_logits"].shape == (1, 11)
    assert cache_seq_len(full["full_cache"]) == 5
    assert cache_seq_len(query["full_cache"]) == 5


def test_suffix_recompute_limits_projection_and_preserves_total_cache_length():
    model = RecordingCacheModel()
    loaded = SimpleNamespace(model=model, device="cpu")
    pack = make_pack()

    repaired = recompute_contiguous_range(
        pack,
        loaded,
        make_cache(3),
        TokenRange(1, 3),
    )

    assert model.calls[0]["logits_to_keep"] == 1
    assert model.calls[0]["input_ids"].shape[1] == 2
    assert cache_seq_len(model.calls[0]["past_key_values"]) == 1
    assert cache_seq_len(repaired) == 3
