from collections import Counter

from safekv.build_diagnostic import CATEGORIES, build_diagnostic_examples, read_jsonl, write_jsonl
from safekv.token_spans import split_doc_spans


def test_diagnostic_generation_is_deterministic() -> None:
    first = build_diagnostic_examples(n_per_category=3, seed=13)
    second = build_diagnostic_examples(n_per_category=3, seed=13)

    assert [example.to_dict() for example in first] == [example.to_dict() for example in second]


def test_diagnostic_generation_category_counts() -> None:
    examples = build_diagnostic_examples(n_per_category=4, seed=13)
    counts = Counter(example.category for example in examples)

    assert len(examples) == 4 * len(CATEGORIES)
    assert counts == {category: 4 for category in CATEGORIES}


def test_jsonl_round_trip(tmp_path) -> None:
    examples = build_diagnostic_examples(n_per_category=1, seed=13)
    out_path = tmp_path / "diagnostic.jsonl"

    write_jsonl(examples, out_path)
    loaded = read_jsonl(out_path)

    assert [example.to_dict() for example in loaded] == [example.to_dict() for example in examples]


def test_generated_documents_have_three_to_five_spans() -> None:
    examples = build_diagnostic_examples(n_per_category=2, seed=13)

    for example in examples:
        for doc in example.documents:
            span_count = len(split_doc_spans(doc.text))
            assert 3 <= span_count <= 5, f"{example.id} doc {doc.doc_id}: {span_count}"


def test_noisy_retrieval_variant_preserves_labels_and_adds_noise() -> None:
    clean = build_diagnostic_examples(n_per_category=1, seed=13)
    noisy = build_diagnostic_examples(n_per_category=1, seed=13, variant="noisy_retrieval")

    assert len(noisy) == len(clean)
    for clean_example, noisy_example in zip(clean, noisy, strict=True):
        noisy_example.validate()
        assert noisy_example.id == f"{clean_example.id}_noisy"
        assert noisy_example.category == clean_example.category
        assert noisy_example.question == clean_example.question
        assert noisy_example.gold_answer == clean_example.gold_answer
        assert noisy_example.evidence == clean_example.evidence
        assert {doc.doc_id for doc in noisy_example.documents} == {
            doc.doc_id for doc in clean_example.documents
        }

    conflict = next(example for example in noisy if example.category == "conflict")
    by_id = {doc.doc_id: doc for doc in conflict.documents}
    assert by_id[1].retrieval_score > by_id[0].retrieval_score
