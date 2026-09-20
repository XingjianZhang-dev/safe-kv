"""Lightweight learned document selector for SAFE-KV answer experiments."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from safekv.data_schema import DiagnosticExample
from safekv.doc_selector import (
    conflict_candidate_docs,
    cross_doc_shared_entity_counts,
    entity_overlap_doc_scores,
    lexical_overlap,
    lexical_terms,
    normalize_by_doc_id,
    query_similarity_doc_scores,
)


FEATURE_NAMES = [
    "retrieval_score",
    "retrieval_norm",
    "retrieval_rank",
    "query_similarity",
    "entity_overlap",
    "title_query_overlap",
    "conflict_indicator",
    "cross_doc_shared_entity",
    "doc_position",
    "doc_position_from_end",
    "doc_length_norm",
    "numeric_overlap",
    "capitalized_overlap",
]


def oracle_label_doc_ids(example: DiagnosticExample) -> set[int]:
    doc_ids = {evidence.doc_id for evidence in example.evidence}
    if example.category == "conflict":
        doc_ids.update(example.conflicting_docs)
    return doc_ids


def doc_feature_rows(example: DiagnosticExample) -> list[dict[str, Any]]:
    query_terms = lexical_terms(example.question)
    question_numbers = _numeric_terms(example.question)
    question_caps = _capitalized_terms(example.question)
    query_scores = {score.doc_id: score.score for score in query_similarity_doc_scores(example)}
    entity_scores = {score.doc_id: score.score for score in entity_overlap_doc_scores(example)}
    conflict_docs = set(conflict_candidate_docs(example))
    cross_doc_norm = normalize_by_doc_id(cross_doc_shared_entity_counts(example))
    retrieval_norm = normalize_by_doc_id(
        {doc.doc_id: doc.retrieval_score for doc in example.documents}
    )
    ranked_doc_ids = [
        doc.doc_id
        for doc in sorted(example.documents, key=lambda doc: (-doc.retrieval_score, doc.doc_id))
    ]
    rank_score_by_id = {}
    denom = max(1, len(ranked_doc_ids) - 1)
    for rank, doc_id in enumerate(ranked_doc_ids):
        rank_score_by_id[doc_id] = 1.0 - rank / denom

    doc_lengths = {
        doc.doc_id: len(lexical_terms(f"{doc.title} {doc.text}"))
        for doc in example.documents
    }
    max_doc_len = max(1, max(doc_lengths.values(), default=1))
    n_docs = len(example.documents)
    rows = []
    for index, doc in enumerate(example.documents):
        doc_text = f"{doc.title} {doc.text}"
        doc_numbers = _numeric_terms(doc_text)
        doc_caps = _capitalized_terms(doc_text)
        features = {
            "retrieval_score": doc.retrieval_score,
            "retrieval_norm": retrieval_norm.get(doc.doc_id, 0.0),
            "retrieval_rank": rank_score_by_id.get(doc.doc_id, 0.0),
            "query_similarity": query_scores.get(doc.doc_id, 0.0),
            "entity_overlap": entity_scores.get(doc.doc_id, 0.0),
            "title_query_overlap": lexical_overlap(query_terms, lexical_terms(doc.title)),
            "conflict_indicator": 1.0 if doc.doc_id in conflict_docs else 0.0,
            "cross_doc_shared_entity": cross_doc_norm.get(doc.doc_id, 0.0),
            "doc_position": index / max(1, n_docs - 1),
            "doc_position_from_end": (n_docs - 1 - index) / max(1, n_docs - 1),
            "doc_length_norm": doc_lengths[doc.doc_id] / max_doc_len,
            "numeric_overlap": _set_overlap(question_numbers, doc_numbers),
            "capitalized_overlap": _set_overlap(question_caps, doc_caps),
        }
        rows.append({"doc_id": doc.doc_id, "features": features})
    return rows


def feature_matrix(examples: list[DiagnosticExample]) -> tuple[list[list[float]], list[int]]:
    labels = []
    matrix = []
    for example in examples:
        positives = oracle_label_doc_ids(example)
        for row in doc_feature_rows(example):
            matrix.append([float(row["features"][name]) for name in FEATURE_NAMES])
            labels.append(1 if row["doc_id"] in positives else 0)
    return matrix, labels


def load_selector_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with Path(path).open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    if artifact.get("feature_names") != FEATURE_NAMES:
        raise ValueError("learned selector feature names do not match this code")
    return artifact


def learned_doc_scores(
    example: DiagnosticExample,
    artifact: dict[str, Any],
) -> list[tuple[int, float]]:
    means = artifact["means"]
    stds = artifact["stds"]
    weights = artifact["weights"]
    bias = float(artifact["bias"])
    scores = []
    for row in doc_feature_rows(example):
        values = [float(row["features"][name]) for name in FEATURE_NAMES]
        normalized = [
            (value - float(mean)) / max(1e-6, float(std))
            for value, mean, std in zip(values, means, stds, strict=True)
        ]
        logit = bias + sum(value * float(weight) for value, weight in zip(normalized, weights, strict=True))
        scores.append((int(row["doc_id"]), _sigmoid(logit)))
    return scores


def select_learned_doc_ids(
    method: str,
    example: DiagnosticExample,
    artifact: dict[str, Any] | None,
) -> list[int]:
    if artifact is None:
        raise ValueError(f"{method} requires --selector-artifact")
    k = _learned_selector_k(method, example)
    scores = learned_doc_scores(example, artifact)
    ordered = sorted(scores, key=lambda item: (-item[1], item[0]))
    selected = {doc_id for doc_id, _score in ordered[:k]}
    return [doc.doc_id for doc in example.documents if doc.doc_id in selected]


def _learned_selector_k(method: str, example: DiagnosticExample) -> int:
    if method == "learned_doc_patch_oracle_count":
        return len(oracle_label_doc_ids(example))
    match = re.search(r"_k(\d+)$", method)
    if match is None:
        raise ValueError(f"unsupported learned selector method {method!r}")
    return int(match.group(1))


def _numeric_terms(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:[.:]\d+)?\b", text.lower()))


def _capitalized_terms(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"\b[A-Z][a-zA-Z]+\b", text)
        if token.lower() not in {"the", "a", "an"}
    }


def _set_overlap(left: set[str], right: set[str]) -> float:
    if not left:
        return 0.0
    return len(left & right) / len(left)


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


__all__ = [
    "FEATURE_NAMES",
    "doc_feature_rows",
    "feature_matrix",
    "learned_doc_scores",
    "load_selector_artifact",
    "oracle_label_doc_ids",
    "select_learned_doc_ids",
]
