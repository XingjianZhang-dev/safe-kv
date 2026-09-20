#!/usr/bin/env python
"""Run SAFE-KV Milestone 5A document-level selectors and safe-composition gates."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_patch_recompute import (  # noqa: E402
    PATCH_CSV_COLUMNS,
    full_prefill_logits_and_cache,
    make_patch_metric_row,
    write_jsonl,
)
from safekv.cache_ops import cache_seq_len
from safekv.config import load_config
from safekv.doc_selector import (  # noqa: E402
    default_doc_selector_methods,
    parse_safe_gate_threshold,
    patch_ranges_for_doc_selector_method,
    summarize_doc_selector_rows,
)
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed
from safekv.modeling import load_causal_lm
from safekv.naive_composition import (  # noqa: E402
    build_naive_composed_context_cache,
    build_prompt_pack_for_config,
    evaluate_query_with_context_cache,
    make_metric_row,
    run_sequential_prefill_logits,
    sequential_summary,
)
from safekv.patch_recompute import replace_cache_slices, validate_patch_ranges_within_documents


DOC_SELECTOR_CSV_COLUMNS = PATCH_CSV_COLUMNS + [
    "patched_doc_count",
    "selected_doc_ids",
    "is_gate",
    "gate_risk_score",
    "gate_threshold",
    "gate_should_patch",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--base-method", default="prefix_conditioned_naive_global")
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--gate-thresholds", nargs="*", type=float, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    set_deterministic_seed(config.seed)
    config_dir = args.config.resolve().parent.parent
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    if args.base_method != "prefix_conditioned_naive_global":
        raise ValueError("Milestone 5A supports base_method=prefix_conditioned_naive_global")
    methods = args.methods or default_doc_selector_methods(args.gate_thresholds)

    rows: list[dict[str, Any]] = []
    base_rows: list[dict[str, Any]] = []
    sequential_rows: list[dict[str, Any]] = []
    failed_examples: list[dict[str, str]] = []

    for example in examples:
        pack = build_prompt_pack_for_config(example, loaded, config)
        full_logits, full_cache = full_prefill_logits_and_cache(
            loaded.model,
            pack,
            loaded.device,
        )
        sequential_logits = run_sequential_prefill_logits(loaded.model, pack, loaded.device)
        sequential_rows.append(
            make_metric_row(
                example=example,
                method="sequential_prefill",
                pack=pack,
                full_logits=full_logits,
                method_logits=sequential_logits,
                tokenizer=loaded.tokenizer,
                composed_context_length=len(pack.full_input_ids),
            )
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
        base_rows.append(
            make_patch_metric_row(
                example=example,
                method=args.base_method,
                pack=pack,
                full_logits=full_logits,
                method_logits=base_logits,
                tokenizer=loaded.tokenizer,
                cache_metadata=base_metadata,
                patched_ranges=[],
            )
        )

        for method in methods:
            try:
                patch_ranges, selected_doc_ids, selector_reason = (
                    patch_ranges_for_doc_selector_method(
                        method,
                        example,
                        pack,
                        seed=config.seed,
                    )
                )
                validate_patch_ranges_within_documents(patch_ranges, pack)
                if patch_ranges:
                    patched_cache = replace_cache_slices(base_cache, full_cache, patch_ranges)
                    if cache_seq_len(patched_cache) != cache_seq_len(base_cache):
                        raise ValueError("patched cache length changed")
                    method_logits = evaluate_query_with_context_cache(
                        loaded.model,
                        pack,
                        patched_cache,
                        loaded.device,
                    )
                else:
                    method_logits = base_logits
                row = make_patch_metric_row(
                    example=example,
                    method=method,
                    pack=pack,
                    full_logits=full_logits,
                    method_logits=method_logits,
                    tokenizer=loaded.tokenizer,
                    cache_metadata=base_metadata,
                    patched_ranges=patch_ranges,
                )
                row["selected_doc_ids"] = selected_doc_ids
                row["patched_doc_count"] = len(selected_doc_ids)
                row["selector_reason"] = selector_reason
                row["is_gate"] = parse_safe_gate_threshold(method) is not None
                row["gate_risk_score"] = selector_reason.get("gate_risk_score")
                row["gate_threshold"] = selector_reason.get("gate_threshold")
                row["gate_should_patch"] = selector_reason.get("gate_should_patch")
                rows.append(row)
            except Exception as exc:  # pragma: no cover - real model diagnostics only
                failed_examples.append(
                    {"example_id": example.id, "method": method, "error": repr(exc)}
                )

    seq_summary = sequential_summary(sequential_rows)
    if not seq_summary["passed"]:
        raise SystemExit("Sequential prefill sanity failed; aborting document selector run.")

    outputs_path = args.results_dir / "doc_selector_outputs.jsonl"
    write_jsonl(outputs_path, rows)
    metrics_path = args.results_dir / "doc_selector_metrics.csv"
    write_doc_selector_metrics_csv(metrics_path, rows)

    summary = summarize_doc_selector_rows(rows, base_rows, failed_examples)
    summary["base_method"] = args.base_method
    summary["sequential_prefill_sanity"] = seq_summary
    summary["selected_methods"] = methods
    summary["outputs"] = {
        "doc_selector_outputs": str(outputs_path),
        "doc_selector_metrics_csv": str(metrics_path),
        "doc_selector_summary": str(args.results_dir / "doc_selector_summary.json"),
        "doc_selector_failure_analysis": str(
            args.results_dir / "doc_selector_failure_analysis.md"
        ),
        "doc_selector_pareto": str(args.results_dir / "doc_selector_pareto.csv"),
    }
    summary_path = args.results_dir / "doc_selector_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    failure_path = args.results_dir / "doc_selector_failure_analysis.md"
    failure_path.write_text(
        doc_selector_failure_analysis_markdown(rows, summary),
        encoding="utf-8",
    )
    pareto_path = args.results_dir / "doc_selector_pareto.csv"
    write_gate_pareto_csv(pareto_path, summary["gate_pareto"])
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def write_doc_selector_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DOC_SELECTOR_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            csv_row = {column: row.get(column, "") for column in DOC_SELECTOR_CSV_COLUMNS}
            csv_row["selected_doc_ids"] = " ".join(str(doc_id) for doc_id in row["selected_doc_ids"])
            writer.writerow(csv_row)


def write_gate_pareto_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "method",
        "threshold",
        "avg_patched_token_ratio",
        "avg_kl",
        "top1_mismatch_rate",
        "top1_match_rate",
        "avg_top10_overlap",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def doc_selector_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    top_n: int = 10,
) -> str:
    method_level = summary.get("method_level", {})
    excluded = {
        "oracle_evidence_doc_patch",
        "random_doc_patch_same_count",
        "random_token_patch_same_budget_as_oracle_doc",
    }
    best_non_oracle = min(
        (method for method in method_level if method not in excluded),
        key=lambda method: method_level[method]["avg_kl"],
        default="",
    )
    focus_rows = [row for row in rows if row["method"] == best_non_oracle]
    sorted_focus = sorted(
        focus_rows,
        key=lambda row: row["first_token_kl_full_to_method"],
        reverse=True,
    )
    category_counts = Counter(row["category"] for row in focus_rows)
    mismatch_counts = Counter(row["category"] for row in focus_rows if not row["top1_match"])

    lines = [
        "# Document Selector Failure Analysis",
        "",
        f"Best non-oracle selector by average KL: `{best_non_oracle}`",
        "",
        "Rows compare document-level patching against the full-prefill first-token distribution.",
        "",
        "## Method Ranking",
        "",
        "| method | avg KL | top1 | top10 | patched ratio | KL gain vs base | KL gap to oracle |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summary.get("method_ranking_by_avg_kl", []):
        method = item["method"]
        data = method_level[method]
        base_delta = data.get("improvement_over_base", {})
        oracle_gap = data.get("gap_to_oracle_evidence_doc_patch", {})
        lines.append(
            "| {method} | {kl:.6g} | {top1:.3f} | {top10:.3f} | {ratio:.3f} | {base:.6g} | {gap:.6g} |".format(
                method=_md(method),
                kl=float(data["avg_kl"]),
                top1=float(data["top1_match_rate"]),
                top10=float(data["avg_top10_overlap"]),
                ratio=float(data.get("avg_patched_token_ratio", 0.0)),
                base=float(base_delta.get("kl_reduction", 0.0)),
                gap=float(oracle_gap.get("kl_gap", 0.0)),
            )
        )

    lines.extend(
        [
            "",
            "## Category Breakdown For Best Non-Oracle Selector",
            "",
            "| category | examples | top1 mismatches |",
            "|---|---:|---:|",
        ]
    )
    for category in sorted(category_counts):
        lines.append(f"| {category} | {category_counts[category]} | {mismatch_counts[category]} |")

    lines.extend(
        [
            "",
            f"## Top {top_n} KL Rows For Best Non-Oracle Selector",
            "",
            "| rank | example_id | category | KL | selected docs | full argmax | method argmax |",
            "|---:|---|---|---:|---|---|---|",
        ]
    )
    for rank, row in enumerate(sorted_focus[:top_n], start=1):
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
    if not sorted_focus:
        lines.append("| none | - | - | 0 | - | - | - |")
    lines.append("")
    return "\n".join(lines)


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
