import pytest

from safekv.build_diagnostic import build_diagnostic_examples
from safekv.doc_selector import (
    conflict_aware_doc_ids,
    conflict_candidate_docs,
    default_doc_selector_methods,
    entity_overlap_doc_scores,
    extract_entities,
    gate_decision,
    gate_pareto_rows,
    lexical_overlap,
    oracle_doc_ids,
    patch_ranges_for_doc_selector_method,
    query_similarity_doc_scores,
    random_doc_ids_same_count,
    risk_guided_doc_scores,
    safe_composition_risk,
    safe_gate_method_name,
    selected_doc_ids_for_method,
    resolve_risk_weights,
    summarize_doc_selector_rows,
)
from safekv.patch_recompute import lexical_terms, token_count
from safekv.prompting import build_rag_prompt
from safekv.token_spans import RegexTokenizer


def _examples():
    return build_diagnostic_examples(n_per_category=1, seed=13)


def _example(category: str):
    return next(example for example in _examples() if example.category == category)


def test_lexical_overlap_and_query_similarity_scores() -> None:
    example = _example("single_evidence")
    scores = query_similarity_doc_scores(example)

    assert lexical_overlap(lexical_terms("Who calibrated Zorvian device"), lexical_terms(example.documents[0].text)) > 0
    assert scores[0].doc_id == 0
    assert scores[0].score > scores[1].score


def test_entity_extraction_and_entity_overlap_scores() -> None:
    entities = extract_entities("According to the Official Schedule, it opens at 8 AM in 2020.")
    example = _example("conflict")
    scores = entity_overlap_doc_scores(example)

    assert "8 am" in entities
    assert "2020" in entities
    assert scores[0].score >= scores[1].score


def test_conflict_candidate_detection_and_conflict_aware_selection() -> None:
    example = _example("conflict")

    candidates = conflict_candidate_docs(example)
    selected = conflict_aware_doc_ids(example)

    assert set(candidates) == {0, 1}
    assert selected == [0, 1]


def test_deterministic_random_doc_selection() -> None:
    example = _example("distractor_heavy")

    first = random_doc_ids_same_count(example, count=2, seed=99)
    second = random_doc_ids_same_count(example, count=2, seed=99)

    assert first == second
    assert len(first) == 2


def test_risk_guided_scores_rank_relevant_document_high() -> None:
    example = _example("distractor_heavy")
    selected, reason = selected_doc_ids_for_method(
        "risk_guided_doc_patch_k1",
        example,
        seed=13,
    )

    assert selected == [1]
    assert "doc_scores" in reason


def test_risk_weights_are_executable_and_validated() -> None:
    example = _example("distractor_heavy")
    retrieval_only = {
        "retrieval_score": 1.0,
        "query_similarity": 0.0,
        "entity_overlap": 0.0,
        "conflict_indicator": 0.0,
        "cross_doc_shared_entity": 0.0,
    }
    scores = risk_guided_doc_scores(example, retrieval_only)

    assert resolve_risk_weights(retrieval_only) == retrieval_only
    for score in scores:
        assert score.score == pytest.approx(score.reason["retrieval_score"])
    with pytest.raises(ValueError, match="missing"):
        resolve_risk_weights({"retrieval_score": 1.0})
    with pytest.raises(ValueError, match="sum to 1"):
        resolve_risk_weights(
            {
                "retrieval_score": 0.20,
                "query_similarity": 0.20,
                "entity_overlap": 0.20,
                "conflict_indicator": 0.20,
                "cross_doc_shared_entity": 0.10,
            }
        )


def test_safe_composition_risk_and_gate_thresholding() -> None:
    single = _example("single_evidence")
    conflict = _example("conflict")

    single_risk, _ = safe_composition_risk(single)
    conflict_decision = gate_decision(conflict, threshold=0.60)
    single_decision = gate_decision(single, threshold=0.60)

    assert single_risk < conflict_decision.risk_score
    assert conflict_decision.should_patch is True
    assert single_decision.should_patch is False


def test_patch_ranges_for_doc_selector_methods() -> None:
    example = _example("multi_hop")
    pack = build_rag_prompt(example, RegexTokenizer(), prompt_format="plain_rag")

    oracle_ranges, oracle_docs, _ = patch_ranges_for_doc_selector_method(
        "oracle_evidence_doc_patch",
        example,
        pack,
        seed=13,
    )
    random_ranges, random_docs, _ = patch_ranges_for_doc_selector_method(
        "random_doc_patch_same_count",
        example,
        pack,
        seed=13,
    )
    token_ranges, token_docs, reason = patch_ranges_for_doc_selector_method(
        "random_token_patch_same_budget_as_oracle_doc",
        example,
        pack,
        seed=13,
    )

    assert oracle_docs == oracle_doc_ids(example)
    assert len(random_docs) == len(oracle_docs)
    assert token_docs == []
    assert token_count(token_ranges) == reason["target_token_count"]
    assert token_count(oracle_ranges) == reason["target_token_count"]
    assert random_ranges


def test_default_methods_include_gate_methods() -> None:
    methods = default_doc_selector_methods([0.25, 0.50])

    assert "risk_guided_doc_patch_k2" in methods
    assert safe_gate_method_name(0.25) in methods
    assert safe_gate_method_name(0.50) in methods


def test_doc_selector_summary_includes_gaps_and_pareto() -> None:
    base_rows = [_fake_row("base", kl=0.4, top1=False, ratio=0.0)]
    rows = [
        _fake_row("oracle_evidence_doc_patch", kl=0.1, top1=True, ratio=0.5),
        _fake_row("random_doc_patch_same_count", kl=0.3, top1=False, ratio=0.5),
        _fake_row("risk_guided_doc_patch_k1", kl=0.2, top1=True, ratio=0.25),
        _fake_row("safe_composition_gate_t0_50", kl=0.25, top1=True, ratio=0.1),
    ]

    summary = summarize_doc_selector_rows(rows, base_rows, [])
    pareto = gate_pareto_rows(summary["method_level"])

    assert summary["method_level"]["risk_guided_doc_patch_k1"]["improvement_over_base"]["kl_reduction"] == pytest.approx(0.2)
    assert summary["method_level"]["risk_guided_doc_patch_k1"]["gap_to_oracle_evidence_doc_patch"]["kl_gap"] == pytest.approx(0.1)
    assert pareto[0]["threshold"] == 0.5


def _fake_row(method: str, kl: float, top1: bool, ratio: float):
    return {
        "example_id": "ex0",
        "category": "conflict",
        "method": method,
        "first_token_kl_full_to_method": kl,
        "first_token_js_divergence": kl / 2,
        "top1_match": top1,
        "top5_overlap": 0.8,
        "top10_overlap": 0.7,
        "composed_context_length": 20,
        "max_abs_logit_diff": 1.0,
        "patched_doc_count": 1 if ratio else 0,
        "patched_token_count": int(20 * ratio),
        "patched_token_ratio": ratio,
    }
