import json

from safekv.build_diagnostic import read_jsonl, write_jsonl
from safekv.build_external import (
    build_2wiki_examples,
    build_hotpotqa_examples,
    hotpotqa_record_to_example,
    twowiki_record_to_example,
)


def test_hotpotqa_like_record_maps_supporting_facts_to_evidence_docs() -> None:
    example = hotpotqa_record_to_example(_hotpot_record(), example_index=0)

    assert example is not None
    assert example.category == "external_hotpotqa"
    assert example.requires_cross_doc
    assert example.gold_answer == "Paris"
    roles = {doc.title: doc.role for doc in example.documents}
    assert roles["Person A"] == "evidence"
    assert roles["Country B"] == "evidence"
    assert roles["Distractor One"] == "distractor"
    assert {evidence.doc_id for evidence in example.evidence} == {0, 1}
    example.validate()


def test_hotpotqa_builder_limits_distractors() -> None:
    result = build_hotpotqa_examples([_hotpot_record()], n=1, seed=13, max_distractors=2)

    assert len(result.examples) == 1
    example = result.examples[0]
    assert len([doc for doc in example.documents if doc.role == "distractor"]) == 2
    assert len(example.documents) == 4


def test_yes_no_answers_are_skipped() -> None:
    record = dict(_hotpot_record())
    record["answer"] = "yes"

    assert hotpotqa_record_to_example(record, example_index=0) is None
    result = build_hotpotqa_examples([record], n=1, seed=13)
    assert result.examples == []
    assert result.summary["skip_reasons"]["yes_no_answer"] == 1


def test_external_schema_round_trip(tmp_path) -> None:
    example = hotpotqa_record_to_example(_hotpot_record(), example_index=0)
    out_path = tmp_path / "external.jsonl"

    write_jsonl([example], out_path)
    loaded = read_jsonl(out_path)

    assert loaded[0].to_dict() == example.to_dict()


def test_2wiki_like_record_parsing() -> None:
    example = twowiki_record_to_example(_twowiki_record(), example_index=0)

    assert example is not None
    assert example.category == "external_2wiki"
    assert example.requires_cross_doc
    assert len({evidence.doc_id for evidence in example.evidence}) == 2
    assert [doc.role for doc in example.documents].count("evidence") == 2
    example.validate()


def test_local_json_shape_for_fake_records(tmp_path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"data": [_hotpot_record()]}), encoding="utf-8")

    from safekv.build_external import load_local_records

    assert load_local_records(path)[0]["answer"] == "Paris"


def _hotpot_record():
    return {
        "id": "fake-hotpot",
        "question": "What city is the capital of the country where Person A was born?",
        "answer": "Paris",
        "supporting_facts": [["Person A", 0], ["Country B", 0]],
        "context": [
            ["Person A", ["Person A was born in Country B.", "Person A wrote a book."]],
            ["Country B", ["The capital of Country B is Paris.", "It has many rivers."]],
            ["Distractor One", ["Person A once visited Berlin.", "The trip was short."]],
            ["Distractor Two", ["Country C has capital Rome.", "Its flag is blue."]],
            ["Distractor Three", ["A museum in Paris opened late.", "The record is unrelated."]],
        ],
    }


def _twowiki_record():
    return {
        "_id": "fake-2wiki",
        "question": "Where was the creator of Project X born?",
        "answer": "Nantes",
        "supporting_facts": [["Project X", 0], ["Designer Y", 0]],
        "context": [
            ["Project X", ["Project X was created by Designer Y.", "It launched in 2001."]],
            ["Designer Y", ["Designer Y was born in Nantes.", "She later moved."]],
            ["Distractor", ["Project Z was created by Someone Else.", "It is unrelated."]],
        ],
    }
