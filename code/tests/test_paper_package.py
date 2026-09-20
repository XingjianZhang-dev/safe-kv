import importlib.util
import sys
from pathlib import Path

from safekv.paper_package import build_paper_package, latex_escape, render_latex_table


def test_latex_escape_handles_special_characters() -> None:
    escaped = latex_escape("safe_kv 50% & $x$")

    assert "safe\\_kv" in escaped
    assert "50\\%" in escaped
    assert "\\&" in escaped
    assert "\\$x\\$" in escaped


def test_render_latex_table_on_fake_rows() -> None:
    table = render_latex_table(
        rows=[{"method": "prefix_conditioned", "score": 0.1234}],
        columns=[
            ("method", "Method", str),
            ("score", "Score", lambda value: f"{float(value):.2f}"),
        ],
        caption="A fake table",
        label="tab:fake",
    )

    assert "\\begin{table*}" in table
    assert "prefix\\_conditioned" in table
    assert "0.12" in table
    assert "\\label{tab:fake}" in table


def test_build_paper_package_dry_run(tmp_path: Path) -> None:
    _write_fake_results(tmp_path)
    out_dir = tmp_path / "paper"

    summary = build_paper_package(tmp_path, out_dir)

    assert summary["out_dir"] == str(out_dir)
    assert (out_dir / "main.tex").exists()
    assert (out_dir / "tables" / "table1_composition_ablation.tex").exists()
    assert (out_dir / "tables" / "table7_cost_accounting.tex").exists()
    assert (out_dir / "figures" / "figure2_category_drift.csv").exists()
    claim_audit = (out_dir / "CLAIM_AUDIT.md").read_text(encoding="utf-8")
    assert "Strongly Supported" in claim_audit
    assert "Unsupported / Do Not Claim" in claim_audit
    assert "improves measured TTFT" in claim_audit


def test_make_paper_tables_defaults_to_results_paper(monkeypatch) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "make_paper_tables.py"
    spec = importlib.util.spec_from_file_location("make_paper_tables_test", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "argv", ["make_paper_tables.py"])
    args = module.parse_args()

    assert args.out_dir == Path("results_paper")


