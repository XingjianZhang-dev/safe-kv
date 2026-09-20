"""Deterministic score/order controls used by the ARR rebuttal checks."""

from __future__ import annotations

import hashlib
import random
from collections import Counter
from dataclasses import replace
from statistics import mean
from typing import Iterable, Literal

from safekv.data_schema import DiagnosticExample
from safekv.patch_recompute import lexical_terms


RetrievalMode = Literal["original", "zero", "lexical"]


def transform_external_example(
    example: DiagnosticExample,
    *,
    retrieval_mode: RetrievalMode = "original",
    shuffle_seed: int | None = None,
    max_documents: int | None = None,
) -> DiagnosticExample | None:
    """Create a controlled retrieval-score and/or order variant.

    If ``max_documents`` is supplied, every evidence document is retained and
    the remaining slots are filled by distractors in their existing order.
    Documents are optionally shuffled afterwards and all document references
    are remapped to the new positional ids.  Score neutralization alone does
    not remove the source dataset's evidence-first order; both confounds are
    removed only when ``retrieval_mode`` is label-blind and ``shuffle_seed`` is
    provided.  Gold labels are still used to keep support in capped prompts.
    """

    if retrieval_mode not in {"original", "zero", "lexical"}:
        raise ValueError(f"unsupported retrieval_mode: {retrieval_mode}")
    if max_documents is not None and max_documents <= 0:
        raise ValueError("max_documents must be positive")

    evidence_ids = {item.doc_id for item in example.evidence}
    documents = list(example.documents)
    if max_documents is not None:
        evidence_documents = [doc for doc in documents if doc.doc_id in evidence_ids]
        if len(evidence_documents) > max_documents:
            return None
        distractors = [doc for doc in documents if doc.doc_id not in evidence_ids]
        documents = evidence_documents + distractors[: max_documents - len(evidence_documents)]
        if len(documents) < max_documents:
            return None

    if shuffle_seed is not None:
        rng = random.Random(_stable_seed(shuffle_seed, example.id))
        rng.shuffle(documents)

    retained_ids = {doc.doc_id for doc in documents}
    old_to_new = {doc.doc_id: position for position, doc in enumerate(documents)}
    query_terms = lexical_terms(example.question)
    transformed_documents = []
    for position, doc in enumerate(documents):
        if retrieval_mode == "zero":
            retrieval_score = 0.0
        elif retrieval_mode == "lexical":
            doc_terms = lexical_terms(f"{doc.title} {doc.text}")
            retrieval_score = len(query_terms & doc_terms) / max(1, len(query_terms))
        else:
            retrieval_score = doc.retrieval_score
        transformed_documents.append(
            replace(doc, doc_id=position, retrieval_score=float(retrieval_score))
        )

    transformed = replace(
        example,
        documents=transformed_documents,
        evidence=[
            replace(item, doc_id=old_to_new[item.doc_id])
            for item in example.evidence
            if item.doc_id in retained_ids
        ],
        conflicting_docs=[
            old_to_new[doc_id]
            for doc_id in example.conflicting_docs
            if doc_id in retained_ids
        ],
    )
    transformed.validate()
    return transformed


def transform_external_examples(
    examples: Iterable[DiagnosticExample],
    *,
    retrieval_mode: RetrievalMode = "original",
    shuffle_seed: int | None = None,
    max_documents: int | None = None,
) -> list[DiagnosticExample]:
    transformed = [
        transform_external_example(
            example,
            retrieval_mode=retrieval_mode,
            shuffle_seed=shuffle_seed,
            max_documents=max_documents,
        )
        for example in examples
    ]
    return [example for example in transformed if example is not None]


