"""Leakage-controlled fallback gate for non-prefix KV-cache reuse.

The gate predicts whether naive non-prefix reuse is unsafe.  It may inspect only
information available before generation: the question, document text/title,
retrieval scores, and prompt length.  Gold answers, evidence annotations,
document roles, and cache-mismatch masks are deliberately outside this module's
feature contract.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np


TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")

FEATURE_DEFINITIONS: tuple[tuple[str, str], ...] = (
    ("log_document_count", "log(1 + number of retrieved documents)"),
    ("log_question_token_count", "log(1 + lexical question-token count)"),
    ("log_total_document_tokens", "log(1 + total lexical document-token count)"),
    ("mean_document_tokens", "mean lexical document-token count"),
    ("std_document_tokens", "population SD of lexical document-token counts"),
    ("max_document_fraction", "largest document length divided by total document length"),
    ("retrieval_score_max", "maximum retriever score"),
    ("retrieval_score_mean", "mean retriever score"),
    ("retrieval_score_std", "population SD of retriever scores"),
    ("retrieval_score_top_margin", "largest minus second-largest retriever score"),
    ("retrieval_score_nonzero_fraction", "fraction of nonzero retriever scores"),
    ("query_overlap_max", "maximum unique query-term recall among documents"),
    ("query_overlap_mean", "mean unique query-term recall among documents"),
    ("query_overlap_std", "population SD of unique query-term recall"),
    ("query_overlap_first", "unique query-term recall in the first document"),
    ("query_overlap_last", "unique query-term recall in the final document"),
    ("title_overlap_max", "maximum unique query-term recall among document titles"),
    ("adjacent_jaccard_mean", "mean lexical Jaccard similarity of adjacent documents"),
    ("adjacent_jaccard_max", "maximum lexical Jaccard similarity of adjacent documents"),
    ("numeric_document_fraction", "fraction of documents containing a number"),
    ("numeric_disagreement", "indicator that documents contain multiple distinct numbers"),
    ("log_prompt_length", "log(1 + tokenized prompt length before generation)"),
)
FEATURE_NAMES: tuple[str, ...] = tuple(name for name, _description in FEATURE_DEFINITIONS)


@dataclass(frozen=True)
class GateRecord:
    example_id: str
    group_id: str
    dataset: str
    condition: str
    unsafe: bool
    changed_and_gold_wrong: bool
    features: tuple[float, ...]


def _tokens(text: Any) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(str(text))]


def _mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _std(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    center = _mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / len(values))


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def runtime_feature_dict(example: dict[str, Any], *, prompt_length: int) -> dict[str, float]:
    """Return the pre-generation feature contract, without reading gold fields."""
    if prompt_length <= 0:
        raise ValueError("prompt_length must be positive")
    documents = example.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("example must contain at least one document")

    question_terms = set(_tokens(example.get("question", "")))
    question_denominator = max(1, len(question_terms))
    document_token_lists = [
        _tokens(f"{document.get('title', '')} {document.get('text', '')}")
        for document in documents
    ]
    document_term_sets = [set(tokens) for tokens in document_token_lists]
    document_lengths = [float(len(tokens)) for tokens in document_token_lists]
    total_length = sum(document_lengths)
    retrieval_scores = [float(document.get("retrieval_score", 0.0)) for document in documents]
    if not all(math.isfinite(score) for score in retrieval_scores):
        raise ValueError("retrieval scores must be finite")
    ordered_scores = sorted(retrieval_scores, reverse=True)

    query_overlaps = [
        len(question_terms & terms) / question_denominator for terms in document_term_sets
    ]
    title_overlaps = [
        len(question_terms & set(_tokens(document.get("title", "")))) / question_denominator
        for document in documents
    ]
    adjacent = [
        _jaccard(document_term_sets[index], document_term_sets[index + 1])
        for index in range(len(document_term_sets) - 1)
    ]
    number_sets = [
        set(NUMBER_RE.findall(f"{document.get('title', '')} {document.get('text', '')}"))
        for document in documents
    ]
    all_numbers = set().union(*number_sets) if number_sets else set()

    values = {
        "log_document_count": math.log1p(len(documents)),
        "log_question_token_count": math.log1p(len(_tokens(example.get("question", "")))),
        "log_total_document_tokens": math.log1p(total_length),
        "mean_document_tokens": _mean(document_lengths),
        "std_document_tokens": _std(document_lengths),
        "max_document_fraction": max(document_lengths, default=0.0) / max(1.0, total_length),
        "retrieval_score_max": max(retrieval_scores, default=0.0),
        "retrieval_score_mean": _mean(retrieval_scores),
        "retrieval_score_std": _std(retrieval_scores),
        "retrieval_score_top_margin": (
            ordered_scores[0] - ordered_scores[1] if len(ordered_scores) > 1 else 0.0
        ),
        "retrieval_score_nonzero_fraction": (
            sum(abs(score) > 1e-12 for score in retrieval_scores) / len(retrieval_scores)
        ),
        "query_overlap_max": max(query_overlaps, default=0.0),
        "query_overlap_mean": _mean(query_overlaps),
        "query_overlap_std": _std(query_overlaps),
        "query_overlap_first": query_overlaps[0],
        "query_overlap_last": query_overlaps[-1],
        "title_overlap_max": max(title_overlaps, default=0.0),
        "adjacent_jaccard_mean": _mean(adjacent),
        "adjacent_jaccard_max": max(adjacent, default=0.0),
        "numeric_document_fraction": sum(bool(numbers) for numbers in number_sets) / len(number_sets),
        "numeric_disagreement": float(len(all_numbers) > 1),
        "log_prompt_length": math.log1p(prompt_length),
    }
    if tuple(values) != FEATURE_NAMES:
        raise AssertionError("feature order drifted from the declared contract")
    if not all(math.isfinite(value) for value in values.values()):
        raise ValueError("gate features must be finite")
    return values


def runtime_feature_vector(example: dict[str, Any], *, prompt_length: int) -> tuple[float, ...]:
    values = runtime_feature_dict(example, prompt_length=prompt_length)
    return tuple(values[name] for name in FEATURE_NAMES)


def dataset_stratified_group_split(
    records: Sequence[GateRecord],
    *,
    validation_fraction: float,
    seed: int,
) -> dict[str, str]:
    """Split source questions, never condition-specific rows, within each dataset."""
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must lie strictly between zero and one")
    groups_by_dataset: dict[str, set[str]] = defaultdict(set)
    group_dataset: dict[str, str] = {}
    for record in records:
        previous = group_dataset.setdefault(record.group_id, record.dataset)
        if previous != record.dataset:
            raise ValueError(f"group occurs in multiple datasets: {record.group_id}")
        groups_by_dataset[record.dataset].add(record.group_id)

    assignments: dict[str, str] = {}
    for dataset, groups in sorted(groups_by_dataset.items()):
        ordered = sorted(
            groups,
            key=lambda group: hashlib.sha256(
                f"{seed}:{dataset}:{group}".encode("utf-8")
            ).hexdigest(),
        )
        validation_count = int(round(len(ordered) * validation_fraction))
        validation_count = min(max(1, validation_count), len(ordered) - 1)
        validation = set(ordered[:validation_count])
        for group in ordered:
            assignments[group] = "validation" if group in validation else "train"
    return assignments


def predict_unsafe_probability(
    feature_matrix: np.ndarray,
    *,
    means: Sequence[float],
    scales: Sequence[float],
    coefficients: Sequence[float],
    intercept: float,
) -> np.ndarray:
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    normalized = (matrix - np.asarray(means)) / np.asarray(scales)
    logits = normalized @ np.asarray(coefficients) + float(intercept)
    logits = np.clip(logits, -50.0, 50.0)
    return 1.0 / (1.0 + np.exp(-logits))


def wilson_interval(successes: int, total: int, *, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= successes <= total:
        raise ValueError("successes must lie in [0, total]")
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(
        proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total)
    ) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def policy_summary(
    records: Sequence[GateRecord],
    unsafe_probabilities: Sequence[float],
    *,
    threshold: float,
) -> dict[str, Any]:
    if len(records) != len(unsafe_probabilities):
        raise ValueError("records and probabilities must have equal length")
    by_dataset: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        by_dataset[record.dataset].append(index)

    def summarize(indices: Iterable[int]) -> dict[str, Any]:
        selected = list(indices)
        reuse = [index for index in selected if unsafe_probabilities[index] <= threshold]
        unsafe_reuse = sum(records[index].unsafe for index in reuse)
        changed_wrong = sum(records[index].changed_and_gold_wrong for index in reuse)
        preserved = len(selected) - unsafe_reuse
        low, high = wilson_interval(preserved, len(selected))
        return {
            "n": len(selected),
            "reuse_count": len(reuse),
            "fallback_count": len(selected) - len(reuse),
            "reuse_rate": len(reuse) / len(selected),
            "fallback_rate": 1.0 - len(reuse) / len(selected),
            "unsafe_reuse_count": unsafe_reuse,
            "unsafe_miss_rate": unsafe_reuse / max(1, sum(records[index].unsafe for index in selected)),
            "answer_preservation": preserved / len(selected),
            "answer_preservation_wilson95_low": low,
            "answer_preservation_wilson95_high": high,
            "changed_and_gold_wrong_count": changed_wrong,
            "changed_and_gold_wrong_rate": changed_wrong / len(selected),
        }

    return {
        "threshold": threshold,
        "overall": summarize(range(len(records))),
        "by_dataset": {
            dataset: summarize(indices) for dataset, indices in sorted(by_dataset.items())
        },
    }


def choose_max_coverage_threshold(
    records: Sequence[GateRecord],
    unsafe_probabilities: Sequence[float],
    *,
    minimum_dataset_lower_bound: float,
) -> tuple[float, dict[str, Any]]:
    if not 0.0 < minimum_dataset_lower_bound < 1.0:
        raise ValueError("minimum_dataset_lower_bound must lie strictly between zero and one")
    if not records:
        raise ValueError("cannot choose a threshold without records")
    probabilities = [float(value) for value in unsafe_probabilities]
    candidates = [-math.inf, *sorted(set(probabilities))]
    eligible: list[tuple[float, float, float, dict[str, Any]]] = []
    for threshold in candidates:
        summary = policy_summary(records, probabilities, threshold=threshold)
        dataset_lows = [
            values["answer_preservation_wilson95_low"]
            for values in summary["by_dataset"].values()
        ]
        if min(dataset_lows) + 1e-15 < minimum_dataset_lower_bound:
            continue
        eligible.append(
            (
                summary["overall"]["reuse_rate"],
                min(dataset_lows),
                -threshold,
                summary,
            )
        )
    if not eligible:
        raise AssertionError("full-prefill-only fallback candidate unexpectedly failed")
    _coverage, _lower, neg_threshold, summary = max(eligible, key=lambda item: item[:3])
    return -neg_threshold, summary

