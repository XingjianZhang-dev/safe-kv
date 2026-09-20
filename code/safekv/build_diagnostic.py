"""Synthetic diagnostic data generation for SAFE-KV v0 Milestone 1."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

from safekv.data_schema import DiagnosticExample, Document, EvidenceSpan

CATEGORIES = [
    "single_evidence",
    "multi_hop",
    "conflict",
    "boundary_sensitive",
    "distractor_heavy",
]

NAMES = [
    "Mira Solen",
    "Aria Lorne",
    "Sera Mavin",
    "Tovan Reed",
    "Lina Kest",
    "Orin Vale",
    "Nadia Voss",
    "Eren Cal",
    "Ilya Marr",
    "Vera Noll",
    "Jalen Irix",
    "Priya Holt",
]

PLACES = [
    "Norwick",
    "Velora",
    "Mariton",
    "Halden",
    "Qorlan",
    "Brevic",
    "Lydora",
    "Kelminster",
    "Aster Port",
    "Rivenfall",
]

PROJECTS = [
    "Valen",
    "Meros",
    "Zorvian",
    "Ralvex",
    "Fenric",
    "Orison",
    "Caldrin",
    "Veyra",
    "Harrow",
    "Nimbar",
]

OBJECTS = [
    "device",
    "observatory",
    "compound",
    "archive",
    "beacon",
    "registry",
    "sensor",
    "atlas",
    "reactor",
    "protocol",
]

DISTRACTOR_SENTENCES = [
    "The Harven moss grows near shaded river stones.",
    "The eastern metro loop closes after midnight on festival days.",
    "The Orin valley receives strong coastal winds in autumn.",
    "A silver pressure gauge was stored near Lab D.",
    "The museum catalog lists three ceramic tablets from the old harbor.",
    "The courier manifest mentions a blue container beside Gate 4.",
    "The garden survey tracked rainfall near the western greenhouse.",
    "The field notebook describes a quiet market on Lantern Street.",
]

BACKGROUND_SENTENCES = [
    "The archive clerk copied the entry onto a cream index card.",
    "A later inventory marked the folder as reviewed but unchanged.",
    "The note includes a catalog stamp from the northern records room.",
    "Two duplicate pages were stored behind the main memorandum.",
    "The attached routing slip lists no emergency handling instructions.",
    "A marginal annotation asks readers to verify the source before quoting it.",
    "The file was moved during the spring shelf audit.",
    "The summary paragraph was prepared for internal reference only.",
    "A table at the end lists unrelated maintenance codes.",
    "The record uses the same naming convention as the adjacent folders.",
    "The document footer says the copy was prepared after routine review.",
    "Several older labels were crossed out in pencil.",
]


def build_diagnostic_examples(
    n_per_category: int = 20,
    seed: int = 13,
    variant: str = "default",
) -> list[DiagnosticExample]:
    """Build a deterministic synthetic dataset with all five SAFE-KV categories."""

    if n_per_category <= 0:
        raise ValueError("n_per_category must be positive")
    if variant not in {"default", "noisy_retrieval"}:
        raise ValueError("variant must be 'default' or 'noisy_retrieval'")

    rng = random.Random(seed)
    examples: list[DiagnosticExample] = []
    for category in CATEGORIES:
        builders = {
            "single_evidence": _build_single_evidence,
            "multi_hop": _build_multi_hop,
            "conflict": _build_conflict,
            "boundary_sensitive": _build_boundary_sensitive,
            "distractor_heavy": _build_distractor_heavy,
        }
        for index in range(n_per_category):
            example = builders[category](index=index, rng=rng)
            example.validate()
            examples.append(example)
    if variant == "noisy_retrieval":
        examples = _make_noisy_retrieval_variant(examples, seed=seed)
    return examples


def write_jsonl(examples: Iterable[DiagnosticExample], path: str | Path) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: str | Path) -> list[DiagnosticExample]:
    examples: list[DiagnosticExample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                examples.append(DiagnosticExample.from_dict(json.loads(line)))
    return examples


def _pick(seq: list[str], index: int, offset: int = 0) -> str:
    return seq[(index + offset) % len(seq)]


def _shuffled_distractors(rng: random.Random, count: int) -> list[str]:
    pool = DISTRACTOR_SENTENCES[:]
    rng.shuffle(pool)
    return pool[:count]


def _filler_sentences(rng: random.Random, count: int) -> list[str]:
    pool = BACKGROUND_SENTENCES + DISTRACTOR_SENTENCES
    rng.shuffle(pool)
    return pool[:count]


def _positioned_doc_text(
    evidence_sentence: str,
    index: int,
    rng: random.Random,
    placement: str | None = None,
) -> str:
    total_sentences = 3 + (index % 3)
    fillers = _filler_sentences(rng, total_sentences - 1)
    sentences = fillers[:]
    resolved_placement = placement or ("start", "middle", "end")[index % 3]
    if resolved_placement == "start":
        insert_at = 0
    elif resolved_placement == "middle":
        insert_at = total_sentences // 2
    elif resolved_placement == "end":
        insert_at = total_sentences - 1
    else:
        raise ValueError(f"unsupported evidence placement {resolved_placement!r}")
    sentences.insert(insert_at, evidence_sentence)
    return " ".join(sentences)


def _distractor_doc_text(rng: random.Random, index: int) -> str:
    total_sentences = 3 + (index % 3)
    return " ".join(_filler_sentences(rng, total_sentences))


def _make_noisy_retrieval_variant(
    examples: list[DiagnosticExample],
    seed: int,
) -> list[DiagnosticExample]:
    """Return a deterministic variant with misleading retrieval and overlap signals.

    The transformation preserves document ids and evidence strings, but shuffles
    document order and injects question-overlap distractor text. This keeps prompt
    span labels valid while making document-level selector validity harder to fake.
    """

    rng = random.Random(seed + 10_003)
    noisy_examples: list[DiagnosticExample] = []
    for example in examples:
        docs = [_noisy_document(example, doc, rng) for doc in example.documents]
        rng.shuffle(docs)
        noisy = DiagnosticExample(
            id=f"{example.id}_noisy",
            category=example.category,
            documents=docs,
            question=example.question,
            gold_answer=example.gold_answer,
            evidence=example.evidence,
            conflicting_docs=example.conflicting_docs,
            requires_cross_doc=example.requires_cross_doc,
        )
        noisy.validate()
        noisy_examples.append(noisy)
    return noisy_examples


def _noisy_document(
    example: DiagnosticExample,
    doc: Document,
    rng: random.Random,
) -> Document:
    support_doc_ids = {evidence.doc_id for evidence in example.evidence}
    conflict_doc_ids = set(example.conflicting_docs)
    is_support = doc.doc_id in support_doc_ids
    is_conflict = doc.doc_id in conflict_doc_ids

    retrieval_score = _noisy_retrieval_score(example, doc, is_support, is_conflict, rng)
    text = doc.text
    if not is_support and rng.random() < 0.85:
        overlap_sentence = _overlap_noise_sentence(example, rng)
        text = _append_sentence_preserving_span_count(text, overlap_sentence)
    return Document(
        doc_id=doc.doc_id,
        title=doc.title,
        text=text,
        role=doc.role,
        retrieval_score=retrieval_score,
    )


def _noisy_retrieval_score(
    example: DiagnosticExample,
    doc: Document,
    is_support: bool,
    is_conflict: bool,
    rng: random.Random,
) -> float:
    if example.category == "conflict" and is_conflict:
        return 1.0
    if example.category == "conflict" and is_support:
        return 0.55
    if is_support:
        return round(rng.uniform(0.45, 0.75), 3)
    return round(rng.uniform(0.70, 0.98), 3)


def _overlap_noise_sentence(example: DiagnosticExample, rng: random.Random) -> str:
    terms = [
        token
        for token in example.question.replace("?", "").replace(",", "").split()
        if len(token) > 3 and token.lower() not in {"what", "when", "where", "which", "according"}
    ]
    if not terms:
        terms = ["archive", "record"]
    rng.shuffle(terms)
    chosen = " ".join(terms[: min(4, len(terms))])
    return f"The appendix repeats the query terms {chosen} for filing cross-reference."


def _append_sentence_preserving_span_count(text: str, sentence: str) -> str:
    parts = [part.strip() for part in text.split(".") if part.strip()]
    if len(parts) >= 5:
        parts[-1] = f"{parts[-1]}; {sentence.rstrip('.')}"
        return ". ".join(parts) + "."
    return f"{text.rstrip()} {sentence}"


def _build_single_evidence(index: int, rng: random.Random) -> DiagnosticExample:
    artifact = _pick(PROJECTS, index)
    person = _pick(NAMES, index)
    year = 1980 + (index % 35)
    distractors = _shuffled_distractors(rng, 2)
    docs = [
        Document(
            doc_id=0,
            title="Archive Note A",
            text=_positioned_doc_text(
                f"The {artifact} device was calibrated by {person} in {year}.",
                index=index,
                rng=rng,
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=1,
            title="Archive Note B",
            text=_positioned_doc_text(distractors[0], index=index + 1, rng=rng),
            role="distractor",
            retrieval_score=0.2,
        ),
        Document(
            doc_id=2,
            title="Archive Note C",
            text=_positioned_doc_text(distractors[1], index=index + 2, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
    ]
    return DiagnosticExample(
        id=f"single_{index:04d}",
        category="single_evidence",
        documents=docs,
        question=f"Who calibrated the {artifact} device?",
        gold_answer=person,
        evidence=[EvidenceSpan(doc_id=0, text=f"calibrated by {person}")],
        conflicting_docs=[],
        requires_cross_doc=False,
    )


def _build_multi_hop(index: int, rng: random.Random) -> DiagnosticExample:
    project = _pick(PROJECTS, index, 1)
    person = _pick(NAMES, index, 2)
    birthplace = _pick(PLACES, index, 3)
    distractor = _shuffled_distractors(rng, 1)[0]
    docs = [
        Document(
            doc_id=0,
            title="Personnel File",
            text=_positioned_doc_text(
                f"{person} was born in {birthplace} before joining the research office.",
                index=index,
                rng=rng,
            ),
            role="evidence",
            retrieval_score=0.9,
        ),
        Document(
            doc_id=1,
            title="Research Log",
            text=_positioned_doc_text(
                f"Project {project} was designed by {person} during the winter review.",
                index=index + 1,
                rng=rng,
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=2,
            title="Unrelated Note",
            text=_positioned_doc_text(distractor, index=index + 2, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
    ]
    return DiagnosticExample(
        id=f"multihop_{index:04d}",
        category="multi_hop",
        documents=docs,
        question=f"Where was the designer of Project {project} born?",
        gold_answer=birthplace,
        evidence=[
            EvidenceSpan(doc_id=0, text=f"{person} was born in {birthplace}"),
            EvidenceSpan(doc_id=1, text=f"Project {project} was designed by {person}"),
        ],
        conflicting_docs=[],
        requires_cross_doc=True,
    )


def _build_conflict(index: int, rng: random.Random) -> DiagnosticExample:
    place = _pick(PLACES, index, 4)
    open_hour = f"{8 + (index % 4)} AM"
    old_hour = f"{10 + (index % 3)} AM"
    if old_hour == open_hour:
        old_hour = "1 PM"
    distractor = _shuffled_distractors(rng, 1)[0]
    docs = [
        Document(
            doc_id=0,
            title="Official Schedule",
            text=_positioned_doc_text(
                f"According to the official schedule, the {place} observatory opens at {open_hour}.",
                index=index,
                rng=rng,
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=1,
            title="Old Visitor Blog",
            text=_positioned_doc_text(
                f"An old visitor blog says the {place} observatory opens at {old_hour}.",
                index=index + 1,
                rng=rng,
            ),
            role="conflict",
            retrieval_score=0.8,
        ),
        Document(
            doc_id=2,
            title="Transit Note",
            text=_positioned_doc_text(distractor, index=index + 2, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
    ]
    return DiagnosticExample(
        id=f"conflict_{index:04d}",
        category="conflict",
        documents=docs,
        question=f"According to the official schedule, when does the {place} observatory open?",
        gold_answer=open_hour,
        evidence=[
            EvidenceSpan(
                doc_id=0,
                text=f"official schedule, the {place} observatory opens at {open_hour}",
            )
        ],
        conflicting_docs=[1],
        requires_cross_doc=False,
    )


def _build_boundary_sensitive(index: int, rng: random.Random) -> DiagnosticExample:
    compound = _pick(PROJECTS, index, 3)
    person = _pick(NAMES, index, 5)
    year = 1990 + (index % 28)
    distractor = _shuffled_distractors(rng, 1)[0]
    docs = [
        Document(
            doc_id=0,
            title="Lab Note Part A",
            text=(
                " ".join(_filler_sentences(rng, 2 + (index % 2)))
                + f" The compound {compound} was first synthesized by Dr. {person} in"
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=1,
            title="Lab Note Part B",
            text=(
                f"{year} during a cold-chamber stability test. "
                + " ".join(_filler_sentences(rng, 2 + ((index + 1) % 2)))
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=2,
            title="Storage Note",
            text=_positioned_doc_text(distractor, index=index + 2, rng=rng),
            role="distractor",
            retrieval_score=0.2,
        ),
    ]
    return DiagnosticExample(
        id=f"boundary_{index:04d}",
        category="boundary_sensitive",
        documents=docs,
        question=f"In what year was {compound} first synthesized?",
        gold_answer=str(year),
        evidence=[
            EvidenceSpan(
                doc_id=0,
                text=f"first synthesized by Dr. {person} in",
            ),
            EvidenceSpan(doc_id=1, text=str(year)),
        ],
        conflicting_docs=[],
        requires_cross_doc=True,
    )


def _build_distractor_heavy(index: int, rng: random.Random) -> DiagnosticExample:
    prize_year = 2010 + (index % 15)
    prize = _pick(PROJECTS, index, 5)
    winner = _pick(NAMES, index, 7)
    topic = _pick(OBJECTS, index, 4)
    distractors = _shuffled_distractors(rng, 5)
    docs = [
        Document(
            doc_id=0,
            title="Botany Note",
            text=_positioned_doc_text(distractors[0], index=index, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
        Document(
            doc_id=1,
            title="Award Note",
            text=_positioned_doc_text(
                (
                    f"The {prize_year} {prize} Prize was awarded to {winner} "
                    f"for {topic} transport research."
                ),
                index=index + 1,
                rng=rng,
            ),
            role="evidence",
            retrieval_score=1.0,
        ),
        Document(
            doc_id=2,
            title="Transit Note",
            text=_positioned_doc_text(distractors[1], index=index + 2, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
        Document(
            doc_id=3,
            title="Weather Note",
            text=_positioned_doc_text(distractors[2], index=index + 3, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
        Document(
            doc_id=4,
            title="Archive Note",
            text=_positioned_doc_text(distractors[3], index=index + 4, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
        Document(
            doc_id=5,
            title="Market Note",
            text=_positioned_doc_text(distractors[4], index=index + 5, rng=rng),
            role="distractor",
            retrieval_score=0.1,
        ),
    ]
    return DiagnosticExample(
        id=f"distractor_{index:04d}",
        category="distractor_heavy",
        documents=docs,
        question=f"Who received the {prize_year} {prize} Prize for {topic} transport research?",
        gold_answer=winner,
        evidence=[
            EvidenceSpan(
                doc_id=1,
                text=f"awarded to {winner} for {topic} transport research",
            )
        ],
        conflicting_docs=[],
        requires_cross_doc=False,
    )
