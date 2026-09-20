#!/usr/bin/env python
"""Build a document-position sweep dataset for SAFE-KV.

The sweep follows the spirit of lost-in-the-middle evaluations: keep the same
answer-bearing document text, vary where that document appears in the retrieved
document list, and preserve SAFE-KV evidence labels.
"""

from __future__ import annotations

import argparse
import copy
import random
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl, write_jsonl  # noqa: E402
from safekv.data_schema import DiagnosticExample, Document  # noqa: E402


POSITION_ALIASES = {
    "first": 0.0,
    "early": 0.25,
    "middle": 0.5,
    "late": 0.75,
    "last": 1.0,
}

FILLER_TEXTS = [
    "The appendix lists routine archive movements unrelated to the query.",
    "A maintenance note describes old shelf labels and duplicate folders.",
    "The registry includes a cross-reference to a different project code.",
    "A background memo summarizes catalog procedures for internal review.",
    "The inventory table records a weathered tag from the storage annex.",
    "A routing slip mentions a courier window but no answer evidence.",
    "The preservation log describes paper quality and binding repairs.",
    "An index card repeats several topic words without the target fact.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--category", default="single_evidence")
    parser.add_argument("--docs-per-example", type=int, default=11)
    parser.add_argument(
        "--positions",
        default="first,early,middle,late,last",
        help="Comma-separated labels or numeric indices.",
    )
    parser.add_argument("--max-base-examples", type=int, default=None)
    parser.add_argument("--seed", type=int, default=13)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = [
        example
        for example in read_jsonl(args.input)
        if example.category == args.category and len({ev.doc_id for ev in example.evidence}) == 1
    ]
    if args.max_base_examples is not None:
        examples = examples[: args.max_base_examples]
    if not examples:
        raise ValueError("no one-evidence examples matched the requested category")

    positions = parse_positions(args.positions, args.docs_per_example)
    swept: list[DiagnosticExample] = []
    rng = random.Random(args.seed)
    for example in examples:
        for label, index in positions:
            swept.append(
                move_evidence_doc(
                    example,
                    position_label=label,
                    target_index=index,
                    docs_per_example=args.docs_per_example,
                    rng=rng,
                )
            )

    write_jsonl(swept, args.out)
    print(
        f"Wrote {len(swept)} position-sweep examples from {len(examples)} base examples "
        f"to {args.out}"
    )


def parse_positions(raw: str, docs_per_example: int) -> list[tuple[str, int]]:
    if docs_per_example < 3:
        raise ValueError("--docs-per-example must be at least 3")
    positions: list[tuple[str, int]] = []
    for item in raw.split(","):
        label = item.strip()
        if not label:
            continue
        if label in POSITION_ALIASES:
            index = round(POSITION_ALIASES[label] * (docs_per_example - 1))
        else:
            index = int(label)
        if not 0 <= index < docs_per_example:
            raise ValueError(f"position {label!r} resolves to invalid index {index}")
        positions.append((label, index))
    if not positions:
        raise ValueError("--positions must contain at least one position")
    return positions


def move_evidence_doc(
    example: DiagnosticExample,
    *,
    position_label: str,
    target_index: int,
    docs_per_example: int,
    rng: random.Random,
) -> DiagnosticExample:
    evidence_doc_id = example.evidence[0].doc_id
    evidence_doc = copy.deepcopy(_doc_by_id(example, evidence_doc_id))
    distractors = [copy.deepcopy(doc) for doc in example.documents if doc.doc_id != evidence_doc_id]
    distractors = pad_distractors(example, distractors, docs_per_example - 1, rng)
    rng.shuffle(distractors)

    ordered_docs = distractors[:]
    ordered_docs.insert(target_index, evidence_doc)
    ordered_docs = ordered_docs[:docs_per_example]
    if evidence_doc not in ordered_docs:
        ordered_docs[-1] = evidence_doc
    swept = replace(
        example,
        id=f"{example.id}_pos_{position_label}",
        documents=ordered_docs,
    )
    swept.validate()
    return swept


def pad_distractors(
    example: DiagnosticExample,
    distractors: list[Document],
    target_count: int,
    rng: random.Random,
) -> list[Document]:
    if len(distractors) >= target_count:
        return distractors[:target_count]
    next_doc_id = max(doc.doc_id for doc in example.documents) + 1
    padded = distractors[:]
    while len(padded) < target_count:
        text = rng.choice(FILLER_TEXTS)
        title = f"Position Sweep Distractor {next_doc_id}"
        padded.append(
            Document(
                doc_id=next_doc_id,
                title=title,
                text=text,
                role="distractor",
                retrieval_score=round(rng.uniform(0.05, 0.65), 3),
            )
        )
        next_doc_id += 1
    return padded


def _doc_by_id(example: DiagnosticExample, doc_id: int) -> Document:
    for doc in example.documents:
        if doc.doc_id == doc_id:
            return doc
    raise ValueError(f"{example.id}: missing document {doc_id}")


if __name__ == "__main__":
    main()
