#!/usr/bin/env python
"""Run SAFE-KV Milestone 3A/3B/3C naive KV composition smoke."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.config import load_config
from safekv.modeling import load_causal_lm
from safekv.naive_composition import (
    build_prompt_pack_for_config,
    full_prefill_logits,
    make_metric_row,
    reference_logits_for_example,
    run_naive_composed_logits,
    select_composition_method_specs,
    run_sequential_prefill_logits,
    sequential_summary,
    summarize_rows,
    write_composition_failure_analysis,
    write_composition_metrics_csv,
)
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--use-sidecar-reference",
        action="store_true",
        help=(
            "Use results/logits/full_prefill/*.pt as the reference logits. "
            "By default, this script uses full logits computed during this run."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    set_deterministic_seed(config.seed)
    config_dir = args.config.resolve().parent.parent
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    sequential_rows = []
    packs_by_id = {}
    full_logits_by_id = {}
    for example in examples:
        pack = build_prompt_pack_for_config(example, loaded, config)
        packs_by_id[example.id] = pack
        full_logits = full_prefill_logits(loaded.model, pack, loaded.device)
        sequential_logits = run_sequential_prefill_logits(loaded.model, pack, loaded.device)
        full_logits_by_id[example.id] = full_logits
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

    sequential_path = args.results_dir / "sequential_prefill_sanity.jsonl"
    write_jsonl(sequential_path, sequential_rows)
    seq_summary = sequential_summary(sequential_rows)
    seq_summary_path = args.results_dir / "sequential_prefill_sanity_summary.json"
    seq_summary_path.write_text(
        json.dumps(seq_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if not seq_summary["passed"]:
        print(json.dumps(seq_summary, indent=2, ensure_ascii=False))
        raise SystemExit("Sequential prefill sanity failed; aborting naive composition.")

    all_naive_rows = []
    failed_examples: list[dict[str, str]] = []
    specs = select_composition_method_specs(config.experiment.methods)
    method_to_path = {
        spec["method"]: args.results_dir / f"{spec['method']}_outputs.jsonl"
        for spec in specs
    }
    method_rows = {method: [] for method in method_to_path}
    for example in examples:
        pack = packs_by_id[example.id]
        reference_logits = reference_logits_for_example(
            current_logits=full_logits_by_id[example.id],
            use_sidecar_reference=args.use_sidecar_reference,
            results_dir=args.results_dir,
            example_id=example.id,
            pack=pack,
        )
        for spec in specs:
            method = str(spec["method"])
            try:
                method_logits, cache_metadata = run_naive_composed_logits(
                    loaded.model,
                    pack,
                    loaded.device,
                    position_mode=str(spec["position_mode"]),
                    includes_prefix_cache=bool(spec["includes_prefix_cache"]),
                    doc_conditioning=str(spec["doc_conditioning"]),
                )
                row = make_metric_row(
                    example=example,
                    method=method,
                    pack=pack,
                    full_logits=reference_logits,
                    method_logits=method_logits,
                    tokenizer=loaded.tokenizer,
                    composed_context_length=int(cache_metadata["composed_context_length"]),
                )
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
                row["cache_summary"] = cache_metadata
                method_rows[method].append(row)
                all_naive_rows.append(row)
            except Exception as exc:  # pragma: no cover - exercised by real smoke failures
                failed_examples.append(
                    {"example_id": example.id, "method": method, "error": repr(exc)}
                )

    for method, path in method_to_path.items():
        write_jsonl(path, method_rows[method])
    alias_paths = {
        "naive_global": args.results_dir / "naive_global_outputs.jsonl",
        "naive_local": args.results_dir / "naive_local_outputs.jsonl",
    }
    if "doc_only_naive_global" in method_rows:
        write_jsonl(alias_paths["naive_global"], method_rows["doc_only_naive_global"])
    if "doc_only_naive_local" in method_rows:
        write_jsonl(alias_paths["naive_local"], method_rows["doc_only_naive_local"])

    metrics_csv_path = args.results_dir / "composition_metrics.csv"
    write_composition_metrics_csv(metrics_csv_path, all_naive_rows)
    failure_analysis_path = args.results_dir / "composition_failure_analysis.md"
    write_composition_failure_analysis(failure_analysis_path, all_naive_rows)

    summary = summarize_rows(all_naive_rows, failed_examples)
    summary["sequential_prefill_sanity"] = seq_summary
    summary["reference_source"] = (
        "sidecar_full_prefill_logits" if args.use_sidecar_reference else "current_run_full_logits"
    )
    summary["selected_methods"] = [str(spec["method"]) for spec in specs]
    summary["outputs"] = {
        "sequential_prefill_sanity": str(sequential_path),
        "sequential_prefill_sanity_summary": str(seq_summary_path),
        **{method: str(path) for method, path in method_to_path.items()},
        "composition_metrics_csv": str(metrics_csv_path),
        "composition_failure_analysis": str(failure_analysis_path),
    }
    if "doc_only_naive_global" in method_rows:
        summary["outputs"]["naive_global_alias"] = str(alias_paths["naive_global"])
    if "doc_only_naive_local" in method_rows:
        summary["outputs"]["naive_local_alias"] = str(alias_paths["naive_local"])
    summary_path = args.results_dir / "naive_composition_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
