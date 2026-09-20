import pytest
import torch

from safekv.cache_ops import (
    cache_device_dtype_summary,
    cache_num_layers,
    cache_seq_len,
    clone_legacy_cache,
    concat_legacy_caches,
    slice_legacy_cache,
    validate_cache_compatible,
)


def _fake_cache(seq_len: int, heads: int = 2):
    return tuple(
        (
            torch.ones(1, heads, seq_len, 4),
            torch.zeros(1, heads, seq_len, 4),
        )
        for _ in range(2)
    )


def _arange_cache(seq_len: int, heads: int = 1):
    key = torch.arange(seq_len, dtype=torch.float32).reshape(1, 1, seq_len, 1)
    value = key + 100
    return tuple((key.repeat(1, heads, 1, 4), value.repeat(1, heads, 1, 4)) for _ in range(2))


def test_concat_legacy_caches_shapes() -> None:
    cache = concat_legacy_caches([_fake_cache(3), _fake_cache(5)])

    assert cache_num_layers(cache) == 2
    assert cache_seq_len(cache) == 8
    assert cache[0][0].shape == (1, 2, 8, 4)
    assert cache[0][1].shape == (1, 2, 8, 4)


def test_cache_device_dtype_summary() -> None:
    summary = cache_device_dtype_summary(_fake_cache(3))

    assert summary["num_layers"] == 2
    assert summary["seq_len"] == 3
    assert summary["device"] == "cpu"
    assert summary["dtype"] == "float32"


def test_validate_cache_compatible_rejects_incompatible_shapes() -> None:
    with pytest.raises(ValueError, match="incompatible shape"):
        validate_cache_compatible([_fake_cache(3, heads=2), _fake_cache(3, heads=3)])


def test_slice_legacy_cache_returns_expected_seq_len_and_values() -> None:
    cache = _fake_cache(8)
    sliced = slice_legacy_cache(cache, 2, 6)

    assert cache_seq_len(sliced) == 4
    assert torch.equal(sliced[0][0], cache[0][0][:, :, 2:6, :])
    assert torch.equal(sliced[0][1], cache[0][1][:, :, 2:6, :])


def test_slice_legacy_cache_excludes_prefix_region() -> None:
    cache = _arange_cache(7)
    doc_slice = slice_legacy_cache(cache, 3, 7)

    assert cache_seq_len(doc_slice) == 4
    assert doc_slice[0][0][0, 0, :, 0].tolist() == [3.0, 4.0, 5.0, 6.0]
    assert 0.0 not in doc_slice[0][0][0, 0, :, 0].tolist()


def test_slice_legacy_cache_rejects_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="exceeds seq_len"):
        slice_legacy_cache(_fake_cache(3), 0, 4)


def test_clone_legacy_cache_detaches_storage() -> None:
    cache = _fake_cache(3)
    cloned = clone_legacy_cache(cache)

    assert cache_seq_len(cloned) == 3
    assert torch.equal(cloned[0][0], cache[0][0])
    assert cloned[0][0].data_ptr() != cache[0][0].data_ptr()
