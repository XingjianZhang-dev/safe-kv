#!/usr/bin/env python
"""Run SAFE-KV Milestone 5B document-selector validity stress tests."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_patch_recompute import (  # noqa: E402
    PATCH_CSV_COLUMNS,
    full_prefill_logits_and_cache,
    make_patch_metric_row,
    write_jsonl,
)
from safekv.cache_ops import cache_seq_len  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.data_schema import DiagnosticExample, PromptPack  # noqa: E402
from safekv.doc_selector import (  # noqa: E402
    DEFAULT_GATE_THRESHOLDS,
    document_ranges_for_ids,
    oracle_doc_ids,
    random_doc_ids_same_count,
    safe_gate_method_name,
    selected_doc_ids_for_method,
)
from safekv.doc_selector_stress import (  # noqa: E402
    SEMANTIC_DOC_SELECTOR_METHODS,
    best_subset_by_metric,
    canonical_doc_subset,
    clone_metric_row_for_method,
    exhaustive_doc_subsets,
    flatten_random_distribution_for_csv,
    random_gate_ids_same_num_patched_examples,
    random_gate_ids_same_patch_rate,
    random_seed_values,
    repair_oracle_method_names,
    summarize_doc_selector_stress_rows,
)
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import (  # noqa: E402
    build_naive_composed_context_cache,
    build_prompt_pack_for_config,
    evaluate_query_with_context_cache,
    make_metric_row,
    run_sequential_prefill_logits,
    sequential_summary,
)
from safekv.patch_recompute import (  # noqa: E402
    replace_cache_slices,
    stable_example_seed,
    validate_patch_ranges_within_documents,
)


STRESS_CSV_COLUMNS = PATCH_CSV_COLUMNS + [
    "patched_doc_count",
    "selected_doc_ids",
    "random_seed",
    "base_first_token_kl_full_to_method",
    "kl_reduction_from_base",
    "kl_reduction_per_patched_token_ratio",
    "kl_reduction_per_doc",
    "selector_reason",
]

RANDOM_DISTRIBUTION_COLUMNS = [
    "method",
    "random_seed",
    "avg_kl",
    "avg_js",
    "top1_match_rate",
    "avg_top5_overlap",
    "avg_top10_overlap",
    "avg_patched_token_ratio",
    "avg_patched_doc_count",
    "kl_reduction_per_patched_token_ratio",
    "kl_reduction_per_doc",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--base-method", default="prefix_conditioned_naive_global")
    parser.add_argument("--num-random-seeds", type=int, default=100)
    parser.add_argument("--repair-oracle-max-k", type=int, default=2)
    parser.add_argument("--gate-thresholds", nargs="*", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.base_method != "prefix_conditioned_naive_global":
        raise ValueError("Milestone 5B supports base_method=prefix_conditioned_naive_global")
    if args.repair_oracle_max_k < 2:
        raise ValueError("--repair-oracle-max-k must be at least 2")

    config = load_config(args.config)
    set_deterministic_seed(config.seed)
    config_dir = args.config.resolve().parent.parent
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    random_seeds = random_seed_values(args.num_random_seeds)
    gate_thresholds = args.gate_thresholds or DEFAULT_GATE_THRESHOLDS

    rows: list[dict[str, Any]] = []
    base_rows: list[dict[str, Any]] = []
    sequential_rows: list[dict[str, Any]] = []
    failed_examples: list[dict[str, str]] = []
    gate_candidate_rows_by_id: dict[str, dict[str, Any]] = {}
    base_rows_by_id: dict[str, dict[str, Any]] = {}
    example_ids: list[str] = []
    gate_rows_by_threshold: dict[float, list[dict[str, Any]]] = {
        threshold: [] for threshold in gate_thresholds
    }

    for example in examples:
        example_ids.append(example.id)
        try:
            example_rows = run_example_stress(
                example=example,
                loaded=loaded,
                config=config,
                random_seeds=random_seeds,
                gate_thresholds=gate_thresholds,
                repair_oracle_max_k=args.repair_oracle_max_k,
            )
        except Exception as exc:  # pragma: no cover - real model diagnostics only
            failed_examples.append({"example_id": example.id, "method": "all", "error": repr(exc)})
            continue

        sequential_rows.append(example_rows["sequential_row"])
        base_row = example_rows["base_row"]
        base_rows.append(base_row)
        base_rows_by_id[example.id] = base_row
        gate_candidate_rows_by_id[example.id] = example_rows["gate_candidate_row"]
        rows.extend(example_rows["rows"])
        for threshold, threshold_rows in example_rows["gate_rows_by_threshold"].items():
            gate_rows_by_threshold[threshold].extend(threshold_rows)

    seq_summary = sequential_summary(sequential_rows)
    if not seq_summary["passed"]:
        raise SystemExit("Sequential prefill sanity failed; aborting selector stress run.")

    rows.extend(
        build_random_gate_baseline_rows(
            example_ids=example_ids,
            base_rows_by_id=base_rows_by_id,
            gate_candidate_rows_by_id=gate_candidate_rows_by_id,
            gate_rows_by_threshold=gate_rows_by_threshold,
            random_seeds=random_seeds,
            config_seed=config.seed,
        )
    )

    outputs_path = args.results_dir / "doc_selector_stress_outputs.jsonl"
    csv_path = args.results_dir / "doc_selector_stress_metrics.csv"
    random_distribution_path = (
        args.results_dir / "doc_selector_stress_random_baseline_distribution.csv"
    )
    summary_path = args.results_dir / "doc_selector_stress_summary.json"
    failure_path = args.results_dir / "doc_selector_stress_failure_analysis.md"

    write_jsonl(outputs_path, rows)
    write_stress_metrics_csv(csv_path, rows)
    summary = summarize_doc_selector_stress_rows(rows, base_rows, failed_examples)
    summary["base_method"] = args.base_method
    summary["num_random_seeds"] = args.num_random_seeds
    summary["repair_oracle_max_k"] = args.repair_oracle_max_k
    summary["gate_thresholds"] = gate_thresholds
    summary["sequential_prefill_sanity"] = seq_summary
    summary["outputs"] = {
        "doc_selector_stress_outputs": str(outputs_path),
        "doc_selector_stress_metrics_csv": str(csv_path),
        "doc_selector_stress_random_baseline_distribution": str(random_distribution_path),
        "doc_selector_stress_summary": str(summary_path),
        "doc_selector_stress_failure_analysis": str(failure_path),
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_random_distribution_csv(
        random_distribution_path,
        flatten_random_distribution_for_csv(summary["random_baseline_distribution"]),
    )
    failure_path.write_text(
        stress_failure_analysis_markdown(rows, summary),
        encoding="utf-8",
    )
    print(json.dumps(compact_console_summary(summary), indent=2, ensure_ascii=False))


def run_example_stress(
    *,
    example: DiagnosticExample,
    loaded: Any,
    config: Any,
    random_seeds: list[int],
    gate_thresholds: list[float],
    repair_oracle_max_k: int,
) -> dict[str, Any]:
    pack = build_prompt_pack_for_config(example, loaded, config)
    full_logits, full_cache = full_prefill_logits_and_cache(
        loaded.model,
        pack,
        loaded.device,
    )
    sequential_logits = run_sequential_prefill_logits(loaded.model, pack, loaded.device)
    sequential_row = make_metric_row(
        example=example,
        method="sequential_prefill",
        pack=pack,
        full_logits=full_logits,
        method_logits=sequential_logits,
        tokenizer=loaded.tokenizer,
        composed_context_length=len(pack.full_input_ids),
    )

    base_cache, base_metadata = build_naive_composed_context_cache(
        loaded.model,
        pack,
        loaded.device,
        position_mode="global",
        includes_prefix_cache=True,
        doc_conditioning="prefix",
    )
    base_logits = evaluate_query_with_context_cache(
        loaded.model,
        pack,
        base_cache,
        loaded.device,
    )
    base_row = make_patch_metric_row(
        example=example,
        method="prefix_conditioned_naive_global",
        pack=pack,
        full_logits=full_logits,
        method_logits=base_logits,
        tokenizer=loaded.tokenizer,
        cache_metadata=base_metadata,
        patched_ranges=[],
    )
    base_row["selected_doc_ids"] = []
    base_row["patched_doc_count"] = 0
    base_row["random_seed"] = None
    base_row["selector_reason"] = {"selector": "base"}

    subset_rows: dict[tuple[int, ...], dict[str, Any]] = {(): base_row}

    def evaluate_subset(doc_ids: list[int] | tuple[int, ...]) -> dict[str, Any]:
        subset = canonical_doc_subset(doc_ids)
        if subset in subset_rows:
            return subset_rows[subset]
        patch_ranges = document_ranges_for_ids(example, pack, subset)
        validate_patch_ranges_within_documents(patch_ranges, pack)
        patched_cache = replace_cache_slices(base_cache, full_cache, patch_ranges)
        if cache_seq_len(patched_cache) != cache_seq_len(base_cache):
            raise ValueError("patched cache length changed")
        method_logits = evaluate_query_with_context_cache(
            loaded.model,
            pack,
            patched_cache,
            loaded.device,
        )
        row = make_patch_metric_row(
            example=example,
            method="doc_subset_patch",
            pack=pack,
            full_logits=full_logits,
            method_logits=method_logits,
            tokenizer=loaded.tokenizer,
            cache_metadata=base_metadata,
            patched_ranges=patch_ranges,
        )
        row["selected_doc_ids"] = list(subset)
        row["patched_doc_count"] = len(subset)
        row["random_seed"] = None
        row["selector_reason"] = {"selector": "doc_subset_patch"}
        subset_rows[subset] = row
        return row

    rows: list[dict[str, Any]] = [
        clone_metric_row_for_method(
            base_row,
            method="prefix_conditioned_naive_global",
            base_row=base_row,
            selected_doc_ids=[],
            selector_reason={"selector": "base"},
        )
    ]

    for subset in exhaustive_doc_subsets(example, max_k=repair_oracle_max_k):
        evaluate_subset(subset)
    oracle_count = len(oracle_doc_ids(example))
    if oracle_count > repair_oracle_max_k:
        for subset in exhaustive_doc_subsets(example, k=oracle_count):
            evaluate_subset(subset)

    rows.extend(
        semantic_selector_rows(
            example=example,
            subset_rows=subset_rows,
            evaluate_subset=evaluate_subset,
            base_row=base_row,
            seed=config.seed,
            repair_oracle_max_k=repair_oracle_max_k,
        )
    )
    rows.extend(
        random_doc_seed_rows(
            example=example,
            subset_rows=subset_rows,
            evaluate_subset=evaluate_subset,
            base_row=base_row,
            random_seeds=random_seeds,
        )
    )

    gate_rows_by_threshold: dict[float, list[dict[str, Any]]] = {}
    for threshold in gate_thresholds:
        method = safe_gate_method_name(threshold)
        selected_doc_ids, reason = selected_doc_ids_for_method(
            method,
            example,
            seed=config.seed,
        )
        subset_row = evaluate_subset(selected_doc_ids)
        row = clone_metric_row_for_method(
            subset_row,
            method=method,
            base_row=base_row,
            selected_doc_ids=selected_doc_ids,
            selector_reason=reason,
        )
        rows.append(row)
        gate_rows_by_threshold[threshold] = [row]

    gate_candidate_ids, gate_candidate_reason = selected_doc_ids_for_method(
        "risk_guided_doc_patch_k2",
        example,
        seed=config.seed,
    )
    gate_candidate_row = clone_metric_row_for_method(
        evaluate_subset(gate_candidate_ids),
        method="risk_guided_doc_patch_k2",
        base_row=base_row,
        selected_doc_ids=gate_candidate_ids,
        selector_reason=gate_candidate_reason,
    )

    return {
        "rows": rows,
        "base_row": base_row,
        "sequential_row": sequential_row,
        "gate_candidate_row": gate_candidate_row,
        "gate_rows_by_threshold": gate_rows_by_threshold,
    }


def semantic_selector_rows(
    *,
    example: DiagnosticExample,
    subset_rows: dict[tuple[int, ...], dict[str, Any]],
    evaluate_subset: Any,
    base_row: dict[str, Any],
    seed: int,
    repair_oracle_max_k: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in SEMANTIC_DOC_SELECTOR_METHODS:
        selected_doc_ids, reason = selected_doc_ids_for_method(method, example, seed=seed)
        subset_row = evaluate_subset(selected_doc_ids)
        rows.append(
            clone_metric_row_for_method(
                subset_row,
                method=method,
                base_row=base_row,
                selected_doc_ids=selected_doc_ids,
                selector_reason=reason,
            )
        )

    repair_specs = repair_oracle_specs(example, repair_oracle_max_k)
    for method, candidates in repair_specs.items():
        best_subset, best_row = best_subset_by_metric(subset_rows, candidates)
        rows.append(
            clone_metric_row_for_method(
                best_row,
                method=method,
                base_row=base_row,
                selected_doc_ids=best_subset,
                selector_reason={
                    "selector": method,
                    "candidate_count": len(candidates),
                    "repair_oracle": True,
                },
            )
        )
    return rows


def repair_oracle_specs(
    example: DiagnosticExample,
    repair_oracle_max_k: int,
) -> dict[str, list[tuple[int, ...]]]:
    specs = {
        "oracle_best_doc_patch_k1": exhaustive_doc_subsets(example, k=1),
        "oracle_best_doc_patch_k2": exhaustive_doc_subsets(example, k=2),
        "oracle_best_doc_patch_same_count": exhaustive_doc_subsets(
            example,
            k=max(1, len(oracle_doc_ids(example))),
        ),
        "oracle_min_kl_doc_subset": exhaustive_doc_subsets(
            example,
            max_k=repair_oracle_max_k,
        ),
    }
    if repair_oracle_max_k >= 3:
        specs["oracle_best_doc_patch_k3"] = exhaustive_doc_subsets(example, k=3)
    return {method: candidates for method, candidates in specs.items() if candidates}


def random_doc_seed_rows(
    *,
    example: DiagnosticExample,
    subset_rows: dict[tuple[int, ...], dict[str, Any]],
    evaluate_subset: Any,
    base_row: dict[str, Any],
    random_seeds: list[int],
) -> list[dict[str, Any]]:
    _ = subset_rows
    rows: list[dict[str, Any]] = []
    oracle_count = len(oracle_doc_ids(example))
    for random_seed in random_seeds:
        same_count_seed = stable_example_seed(
            random_seed,
            example.id,
            "random_doc_patch_same_count_seeded",
        )
        same_count_docs = random_doc_ids_same_count(example, oracle_count, same_count_seed)
        rows.append(
            clone_metric_row_for_method(
                evaluate_subset(same_count_docs),
                method="random_doc_patch_same_count_seeded",
                base_row=base_row,
                selected_doc_ids=same_count_docs,
                selector_reason={"selector": "random_doc_patch_same_count_seeded"},
                random_seed=random_seed,
            )
        )
        for k in (1, 2):
            method = f"random_doc_patch_k{k}_seeded"
            method_seed = stable_example_seed(random_seed, example.id, method)
            selected = random_doc_ids_same_count(example, k, method_seed)
            rows.append(
                clone_metric_row_for_method(
                    evaluate_subset(selected),
                    method=method,
                    base_row=base_row,
                    selected_doc_ids=selected,
                    selector_reason={"selector": method},
                    random_seed=random_seed,
                )
            )
    return rows


def build_random_gate_baseline_rows(
    *,
    example_ids: list[str],
    base_rows_by_id: dict[str, dict[str, Any]],
    gate_candidate_rows_by_id: dict[str, dict[str, Any]],
    gate_rows_by_threshold: dict[float, list[dict[str, Any]]],
    random_seeds: list[int],
    config_seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidate_ratios = {
        example_id: gate_candidate_rows_by_id[example_id]["patched_token_ratio"]
        for example_id in example_ids
    }
    for threshold, gate_rows in gate_rows_by_threshold.items():
        target_count = sum(1 for row in gate_rows if row.get("patched_doc_count", 0) > 0)
        target_avg_ratio = (
            sum(float(row["patched_token_ratio"]) for row in gate_rows) / len(gate_rows)
            if gate_rows
            else 0.0
        )
        suffix = safe_gate_method_name(threshold).removeprefix("safe_composition_gate_t")
        for random_seed in random_seeds:
            same_num_ids = random_gate_ids_same_num_patched_examples(
                example_ids,
                target_count=target_count,
                seed=stable_example_seed(
                    config_seed + random_seed,
                    f"gate-{threshold}",
                    "same_num",
                ),
            )
            rows.extend(
                _random_gate_rows_for_selection(
                    method=f"random_gate_same_num_patched_examples_t{suffix}",
                    selected_example_ids=same_num_ids,
                    example_ids=example_ids,
                    base_rows_by_id=base_rows_by_id,
                    gate_candidate_rows_by_id=gate_candidate_rows_by_id,
                    random_seed=random_seed,
                    selector_reason={
                        "selector": "random_gate_same_num_patched_examples",
                        "matched_threshold": threshold,
                        "target_patched_examples": target_count,
                    },
                )
            )

            same_rate_ids = random_gate_ids_same_patch_rate(
                candidate_ratios,
                target_avg_patch_ratio=target_avg_ratio,
                seed=stable_example_seed(
                    config_seed + random_seed,
                    f"gate-{threshold}",
                    "same_patch_rate",
                ),
            )
            rows.extend(
                _random_gate_rows_for_selection(
                    method=f"random_gate_same_patch_rate_t{suffix}",
                    selected_example_ids=same_rate_ids,
                    example_ids=example_ids,
                    base_rows_by_id=base_rows_by_id,
                    gate_candidate_rows_by_id=gate_candidate_rows_by_id,
                    random_seed=random_seed,
                    selector_reason={
                        "selector": "random_gate_same_patch_rate",
                        "matched_threshold": threshold,
                        "target_avg_patch_ratio": target_avg_ratio,
                    },
                )
            )
    return rows


def _random_gate_rows_for_selection(
    *,
    method: str,
    selected_example_ids: set[str],
    example_ids: list[str],
    base_rows_by_id: dict[str, dict[str, Any]],
    gate_candidate_rows_by_id: dict[str, dict[str, Any]],
    random_seed: int,
    selector_reason: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for example_id in example_ids:
        base_row = base_rows_by_id[example_id]
        source_row = (
            gate_candidate_rows_by_id[example_id]
            if example_id in selected_example_ids
            else base_row
        )
        selected_docs = source_row.get("selected_doc_ids", []) if example_id in selected_example_ids else []
        rows.append(
            clone_metric_row_for_method(
                source_row,
                method=method,
                base_row=base_row,
                selected_doc_ids=selected_docs,
                selector_reason=selector_reason,
                random_seed=random_seed,
            )
        )
    return rows


def write_stress_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STRESS_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            csv_row = {column: row.get(column, "") for column in STRESS_CSV_COLUMNS}
            csv_row["selected_doc_ids"] = " ".join(
                str(doc_id) for doc_id in row.get("selected_doc_ids", [])
            )
            csv_row["selector_reason"] = json.dumps(
                row.get("selector_reason", {}),
                ensure_ascii=False,
                sort_keys=True,
            )
            writer.writerow(csv_row)


def write_random_distribution_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RANDOM_DISTRIBUTION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in RANDOM_DISTRIBUTION_COLUMNS})


def compact_console_summary(summary: dict[str, Any]) -> dict[str, Any]:
    methods = [
        "prefix_conditioned_naive_global",
        "oracle_evidence_doc_patch",
        "oracle_min_kl_doc_subset",
        "random_doc_patch_same_count_seeded",
        "random_doc_patch_k1_seeded",
        "random_doc_patch_k2_seeded",
        "query_similarity_doc_patch_k2",
        "risk_guided_doc_patch_k2",
        "entity_overlap_doc_patch_k2",
        "safe_composition_gate_t0_30",
        "safe_composition_gate_t0_45",
        "safe_composition_gate_t0_60",
    ]
    method_level = summary.get("method_level", {})
    compact_methods = {}
    for method in methods:
        if method not in method_level:
            continue
        data = method_level[method]
        compact_methods[method] = {
            "avg_kl": data["avg_kl"],
            "top1_match_rate": data["top1_match_rate"],
            "avg_top10_overlap": data["avg_top10_overlap"],
            "avg_patched_token_ratio": data.get("avg_patched_token_ratio", 0.0),
            "avg_patched_doc_count": data.get("avg_patched_doc_count", 0.0),
        }
    return {
        "num_rows": summary.get("num_rows"),
        "category_counts": summary.get("category_counts"),
        "sequential_prefill_sanity": summary.get("sequential_prefill_sanity"),
        "best_method_by_avg_kl": summary.get("best_method_by_avg_kl"),
        "method_level_compact": compact_methods,
        "semantic_selector_percentiles": summary.get("semantic_selector_percentiles", {}),
        "budget_warnings": summary.get("budget_warnings", []),
        "outputs": summary.get("outputs", {}),
    }


def stress_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    top_n: int = 10,
) -> str:
    method_level = summary.get("method_level", {})
    percentiles = summary.get("semantic_selector_percentiles", {})
    warnings = summary.get("budget_warnings", [])
    repair_method = "oracle_min_kl_doc_subset"
    repair_rows = [row for row in rows if row["method"] == repair_method]
    repair_rows = sorted(
        repair_rows,
        key=lambda row: row["first_token_kl_full_to_method"],
        reverse=True,
    )

    lines = [
        "# Document Selector Stress Failure Analysis",
        "",
        "This stress test compares semantic document selectors against multi-seed "
        "random baselines and repair oracles. Lower KL is better.",
        "",
        "## Method Ranking",
        "",
        "| method | avg KL | top1 | top10 | patched ratio | patched docs | KL gain / ratio |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary.get("method_ranking_by_avg_kl", []):
        method = item["method"]
        data = method_level[method]
        lines.append(
            "| {method} | {kl:.6g} | {top1:.3f} | {top10:.3f} | {ratio:.3f} | {docs:.2f} | {gain:.6g} |".format(
                method=_md(method),
                kl=float(data["avg_kl"]),
                top1=float(data["top1_match_rate"]),
                top10=float(data["avg_top10_overlap"]),
                ratio=float(data.get("avg_patched_token_ratio", 0.0)),
                docs=float(data.get("avg_patched_doc_count", 0.0)),
                gain=float(data.get("kl_reduction_per_patched_token_ratio", 0.0)),
            )
        )

    lines.extend(["", "## Semantic Selector Percentiles", ""])
    if percentiles:
        lines.extend(
            [
                "| method | matched random | semantic KL | random mean KL | % random worse/equal |",
                "|---|---|---:|---:|---:|",
            ]
        )
        for method, data in sorted(percentiles.items()):
            lines.append(
                "| {method} | {baseline} | {semantic:.6g} | {random:.6g} | {pct:.1f} |".format(
                    method=_md(method),
                    baseline=_md(data["matched_random_baseline"]),
                    semantic=float(data["semantic_avg_kl"]),
                    random=float(data["random_avg_kl_mean"]),
                    pct=float(data["percent_random_seeds_worse_or_equal"]),
                )
            )
    else:
        lines.append("No matched random baseline percentiles were available.")

    lines.extend(["", "## Budget Warnings", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("No budget warnings were triggered.")

    lines.extend(
        [
            "",
            f"## Top {top_n} Residual KL Rows For Repair Oracle",
            "",
            "| rank | example_id | category | KL | selected docs | full argmax | method argmax |",
            "|---:|---|---|---:|---|---|---|",
        ]
    )
    for rank, row in enumerate(repair_rows[:top_n], start=1):
        lines.append(
            "| {rank} | {example_id} | {category} | {kl:.6g} | `{docs}` | `{full}` | `{method}` |".format(
                rank=rank,
                example_id=_md(row["example_id"]),
                category=_md(row["category"]),
                kl=float(row["first_token_kl_full_to_method"]),
                docs=_md(row.get("selected_doc_ids", [])),
                full=_md(row.get("argmax_full_decoded", "")),
                method=_md(row.get("argmax_method_decoded", "")),
            )
        )
    if not repair_rows:
        lines.append("| none | - | - | 0 | - | - | - |")
    lines.append("")
    return "\n".join(lines)


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
