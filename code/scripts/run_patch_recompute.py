#!/usr/bin/env python
"""Run SAFE-KV Milestone 4A oracle cache patch diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.cache_ops import cache_seq_len, to_legacy_cache
from safekv.config import load_config
from safekv.data_schema import DiagnosticExample, PromptPack, TokenRange
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed
from safekv.metrics import logit_preservation_metrics
from safekv.modeling import load_causal_lm
from safekv.naive_composition import (
    average_metric_summary,
    build_naive_composed_context_cache,
    build_prompt_pack_for_config,
    evaluate_query_with_context_cache,
    make_metric_row,
    run_sequential_prefill_logits,
    sequential_summary,
    summarize_rows,
)
from safekv.patch_recompute import (
    full_doc_patch_ranges,
    oracle_evidence_doc_patch_ranges,
    oracle_evidence_span_patch_ranges,
    random_span_patch_ranges_same_budget,
    replace_cache_slices,
    stable_example_seed,
    token_count,
    validate_patch_ranges_within_documents,
)


PATCH_METHODS = [
    "full_doc_cache_patch_sanity",
    "oracle_evidence_doc_patch",
    "oracle_evidence_span_patch",
    "random_span_patch_same_budget",
]

PATCH_CSV_COLUMNS = [
    "example_id",
    "category",
    "method",
    "first_token_kl_full_to_method",
    "first_token_js_divergence",
    "top1_match",
    "top5_overlap",
    "top10_overlap",
    "patched_token_count",
    "patched_token_ratio",
    "patched_range_count",
    "prompt_length",
    "prefix_length",
    "doc_cache_length",
    "query_length",
    "position_mode",
    "composition_mode",
    "doc_conditioning",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--base-method", default="prefix_conditioned_naive_global")
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--full-doc-kl-threshold", type=float, default=1e-4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    set_deterministic_seed(config.seed)
    config_dir = args.config.resolve().parent.parent
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    methods = args.methods or PATCH_METHODS
    unsupported = sorted(set(methods) - set(PATCH_METHODS))
    if unsupported:
        raise ValueError(f"unsupported patch methods: {unsupported}")
    if args.base_method != "prefix_conditioned_naive_global":
        raise ValueError("Milestone 4A currently supports base_method=prefix_conditioned_naive_global")

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
        base_row = make_patch_metric_row(
            example=example,
            method=args.base_method,
            pack=pack,
            full_logits=full_logits,
            method_logits=base_logits,
            tokenizer=loaded.tokenizer,
            cache_metadata=base_metadata,
            patched_ranges=[],
        )
        base_rows.append(base_row)

        oracle_span_ranges = oracle_evidence_span_patch_ranges(
            pack,
            expand_window_tokens=config.recompute.expand_window_tokens,
        )
        ranges_by_method = {
            "full_doc_cache_patch_sanity": full_doc_patch_ranges(pack),
            "oracle_evidence_doc_patch": oracle_evidence_doc_patch_ranges(example, pack),
            "oracle_evidence_span_patch": oracle_span_ranges,
            "random_span_patch_same_budget": random_span_patch_ranges_same_budget(
                pack,
                target_token_count=token_count(oracle_span_ranges),
                seed=stable_example_seed(
                    config.seed,
                    example.id,
                    "random_span_patch_same_budget",
                ),
            ),
        }

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
                rows.append(row)
            except Exception as exc:  # pragma: no cover - exercised by real smoke failures
                failed_examples.append(
                    {"example_id": example.id, "method": method, "error": repr(exc)}
                )

    seq_summary = sequential_summary(sequential_rows)
    if not seq_summary["passed"]:
        raise SystemExit("Sequential prefill sanity failed; aborting patch recompute.")
    full_doc_errors = [
        row for row in failed_examples if row["method"] == "full_doc_cache_patch_sanity"
    ]
    if full_doc_errors:
        raise SystemExit(
            "full_doc_cache_patch_sanity failed before metric comparison; "
            f"first error: {full_doc_errors[0]}"
        )
    sanity_failures = [
        row
        for row in rows
        if row["method"] == "full_doc_cache_patch_sanity"
        and (
            (not row["top1_match"])
            or row["first_token_kl_full_to_method"] > args.full_doc_kl_threshold
        )
    ]
    if sanity_failures:
        first = sanity_failures[0]
        raise SystemExit(
            "full_doc_cache_patch_sanity failed; patch mechanics are not trustworthy. "
            f"First failure: {first['example_id']} KL={first['first_token_kl_full_to_method']}"
        )

    outputs_path = args.results_dir / "patch_recompute_outputs.jsonl"
    write_jsonl(outputs_path, rows)
    csv_path = args.results_dir / "patch_recompute_metrics.csv"
    write_patch_metrics_csv(csv_path, rows)
    failure_path = args.results_dir / "patch_failure_analysis.md"
    write_patch_failure_analysis(failure_path, rows, base_rows)

    summary = summarize_rows(rows, failed_examples)
    summary["base_method"] = args.base_method
    summary["base_method_level"] = average_metric_summary(base_rows)
    summary["sequential_prefill_sanity"] = seq_summary
    summary["selected_methods"] = methods
    summary["outputs"] = {
        "patch_recompute_outputs": str(outputs_path),
        "patch_recompute_metrics_csv": str(csv_path),
        "patch_failure_analysis": str(failure_path),
    }
    summary_path = args.results_dir / "patch_recompute_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def full_prefill_logits_and_cache(model: Any, pack: PromptPack, device: str) -> tuple[Any, Any]:
    import torch

    input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(input_ids.shape[1], dtype=torch.long, device=device).unsqueeze(0)
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
        )
    logits = outputs.logits[:, -1, :].detach().float().cpu()[0]
    return logits, to_legacy_cache(outputs.past_key_values)


def make_patch_metric_row(
    example: DiagnosticExample,
    method: str,
    pack: PromptPack,
    full_logits: Any,
    method_logits: Any,
    tokenizer: Any,
    cache_metadata: dict[str, Any],
    patched_ranges: list[TokenRange],
) -> dict[str, Any]:
    metrics = logit_preservation_metrics(full_logits, method_logits, tokenizer)
    patched_count = token_count(patched_ranges)
    composed_length = int(cache_metadata["composed_context_length"])
    row = {
        "example_id": example.id,
        "id": example.id,
        "category": example.category,
        "method": method,
        "patched_token_count": patched_count,
        "patched_token_ratio": patched_count / composed_length if composed_length else 0.0,
        "patched_range_count": len(patched_ranges),
        "patched_ranges": [
            {"start": token_range.start, "end": token_range.end}
            for token_range in patched_ranges
        ],
        **metrics,
    }
    for key in (
        "prompt_length",
        "prefix_length",
        "prefix_cache_length",
        "doc_cache_length",
        "query_length",
        "composed_context_length",
        "missing_prefix_length",
        "includes_prefix_cache",
        "position_mode",
        "composition_mode",
        "doc_conditioning",
    ):
        row[key] = cache_metadata[key]
    return row


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_patch_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PATCH_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in PATCH_CSV_COLUMNS})


def write_patch_failure_analysis(
    path: Path,
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(patch_failure_analysis_markdown(rows, base_rows), encoding="utf-8")


def patch_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    focus_method: str = "oracle_evidence_span_patch",
    top_n: int = 10,
) -> str:
    focus_rows = [row for row in rows if row["method"] == focus_method]
    base_by_id = {row["example_id"]: row for row in base_rows}
    category_counts = Counter(row["category"] for row in focus_rows)
    mismatch_counts = Counter(row["category"] for row in focus_rows if not row["top1_match"])
    sorted_rows = sorted(
        focus_rows,
        key=lambda row: row["first_token_kl_full_to_method"],
        reverse=True,
    )
    lines = [
        "# Patch Failure Analysis",
        "",
        f"Focus method: `{focus_method}`",
        "",
        "This is an oracle patch diagnostic. Interpret rows as behavior-preservation "
        "differences, not task-correctness claims.",
        "",
        "## Category Breakdown",
        "",
        "| category | examples | top1 mismatches |",
        "|---|---:|---:|",
    ]
    for category in sorted(category_counts):
        lines.append(f"| {category} | {category_counts[category]} | {mismatch_counts[category]} |")
    lines.extend(
        [
            "",
            f"## Top {top_n} Focus-Method KL Rows",
            "",
            "| rank | example_id | category | base KL | patch KL | patched tokens | full argmax | patch argmax | interpretation |",
            "|---:|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    for rank, row in enumerate(sorted_rows[:top_n], start=1):
        base = base_by_id.get(row["example_id"], {})
        lines.append(
            "| {rank} | {example_id} | {category} | {base_kl:.6g} | {patch_kl:.6g} | "
            "{tokens} | `{full}` | `{patch}` | {interp} |".format(
                rank=rank,
                example_id=_md(row["example_id"]),
                category=_md(row["category"]),
                base_kl=float(base.get("first_token_kl_full_to_method", 0.0)),
                patch_kl=float(row["first_token_kl_full_to_method"]),
                tokens=int(row["patched_token_count"]),
                full=_md(row.get("argmax_full_decoded", "")),
                patch=_md(row.get("argmax_method_decoded", "")),
                interp=_patch_interpretation(row, base),
            )
        )
    lines.extend(
        [
            "",
            "## Top1 Mismatches",
            "",
            "| example_id | category | patch KL | full argmax | patch argmax | interpretation |",
            "|---|---|---:|---|---|---|",
        ]
    )
    mismatches = [row for row in focus_rows if not row["top1_match"]]
    for row in mismatches:
        lines.append(
            "| {example_id} | {category} | {kl:.6g} | `{full}` | `{patch}` | {interp} |".format(
                example_id=_md(row["example_id"]),
                category=_md(row["category"]),
                kl=float(row["first_token_kl_full_to_method"]),
                full=_md(row.get("argmax_full_decoded", "")),
                patch=_md(row.get("argmax_method_decoded", "")),
                interp=_patch_interpretation(row, base_by_id.get(row["example_id"], {})),
            )
        )
    if not mismatches:
        lines.append("| none | - | 0 | - | - | No top1 mismatches observed. |")
    lines.append("")
    return "\n".join(lines)


def _patch_interpretation(row: dict[str, Any], base: dict[str, Any]) -> str:
    base_kl = float(base.get("first_token_kl_full_to_method", 0.0))
    patch_kl = float(row.get("first_token_kl_full_to_method", 0.0))
    if not bool(row.get("top1_match")):
        return "Patch did not preserve the full-prefill top token."
    if patch_kl < base_kl:
        return "Patch reduced first-token KL relative to the base composition."
    return "Patch preserved top1 but did not reduce KL relative to the base composition."


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
