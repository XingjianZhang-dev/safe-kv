from __future__ import annotations

import json

from safekv.data_schema import DiagnosticExample
from safekv_ipm.data_build import (
    SourceDocument,
    SourceExample,
    convert_example,
    normalize_scores,
    order_documents,
    parse_2wiki,
    parse_musique,
)


class LabelBlindDenseRanker:
    model_name = "test/dense"
    revision = "pinned"

    def scores(self, question: str, documents: list[str]) -> list[float]:
        return [float(text.lower().count("paris")) for text in documents]


def example() -> SourceExample:
    return SourceExample(
        source_id="x",
        category="external_2wiki",
        question="Which city hosted the event?",
        answer="Paris",
        documents=(
            SourceDocument(0, "Noise", "Unrelated text.", ()),
            SourceDocument(1, "Bridge", "The event was held in Paris.", ("The event was held in Paris.",)),
            SourceDocument(2, "Paris", "Paris is in France.", ("Paris is in France.",)),
        ),
    )


def test_natural_order_is_preserved_and_scores_are_neutral():
    ordered, scores = order_documents(example(), "natural", 7, None)
    assert [doc.source_index for doc in ordered] == [0, 1, 2]
    assert scores == [0.0, 0.0, 0.0]


def test_shuffle_is_deterministic_and_does_not_add_scores():
    first, first_scores = order_documents(example(), "shuffle", 7, None)
    second, second_scores = order_documents(example(), "shuffle", 7, None)
    assert [doc.source_index for doc in first] == [doc.source_index for doc in second]
    assert first_scores == second_scores == [0.0, 0.0, 0.0]


def test_bm25_ranking_does_not_read_evidence_labels():
    original, scores = order_documents(example(), "bm25", 7, None)
    relabeled = SourceExample(
        source_id=example().source_id,
        category=example().category,
        question=example().question,
        answer=example().answer,
        documents=tuple(
            SourceDocument(doc.source_index, doc.title, doc.text, ())
            for doc in example().documents
        ),
    )
    changed, changed_scores = order_documents(relabeled, "bm25", 7, None)
    assert [doc.source_index for doc in original] == [doc.source_index for doc in changed]
    assert scores == changed_scores


def test_dense_ranking_does_not_read_evidence_labels():
    ranker = LabelBlindDenseRanker()
    original, scores = order_documents(example(), "dense", 7, ranker)
    relabeled = SourceExample(
        source_id=example().source_id,
        category=example().category,
        question=example().question,
        answer=example().answer,
        documents=tuple(
            SourceDocument(doc.source_index, doc.title, doc.text, ())
            for doc in example().documents
        ),
    )
    changed, changed_scores = order_documents(relabeled, "dense", 7, ranker)
    assert [doc.source_index for doc in original] == [doc.source_index for doc in changed]
    assert scores == changed_scores


def test_conversion_remaps_evidence_and_validates_runtime_schema():
    row = convert_example(
        example(),
        dataset="2wiki",
        split="test",
        condition="shuffle",
        seed=9,
        dense_ranker=None,
    )
    parsed = DiagnosticExample.from_dict(row)
    assert len({item.doc_id for item in parsed.evidence}) == 2
    assert row["source_metadata"]["gold_labels_used_for_ranking"] is False
    assert sorted(row["source_metadata"]["source_doc_indices_in_prompt_order"]) == [0, 1, 2]


def test_parse_2wiki_uses_supporting_sentences(tmp_path):
    path = tmp_path / "dev.json"
    path.write_text(
        json.dumps(
            [
                {
                    "_id": "q1",
                    "question": "q?",
                    "answer": "a",
                    "context": [
                        ["A", ["a0", "a1"]],
                        ["B", ["b0"]],
                        ["C", ["c0"]],
                    ],
                    "supporting_facts": [["A", 1], ["B", 0]],
                }
            ]
        ),
        encoding="utf-8",
    )
    parsed = parse_2wiki(path)[0]
    assert parsed.documents[0].evidence_texts == ("a1",)
    assert parsed.documents[1].evidence_texts == ("b0",)


def test_parse_musique_uses_answerable_supporting_paragraphs(tmp_path):
    path = tmp_path / "dev.jsonl"
    row = {
        "id": "m1",
        "question": "q?",
        "answer": "a",
        "answerable": True,
        "paragraphs": [
            {"idx": 0, "title": "A", "paragraph_text": "alpha", "is_supporting": True},
            {"idx": 1, "title": "B", "paragraph_text": "beta", "is_supporting": False},
            {"idx": 2, "title": "C", "paragraph_text": "gamma", "is_supporting": True},
        ],
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    parsed = parse_musique(path)[0]
    assert parsed.category == "external_musique"
    assert parsed.documents[0].evidence_texts == ("alpha",)
    assert parsed.documents[1].evidence_texts == ()


def test_normalize_scores_handles_constant_values():
    assert normalize_scores([3.0, 3.0]) == [0.0, 0.0]
    assert normalize_scores([1.0, 3.0]) == [0.0, 1.0]
