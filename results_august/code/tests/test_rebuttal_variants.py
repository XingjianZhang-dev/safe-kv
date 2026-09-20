from safekv.build_diagnostic import build_diagnostic_examples
from safekv.rebuttal_variants import (
    build_nested_single_evidence_variant,
    transform_external_example,
    variant_summary,
)


def test_transform_neutralizes_shuffles_and_remaps_evidence() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    transformed = transform_external_example(
        example,
        retrieval_mode="zero",
        shuffle_seed=101,
    )

    assert transformed is not None
    transformed.validate()
    assert [doc.doc_id for doc in transformed.documents] == list(
        range(len(transformed.documents))
    )
    assert {doc.retrieval_score for doc in transformed.documents} == {0.0}
    assert all(
        evidence.text in transformed.documents[evidence.doc_id].text
        for evidence in transformed.evidence
    )


def test_document_cap_keeps_evidence_or_skips() -> None:
    example = next(
        candidate
        for candidate in build_diagnostic_examples(n_per_category=1, seed=13)
        if len({item.doc_id for item in candidate.evidence}) > 1
    )
    evidence_count = len({item.doc_id for item in example.evidence})

    assert transform_external_example(example, max_documents=evidence_count - 1) is None
    transformed = transform_external_example(example, max_documents=evidence_count)
    assert transformed is not None
    assert len(transformed.documents) == evidence_count
    transformed.validate()


def test_variant_summary_detects_neutral_scores() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    transformed = transform_external_example(example, retrieval_mode="zero")
    assert transformed is not None

    summary = variant_summary([transformed])
    assert summary["num_examples"] == 1
    assert summary["perfect_gold_score_separation_rate"] == 0.0


def test_nested_variants_preserve_relative_order_and_support() -> None:
    example = build_diagnostic_examples(n_per_category=1, seed=13)[0]
    small = build_nested_single_evidence_variant(
        example,
        num_documents=2,
        layout_seed=101,
    )
    large = build_nested_single_evidence_variant(
        example,
        num_documents=3,
        layout_seed=101,
    )
    assert small is not None and large is not None
    small_titles = [doc.title for doc in small.documents]
    large_titles = [doc.title for doc in large.documents]
    assert set(small_titles).issubset(large_titles)
    assert small_titles == [title for title in large_titles if title in set(small_titles)]
    assert all(item.text in small.documents[item.doc_id].text for item in small.evidence)
