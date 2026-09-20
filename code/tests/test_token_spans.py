from safekv.build_diagnostic import CATEGORIES, build_diagnostic_examples
from safekv.prompting import build_plain_rag_prompt
from safekv.token_spans import RegexTokenizer, encode_no_special, split_doc_spans


def test_split_doc_spans_preserves_document_slices() -> None:
    text = "First sentence. Second sentence? Final fragment"

    ranges = split_doc_spans(text)

    assert [text[start:end] for start, end in ranges] == [
        "First sentence.",
        "Second sentence?",
        "Final fragment",
    ]


def test_span_ranges_are_valid_for_all_categories() -> None:
    tokenizer = RegexTokenizer()
    examples = build_diagnostic_examples(n_per_category=1, seed=13)

    assert {example.category for example in examples} == set(CATEGORIES)

    for example in examples:
        pack = build_plain_rag_prompt(example, tokenizer)

        assert pack.evidence_span_ids
        span_ids = {span.span_id for span in pack.span_ranges}
        assert set(pack.evidence_span_ids).issubset(span_ids)

        for span in pack.span_ranges:
            assert 0 <= span.token_range.start <= span.token_range.end <= len(pack.context_input_ids)
            assert span.char_range_in_doc is not None

            doc = next(doc for doc in example.documents if doc.doc_id == span.doc_id)
            char_start, char_end = span.char_range_in_doc
            assert doc.text[char_start:char_end] == span.text
            assert pack.context_input_ids[span.token_range.start : span.token_range.end] == (
                encode_no_special(tokenizer, span.text)
            )


def test_evidence_texts_map_to_gold_spans() -> None:
    tokenizer = RegexTokenizer()
    examples = build_diagnostic_examples(n_per_category=2, seed=7)

    for example in examples:
        pack = build_plain_rag_prompt(example, tokenizer)
        evidence_spans = {
            span.span_id: span
            for span in pack.span_ranges
            if span.contains_gold_evidence
        }

        assert evidence_spans
        for evidence in example.evidence:
            matching = [
                span
                for span in evidence_spans.values()
                if span.doc_id == evidence.doc_id and evidence.text in span.text
            ]
            assert matching, f"{example.id}: evidence did not map to a span: {evidence.text}"
