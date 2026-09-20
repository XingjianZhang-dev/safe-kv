#!/usr/bin/env python
"""Run SAFE-KV Milestone 4B patch granularity and causal-closure ablations."""

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
from safekv.patch_granularity import (  # noqa: E402
    DEFAULT_SPAN_WINDOWS,
    build_ranges_for_methods,
    default_patch_granularity_methods,
    is_random_budget_method,
    paired_oracle_method,
    summarize_patch_granularity_rows,
)
from safekv.patch_recompute import (  # noqa: E402
    replace_cache_slices,
    validate_patch_ranges_within_documents,
)


GRANULARITY_CSV_COLUMNS = PATCH_CSV_COLUMNS + [
    "paired_oracle_method",
    "is_random_budget_baseline",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--base-method", default="prefix_conditioned_naive_global")
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--windows", nargs="*", type=int, default=DEFAULT_SPAN_WINDOWS)
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
        raise ValueError("Milestone 4B supports base_method=prefix_conditioned_naive_global")
    methods = args.methods or default_patch_granularity_methods(args.windows)

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

        try:
            ranges_by_method = build_ranges_for_methods(
                example,
                pack,
                methods,
                seed=config.seed,
                windows=args.windows,
            )
        except Exception as exc:
            for method in methods:
                failed_examples.append(
                    {"example_id": example.id, "method": method, "error": repr(exc)}
                )
            continue

        for method in methods:
            try:
                patch_ranges = ranges_by_method[method]
                validate_patch_ranges_within_documents(patch_ranges, pack)
                patched_cache = replace_cache_slices(base_cache, full_cache, patch_ranges)
                if cache_seq_len(patched_cache) != cache_seq_len(base_cache):
                    raise ValueError("patched cache length changed")
                patched_logits = evaluate_query_with_context_cache(
                    loaded.model,
                    pack,
                    patched_cache,
                    loaded.device,
                )
                row = make_patch_metric_row(
                    example=example,
                    method=method,
                    pack=pack,
                    full_logits=full_logits,
                    method_logits=patched_logits,
                    tokenizer=loaded.tokenizer,
                    cache_metadata=base_metadata,
                    patched_ranges=patch_ranges,
                )
                row["paired_oracle_method"] = paired_oracle_method(method)
                row["is_random_budget_baseline"] = is_random_budget_method(method)
                rows.append(row)
            except Exception as exc:  # pragma: no cover - real model diagnostics only
                failed_examples.append(
                    {"example_id": example.id, "method": method, "error": repr(exc)}
                )

    seq_summary = sequential_summary(sequential_rows)
    if not seq_summary["passed"]:
        raise SystemExit("Sequential prefill sanity failed; aborting patch granularity run.")

    outputs_path = args.results_dir / "patch_granularity_outputs.jsonl"
    write_jsonl(outputs_path, rows)
    csv_path = args.results_dir / "patch_granularity_metrics.csv"
    write_granularity_metrics_csv(csv_path, rows)

    summary = summarize_patch_granularity_rows(rows, base_rows, failed_examples)
    summary["base_method"] = args.base_method
    summary["sequential_prefill_sanity"] = seq_summary
    summary["selected_methods"] = methods
    summary["windows"] = args.windows
    summary["outputs"] = {
        "patch_granularity_outputs": str(outputs_path),
        "patch_granularity_metrics_csv": str(csv_path),
        "patch_granularity_failure_analysis": str(
            args.results_dir / "patch_granularity_failure_analysis.md"
        ),
    }
    summary_path = args.results_dir / "patch_granularity_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    failure_path = args.results_dir / "patch_granularity_failure_analysis.md"
    failure_path.write_text(
        patch_granularity_failure_analysis_markdown(rows, summary),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def write_granularity_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GRANULARITY_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in GRANULARITY_CSV_COLUMNS})


def patch_granularity_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    top_n: int = 10,
) -> str:
    non_random_rows = [
        row
        for row in rows
        if not is_random_budget_method(row["method"])
        and row["method"] != "oracle_evidence_doc_patch"
    ]
    method_level = summary.get("method_level", {})
    best_non_doc = min(
        (
            method
            for method in method_level
            if not is_random_budget_method(method) and method != "oracle_evidence_doc_patch"
        ),
        key=lambda method: method_level[method]["avg_kl"],
        default="",
    )
    focus_rows = [row for row in rows if row["method"] == best_non_doc]
    sorted_focus = sorted(
        focus_rows,
        key=lambda row: row["first_token_kl_full_to_method"],
        reverse=True,
    )
    category_counts = Counter(row["category"] for row in focus_rows)
    mismatch_counts = Counter(row["category"] for row in focus_rows if not row["top1_match"])

    lines = [
        "# Patch Granularity Failure Analysis",
        "",
        f"Best non-document oracle method by average KL: `{best_non_doc}`",
        "",
        "This diagnostic compares oracle repair granularity. Random baselines are "
        "budget matched per example and should be interpreted as non-semantic controls.",
        "",
        "## Non-Document Oracle Ranking",
        "",
        "| method | avg KL | top1 | top10 | avg patched ratio | KL gain vs base | KL gain vs random |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    ranking = sorted(
        (
            (method, data)
            for method, data in method_level.items()
            if not is_random_budget_method(method) and method != "oracle_evidence_doc_patch"
        ),
        key=lambda item: item[1]["avg_kl"],
    )
    for method, data in ranking:
        base_delta = data.get("improvement_over_base", {})
        random_delta = data.get("improvement_over_budget_random", {})
        lines.append(
            "| {method} | {kl:.6g} | {top1:.3f} | {top10:.3f} | {ratio:.3f} | {base:.6g} | {random:.6g} |".format(
                method=_md(method),
                kl=float(data["avg_kl"]),
                top1=float(data["top1_match_rate"]),
                top10=float(data["avg_top10_overlap"]),
                ratio=float(data.get("avg_patched_token_ratio", 0.0)),
                base=float(base_delta.get("kl_reduction", 0.0)),
                random=float(random_delta.get("kl_reduction", 0.0)),
            )
        )

    lines.extend(
        [
            "",
            "## Category Breakdown For Best Non-Document Method",
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
            f"## Top {top_n} KL Rows For Best Non-Document Method",
            "",
            "| rank | example_id | category | KL | patched tokens | full argmax | method argmax |",
            "|---:|---|---|---:|---:|---|---|",
        ]
    )
    for rank, row in enumerate(sorted_focus[:top_n], start=1):
        lines.append(
            "| {rank} | {example_id} | {category} | {kl:.6g} | {tokens} | `{full}` | `{method}` |".format(
                rank=rank,
                example_id=_md(row["example_id"]),
                category=_md(row["category"]),
                kl=float(row["first_token_kl_full_to_method"]),
                tokens=int(row["patched_token_count"]),
                full=_md(row.get("argmax_full_decoded", "")),
                method=_md(row.get("argmax_method_decoded", "")),
            )
        )
    if not sorted_focus:
        lines.append("| none | - | - | 0 | 0 | - | - |")
    lines.append("")
    _ = non_random_rows
    return "\n".join(lines)


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