def build_nested_single_evidence_variant(
    example: DiagnosticExample,
    *,
    num_documents: int,
    layout_seed: int,
    retrieval_mode: RetrievalMode = "zero",
) -> DiagnosticExample | None:
    """Build a support-included, label-independent-order document-count variant.

    The source must contain exactly one evidence document.  Gold labels are used
    only to keep that support document in the controlled prompt.  Distractor
    inclusion and final order are stable content-hash decisions, so a document's
    order key is unchanged as ``num_documents`` grows.
    """

    if num_documents <= 0:
        raise ValueError("num_documents must be positive")
    evidence_ids = {item.doc_id for item in example.evidence}
    if len(evidence_ids) != 1:
        return None
    evidence_documents = [doc for doc in example.documents if doc.doc_id in evidence_ids]
    distractors = [doc for doc in example.documents if doc.doc_id not in evidence_ids]
    distractors.sort(
        key=lambda doc: _document_order_key(
            layout_seed,
            f"{example.id}:selection",
            doc,
        )
    )
    selected = evidence_documents + distractors[: max(0, num_documents - 1)]
    if len(selected) < num_documents:
        return None
    selected.sort(
        key=lambda doc: _document_order_key(
            layout_seed,
            f"{example.id}:layout",
            doc,
        )
    )

    retained_ids = {doc.doc_id for doc in selected}
    old_to_new = {doc.doc_id: position for position, doc in enumerate(selected)}
    query_terms = lexical_terms(example.question)
    transformed_documents = []
    for position, doc in enumerate(selected):
        if retrieval_mode == "zero":
            score = 0.0
        elif retrieval_mode == "lexical":
            doc_terms = lexical_terms(f"{doc.title} {doc.text}")
            score = len(query_terms & doc_terms) / max(1, len(query_terms))
        elif retrieval_mode == "original":
            score = doc.retrieval_score
        else:
            raise ValueError(f"unsupported retrieval_mode: {retrieval_mode}")
        transformed_documents.append(replace(doc, doc_id=position, retrieval_score=float(score)))

    transformed = replace(
        example,
        documents=transformed_documents,
        evidence=[
            replace(item, doc_id=old_to_new[item.doc_id])
            for item in example.evidence
            if item.doc_id in retained_ids
        ],
        conflicting_docs=[
            old_to_new[doc_id]
            for doc_id in example.conflicting_docs
            if doc_id in retained_ids
        ],
    )
    transformed.validate()
    return transformed


def variant_summary(examples: Iterable[DiagnosticExample]) -> dict[str, object]:
    rows = list(examples)
    doc_counts = Counter(len(example.documents) for example in rows)
    earliest_evidence_positions = []
    score_separation = []
    for example in rows:
        evidence_ids = {item.doc_id for item in example.evidence}
        positions = [
            position
            for position, doc in enumerate(example.documents)
            if doc.doc_id in evidence_ids
        ]
        if positions:
            earliest_evidence_positions.append(min(positions))
        evidence_scores = [
            doc.retrieval_score for doc in example.documents if doc.doc_id in evidence_ids
        ]
        distractor_scores = [
            doc.retrieval_score for doc in example.documents if doc.doc_id not in evidence_ids
        ]
        if evidence_scores and distractor_scores:
            score_separation.append(float(min(evidence_scores) > max(distractor_scores)))
    return {
        "num_examples": len(rows),
        "document_count_distribution": dict(sorted(doc_counts.items())),
        "earliest_evidence_position_distribution": dict(
            sorted(Counter(earliest_evidence_positions).items())
        ),
        "mean_earliest_evidence_position": (
            mean(earliest_evidence_positions) if earliest_evidence_positions else None
        ),
        "perfect_gold_score_separation_rate": (
            mean(score_separation) if score_separation else None
        ),
    }


def _stable_seed(seed: int, example_id: str) -> int:
    digest = hashlib.sha256(f"{seed}:{example_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def _document_order_key(seed: int, example_id: str, doc: object) -> bytes:
    payload = f"{seed}:{example_id}:{doc.title}:{doc.text}".encode("utf-8")
    return hashlib.sha256(payload).digest()


__all__ = [
    "RetrievalMode",
    "build_nested_single_evidence_variant",
    "transform_external_example",
    "transform_external_examples",
    "variant_summary",
]
