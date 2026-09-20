from safekv.data_schema import DiagnosticExample, Document
from safekv.doc_selector import DocumentScore
from scripts.run_staleness_doccount_sweep import (
    repair_operator_for_action,
    stable_uniform,
    top_k_candidate_positions,
)
from scripts.run_answer_eval import (
    recompute_answer_ranges_locally,
    recompute_answer_suffix,
)


def _example() -> DiagnosticExample:
    return DiagnosticExample(
        id="paired-example",
        category="single_evidence",
        documents=[
            Document(0, "first", "alpha", "distractor", 0.0),
            Document(1, "second", "beta", "evidence", 0.0),
            Document(2, "third", "gamma", "distractor", 0.0),
        ],
        question="beta?",
        gold_answer="beta",
        evidence=[],
        conflicting_docs=[],
        requires_cross_doc=False,
    )


def test_staleness_uniform_depends_on_content_not_position() -> None:
    document = Document(7, "same", "content", "distractor", 0.0)
    remapped = Document(2, "same", "content", "distractor", 0.0)
    assert stable_uniform(13, "example", document) == stable_uniform(
        13, "example", remapped
    )


def test_staleness_uses_local_forward_before_frontier_and_suffix_at_frontier() -> None:
    assert (
        repair_operator_for_action(start=2, end=3, num_documents=8)
        is recompute_answer_ranges_locally
    )
    assert (
        repair_operator_for_action(start=2, end=6, num_documents=8)
        is recompute_answer_ranges_locally
    )
    assert (
        repair_operator_for_action(start=2, end=8, num_documents=8)
        is recompute_answer_suffix
    )
    assert (
        repair_operator_for_action(start=8, end=8, num_documents=8)
        is recompute_answer_ranges_locally
    )


def test_operational_selector_ranks_all_structurally_eligible_docs() -> None:
    example = _example()
    scores = [
        DocumentScore(0, 10.0, {}),
        DocumentScore(1, 1.0, {}),
        DocumentScore(2, 2.0, {}),
    ]
    assert top_k_candidate_positions(
        scores,
        candidate_ids={1, 2},
        example=example,
        k=1,
    ) == [2]
