"""Typed schemas for SAFE-KV diagnostic examples and prompt packs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Category = Literal[
    "single_evidence",
    "multi_hop",
    "conflict",
    "boundary_sensitive",
    "distractor_heavy",
    "external_hotpotqa",
    "external_2wiki",
    "external_musique",
]

Role = Literal["evidence", "conflict", "distractor", "unknown"]


@dataclass(frozen=True)
class Document:
    doc_id: int
    title: str
    text: str
    role: Role
    retrieval_score: float

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Document":
        return cls(
            doc_id=int(row["doc_id"]),
            title=str(row["title"]),
            text=str(row["text"]),
            role=row.get("role", "unknown"),
            retrieval_score=float(row.get("retrieval_score", 0.0)),
        )


@dataclass(frozen=True)
class EvidenceSpan:
    doc_id: int
    text: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "EvidenceSpan":
        return cls(doc_id=int(row["doc_id"]), text=str(row["text"]))


@dataclass(frozen=True)
class DiagnosticExample:
    id: str
    category: Category
    documents: list[Document]
    question: str
    gold_answer: str
    evidence: list[EvidenceSpan]
    conflicting_docs: list[int]
    requires_cross_doc: bool

    def validate(self) -> None:
        if not self.id:
            raise ValueError("example id must be non-empty")
        if not self.documents:
            raise ValueError(f"{self.id}: at least one document is required")

        doc_ids = {doc.doc_id for doc in self.documents}
        if len(doc_ids) != len(self.documents):
            raise ValueError(f"{self.id}: document ids must be unique")

        for evidence in self.evidence:
            if evidence.doc_id not in doc_ids:
                raise ValueError(f"{self.id}: evidence doc_id {evidence.doc_id} is missing")
            doc = next(doc for doc in self.documents if doc.doc_id == evidence.doc_id)
            if evidence.text not in doc.text:
                raise ValueError(
                    f"{self.id}: evidence text {evidence.text!r} not found in doc {evidence.doc_id}"
                )

        missing_conflicts = [doc_id for doc_id in self.conflicting_docs if doc_id not in doc_ids]
        if missing_conflicts:
            raise ValueError(f"{self.id}: conflicting doc ids are missing: {missing_conflicts}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "DiagnosticExample":
        example = cls(
            id=str(row["id"]),
            category=row["category"],
            documents=[Document.from_dict(doc) for doc in row["documents"]],
            question=str(row["question"]),
            gold_answer=str(row["gold_answer"]),
            evidence=[EvidenceSpan.from_dict(ev) for ev in row.get("evidence", [])],
            conflicting_docs=[int(doc_id) for doc_id in row.get("conflicting_docs", [])],
            requires_cross_doc=bool(row.get("requires_cross_doc", False)),
        )
        example.validate()
        return example


@dataclass(frozen=True)
class TokenRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError("token range start must be non-negative")
        if self.end < self.start:
            raise ValueError("token range end must be >= start")

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class CharRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError("char range start must be non-negative")
        if self.end < self.start:
            raise ValueError("char range end must be >= start")

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class DocCharInfo:
    doc_id: int
    prompt_doc_index: int
    title: str
    block_char_range: CharRange
    text_char_range: CharRange


@dataclass(frozen=True)
class SpanCharInfo:
    span_id: str
    doc_id: int
    text: str
    prompt_char_range: CharRange
    char_range_in_doc: tuple[int, int]
    role: Role
    retrieval_score: float
    contains_gold_evidence: bool


@dataclass(frozen=True)
class PromptTextAndCharRanges:
    example_id: str
    prompt_format: str
    full_text: str
    context_text: str
    query_text: str
    context_char_range: CharRange
    query_char_range: CharRange
    doc_char_ranges: list[DocCharInfo]
    span_char_ranges: list[SpanCharInfo]
    evidence_span_ids: list[str]
    conflict_doc_ids: list[int]


@dataclass(frozen=True)
class SpanInfo:
    span_id: str
    doc_id: int
    text: str
    token_range: TokenRange
    prompt_char_range: CharRange
    char_range_in_doc: tuple[int, int] | None
    role: Role
    retrieval_score: float
    token_distance_to_doc_start: int
    token_distance_to_doc_end: int
    boundary_token_overlap_ratio: float
    effective_boundary_window_tokens: int
    contains_gold_evidence: bool


@dataclass(frozen=True)
class PromptPack:
    example_id: str
    prompt_format: str
    full_text: str
    context_text: str
    query_text: str
    full_input_ids: list[int]
    context_input_ids: list[int]
    query_input_ids: list[int]
    doc_ranges: list[TokenRange]
    doc_text_ranges: list[TokenRange]
    context_token_range: TokenRange
    query_token_range: TokenRange
    doc_char_ranges: list[DocCharInfo]
    span_ranges: list[SpanInfo]
    evidence_span_ids: list[str]
    conflict_doc_ids: list[int]
    offset_mapping: list[tuple[int, int]]
    offset_mapping_source: str
    boundary_window_tokens: int
