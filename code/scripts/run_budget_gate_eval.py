#!/usr/bin/env python
"""Run budget-targeted gate evaluation for SAFE-KV Milestone 7A."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import (  # noqa: E402
    answer_failure_analysis_markdown,
    append_answer_rows,
    make_answer_eval_row,
    read_answer_rows,
    summarize_answer_eval_rows,
    write_answer_metrics_csv,
)
from safekv.budget_gate import (  # noqa: E402
    BudgetExampleInfo,
    budget_method_name,
    random_budget_order,
    safe_budget_order,
    select_examples_for_budget,
    summarize_random_against_safe,
)
from safekv.cache_ops import cache_seq_len  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.doc_selector import document_ranges_for_ids, selected_doc_ids_for_method  # noqa: E402
from safekv.full_prefill import load_examples_for_config, select_examples_per_category, set_deterministic_seed  # noqa: E402
from safekv.metrics import logit_preservation_metrics  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import replace_cache_slices, token_count, validate_patch_ranges_within_documents  # noqa: E402
from safekv.doc_selector import safe_composition_risk  # noqa: E402

from run_answer_eval import (  # noqa: E402
    full_prefill_answer_row,
    run_base_answer_state,
    run_full_prefill_answer_state,
    run_query_and_generate_from_context_cache,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--max-examples-per-category", type=int, default=None)
    parser.add_argument("--target-budgets", type=str, default="0.10,0.25,0.40")
    parser.add_argument("--num-random-seeds", type=int, default=100)
    parser.add_argument("--random-seed", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_budgets = [float(item.strip()) for item in args.target_budgets.split(",") if item.strip()]
    config = load_config(args.config)
    if config.generation.do_sample or config.generation.temperature != 0.0:
        raise ValueError("budget gate evaluation requires deterministic generation")

    config_dir = args.config.resolve().parent.parent
    set_deterministic_seed(config.seed)
    examples = load_examples_for_config(config, config_dir=config_dir)
    if args.max_examples_per_category is not None:
        examples = select_examples_per_category(examples, args.max_examples_per_category)
    if args.max_examples is not None:
        examples = examples[: args.max_examples]

    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    base_rows: dict[str, dict[str, Any]] = {}
    patch_rows: dict[str, dict[str, Any]] = {}
    full_rows: dict[str, dict[str, Any]] = {}
    infos: list[BudgetExampleInfo] = []
    failed_rows: list[dict[str, Any]] = []

    for example in examples:
        try:
            pack = build_prompt_pack_for_config(example, loaded, config)
            full_state = run_full_prefill_answer_state(
                example=example,
                pack=pack,
                loaded=loaded,
                config=config,
            )
            base_state = run_base_answer_state(
                example=example,
                pack=pack,
                loaded=loaded,
                config=config,
                full_logits=full_state["first_logits"],
            )
            full_rows[example.id] = full_prefill_answer_row(example, pack, full_state)
            base_rows[example.id] = _base_row(example, pack, base_state, full_state)
            patch_row, patch_cost, selected_doc_ids = _risk_guided_patch_row(
                example=example,
                pack=pack,
                loaded=loaded,
                config=config,
                full_state=full_state,
                full_cache=full_state["full_cache"],
                base_state=base_state,
            )
            patch_rows[example.id] = patch_row
            risk_score, risk_reason = safe_composition_risk(example)
            denominator = int(base_state["cache_metadata"]["composed_context_length"])
            infos.append(
                BudgetExampleInfo(
                    example_id=example.id,
                    risk_score=risk_score,
                    patch_cost=patch_cost,
                    denominator=denominator,
                )
            )
            patch_row["gate_risk_score"] = risk_score
            patch_row["gate_risk_reason"] = risk_reason
            patch_row["selected_doc_ids"] = selected_doc_ids
        except Exception as exc:  # pragma: no cover - real model diagnostics only
            failed_rows.append(
                {
                    "example_id": example.id,
                    "category": example.category,
                    "error": repr(exc),
                }
            )

    rows = []
    for example_id in full_rows:
        rows.append(full_rows[example_id])
        rows.append(base_rows[example_id])
        rows.append(patch_rows[example_id])

    pareto_rows = []
    random_seed_summaries: dict[str, list[dict[str, Any]]] = {}
    for target_budget in target_budgets:
        safe_name = budget_method_name("safe_gate_budget", target_budget)
        safe_selected, safe_actual = select_examples_for_budget(
            infos,
            target_budget=target_budget,
            order=safe_budget_order(infos),
        )
        safe_rows = _materialize_gate_rows(
            method=safe_name,
            selected=safe_selected,
            actual_budget=safe_actual,
            target_budget=target_budget,
            base_rows=base_rows,
            patch_rows=patch_rows,
        )
        rows.extend(safe_rows)
        safe_summary = summarize_answer_eval_rows(safe_rows)["method_level"][safe_name]

        seed_summaries = []
        for seed in range(args.random_seed, args.random_seed + args.num_random_seeds):
            random_name = f"{budget_method_name('random_gate_budget', target_budget)}_seed{seed:03d}"
            selected, actual = select_examples_for_budget(
                infos,
                target_budget=target_budget,
                order=random_budget_order(infos, seed=seed),
            )
            random_rows = _materialize_gate_rows(
                method=random_name,
                selected=selected,
                actual_budget=actual,
                target_budget=target_budget,
                base_rows=base_rows,
                patch_rows=patch_rows,
                random_seed=seed,
            )
            rows.extend(random_rows)
            random_summary = summarize_answer_eval_rows(random_rows)["method_level"][random_name]
            random_summary["actual_budget"] = actual
            random_summary["seed"] = seed
            seed_summaries.append(random_summary)
        random_seed_summaries[budget_method_name("random_gate_budget", target_budget)] = seed_summaries

        random_equiv = [
            item["answer_equivalence_to_full_prefill"] for item in seed_summaries
        ]
        random_wrong = [item["answer_changed_and_gold_wrong_count"] for item in seed_summaries]
        random_kl = [item["avg_first_token_kl"] for item in seed_summaries]
        random_stats = summarize_random_against_safe(
            safe_value=safe_summary["answer_equivalence_to_full_prefill"],
            random_values=random_equiv,
        )
        pareto_rows.append(
            {
                "target_budget": target_budget,
                "method": safe_name,
                "actual_budget": safe_actual,
                "answer_equivalence": safe_summary["answer_equivalence_to_full_prefill"],
                "changed_wrong": safe_summary["answer_changed_and_gold_wrong_count"],
                "avg_first_token_kl": safe_summary["avg_first_token_kl"],
                **random_stats,
                "random_changed_wrong_mean": sum(random_wrong) / len(random_wrong),
                "random_kl_mean": sum(random_kl) / len(random_kl),
            }
        )

    outputs_path = args.results_dir / "budget_gate_outputs.jsonl"
    metrics_path = args.results_dir / "budget_gate_metrics.csv"
    summary_path = args.results_dir / "budget_gate_summary.json"
    pareto_path = args.results_dir / "budget_gate_pareto.csv"
    failure_path = args.results_dir / "budget_gate_failure_analysis.md"

    if outputs_path.exists():
        outputs_path.unlink()
    append_answer_rows(outputs_path, rows)
    write_answer_metrics_csv(metrics_path, rows)
    summary = summarize_answer_eval_rows(rows)
    summary["failed_rows"] = failed_rows
    summary["num_failed_rows"] = len(failed_rows)
    summary["config_path"] = str(args.config)
    summary["dataset_path"] = config.data.path
    summary["model_name"] = config.model.name
    summary["target_budgets"] = target_budgets
    summary["num_random_seeds"] = args.num_random_seeds
    summary["budget_gate_pareto"] = pareto_rows
    summary["random_seed_summaries"] = random_seed_summaries
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_pareto_csv(pareto_path, pareto_rows)
    failure_path.write_text(_failure_markdown(rows, summary, pareto_rows), encoding="utf-8")
    print(json.dumps(_compact_summary(summary), indent=2, ensure_ascii=False))


def _base_row(example, pack, base_state, full_state):
    return make_answer_eval_row(
        example_id=example.id,
        category=example.category,
        method="prefix_conditioned_naive_global",
        generated_answer=base_state["generated_answer"],
        full_prefill_answer=full_state["generated_answer"],
        gold_answer=example.gold_answer,
        patched_doc_count=0,
        patched_token_count=0,
        patched_token_ratio=0.0,
        prompt_length=len(pack.full_input_ids),
        query_length=pack.query_token_range.length,
        first_token_kl_full_to_method=base_state["logit_metrics"][
            "first_token_kl_full_to_method"
        ],
        top1_match=base_state["logit_metrics"]["top1_match"],
    )


def _risk_guided_patch_row(*, example, pack, loaded, config, full_state, full_cache, base_state):
    selected_doc_ids, _reason = selected_doc_ids_for_method(
        "risk_guided_doc_patch_k2",
        example,
        seed=0,
    )
    patch_ranges = document_ranges_for_ids(example, pack, selected_doc_ids)
    validate_patch_ranges_within_documents(patch_ranges, pack)
    context_cache = (
        base_state["context_cache"]
        if not patch_ranges
        else replace_cache_slices(base_state["context_cache"], full_cache, patch_ranges)
    )
    query_state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=context_cache,
    )
    logit_metrics = logit_preservation_metrics(
        full_state["first_logits"],
        query_state["first_logits"],
        loaded.tokenizer,
    )
    patched_count = token_count(patch_ranges)
    composed_len = cache_seq_len(base_state["context_cache"])
    row = make_answer_eval_row(
        example_id=example.id,
        category=example.category,
        method="risk_guided_doc_patch_k2",
        generated_answer=query_state["generated_answer"],
        full_prefill_answer=full_state["generated_answer"],
        gold_answer=example.gold_answer,
        patched_doc_count=len(selected_doc_ids),
        patched_token_count=patched_count,
        patched_token_ratio=patched_count / composed_len if composed_len else 0.0,
        prompt_length=len(pack.full_input_ids),
        query_length=pack.query_token_range.length,
        first_token_kl_full_to_method=logit_metrics["first_token_kl_full_to_method"],
        top1_match=logit_metrics["top1_match"],
    )
    return row, patched_count, selected_doc_ids


def _materialize_gate_rows(
    *,
    method: str,
    selected: set[str],
    actual_budget: float,
    target_budget: float,
    base_rows: dict[str, dict[str, Any]],
    patch_rows: dict[str, dict[str, Any]],
    random_seed: int | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for example_id in sorted(base_rows):
        source = patch_rows[example_id] if example_id in selected else base_rows[example_id]
        row = dict(source)
        row["method"] = method
        row["budget_selected"] = example_id in selected
        row["target_budget"] = target_budget
        row["actual_budget"] = actual_budget
        if random_seed is not None:
            row["random_seed"] = random_seed
        rows.append(row)
    return rows


def _write_pareto_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
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
        "random_changed_wrong_mean",
        "random_kl_mean",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _failure_markdown(rows, summary, pareto_rows):
    lines = [
        "# Budget Gate Failure Analysis",
        "",
        "## Pareto Summary",
        "",
        "| target | actual | safe equiv | random mean | percentile | changed+wrong |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pareto_rows:
        lines.append(
            "| {target:.2f} | {actual:.3f} | {equiv:.3f} | {rand:.3f} | {pct:.3f} | {wrong} |".format(
                target=float(row["target_budget"]),
                actual=float(row["actual_budget"]),
                equiv=float(row["answer_equivalence"]),
                rand=float(row["random_mean"]),
                pct=float(row["percentile_vs_random"]),
                wrong=int(row["changed_wrong"]),
            )
        )
    lines.extend(["", answer_failure_analysis_markdown(rows, summary)])
    return "\n".join(lines)


def _compact_summary(summary):
    return {
        "num_rows": summary["num_rows"],
        "num_failed_rows": summary["num_failed_rows"],
        "category_counts": summary["category_counts"],
        "budget_gate_pareto": summary["budget_gate_pareto"],
    }


if __name__ == "__main__":
    main()

