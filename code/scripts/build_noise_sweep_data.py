#!/usr/bin/env python
"""Build retrieval-noise sweep datasets for SAFE-KV."""

from __future__ import annotations

import argparse
import random
import re
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl, write_jsonl  # noqa: E402
from safekv.data_schema import DiagnosticExample, Document  # noqa: E402


DISTRACTOR_TEMPLATES = [
    "The archive index repeats the terms {terms}, but it gives no answer to the question.",
    "A related catalog note mentions {terms} while describing an unrelated maintenance record.",
    "The retrieval appendix includes {terms} as cross-reference tags without factual support.",
    "An older memo uses the phrase {terms}, but discusses a different registry entry.",
    "The background report lists {terms} in a filing table unrelated to the requested fact.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--extra-distractors", type=int, required=True)
    parser.add_argument("--max-per-category", type=int, default=None)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--shuffle-docs", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.extra_distractors < 0:
        raise ValueError("--extra-distractors must be non-negative")
    rng = random.Random(args.seed + args.extra_distractors * 997)
    examples = limit_per_category(read_jsonl(args.input), args.max_per_category)
    swept = [
        add_retrieval_noise(
            example,
            extra_distractors=args.extra_distractors,
            rng=rng,
            shuffle_docs=args.shuffle_docs,
        )
        for example in examples
    ]
    write_jsonl(swept, args.out)
    print(
        f"Wrote {len(swept)} examples with {args.extra_distractors} extra distractors "
        f"to {args.out}"
    )


def limit_per_category(
    examples: list[DiagnosticExample],
    max_per_category: int | None,
) -> list[DiagnosticExample]:
    if max_per_category is None:
        return examples
    counts: Counter[str] = Counter()
    kept: list[DiagnosticExample] = []
    for example in examples:
        if counts[example.category] >= max_per_category:
            continue
        kept.append(example)
        counts[example.category] += 1
    return kept


def add_retrieval_noise(
    example: DiagnosticExample,
    *,
    extra_distractors: int,
    rng: random.Random,
    shuffle_docs: bool,
) -> DiagnosticExample:
    docs = list(example.documents)
    next_doc_id = max(doc.doc_id for doc in docs) + 1
    query_terms = query_content_terms(example.question)
    for offset in range(extra_distractors):
        terms = " ".join(rng.sample(query_terms, k=min(len(query_terms), max(1, min(4, len(query_terms))))))
        template = DISTRACTOR_TEMPLATES[(offset + len(example.id)) % len(DISTRACTOR_TEMPLATES)]
        docs.append(
            Document(
                doc_id=next_doc_id + offset,
                title=f"Noise Sweep Distractor {offset + 1}",
                text=template.format(terms=terms),
                role="distractor",
                retrieval_score=round(rng.uniform(0.70, 0.99), 3),
            )
        )
    if shuffle_docs:
        rng.shuffle(docs)
    noisy = replace(
        example,
        id=f"{example.id}_noise{extra_distractors}",
        documents=docs,
    )
    noisy.validate()
    return noisy


def query_content_terms(question: str) -> list[str]:
    terms = [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]+", question)
        if len(token) > 3
        and token.lower()
        not in {
            "what",
            "when",
            "where",
            "which",
            "according",
            "answer",
            "from",
            "with",
            "documents",
        }
    ]
    return sorted(set(terms)) or ["archive", "record", "question"]


if __name__ == "__main__":
    main()
