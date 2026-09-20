"""Leakage-controlled features and policy helpers for suffix-frontier selection."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from safekv_ipm.safety_gate import FEATURE_NAMES as GATE_FEATURE_NAMES
from safekv_ipm.safety_gate import runtime_feature_vector, wilson_interval


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
FRONTIER_FEATURE_NAMES: tuple[str, ...] = tuple(
    f"global__{name}" for name in GATE_FEATURE_NAMES
) + (
    "candidate_start_fraction",
    "suffix_document_fraction",
    "candidate_is_no_repair",
    "candidate_document_length_fraction",
    "candidate_retrieval_score_normalized",
    "candidate_query_overlap",
    "candidate_title_overlap",
    "boundary_adjacent_jaccard",
    "prefix_query_overlap_max",
    "prefix_query_overlap_mean",
    "suffix_query_overlap_max",
    "suffix_query_overlap_mean",
    "prefix_retrieval_score_max",
    "prefix_retrieval_score_mean",
    "suffix_retrieval_score_max",
    "suffix_retrieval_score_mean",
    "prefix_document_length_fraction",
    "suffix_document_length_fraction",
)


@dataclass(frozen=True)
class FrontierCandidate:
    example_id: str
    group_id: str
    dataset: str
    condition: str
    start: int
    num_documents: int
    unsafe: bool
    patch_ratio: float
    features: tuple[float, ...]


def _tokens(value: Any) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(str(value))]


def _mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _max(values: Sequence[float]) -> float:
    return float(max(values)) if values else 0.0


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def frontier_feature_vector(
    example: dict[str, Any],
    *,
    start: int,
    prompt_length: int,
) -> tuple[float, ...]:
    """Features available before generation for one possible suffix start."""

    documents = example.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("example must contain documents")
    count = len(documents)
    if not 0 <= start <= count:
        raise ValueError("frontier start must lie in [0, number of documents]")
    global_features = runtime_feature_vector(example, prompt_length=prompt_length)

    question_terms = set(_tokens(example.get("question", "")))
    denominator = max(1, len(question_terms))
    doc_tokens = [
        _tokens(f"{document.get('title', '')} {document.get('text', '')}")
        for document in documents
    ]
    doc_terms = [set(tokens) for tokens in doc_tokens]
    lengths = [float(len(tokens)) for tokens in doc_tokens]
    total_length = max(1.0, sum(lengths))
    scores = [float(document.get("retrieval_score", 0.0)) for document in documents]
    if not all(math.isfinite(score) for score in scores):
        raise ValueError("retrieval scores must be finite")
    minimum_score = min(scores)
    score_span = max(scores) - minimum_score
    normalized_scores = [
        (score - minimum_score) / score_span if score_span > 1e-12 else 0.0
        for score in scores
    ]
    overlaps = [len(question_terms & terms) / denominator for terms in doc_terms]
    title_overlaps = [
        len(question_terms & set(_tokens(document.get("title", "")))) / denominator
        for document in documents
    ]
    prefix_indices = list(range(start))
    suffix_indices = list(range(start, count))
    candidate_exists = start < count
    boundary_jaccard = (
        _jaccard(doc_terms[start - 1], doc_terms[start])
        if 0 < start < count
        else 0.0
    )

    candidate_features = (
        start / count,
        (count - start) / count,
        float(start == count),
        lengths[start] / total_length if candidate_exists else 0.0,
        normalized_scores[start] if candidate_exists else 0.0,
        overlaps[start] if candidate_exists else 0.0,
        title_overlaps[start] if candidate_exists else 0.0,
        boundary_jaccard,
        _max([overlaps[index] for index in prefix_indices]),
        _mean([overlaps[index] for index in prefix_indices]),
        _max([overlaps[index] for index in suffix_indices]),
        _mean([overlaps[index] for index in suffix_indices]),
        _max([normalized_scores[index] for index in prefix_indices]),
        _mean([normalized_scores[index] for index in prefix_indices]),
        _max([normalized_scores[index] for index in suffix_indices]),
        _mean([normalized_scores[index] for index in suffix_indices]),
        sum(lengths[index] for index in prefix_indices) / total_length,
        sum(lengths[index] for index in suffix_indices) / total_length,
    )
    values = tuple(float(value) for value in global_features) + candidate_features
    if len(values) != len(FRONTIER_FEATURE_NAMES):
        raise AssertionError("frontier feature contract length drifted")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("frontier features must be finite")
    return values


def choose_frontier_actions(
    candidates: Sequence[FrontierCandidate],
    unsafe_probabilities: Sequence[float],
    *,
    threshold: float,
) -> dict[str, FrontierCandidate | None]:
    if len(candidates) != len(unsafe_probabilities):
        raise ValueError("candidate and probability lengths differ")
    grouped: dict[str, list[tuple[FrontierCandidate, float]]] = {}
    for candidate, probability in zip(candidates, unsafe_probabilities):
        grouped.setdefault(candidate.example_id, []).append((candidate, float(probability)))
    decisions: dict[str, FrontierCandidate | None] = {}
    for example_id, items in grouped.items():
        eligible = [candidate for candidate, probability in items if probability <= threshold]
        decisions[example_id] = max(eligible, key=lambda candidate: candidate.start) if eligible else None
    return decisions


def frontier_policy_summary(
    candidates: Sequence[FrontierCandidate],
    unsafe_probabilities: Sequence[float],
    *,
    threshold: float,
) -> dict[str, Any]:
    decisions = choose_frontier_actions(
        candidates, unsafe_probabilities, threshold=threshold
    )
    examples: dict[str, FrontierCandidate] = {}
    for candidate in candidates:
        previous = examples.setdefault(candidate.example_id, candidate)
        if (
            previous.dataset != candidate.dataset
            or previous.condition != candidate.condition
            or previous.group_id != candidate.group_id
        ):
            raise ValueError("candidate metadata differs within an example")

    def summarize(example_ids: Iterable[str]) -> dict[str, Any]:
        ids = list(example_ids)
        selected = [decisions[example_id] for example_id in ids]
        unsafe = sum(action is not None and action.unsafe for action in selected)
        preserved = len(ids) - unsafe
        low, high = wilson_interval(preserved, len(ids))
        fallback = sum(action is None for action in selected)
        recompute = [1.0 if action is None else action.patch_ratio for action in selected]
        return {
            "n": len(ids),
            "answer_preservation": preserved / len(ids),
            "answer_preservation_wilson95_low": low,
            "answer_preservation_wilson95_high": high,
            "unsafe_selected_count": unsafe,
            "unsafe_selected_rate": unsafe / len(ids),
            "full_prefill_fallback_count": fallback,
            "full_prefill_fallback_rate": fallback / len(ids),
            "non_fallback_coverage": 1.0 - fallback / len(ids),
            "mean_recomputed_context_ratio": _mean(recompute),
            "mean_saved_context_ratio": 1.0 - _mean(recompute),
        }

    by_dataset: dict[str, list[str]] = {}
    for example_id, candidate in examples.items():
        by_dataset.setdefault(candidate.dataset, []).append(example_id)
    return {
        "threshold": threshold,
        "overall": summarize(sorted(examples)),
        "by_dataset": {
            dataset: summarize(sorted(example_ids))
            for dataset, example_ids in sorted(by_dataset.items())
        },
    }


def choose_frontier_threshold(
    candidates: Sequence[FrontierCandidate],
    unsafe_probabilities: Sequence[float],
    *,
    minimum_dataset_lower_bound: float,
) -> tuple[float, dict[str, Any]]:
    if not candidates:
        raise ValueError("cannot choose a threshold without candidates")
    probabilities = [float(value) for value in unsafe_probabilities]
    eligible: list[tuple[float, float, float, dict[str, Any]]] = []
    for threshold in [-math.inf, *sorted(set(probabilities))]:
        summary = frontier_policy_summary(
            candidates, probabilities, threshold=threshold
        )
        if all(
            values["answer_preservation_wilson95_low"]
            >= minimum_dataset_lower_bound
            for values in summary["by_dataset"].values()
        ):
            eligible.append(
                (
                    float(summary["overall"]["mean_saved_context_ratio"]),
                    -float(summary["overall"]["unsafe_selected_rate"]),
                    -float(threshold),
                    summary,
                )
            )
    if not eligible:
        raise ValueError("no threshold satisfies the quality constraint")
    _saving, _safety, neg_threshold, summary = max(eligible, key=lambda item: item[:3])
    return -neg_threshold, summary
