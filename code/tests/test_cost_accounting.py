import pytest

from safekv.cost_accounting import cost_accounting_rows, cost_markdown_table


def test_cost_accounting_extracts_patch_ratios_and_savings() -> None:
    rows = cost_accounting_rows(
        model="m",
        dataset="d",
        metric_rows=[
            _row("ex0", "base", equiv=True, wrong=False, docs=0, ratio=0.0),
            _row("ex1", "base", equiv=False, wrong=True, docs=0, ratio=0.0),
            _row("ex0", "repair", equiv=True, wrong=False, docs=2, ratio=0.4),
            _row("ex1", "repair", equiv=True, wrong=False, docs=2, ratio=0.2),
        ],
    )

    repair = next(row for row in rows if row["method"] == "repair")
    base = next(row for row in rows if row["method"] == "base")

    assert base["answer_equivalence_to_full_prefill"] == pytest.approx(0.5)
    assert base["changed_wrong_rate"] == pytest.approx(0.5)
    assert repair["patched_token_ratio"] == pytest.approx(0.3)
    assert repair["estimated_recompute_ratio"] == pytest.approx(0.3)
    assert repair["estimated_prefill_saving"] == pytest.approx(0.7)


def test_cost_accounting_filters_missing_methods_and_formats_markdown() -> None:
    rows = cost_accounting_rows(
        model="m",
        dataset="d",
        metric_rows=[
            _row("ex0", "base", equiv=True, wrong=False, docs=0, ratio=0.0),
            _row("ex0", "unused", equiv=True, wrong=False, docs=1, ratio=0.5),
        ],
        methods={"base", "missing"},
    )

    assert [row["method"] for row in rows] == ["base"]
    markdown = cost_markdown_table(rows)
    assert "| model | dataset | method |" in markdown
    assert "| m | d | base |" in markdown


def _row(example_id: str, method: str, *, equiv: bool, wrong: bool, docs: int, ratio: float):
    return {
        "example_id": example_id,
        "method": method,
        "answer_equivalence_to_full_prefill": str(equiv),
        "answer_changed_and_gold_wrong": str(wrong),
        "patched_doc_count": str(docs),
        "patched_token_ratio": str(ratio),
    }
