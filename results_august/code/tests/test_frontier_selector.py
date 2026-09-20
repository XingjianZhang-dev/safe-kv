from __future__ import annotations

from safekv_ipm.frontier_selector import (
    FRONTIER_FEATURE_NAMES,
    FrontierCandidate,
    choose_frontier_actions,
    frontier_feature_vector,
)


def example():
    return {
        "id": "x",
        "question": "Which city hosted the 2024 event?",
        "documents": [
            {"title": "Noise", "text": "Unrelated text", "retrieval_score": 0.1},
            {"title": "Event", "text": "Held in Paris in 2024", "retrieval_score": 0.9},
            {"title": "Paris", "text": "Paris is in France", "retrieval_score": 0.5},
        ],
        "gold_answer": "forbidden gold",
        "evidence": [{"doc_id": 1}],
        "sampled_mismatch_mask": [1, 0, 1],
    }


def test_frontier_features_ignore_gold_and_mismatch_fields():
    original = example()
    changed = example()
    changed["gold_answer"] = "different"
    changed["evidence"] = [{"doc_id": 2}]
    changed["sampled_mismatch_mask"] = [0, 0, 0]
    assert frontier_feature_vector(original, start=1, prompt_length=100) == frontier_feature_vector(
        changed, start=1, prompt_length=100
    )
    assert len(frontier_feature_vector(original, start=3, prompt_length=100)) == len(
        FRONTIER_FEATURE_NAMES
    )


def test_frontier_action_is_latest_eligible_start():
    candidates = [
        FrontierCandidate("x", "g", "d", "c", start, 3, False, 1 - start / 3, (0.0,))
        for start in range(4)
    ]
    actions = choose_frontier_actions(candidates, [0.1, 0.2, 0.8, 0.4], threshold=0.5)
    assert actions["x"].start == 3