def _write_fake_results(root: Path) -> None:
    _write_csv(
        root / "results_paper/table1_composition_ablation.csv",
        ["method", "n", "avg_kl", "top1", "top10", "patch_ratio"],
        [
            ["doc_only_naive_global", "2", "0.8", "0.5", "0.6", "0.0"],
            ["prefix_plus_naive_global", "2", "0.7", "0.6", "0.6", "0.0"],
            ["prefix_conditioned_naive_global", "2", "0.2", "0.9", "0.7", "0.0"],
        ],
    )
    _write_csv(
        root / "results_paper/table2_repair_granularity.csv",
        ["method", "n", "avg_kl", "top1", "top10", "patch_ratio"],
        [
            ["oracle_evidence_span_window_16", "2", "0.2", "0.9", "0.7", "0.2"],
            ["oracle_support_and_conflict_suffix_patch", "2", "0.18", "0.9", "0.7", "0.2"],
            ["random_patch_same_budget::oracle_support_and_conflict_suffix_patch", "2", "0.16", "0.9", "0.7", "0.2"],
            ["oracle_evidence_doc_patch", "2", "0.09", "1.0", "0.8", "0.4"],
        ],
    )
    for name in [
        "table3_answer_level_synthetic.csv",
        "table4_answer_level_external.csv",
        "table5_external_full_prefill_correct_subset.csv",
    ]:
        _write_csv(root / f"results_paper/{name}", ["placeholder"], [["ok"]])
    _write_csv(
        root / "results_paper/table6_budget_gate_pareto.csv",
        [
            "run",
            "target_budget",
            "method",
            "actual_budget",
            "answer_equivalence",
            "changed_wrong",
            "avg_first_token_kl",
            "random_mean",
            "random_std",
            "random_95ci_low",
            "random_95ci_high",
            "percentile_vs_random",
        ],
        [["qwen05_noisy", "0.25", "safe_gate_budget_0.25", "0.24", "0.8", "1", "0.2", "0.7", "0.1", "0.6", "0.8", "0.9"]],
    )
    _write_csv(
        root / "results_paper/table7_cost_accounting.csv",
        [
            "model",
            "dataset",
            "method",
            "n_examples",
            "answer_equivalence_to_full_prefill",
            "changed_wrong_rate",
            "patched_doc_count",
            "patched_token_ratio",
            "estimated_recompute_ratio",
            "estimated_prefill_saving",
        ],
        [
            ["qwen05", "diagnostic_noisy", "prefix_conditioned_naive_global", "2", "0.7", "0.2", "0", "0", "0", "1"],
            ["qwen05", "diagnostic_noisy", "oracle_evidence_doc_patch", "2", "0.9", "0.1", "1", "0.4", "0.4", "0.6"],
        ],
    )
    _write_csv(
        root / "results_paper/heldout_gate_calibration_metrics.csv",
        ["model", "dataset", "target_budget", "answer_equivalence_to_full_prefill"],
        [["qwen05", "diagnostic_100_noisy", "0.25", "0.8"]],
    )
    _write_csv(
        root / "results_qwen05_100/patch_recompute_metrics.csv",
        [
            "example_id",
            "category",
            "method",
            "first_token_kl_full_to_method",
            "top1_match",
            "top10_overlap",
            "patched_token_ratio",
        ],
        [
            ["ex0", "single_evidence", "oracle_evidence_span_patch", "0.2", "True", "0.7", "0.1"],
            ["ex0", "single_evidence", "full_doc_cache_patch_sanity", "0.0", "True", "1.0", "1.0"],
        ],
    )
    for rel in [
        "results_qwen05_100_answer/answer_eval_metrics.csv",
        "results_qwen05_100_noisy_answer/answer_eval_metrics.csv",
        "results_qwen15_100_answer/answer_eval_metrics.csv",
        "results_qwen15_100_noisy_answer/answer_eval_metrics.csv",
        "results_qwen05_external_answer/answer_eval_metrics.csv",
        "results_qwen15_external_answer/answer_eval_metrics.csv",
        "results_smollm17_noisy_answer/answer_eval_metrics.csv",
        "results_smollm17_external_answer/answer_eval_metrics.csv",
    ]:
        _write_answer_metrics(root / rel)


def _write_answer_metrics(path: Path) -> None:
    methods = [
        "full_prefill",
        "prefix_conditioned_naive_global",
        "oracle_evidence_doc_patch",
        "query_similarity_doc_patch_k2",
        "entity_overlap_doc_patch_k2",
        "safe_gate_t0.45",
        "safe_gate_t0.60",
        "random_doc_patch_k2_seeded",
    ]
    rows = []
    for method in methods:
        equiv = method in {"full_prefill", "oracle_evidence_doc_patch", "query_similarity_doc_patch_k2", "entity_overlap_doc_patch_k2"}
        rows.append(
            [
                "ex0",
                "single_evidence",
                method,
                "answer",
                "answer",
                "answer",
                "answer",
                "answer",
                "answer",
                str(equiv),
                "True",
                "1.0",
                "True",
                str(not equiv),
                str(not equiv),
                "1" if method != "full_prefill" else "0",
                "10" if method != "full_prefill" else "0",
                "0.4" if method != "full_prefill" else "0.0",
                "0.2" if method != "full_prefill" else "0.0",
                str(equiv),
                "100",
                "20",
            ]
        )
    _write_csv(
        path,
        [
            "example_id",
            "category",
            "method",
            "generated_answer",
            "full_prefill_answer",
            "gold_answer",
            "normalized_generated_answer",
            "normalized_full_prefill_answer",
            "normalized_gold_answer",
            "answer_equivalence_to_full_prefill",
            "gold_exact_match",
            "gold_token_f1",
            "answer_contains_gold",
            "answer_changed_from_full",
            "answer_changed_and_gold_wrong",
            "patched_doc_count",
            "patched_token_count",
            "patched_token_ratio",
            "first_token_kl_full_to_method",
            "top1_match",
            "prompt_length",
            "query_length",
        ],
        rows,
    )


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")
