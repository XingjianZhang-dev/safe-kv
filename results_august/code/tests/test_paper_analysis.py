from pathlib import Path

import pytest

from safekv.paper_analysis import (
    external_subset_rows,
    markdown_table,
    write_claim_audit,
)


def test_external_subset_filtering_and_repair_rates() -> None:
    rows = [
        _row("ex0", "external_hotpotqa", "full_prefill", equiv=True, em=True, f1=1.0),
        _row(
            "ex0",
            "external_hotpotqa",
            "prefix_conditioned_naive_global",
            equiv=False,
            em=False,
            f1=0.0,
        ),
        _row("ex0", "external_hotpotqa", "oracle_evidence_doc_patch", equiv=True, em=True, f1=1.0),
        _row("ex1", "external_2wiki", "full_prefill", equiv=True, em=False, f1=0.75),
        _row("ex1", "external_2wiki", "prefix_conditioned_naive_global", equiv=False, em=False, f1=0.0),
        _row("ex1", "external_2wiki", "oracle_evidence_doc_patch", equiv=False, em=False, f1=0.0),
        _row("ex2", "external_2wiki", "full_prefill", equiv=True, em=False, f1=0.25),
        _row("ex2", "external_2wiki", "prefix_conditioned_naive_global", equiv=True, em=False, f1=0.25),
        _row("ex2", "external_2wiki", "oracle_evidence_doc_patch", equiv=True, em=False, f1=0.25),
    ]

    subset_rows, summary = external_subset_rows(
        model_label="qwen-test",
        metrics_rows=rows,
        small_n_threshold=4,
    )

    exact_oracle = _find(
        subset_rows,
        dataset_split="all_external",
        quality_subset="full_prefill_gold_exact_match",
        method="oracle_evidence_doc_patch",
    )
    assert exact_oracle["n_examples"] == 1
    assert exact_oracle["small_n_warning"] is True
    assert exact_oracle["base_changed_count"] == 1
    assert exact_oracle["repaired_base_changes_by_method"] == 1
    assert exact_oracle["repair_rate_among_base_changes"] == pytest.approx(1.0)

    high_f1_base = _find(
        subset_rows,
        dataset_split="all_external",
        quality_subset="full_prefill_gold_f1_ge_0.5",
        method="prefix_conditioned_naive_global",
    )
    assert high_f1_base["n_examples"] == 2
    assert high_f1_base["answer_equivalence_to_full_prefill"] == pytest.approx(0.0)
    assert summary["subsets"][0]["n_examples"] == 3


def test_markdown_table_and_claim_audit_generation(tmp_path: Path) -> None:
    table = markdown_table([{"method": "base", "score": "0.5"}], ["method", "score"])
    assert "| method | score |" in table
    assert "| base | 0.5 |" in table

    out_path = tmp_path / "claim_audit.md"
    write_claim_audit(out_path)

    text = out_path.read_text(encoding="utf-8")
    assert "Strongly Supported" in text
    assert "Universal semantic selector dominance" in text


def _find(rows, *, dataset_split: str, quality_subset: str, method: str):
    for row in rows:
        if (
            row["dataset_split"] == dataset_split
            and row["quality_subset"] == quality_subset
            and row["method"] == method
        ):
            return row
    raise AssertionError(f"missing row for {dataset_split}/{quality_subset}/{method}")


def _row(
    example_id: str,
    category: str,
    method: str,
    *,
    equiv: bool,
    em: bool,
    f1: float,
):
    return {
        "example_id": example_id,
        "category": category,
        "method": method,
        "answer_equivalence_to_full_prefill": str(equiv),
        "gold_exact_match": str(em),
        "gold_token_f1": str(f1),
        "answer_contains_gold": str(f1 > 0),
        "answer_changed_from_full": str(not equiv),
        "answer_changed_and_gold_wrong": str((not equiv) and (not em)),
        "patched_token_ratio": "0.25" if method != "full_prefill" else "0.0",
        "first_token_kl_full_to_method": "0.2" if method != "full_prefill" else "0.0",
        "top1_match": str(equiv),
    }
