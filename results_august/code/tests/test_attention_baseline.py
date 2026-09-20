from __future__ import annotations

import pytest

from safekv.attention_baseline import (
    aggregate_query_attention,
    candidate_positions_from_ranges,
    fp32_selection_attention_forward,
    positions_to_ranges,
    rank_candidate_positions,
    selected_count,
)
from safekv.data_schema import TokenRange


def test_aggregate_query_attention_excludes_query_keys():
    torch = pytest.importorskip("torch")
    layer1 = torch.tensor([[[[0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]]]])
    layer2 = torch.tensor([[[[0.3, 0.1, 0.2, 0.4], [0.1, 0.5, 0.2, 0.2]]]])
    scores = aggregate_query_attention(
        [layer1, layer2], context_length=2, query_length=2
    )
    assert scores == pytest.approx([0.225, 0.275])


def test_candidate_ranking_and_ranges_are_deterministic():
    candidates = candidate_positions_from_ranges(
        [TokenRange(1, 3), TokenRange(5, 7)], context_length=8
    )
    ranked = rank_candidate_positions(
        [0.0, 0.4, 0.9, 0.0, 0.0, 0.9, 0.2, 0.0], candidates
    )
    assert ranked == [2, 5, 1, 6]
    assert positions_to_ranges(ranked[:3]) == [TokenRange(1, 3), TokenRange(5, 6)]


@pytest.mark.parametrize(
    ("candidate_count", "fraction", "expected"),
    [(0, 0.2, 0), (3, 0.0, 0), (3, 0.1, 1), (10, 0.16, 1), (10, 1.0, 10)],
)
def test_selected_count(candidate_count, fraction, expected):
    assert selected_count(candidate_count, fraction) == expected


def test_candidate_overlap_is_rejected():
    with pytest.raises(ValueError, match="overlap"):
        candidate_positions_from_ranges(
            [TokenRange(1, 4), TokenRange(3, 5)], context_length=8
        )


def test_fp32_selection_attention_avoids_fp16_qk_overflow():
    torch = pytest.importorskip("torch")

    class Module:
        num_key_value_groups = 1

    query = torch.full((1, 1, 1, 2), 60_000.0, dtype=torch.float16)
    key = torch.full((1, 1, 2, 2), 60_000.0, dtype=torch.float16)
    value = torch.tensor([[[[1.0, 2.0], [3.0, 4.0]]]], dtype=torch.float16)
    output, weights = fp32_selection_attention_forward(
        Module(), query, key, value, None, scaling=2**-0.5
    )
    assert torch.isfinite(weights).all()
    assert torch.isfinite(output).all()
    assert weights.float().sum().item() == pytest.approx(1.0)
