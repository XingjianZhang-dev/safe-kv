#!/usr/bin/env python
"""Evaluate observed answer-equivalent executable suffix starts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import answer_equivalent  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.full_prefill import (  # noqa: E402
    load_examples_for_config,
    set_deterministic_seed,
)
from safekv.metrics import logit_preservation_metrics  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import token_count  # noqa: E402
from scripts.run_answer_eval import (  # noqa: E402
    assert_answer_execution_snapshot_unchanged,
    capture_answer_execution_snapshot,
    patch_ranges_for_answer_method,
    recompute_answer_suffix,
    require_fixed_python_hash_seed,
    runtime_provenance,
    run_base_answer_state,
    run_full_prefill_answer_state,
    run_query_and_generate_from_context_cache,
    tokenizer_sha256,
)


SELECTOR_POLICIES = [
    "query_similarity_suffix_closure_k1",
    "query_similarity_suffix_closure_k2",
    "risk_guided_suffix_closure_k1",
    "risk_guided_suffix_closure_k2",
    "hybrid_query_risk_union_suffix_k1",
]

EQUIVALENCE_SPECS = [
    (
        "normalized_qa_equivalent",
        "observed_latest_normalized_qa_equivalent_start",
        "observed_min_normalized_qa_equivalent_patch_ratio",
        "normalized_qa_equivalent_start_monotonicity_violation",
    ),
    (
        "raw_trimmed_answer_exact",
        "observed_latest_raw_trimmed_exact_start",
        "observed_min_raw_trimmed_exact_patch_ratio",
        "raw_trimmed_exact_start_monotonicity_violation",
    ),
    (
        "generated_token_sequence_exact",
        "observed_latest_generated_token_sequence_exact_start",
        "observed_min_generated_token_sequence_exact_patch_ratio",
        "generated_token_sequence_exact_start_monotonicity_violation",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--data-path", type=str, default=None)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument(
        "--summarize-only",
        action="store_true",
        help="recompute summaries from an existing frontier_outputs.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require_fixed_python_hash_seed()
    if args.start_index < 0:
        raise ValueError("--start-index must be non-negative")
    config_path = args.config.resolve()
    config = load_config(args.config)
    if args.data_path is not None:
        config = replace(config, data=replace(config.data, path=args.data_path))
    if config.generation.do_sample or config.generation.temperature != 0.0:
        raise ValueError("frontier evaluation requires deterministic decoding")
    config_dir = args.config.resolve().parent.parent
    data_path = Path(config.data.path)
    if not data_path.is_absolute():
        data_path = (config_dir / data_path).resolve()
    else:
        data_path = data_path.resolve()
    execution_snapshot = capture_answer_execution_snapshot(
        config_path=config_path,
        data_path=data_path,
        selector_path=None,
    )
    set_deterministic_seed(config.seed)
    examples = load_examples_for_config(config, config_dir=config_dir)
    examples = examples[args.start_index :]
    if args.max_examples is not None:
        examples = examples[: args.max_examples]

    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / "frontier_outputs.jsonl"
    if args.summarize_only:
        if not output_path.exists():
            raise FileNotFoundError(output_path)
        rows = [
            json.loads(line)
            for line in output_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        loaded = load_causal_lm(config.model)
        assert_answer_execution_snapshot_unchanged(
            execution_snapshot,
            config_path=config_path,
            data_path=data_path,
            selector_path=None,
            results_dir=args.results_dir,
            stage="after_model_load",
        )
        manifest = {
            "schema_version": 1,
            "config_path": execution_snapshot["config_path"],
            "config_sha256": execution_snapshot["config_sha256"],
            "data_path": execution_snapshot["data_path"],
            "data_sha256": execution_snapshot["data_sha256"],
            "implementation_sha256": execution_snapshot["implementation_sha256"],
            "model_name": config.model.name,
            "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
            "tokenizer_sha256": tokenizer_sha256(loaded.tokenizer),
            "model_dtype": config.model.dtype,
            "resolved_torch_dtype": loaded.torch_dtype_name,
            "actual_device": loaded.device,
            "attention_implementation": getattr(
                loaded.model.config, "_attn_implementation", None
            ),
            "runtime": runtime_provenance(loaded),
            "seed": config.seed,
            "random_seed": args.random_seed,
            "start_index": args.start_index,
            "max_examples": args.max_examples,
            "selector_policies": SELECTOR_POLICIES,
            "risk_weights": config.risk.weights,
        }
        (args.results_dir / "frontier_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        rows: list[dict[str, Any]] = []
        with output_path.open("w", encoding="utf-8") as handle:
            for example in examples:
                row = evaluate_example(example, loaded, config, args.random_seed)
                rows.append(row)
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
        assert_answer_execution_snapshot_unchanged(
            execution_snapshot,
            config_path=config_path,
            data_path=data_path,
            selector_path=None,
            results_dir=args.results_dir,
            stage="after_evaluation",
        )

    rows = [normalize_frontier_row(row) for row in rows]
    selector_rows = selector_metric_rows(rows)
    write_csv(args.results_dir / "selector_frontier_metrics.csv", selector_rows)
    summary = {
        "schema_version": 2,
        "model_name": config.model.name,
        "config_path": str(args.config.resolve()),
        "model_dtype": config.model.dtype,
        "model_device": config.model.device,
        "prompt_format": config.experiment.prompt_format,
        "random_seed": args.random_seed,
        "dataset_path": str(data_path),
        "dataset_sha256": execution_snapshot["data_sha256"],
        "start_index": args.start_index,
        "num_examples": len(rows),
        "equivalence_definitions": {
            "normalized_qa_equivalent": (
                "SQuAD-style normalized exact match; case, punctuation, and articles "
                "are ignored"
            ),
            "raw_trimmed_answer_exact": "exact equality of the decoded, trimmed answer strings",
            "generated_token_sequence_exact": "exact equality of generated token-id sequences",
        },
        "prefix_normalized_qa_equivalence": mean(
            float(row["prefix_normalized_qa_equivalent"]) for row in rows
        ),
        "prefix_raw_trimmed_answer_exact_match_rate": mean(
            float(row["prefix_raw_trimmed_answer_exact"]) for row in rows
        ),
        "prefix_generated_token_sequence_exact_match_rate": optional_bool_mean(
            row.get("prefix_generated_token_sequence_exact") for row in rows
        ),
        "generated_token_sequence_exact_available_examples": sum(
            row.get("prefix_generated_token_sequence_exact") is not None for row in rows
        ),
        "observed_normalized_qa_equivalent_frontier_available_examples": sum(
            row["observed_latest_normalized_qa_equivalent_start"] is not None for row in rows
        ),
        "observed_raw_trimmed_exact_frontier_available_examples": sum(
            row["observed_latest_raw_trimmed_exact_start"] is not None for row in rows
        ),
        "observed_generated_token_sequence_exact_frontier_available_examples": sum(
            row["observed_latest_generated_token_sequence_exact_start"] is not None
            for row in rows
        ),
        "observed_latest_normalized_qa_equivalent_start_distribution": dict(
            sorted(
                counts(
                    row["observed_latest_normalized_qa_equivalent_start"]
                    for row in rows
                    if row["observed_latest_normalized_qa_equivalent_start"] is not None
                ).items()
            )
        ),
        "observed_latest_raw_trimmed_exact_start_distribution": dict(
            sorted(
                counts(
                    row["observed_latest_raw_trimmed_exact_start"]
                    for row in rows
                    if row["observed_latest_raw_trimmed_exact_start"] is not None
                ).items()
            )
        ),
        "observed_latest_generated_token_sequence_exact_start_distribution": dict(
            sorted(
                counts(
                    row["observed_latest_generated_token_sequence_exact_start"]
                    for row in rows
                    if row["observed_latest_generated_token_sequence_exact_start"] is not None
                ).items()
            )
        ),
        "observed_avg_min_normalized_qa_equivalent_patch_ratio": optional_float_mean(
            row["observed_min_normalized_qa_equivalent_patch_ratio"] for row in rows
        ),
        "observed_avg_min_raw_trimmed_exact_patch_ratio": optional_float_mean(
            row["observed_min_raw_trimmed_exact_patch_ratio"] for row in rows
        ),
        "observed_avg_min_generated_token_sequence_exact_patch_ratio": optional_float_mean(
            row["observed_min_generated_token_sequence_exact_patch_ratio"] for row in rows
        ),
        "normalized_qa_equivalent_start_monotonicity_violation_rate": optional_bool_mean(
            row["normalized_qa_equivalent_start_monotonicity_violation"] for row in rows
        ),
        "raw_trimmed_exact_start_monotonicity_violation_rate": optional_bool_mean(
            row["raw_trimmed_exact_start_monotonicity_violation"] for row in rows
        ),
        "generated_token_sequence_exact_start_monotonicity_violation_rate": optional_bool_mean(
            row["generated_token_sequence_exact_start_monotonicity_violation"]
            for row in rows
        ),
        "selector_metrics": selector_rows,
        "outputs": str(output_path),
    }
    (args.results_dir / "frontier_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


def evaluate_example(example: Any, loaded: Any, config: Any, seed: int) -> dict[str, Any]:
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
    composed_len = int(base_state["cache_metadata"]["composed_context_length"])
    full_answer = full_state["generated_answer"]
    prefix_answer = base_state["generated_answer"]

    starts: list[dict[str, Any]] = []
    for start in range(len(example.documents)):
        ranges = list(pack.doc_ranges[start:])
        context_cache = recompute_answer_suffix(
            pack=pack,
            loaded=loaded,
            base_cache=base_state["context_cache"],
            patch_ranges=ranges,
        )
        query_state = run_query_and_generate_from_context_cache(
            loaded=loaded,
            config=config,
            pack=pack,
            context_cache=context_cache,
        )
        metrics = logit_preservation_metrics(
            full_state["first_logits"],
            query_state["first_logits"],
            loaded.tokenizer,
        )
        starts.append(
            {
                "start": start,
                "answer": query_state["generated_answer"],
                "generated_token_ids": query_state["generated_token_ids"],
                "patch_ratio": token_count(ranges) / composed_len if composed_len else 0.0,
                "first_token_kl": metrics["first_token_kl_full_to_method"],
            }
        )

    no_repair = {
        "start": len(example.documents),
        "answer": prefix_answer,
        "generated_token_ids": base_state["generated_token_ids"],
        "patch_ratio": 0.0,
        "first_token_kl": base_state["logit_metrics"]["first_token_kl_full_to_method"],
    }

    selector_results: dict[str, Any] = {}
    starts_by_index = {
        int(item["start"]): item
        for item in starts + [no_repair]
    }
    ordered_ids = [doc.doc_id for doc in example.documents]
    for policy in SELECTOR_POLICIES:
        ranges, selected_ids = patch_ranges_for_answer_method(
            method=policy,
            example=example,
            pack=pack,
            seed=seed,
            risk_weights=config.risk.weights,
        )
        selected_positions = [
            position for position, doc_id in enumerate(ordered_ids) if doc_id in set(selected_ids)
        ]
        start = min(selected_positions) if selected_positions else len(example.documents)
        result = starts_by_index[start]
        selector_results[policy] = {
            "selected_doc_ids": selected_ids,
            "start": start,
            "patch_ratio": token_count(ranges) / composed_len if composed_len else 0.0,
            "first_token_kl": result["first_token_kl"],
        }

    return normalize_frontier_row({
        "example_id": example.id,
        "category": example.category,
        "num_documents": len(example.documents),
        "prompt_length": len(pack.full_input_ids),
        "full_prefill_answer": full_answer,
        "full_prefill_token_ids": full_state["generated_token_ids"],
        "prefix_answer": prefix_answer,
        "prefix_generated_token_ids": base_state["generated_token_ids"],
        "suffix_starts": starts,
        "no_repair": no_repair,
        "selector_results": selector_results,
    })


def normalize_frontier_row(row: dict[str, Any]) -> dict[str, Any]:
    """Upgrade old answer-only rows and derive all observed equivalence frontiers."""

    migrated = dict(row)
    migrated["frontier_schema_version"] = 2
    full_answer = str(row["full_prefill_answer"])
    full_token_ids = row.get("full_prefill_token_ids")
    normalized_starts = [
        normalize_start_item(item, full_answer, full_token_ids)
        for item in row.get("suffix_starts", [])
    ]

    no_repair_source = row.get("no_repair")
    if no_repair_source is None:
        no_repair_source = {
            "start": int(row["num_documents"]),
            "answer": row["prefix_answer"],
            "generated_token_ids": row.get("prefix_generated_token_ids"),
            "patch_ratio": 0.0,
            "first_token_kl": row.get("prefix_first_token_kl"),
            "answer_equivalent": row.get("prefix_answer_equivalent"),
        }
    normalized_no_repair = normalize_start_item(
        no_repair_source,
        full_answer,
        full_token_ids,
    )
    all_starts = normalized_starts + [normalized_no_repair]
    starts_by_index = {int(item["start"]): item for item in all_starts}

    observed_frontiers: dict[str, dict[str, Any] | None] = {}
    for metric, start_key, ratio_key, violation_key in EQUIVALENCE_SPECS:
        observed = latest_matching_start(all_starts, metric)
        observed_frontiers[metric] = observed
        migrated[start_key] = int(observed["start"]) if observed is not None else None
        migrated[ratio_key] = float(observed["patch_ratio"]) if observed is not None else None
        migrated[violation_key] = start_monotonicity_violation(all_starts, metric)

    migrated["prefix_normalized_qa_equivalent"] = normalized_no_repair[
        "normalized_qa_equivalent"
    ]
    migrated["prefix_raw_trimmed_answer_exact"] = normalized_no_repair[
        "raw_trimmed_answer_exact"
    ]
    migrated["prefix_generated_token_sequence_exact"] = normalized_no_repair[
        "generated_token_sequence_exact"
    ]
    migrated["suffix_starts"] = normalized_starts
    migrated["no_repair"] = normalized_no_repair

    normalized_selector_results: dict[str, Any] = {}
    for policy, source in row.get("selector_results", {}).items():
        item = dict(source)
        result = starts_by_index[int(item["start"])]
        for metric, start_key, _ratio_key, _violation_key in EQUIVALENCE_SPECS:
            value = result[metric]
            observed = observed_frontiers[metric]
            item[metric] = value
            item[f"{metric}_and_not_later_than_observed_latest_start"] = (
                None
                if value is None or observed is None
                else bool(value and int(item["start"]) <= int(observed["start"]))
            )
            item[f"{metric}_patch_excess_vs_observed_min"] = (
                float(item["patch_ratio"]) - float(observed["patch_ratio"])
                if value is True and observed is not None
                else None
            )
        for old_key in (
            "answer_equivalent",
            "conservative_vs_oracle",
            "safe_and_not_later_than_observed_frontier",
            "safe_patch_excess_vs_oracle",
        ):
            item.pop(old_key, None)
        normalized_selector_results[policy] = item
    migrated["selector_results"] = normalized_selector_results

    for old_key in (
        "prefix_answer_equivalent",
        "oracle_latest_safe_start",
        "oracle_min_patch_ratio",
        "safe_start_monotonicity_violation",
    ):
        migrated.pop(old_key, None)
    return migrated


def normalize_start_item(
    source: dict[str, Any],
    full_answer: str,
    full_token_ids: Any,
) -> dict[str, Any]:
    item = dict(source)
    answer = str(item["answer"])
    normalized = item.get("normalized_qa_equivalent")
    if normalized is None:
        normalized = item.get("answer_equivalent")
    if normalized is None:
        normalized = answer_equivalent(answer, full_answer)

    token_exact = item.get("generated_token_sequence_exact")
    generated_token_ids = item.get("generated_token_ids")
    if token_exact is None and generated_token_ids is not None and full_token_ids is not None:
        token_exact = list(generated_token_ids) == list(full_token_ids)

    item["normalized_qa_equivalent"] = bool(normalized)
    item["raw_trimmed_answer_exact"] = bool(
        item.get("raw_trimmed_answer_exact", answer == full_answer)
    )
    item["generated_token_sequence_exact"] = (
        bool(token_exact) if token_exact is not None else None
    )
    item.pop("answer_equivalent", None)
    return item


def latest_matching_start(
    items: list[dict[str, Any]],
    metric: str,
) -> dict[str, Any] | None:
    matching = [item for item in items if item.get(metric) is True]
    return max(matching, key=lambda item: int(item["start"])) if matching else None


def start_monotonicity_violation(
    items: list[dict[str, Any]],
    metric: str,
) -> bool | None:
    if any(item.get(metric) is None for item in items):
        return None
    matching_indices = {
        int(item["start"])
        for item in items
        if item.get(metric) is True
    }
    ordered_indices = sorted(int(item["start"]) for item in items)
    return any(
        later in matching_indices and earlier not in matching_indices
        for later in ordered_indices
        for earlier in ordered_indices
        if earlier < later
    )


def selector_metric_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for policy in SELECTOR_POLICIES:
        items = [row["selector_results"][policy] for row in rows]
        summary: dict[str, Any] = {
            "method": policy,
            "num_examples": len(items),
            "avg_start": mean(float(item["start"]) for item in items),
            "avg_patch_ratio": mean(float(item["patch_ratio"]) for item in items),
        }
        for metric, _start_key, _ratio_key, _violation_key in EQUIVALENCE_SPECS:
            values = [item.get(metric) for item in items]
            excess_key = f"{metric}_patch_excess_vs_observed_min"
            order_key = f"{metric}_and_not_later_than_observed_latest_start"
            summary[f"{metric}_available_examples"] = sum(value is not None for value in values)
            summary[f"{metric}_rate"] = optional_bool_mean(values)
            successes = sum(value is True for value in values)
            available = sum(value is not None for value in values)
            ci_low, ci_high = wilson_interval(successes, available)
            summary[f"{metric}_wilson_ci95_low"] = ci_low
            summary[f"{metric}_wilson_ci95_high"] = ci_high
            summary[f"{metric}_mismatch_rate"] = optional_bool_mean(
                None if value is None else not value for value in values
            )
            summary[f"{metric}_and_not_later_than_observed_latest_start_rate"] = (
                optional_bool_mean(item.get(order_key) for item in items)
            )
            summary[f"avg_{metric}_patch_excess_vs_observed_min"] = optional_float_mean(
                item.get(excess_key) for item in items
            )
            summary[f"{metric}_patch_excess_available_examples"] = sum(
                item.get(excess_key) is not None for item in items
            )
        output.append(summary)
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean(values: Any) -> float:
    materialized = list(values)
    return statistics.fmean(materialized) if materialized else 0.0


def optional_bool_mean(values: Any) -> float | None:
    materialized = [bool(value) for value in values if value is not None]
    return statistics.fmean(float(value) for value in materialized) if materialized else None


def optional_float_mean(values: Any) -> float | None:
    materialized = [float(value) for value in values if value is not None]
    return statistics.fmean(materialized) if materialized else None


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if total <= 0:
        return (None, None)
    probability = successes / total
    denominator = 1.0 + (z * z / total)
    center = (probability + z * z / (2.0 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            probability * (1.0 - probability) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return (max(0.0, center - half_width), min(1.0, center + half_width))


def counts(values: Any) -> dict[int, int]:
    result: dict[int, int] = {}
    for value in values:
        resolved = int(value)
        result[resolved] = result.get(resolved, 0) + 1
    return result


if __name__ == "__main__":
    main()
