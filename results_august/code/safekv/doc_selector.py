"""Document-level selectors and safe-composition gates for Milestone 5A."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from safekv.data_schema import DiagnosticExample, Document, PromptPack, TokenRange
from safekv.naive_composition import average_metric_summary
from safekv.patch_recompute import (
    lexical_terms,
    oracle_evidence_doc_patch_ranges,
    random_span_patch_ranges_same_budget,
    stable_example_seed,
    token_count,
)


DOC_SELECTOR_KINDS = [
    "oracle_evidence_doc_patch",
    "random_doc_patch_same_count",
    "random_token_patch_same_budget_as_oracle_doc",
    "top_retrieval_doc_patch_oracle_count",
    "top_retrieval_doc_patch_k1",
    "top_retrieval_doc_patch_k2",
    "top_retrieval_doc_patch_k4",
    "query_similarity_doc_patch_oracle_count",
    "query_similarity_doc_patch_k1",
    "query_similarity_doc_patch_k2",
    "query_similarity_doc_patch_k4",
    "entity_overlap_doc_patch_oracle_count",
    "entity_overlap_doc_patch_k1",
    "entity_overlap_doc_patch_k2",
    "entity_overlap_doc_patch_k4",
    "conflict_aware_doc_patch",
    "risk_guided_doc_patch_oracle_count",
    "risk_guided_doc_patch_k1",
    "risk_guided_doc_patch_k2",
    "risk_guided_doc_patch_k4",
]
DEFAULT_GATE_THRESHOLDS = [0.15, 0.30, 0.45, 0.60, 0.75]
DEFAULT_RISK_WEIGHTS = {
    "retrieval_score": 0.25,
    "query_similarity": 0.30,
    "entity_overlap": 0.20,
    "conflict_indicator": 0.15,
    "cross_doc_shared_entity": 0.10,
}


@dataclass(frozen=True)
class DocumentScore:
    doc_id: int
    score: float
    reason: dict[str, float]


@dataclass(frozen=True)
class GateDecision:
    should_patch: bool
    risk_score: float
    threshold: float
    reason: dict[str, float]


def default_doc_selector_methods(
    gate_thresholds: list[float] | None = None,
) -> list[str]:
    thresholds = DEFAULT_GATE_THRESHOLDS if gate_thresholds is None else gate_thresholds
    return DOC_SELECTOR_KINDS + [
        safe_gate_method_name(threshold) for threshold in thresholds
    ]


def safe_gate_method_name(threshold: float) -> str:
    label = f"{threshold:.2f}".replace(".", "_")
    return f"safe_composition_gate_t{label}"


def parse_safe_gate_threshold(method: str) -> float | None:
    prefix = "safe_composition_gate_t"
    if not method.startswith(prefix):
        return None
    return float(method.removeprefix(prefix).replace("_", "."))


def oracle_doc_ids(example: DiagnosticExample) -> list[int]:
    doc_ids = {evidence.doc_id for evidence in example.evidence}
    if example.category == "conflict":
        doc_ids.update(example.conflicting_docs)
    ordered_doc_ids = [doc.doc_id for doc in example.documents]
    return [doc_id for doc_id in ordered_doc_ids if doc_id in doc_ids]


def document_ranges_for_ids(
    example: DiagnosticExample,
    pack: PromptPack,
    doc_ids: Iterable[int],
) -> list[TokenRange]:
    wanted = set(doc_ids)
    ranges: list[TokenRange] = []
    for doc, token_range in zip(example.documents, pack.doc_ranges, strict=True):
        if doc.doc_id in wanted:
            ranges.append(token_range)
    return ranges


def selected_doc_token_count(
    example: DiagnosticExample,
    pack: PromptPack,
    doc_ids: Iterable[int],
) -> int:
    return token_count(document_ranges_for_ids(example, pack, doc_ids))


def random_doc_ids_same_count(
    example: DiagnosticExample,
    count: int,
    seed: int,
) -> list[int]:
    doc_ids = [doc.doc_id for doc in example.documents]
    if count <= 0:
        return []
    sample_count = min(count, len(doc_ids))
    import random

    rng = random.Random(seed)
    return sorted(rng.sample(doc_ids, sample_count))


def select_top_k_doc_ids(
    scores: list[DocumentScore],
    k: int,
) -> list[int]:
    if k <= 0:
        return []
    ordered = sorted(scores, key=lambda item: (-item.score, item.doc_id))
    return [item.doc_id for item in ordered[:k]]


def resolve_doc_k(
    method: str,
    example: DiagnosticExample,
) -> int:
    if method.endswith("_oracle_count") or method in {
        "random_doc_patch_same_count",
        "random_token_patch_same_budget_as_oracle_doc",
    }:
        return len(oracle_doc_ids(example))
    if method.endswith("_k1"):
        return 1
    if method.endswith("_k2"):
        return 2
    match = re.search(r"_k(\d+)$", method)
    if match is not None:
        return int(match.group(1))
    raise ValueError(f"cannot resolve k for method {method!r}")


def retrieval_doc_scores(example: DiagnosticExample) -> list[DocumentScore]:
    return [
        DocumentScore(
            doc_id=doc.doc_id,
            score=doc.retrieval_score,
            reason={"retrieval_score": doc.retrieval_score},
        )
        for doc in example.documents
    ]


def query_similarity_doc_scores(example: DiagnosticExample) -> list[DocumentScore]:
    query_terms = lexical_terms(example.question)
    scores = []
    for doc in example.documents:
        score = lexical_overlap(query_terms, lexical_terms(f"{doc.title} {doc.text}"))
        scores.append(
            DocumentScore(
                doc_id=doc.doc_id,
                score=score,
                reason={"query_lexical_similarity": score},
            )
        )
    return scores


def entity_overlap_doc_scores(example: DiagnosticExample) -> list[DocumentScore]:
    question_entities = extract_entities(example.question)
    scores = []
    for doc in example.documents:
        doc_entities = extract_entities(f"{doc.title} {doc.text}")
        score = entity_overlap(question_entities, doc_entities)
        scores.append(
            DocumentScore(
                doc_id=doc.doc_id,
                score=score,
                reason={"entity_overlap": score},
            )
        )
    return scores


def conflict_aware_doc_ids(example: DiagnosticExample) -> list[int]:
    candidates = conflict_candidate_docs(example)
    if not candidates:
        return select_top_k_doc_ids(risk_guided_doc_scores(example), 1)

    support_doc_id = likely_support_doc_id(example, candidates)
    selected = [support_doc_id] if support_doc_id is not None else []
    support_candidates = candidates.get(support_doc_id, set()) if support_doc_id is not None else set()
    conflicting_doc_ids = [
        doc_id
        for doc_id, values in candidates.items()
        if doc_id != support_doc_id and values and values != support_candidates
    ]
    if conflicting_doc_ids:
        ranked_conflicts = sorted(
            conflicting_doc_ids,
            key=lambda doc_id: (
                -_doc_lookup(example, doc_id).retrieval_score,
                -lexical_overlap(
                    lexical_terms(example.question),
                    lexical_terms(
                        f"{_doc_lookup(example, doc_id).title} {_doc_lookup(example, doc_id).text}"
                    ),
                ),
                doc_id,
            ),
        )
        selected.append(ranked_conflicts[0])
    return selected


def resolve_risk_weights(weights: dict[str, float] | None) -> dict[str, float]:
    resolved = dict(DEFAULT_RISK_WEIGHTS if weights is None else weights)
    if set(resolved) != set(DEFAULT_RISK_WEIGHTS):
        missing = sorted(set(DEFAULT_RISK_WEIGHTS) - set(resolved))
        extra = sorted(set(resolved) - set(DEFAULT_RISK_WEIGHTS))
        raise ValueError(f"risk weights have missing={missing} extra={extra}")
    if any(not math.isfinite(value) or value < 0.0 for value in resolved.values()):
        raise ValueError("risk weights must be finite and non-negative")
    if not math.isclose(sum(resolved.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("risk weights must sum to 1")
    return resolved


def risk_guided_doc_scores(
    example: DiagnosticExample,
    weights: dict[str, float] | None = None,
) -> list[DocumentScore]:
    resolved_weights = resolve_risk_weights(weights)
    retrieval_values = [doc.retrieval_score for doc in example.documents]
    retrieval_norm = normalize_by_doc_id(
        {doc.doc_id: doc.retrieval_score for doc in example.documents}
    )
    query_scores = {score.doc_id: score.score for score in query_similarity_doc_scores(example)}
    entity_scores = {score.doc_id: score.score for score in entity_overlap_doc_scores(example)}
    conflict_docs = set(conflict_candidate_docs(example))
    cross_doc_counts = cross_doc_shared_entity_counts(example)
    cross_doc_norm = normalize_by_doc_id(cross_doc_counts)
    _ = retrieval_values

    scores: list[DocumentScore] = []
    for doc in example.documents:
        conflict_indicator = 1.0 if doc.doc_id in conflict_docs else 0.0
        reason = {
            "retrieval_score": retrieval_norm.get(doc.doc_id, 0.0),
            "query_similarity": query_scores.get(doc.doc_id, 0.0),
            "entity_overlap": entity_scores.get(doc.doc_id, 0.0),
            "conflict_indicator": conflict_indicator,
            "cross_doc_shared_entity": cross_doc_norm.get(doc.doc_id, 0.0),
        }
        score = sum(
            resolved_weights[feature] * reason[feature]
            for feature in DEFAULT_RISK_WEIGHTS
        )
        scores.append(DocumentScore(doc_id=doc.doc_id, score=score, reason=reason))
    return scores


def safe_composition_risk(example: DiagnosticExample) -> tuple[float, dict[str, float]]:
    query_scores = [score.score for score in query_similarity_doc_scores(example)]
    high_similarity_docs = sum(1 for score in query_scores if score >= 0.25)
    max_entity_overlap = max_doc_doc_entity_overlap(example)
    sorted_retrieval = sorted((doc.retrieval_score for doc in example.documents), reverse=True)
    if len(sorted_retrieval) >= 2:
        retrieval_gap = max(0.0, sorted_retrieval[0] - sorted_retrieval[1])
    else:
        retrieval_gap = 1.0
    retrieval_gap_risk = 1.0 - min(1.0, retrieval_gap)
    conflict_risk = 1.0 if conflict_candidate_docs(example) else 0.0
    multihop_risk = 1.0 if has_multihop_like_cue(example.question) else 0.0
    reason = {
        "max_doc_doc_entity_overlap": max_entity_overlap,
        "high_similarity_doc_ratio": min(1.0, high_similarity_docs / 3.0),
        "retrieval_gap_risk": retrieval_gap_risk,
        "conflict_candidate_risk": conflict_risk,
        "multihop_like_cue": multihop_risk,
    }
    risk = (
        0.25 * reason["max_doc_doc_entity_overlap"]
        + 0.20 * reason["high_similarity_doc_ratio"]
        + 0.20 * reason["retrieval_gap_risk"]
        + 0.25 * reason["conflict_candidate_risk"]
        + 0.10 * reason["multihop_like_cue"]
    )
    return min(1.0, max(0.0, risk)), reason


def gate_decision(example: DiagnosticExample, threshold: float) -> GateDecision:
    risk, reason = safe_composition_risk(example)
    return GateDecision(
        should_patch=risk >= threshold,
        risk_score=risk,
        threshold=threshold,
        reason=reason,
    )


def selected_doc_ids_for_method(
    method: str,
    example: DiagnosticExample,
    seed: int,
    risk_weights: dict[str, float] | None = None,
) -> tuple[list[int], dict[str, Any]]:
    gate_threshold = parse_safe_gate_threshold(method)
    if gate_threshold is not None:
        decision = gate_decision(example, gate_threshold)
        if not decision.should_patch:
            return [], {
                "gate_risk_score": decision.risk_score,
                "gate_threshold": decision.threshold,
                "gate_should_patch": False,
                **decision.reason,
            }
        selected = select_top_k_doc_ids(
            risk_guided_doc_scores(example, risk_weights), 2
        )
        return selected, {
            "gate_risk_score": decision.risk_score,
            "gate_threshold": decision.threshold,
            "gate_should_patch": True,
            **decision.reason,
        }

    if method == "oracle_evidence_doc_patch":
        selected = oracle_doc_ids(example)
        return selected, {"selector": "oracle_evidence_doc_patch"}
    if method == "random_doc_patch_same_count":
        selected = random_doc_ids_same_count(
            example,
            count=len(oracle_doc_ids(example)),
            seed=stable_example_seed(seed, example.id, method),
        )
        return selected, {"selector": "random_doc_patch_same_count"}
    if method == "conflict_aware_doc_patch":
        return conflict_aware_doc_ids(example), {"selector": "conflict_aware_doc_patch"}

    scorer: list[DocumentScore]
    if method.startswith("top_retrieval_doc_patch"):
        scorer = retrieval_doc_scores(example)
    elif method.startswith("query_similarity_doc_patch"):
        scorer = query_similarity_doc_scores(example)
    elif method.startswith("entity_overlap_doc_patch"):
        scorer = entity_overlap_doc_scores(example)
    elif method.startswith("risk_guided_doc_patch"):
        scorer = risk_guided_doc_scores(example, risk_weights)
    else:
        raise ValueError(f"unsupported document selector method {method!r}")

    k = resolve_doc_k(method, example)
    selected = select_top_k_doc_ids(scorer, k)
    return selected, {
        "selector": method,
        "doc_scores": {
            str(score.doc_id): {"score": score.score, **score.reason}
            for score in scorer
        },
    }


def patch_ranges_for_doc_selector_method(
    method: str,
    example: DiagnosticExample,
    pack: PromptPack,
    seed: int,
    risk_weights: dict[str, float] | None = None,
) -> tuple[list[TokenRange], list[int], dict[str, Any]]:
    if method == "random_token_patch_same_budget_as_oracle_doc":
        oracle_ranges = oracle_evidence_doc_patch_ranges(example, pack)
        target_token_count = token_count(oracle_ranges)
        ranges = random_span_patch_ranges_same_budget(
            pack,
            target_token_count=target_token_count,
            seed=stable_example_seed(seed, example.id, method),
        )
        return ranges, [], {
            "selector": "random_token_patch_same_budget_as_oracle_doc",
            "target_token_count": target_token_count,
        }

    selected_doc_ids, reason = selected_doc_ids_for_method(
        method, example, seed, risk_weights=risk_weights
    )
    return document_ranges_for_ids(example, pack, selected_doc_ids), selected_doc_ids, reason


def lexical_overlap(left_terms: set[str], right_terms: set[str]) -> float:
    if not left_terms:
        return 0.0
    return len(left_terms & right_terms) / len(left_terms)


def extract_entities(text: str) -> set[str]:
    entities: set[str] = set()
    for match in re.finditer(r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text):
        entities.add(match.group(0).lower())
    for match in re.finditer(r"\b[A-Z]{2,}(?:[-_][A-Z0-9]+)*\b", text):
        entities.add(match.group(0).lower())
    for match in re.finditer(r"\b[A-Za-z]*\d+[A-Za-z0-9:.-]*(?:\s*(?:AM|PM|am|pm))?\b", text):
        entities.add(match.group(0).lower())
    for token in re.findall(r"\b[A-Z][a-z]+\b", text):
        if token.lower() not in _ENTITY_STOPWORDS:
            entities.add(token.lower())
    return entities


def entity_overlap(question_entities: set[str], doc_entities: set[str]) -> float:
    if not question_entities:
        return 0.0
    return len(question_entities & doc_entities) / len(question_entities)


def answer_candidate_terms(text: str) -> set[str]:
    candidates = set()
    for match in re.finditer(r"\b\d{1,4}(?:[:.]\d{2})?\s*(?:AM|PM|am|pm)?\b", text):
        candidates.add(" ".join(match.group(0).lower().split()))
    for match in re.finditer(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b", text, re.I):
        candidates.add(" ".join(match.group(0).lower().split()))
    return candidates


def conflict_candidate_docs(example: DiagnosticExample) -> dict[int, set[str]]:
    question_has_cue = has_conflict_like_cue(example.question)
    question_terms = lexical_terms(example.question)
    values_by_doc: dict[int, set[str]] = {}
    for doc in example.documents:
        candidates = answer_candidate_terms(doc.text)
        q_overlap = lexical_overlap(question_terms, lexical_terms(f"{doc.title} {doc.text}"))
        if candidates and (question_has_cue or q_overlap >= 0.25):
            values_by_doc[doc.doc_id] = candidates
    unique_values = {tuple(sorted(values)) for values in values_by_doc.values()}
    if len(unique_values) <= 1:
        return {}
    return values_by_doc


def likely_support_doc_id(
    example: DiagnosticExample,
    candidates: dict[int, set[str]],
) -> int | None:
    if not candidates:
        return None
    question_terms = lexical_terms(example.question)
    support_cues = support_source_cues(example.question)

    def score(doc_id: int) -> tuple[float, int]:
        doc = _doc_lookup(example, doc_id)
        doc_terms = lexical_terms(f"{doc.title} {doc.text}")
        cue_score = lexical_overlap(support_cues, doc_terms) if support_cues else 0.0
        query_score = lexical_overlap(question_terms, doc_terms)
        return (0.45 * doc.retrieval_score + 0.35 * cue_score + 0.20 * query_score, -doc_id)

    return max(candidates, key=score)


def support_source_cues(question: str) -> set[str]:
    cues = {
        "official",
        "schedule",
        "latest",
        "current",
        "according",
        "source",
        "trusted",
    }
    return lexical_terms(question) & cues


def has_conflict_like_cue(question: str) -> bool:
    text = question.lower()
    return any(
        cue in text
        for cue in [
            "according to",
            "official",
            "latest",
            "current",
            "schedule",
            "trusted",
        ]
    )


def has_multihop_like_cue(question: str) -> bool:
    text = question.lower()
    return any(
        cue in text
        for cue in [
            "designer of",
            "where was the",
            "in what year",
            "who received",
            "for ",
        ]
    )


def max_doc_doc_entity_overlap(example: DiagnosticExample) -> float:
    doc_entities = [extract_entities(f"{doc.title} {doc.text}") for doc in example.documents]
    max_overlap = 0.0
    for index, left in enumerate(doc_entities):
        for right in doc_entities[index + 1 :]:
            denom = max(1, min(len(left), len(right)))
            max_overlap = max(max_overlap, len(left & right) / denom)
    return max_overlap


def cross_doc_shared_entity_counts(example: DiagnosticExample) -> dict[int, float]:
    entity_to_docs: dict[str, set[int]] = defaultdict(set)
    doc_entities: dict[int, set[str]] = {}
    for doc in example.documents:
        entities = extract_entities(f"{doc.title} {doc.text}")
        doc_entities[doc.doc_id] = entities
        for entity in entities:
            entity_to_docs[entity].add(doc.doc_id)
    counts: Counter[int] = Counter()
    for entity, doc_ids in entity_to_docs.items():
        if len(doc_ids) <= 1:
            continue
        for doc_id in doc_ids:
            counts[doc_id] += 1
    return {doc_id: float(counts.get(doc_id, 0)) for doc_id in doc_entities}


def normalize_by_doc_id(values: dict[int, float]) -> dict[int, float]:
    if not values:
        return {}
    min_value = min(values.values())
    max_value = max(values.values())
    if math.isclose(max_value, min_value):
        return {doc_id: 1.0 if max_value > 0 else 0.0 for doc_id in values}
    return {
        doc_id: (value - min_value) / (max_value - min_value)
        for doc_id, value in values.items()
    }


def summarize_doc_selector_rows(
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    failed_examples: list[dict[str, str]],
) -> dict[str, Any]:
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts_by_id: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        method_groups[row["method"]].append(row)
        category_groups[f"{row['method']}::{row['category']}"].append(row)
        category_counts_by_id[row["category"]].add(row["example_id"])

    base_summary = average_metric_summary(base_rows)
    method_level = {
        method: _selector_summary_with_patch_stats(group, base_summary)
        for method, group in sorted(method_groups.items())
    }
    oracle_summary = method_level.get("oracle_evidence_doc_patch")
    random_doc_summary = method_level.get("random_doc_patch_same_count")
    random_token_summary = method_level.get("random_token_patch_same_budget_as_oracle_doc")
    for method, summary in method_level.items():
        if oracle_summary is not None and method != "oracle_evidence_doc_patch":
            summary["gap_to_oracle_evidence_doc_patch"] = _gap_to_reference(
                summary,
                oracle_summary,
            )
        if random_doc_summary is not None and method != "random_doc_patch_same_count":
            summary["improvement_over_random_doc_patch_same_count"] = _improvement_delta(
                summary,
                random_doc_summary,
            )
        if random_token_summary is not None and method != "random_token_patch_same_budget_as_oracle_doc":
            summary["improvement_over_random_token_patch_same_budget_as_oracle_doc"] = (
                _improvement_delta(summary, random_token_summary)
            )

    category_level = {
        key: _selector_summary_with_patch_stats(group, None)
        for key, group in sorted(category_groups.items())
    }
    ranking = sorted(
        (
            {
                "method": method,
                "avg_kl": summary["avg_kl"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
            }
            for method, summary in method_level.items()
        ),
        key=lambda row: row["avg_kl"],
    )
    return {
        "num_rows": len(rows),
        "num_failed_examples": len(failed_examples),
        "failed_examples": failed_examples,
        "category_counts": {
            category: len(example_ids)
            for category, example_ids in sorted(category_counts_by_id.items())
        },
        "base_method_level": base_summary,
        "method_level": method_level,
        "category_level": category_level,
        "method_ranking_by_avg_kl": ranking,
        "best_method_by_avg_kl": ranking[0]["method"] if ranking else None,
        "gate_pareto": gate_pareto_rows(method_level),
    }


def gate_pareto_rows(method_level: dict[str, dict[str, Any]]) -> list[dict[str, float | str]]:
    rows = []
    for method, summary in method_level.items():
        threshold = parse_safe_gate_threshold(method)
        if threshold is None:
            continue
        rows.append(
            {
                "method": method,
                "threshold": threshold,
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                "avg_kl": summary["avg_kl"],
                "top1_mismatch_rate": 1.0 - summary["top1_match_rate"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
            }
        )
    return sorted(rows, key=lambda row: float(row["threshold"]))


def _selector_summary_with_patch_stats(
    rows: list[dict[str, Any]],
    base_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    summary = dict(average_metric_summary(rows))
    summary["avg_patched_doc_count"] = _mean(row.get("patched_doc_count", 0.0) for row in rows)
    summary["avg_patched_token_count"] = _mean(row.get("patched_token_count", 0.0) for row in rows)
    summary["avg_patched_token_ratio"] = _mean(row.get("patched_token_ratio", 0.0) for row in rows)
    if base_summary is not None:
        summary["improvement_over_base"] = _improvement_delta(summary, base_summary)
    return summary


def _improvement_delta(
    method_summary: dict[str, Any],
    reference_summary: dict[str, Any],
) -> dict[str, float]:
    return {
        "kl_reduction": float(reference_summary["avg_kl"] - method_summary["avg_kl"]),
        "js_reduction": float(reference_summary["avg_js"] - method_summary["avg_js"]),
        "top1_gain": float(
            method_summary["top1_match_rate"] - reference_summary["top1_match_rate"]
        ),
        "top10_gain": float(
            method_summary["avg_top10_overlap"] - reference_summary["avg_top10_overlap"]
        ),
    }


def _gap_to_reference(
    method_summary: dict[str, Any],
    reference_summary: dict[str, Any],
) -> dict[str, float]:
    return {
        "kl_gap": float(method_summary["avg_kl"] - reference_summary["avg_kl"]),
        "js_gap": float(method_summary["avg_js"] - reference_summary["avg_js"]),
        "top1_gap": float(
            method_summary["top1_match_rate"] - reference_summary["top1_match_rate"]
        ),
        "top10_gap": float(
            method_summary["avg_top10_overlap"] - reference_summary["avg_top10_overlap"]
        ),
    }


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(sum(float(value) for value in values) / len(values))


def _doc_lookup(example: DiagnosticExample, doc_id: int) -> Document:
    for doc in example.documents:
        if doc.doc_id == doc_id:
            return doc
    raise KeyError(doc_id)


_ENTITY_STOPWORDS = {
    "A",
    "An",
    "And",
    "Archive",
    "Document",
    "Note",
    "Question",
    "The",
}.union({item.lower() for item in ["A", "An", "And", "Archive", "Document", "Note", "Question", "The"]})


__all__ = [
    "DEFAULT_GATE_THRESHOLDS",
    "DOC_SELECTOR_KINDS",
    "DocumentScore",
    "GateDecision",
    "answer_candidate_terms",
    "conflict_aware_doc_ids",
    "conflict_candidate_docs",
    "default_doc_selector_methods",
    "document_ranges_for_ids",
    "entity_overlap_doc_scores",
    "extract_entities",
    "gate_decision",
    "gate_pareto_rows",
    "oracle_doc_ids",
    "parse_safe_gate_threshold",
    "patch_ranges_for_doc_selector_method",
    "query_similarity_doc_scores",
    "random_doc_ids_same_count",
    "retrieval_doc_scores",
    "risk_guided_doc_scores",
    "safe_composition_risk",
    "safe_gate_method_name",
    "select_top_k_doc_ids",
    "selected_doc_ids_for_method",
    "summarize_doc_selector_rows",
]
