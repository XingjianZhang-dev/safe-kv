import copy

import numpy as np
import pytest

from safekv_ipm.safety_gate import (
    FEATURE_NAMES,
    GateRecord,
    choose_max_coverage_threshold,
    dataset_stratified_group_split,
    policy_summary,
    runtime_feature_vector,
    wilson_interval,
)


def _example():
    return {
        "id": "hotpotqa_q1",
        "question": "Which city hosted the event in 2012?",
        "gold_answer": "forbidden",
        "evidence": [{"doc_id": 0, "text": "forbidden"}],
        "conflicting_docs": [1],
        "documents": [
            {
                "doc_id": 0,
                "title": "Event",
                "text": "The event was hosted in Paris in 2012.",
                "retrieval_score": 0.8,
                "role": "evidence",
            },
            {
                "doc_id": 1,
                "title": "Paris",
                "text": "Paris is a city in France with 2 million residents.",
                "retrieval_score": 0.3,
                "role": "distractor",
            },
        ],
    }


def _record(group, dataset, condition, unsafe):
    return GateRecord(
        example_id=f"{group}:{condition}",
        group_id=group,
        dataset=dataset,
        condition=condition,
        unsafe=unsafe,
        changed_and_gold_wrong=unsafe,
        features=(0.0,) * len(FEATURE_NAMES),
    )


def test_features_ignore_gold_evidence_roles_and_mismatch_annotations():
    base = _example()
    modified = copy.deepcopy(base)
    modified["gold_answer"] = "entirely different"
    modified["evidence"] = []
    modified["conflicting_docs"] = []
    modified["sampled_mismatch_mask"] = [True, False]
    modified["documents"][0]["role"] = "distractor"
    modified["documents"][1]["role"] = "evidence"

    first = runtime_feature_vector(base, prompt_length=128)
    second = runtime_feature_vector(modified, prompt_length=128)

    assert first == second
    assert len(first) == len(FEATURE_NAMES)
    assert all(np.isfinite(first))


def test_group_split_keeps_retrieval_conditions_together_and_is_deterministic():
    records = []
    for index in range(10):
        for condition in ("natural", "shuffle", "bm25", "dense"):
            records.append(_record(f"hotpotqa:q{index}", "hotpotqa", condition, index % 2 == 0))
    first = dataset_stratified_group_split(records, validation_fraction=0.3, seed=17)
    second = dataset_stratified_group_split(list(reversed(records)), validation_fraction=0.3, seed=17)

    assert first == second
    assert sum(split == "validation" for split in first.values()) == 3
    for record in records:
        assert first[record.group_id] in {"train", "validation"}


def test_threshold_maximizes_coverage_subject_to_each_dataset_ci_gate():
    records = []
    probabilities = []
    for dataset in ("a", "b"):
        for index in range(100):
            unsafe = index >= 95
            records.append(_record(f"{dataset}:q{index}", dataset, "natural", unsafe))
            probabilities.append(0.9 if unsafe else index / 1000.0)

    threshold, summary = choose_max_coverage_threshold(
        records,
        probabilities,
        minimum_dataset_lower_bound=0.95,
    )

    assert threshold == pytest.approx(0.094)
    assert summary["overall"]["reuse_rate"] == pytest.approx(0.95)
    assert summary["overall"]["unsafe_reuse_count"] == 0
    assert all(
        values["answer_preservation_wilson95_low"] >= 0.95
        for values in summary["by_dataset"].values()
    )


def test_policy_summary_counts_only_unsafe_reuse_as_behavior_failure():
    records = [
        _record("a:q1", "a", "natural", False),
        _record("a:q2", "a", "natural", True),
        _record("a:q3", "a", "natural", True),
    ]
    summary = policy_summary(records, [0.1, 0.2, 0.9], threshold=0.5)["overall"]
    assert summary["reuse_count"] == 2
    assert summary["fallback_count"] == 1
    assert summary["unsafe_reuse_count"] == 1
    assert summary["answer_preservation"] == pytest.approx(2 / 3)


def test_wilson_interval_known_boundary():
    low, high = wilson_interval(100, 100)
    assert low == pytest.approx(0.9630, abs=1e-4)
    assert high == pytest.approx(1.0)

