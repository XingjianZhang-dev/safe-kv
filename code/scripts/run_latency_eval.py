#!/usr/bin/env python
"""Measure first-token latency and peak CUDA memory for SAFE-KV paths."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.cache_ops import cache_seq_len, legacy_cache_to_model_cache, slice_legacy_cache, to_legacy_cache  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.doc_selector import document_ranges_for_ids, random_doc_ids_same_count, selected_doc_ids_for_method  # noqa: E402
from safekv.data_schema import TokenRange  # noqa: E402
from safekv.full_prefill import load_examples_for_config, select_examples_per_category, set_deterministic_seed  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_naive_composed_context_cache, build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import merge_token_ranges, oracle_evidence_doc_patch_ranges, replace_cache_slices, stable_example_seed, token_count  # noqa: E402


CSV_FIELDS = [
    "example_id",
    "category",
    "method",
    "prompt_length",
    "context_cache_length",
    "query_length",
    "patched_token_count",
    "patched_token_ratio",
    "wall_time_s",
    "peak_cuda_memory_mb",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=Path("results/latency_eval"))
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--max-examples-per-category", type=int, default=None)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--data-path", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.data_path is not None:
        config = replace(config, data=replace(config.data, path=args.data_path))
    config_dir = args.config.resolve().parent.parent
    set_deterministic_seed(config.seed)

    examples = load_examples_for_config(config, config_dir=config_dir)
    if args.max_examples_per_category is not None:
        examples = select_examples_per_category(examples, args.max_examples_per_category)
    if args.max_examples is not None:
        examples = examples[: args.max_examples]

    loaded = load_causal_lm(config.model)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    for example in examples:
        pack = build_prompt_pack_for_config(example, loaded, config)
        full_timing, full_state = timed_call(
            lambda: full_prefill_first_token(example, pack, loaded),
            device=loaded.device,
        )
        rows.append(
            row_for_timing(
                example=example,
                pack=pack,
                method="full_prefill_forward",
                timing=full_timing,
                context_cache_length=0,
                patched_token_count=0,
                patched_token_ratio=0.0,
            )
        )

        compose_timing, base_cache = timed_call(
            lambda: build_prefix_conditioned_cache(pack, loaded),
            device=loaded.device,
        )
        rows.append(
            row_for_timing(
                example=example,
                pack=pack,
                method="prefix_conditioned_context_build",
                timing=compose_timing,
                context_cache_length=cache_seq_len(base_cache),
                patched_token_count=0,
                patched_token_ratio=0.0,
            )
        )

        query_timing, _ = timed_call(
            lambda: query_first_token(pack, loaded, base_cache),
            device=loaded.device,
        )
        rows.append(
            row_for_timing(
                example=example,
                pack=pack,
                method="prefix_conditioned_query_forward",
                timing=query_timing,
                context_cache_length=cache_seq_len(base_cache),
                patched_token_count=0,
                patched_token_ratio=0.0,
            )
        )

        full_cache = full_state["full_cache"]
        for method, ranges in {
            "oracle_doc_patch": oracle_evidence_doc_patch_ranges(example, pack),
            "random_k2_patch": document_ranges_for_ids(
                example,
                pack,
                random_doc_ids_same_count(
                    example,
                    count=2,
                    seed=stable_example_seed(args.random_seed, example.id, "latency_random_k2"),
                ),
            ),
        }.items():
            patched_tokens = token_count(ranges)
            ratio = patched_tokens / cache_seq_len(base_cache) if cache_seq_len(base_cache) else 0.0
            patch_timing, patched_cache = timed_call(
                lambda ranges=ranges: replace_cache_slices(base_cache, full_cache, ranges),
                device=loaded.device,
            )
            rows.append(
                row_for_timing(
                    example=example,
                    pack=pack,
                    method=f"{method}_replace",
                    timing=patch_timing,
                    context_cache_length=cache_seq_len(patched_cache),
                    patched_token_count=patched_tokens,
                    patched_token_ratio=ratio,
                )
            )
            patched_query_timing, _ = timed_call(
                lambda patched_cache=patched_cache: query_first_token(pack, loaded, patched_cache),
                device=loaded.device,
            )
            rows.append(
                row_for_timing(
                    example=example,
                    pack=pack,
                    method=f"{method}_query_forward",
                    timing=patched_query_timing,
                    context_cache_length=cache_seq_len(patched_cache),
                    patched_token_count=patched_tokens,
                    patched_token_ratio=ratio,
                )
            )

        for method, ranges in suffix_latency_ranges(example, pack, args.random_seed).items():
            patched_tokens = token_count(ranges)
            ratio = patched_tokens / cache_seq_len(base_cache) if cache_seq_len(base_cache) else 0.0
            suffix_timing, _ = timed_call(
                lambda ranges=ranges: suffix_recompute_and_query(pack, loaded, base_cache, ranges),
                device=loaded.device,
            )
            rows.append(
                row_for_timing(
                    example=example,
                    pack=pack,
                    method=f"{method}_recompute_plus_query",
                    timing=suffix_timing,
                    context_cache_length=cache_seq_len(base_cache),
                    patched_token_count=patched_tokens,
                    patched_token_ratio=ratio,
                )
            )

    metrics_path = args.results_dir / "latency_metrics.csv"
    summary_path = args.results_dir / "latency_summary.json"
    write_csv(metrics_path, rows)
    summary = summarize(rows)
    summary["config_path"] = str(args.config)
    summary["dataset_path"] = config.data.path
    summary["model_name"] = config.model.name
    summary["num_examples"] = len(examples)
    summary["metrics_csv"] = str(metrics_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def full_prefill_first_token(example: Any, pack: Any, loaded: Any) -> dict[str, Any]:
    import torch

    _ = example
    input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=loaded.device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(input_ids.shape[1], dtype=torch.long, device=loaded.device).unsqueeze(0)
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
            # TTFT needs only the final prompt-position logits.  Qwen2's
            # default (0) projects every hidden state through the vocabulary
            # head, which unfairly charges longer full-prefill inputs.
            logits_to_keep=1,
        )
    return {"first_logits": outputs.logits[:, -1, :], "full_cache": to_legacy_cache(outputs.past_key_values)}


def build_prefix_conditioned_cache(pack: Any, loaded: Any) -> Any:
    cache, _metadata = build_naive_composed_context_cache(
        loaded.model,
        pack,
        loaded.device,
        position_mode="global",
        includes_prefix_cache=True,
        doc_conditioning="prefix",
    )
    return cache


def query_first_token(pack: Any, loaded: Any, context_cache: Any) -> Any:
    import torch

    query_range = pack.query_token_range
    query_ids = torch.tensor(
        [pack.full_input_ids[query_range.start : query_range.end]],
        dtype=torch.long,
        device=loaded.device,
    )
    query_position_ids = torch.arange(
        query_range.start,
        query_range.end,
        dtype=torch.long,
        device=loaded.device,
    ).unsqueeze(0)
    attention_mask = torch.ones(
        (1, cache_seq_len(context_cache) + query_ids.shape[1]),
        dtype=torch.long,
        device=loaded.device,
    )
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=query_ids,
            attention_mask=attention_mask,
            position_ids=query_position_ids,
            past_key_values=legacy_cache_to_model_cache(context_cache),
            use_cache=True,
            logits_to_keep=1,
        )
    # Keep the generation-ready cache alive through the end of the timed call,
    # matching ``full_prefill_first_token``.  Returning logits alone would let
    # Python release the query cache before the timer stops and make the two
    # paths measure different output lifetimes.
    return {
        "first_logits": outputs.logits[:, -1, :],
        "full_cache": to_legacy_cache(outputs.past_key_values),
    }


def suffix_latency_ranges(example: Any, pack: Any, seed: int) -> dict[str, list[TokenRange]]:
    query_k1 = selected_doc_ids_for_method(
        "query_similarity_doc_patch_k1",
        example,
        seed=seed,
    )[0]
    risk_k1 = selected_doc_ids_for_method(
        "risk_guided_doc_patch_k1",
        example,
        seed=seed,
    )[0]
    methods = {
        "query_suffix_k1": query_k1,
        "query_suffix_k2": selected_doc_ids_for_method(
            "query_similarity_doc_patch_k2",
            example,
            seed=seed,
        )[0],
        "risk_suffix_k1": risk_k1,
        "hybrid_query_risk_union_suffix_k1": sorted(set(query_k1) | set(risk_k1)),
        "risk_suffix_k2": selected_doc_ids_for_method(
            "risk_guided_doc_patch_k2",
            example,
            seed=seed,
        )[0],
        "random_suffix_k1": random_doc_ids_same_count(
            example,
            count=1,
            seed=stable_example_seed(seed, example.id, "latency_random_suffix_k1"),
        ),
        "random_suffix_k2": random_doc_ids_same_count(
            example,
            count=2,
            seed=stable_example_seed(seed, example.id, "latency_random_suffix_k2"),
        ),
    }
    return {
        method: contiguous_suffix_range(example, pack, selected_doc_ids)
        for method, selected_doc_ids in methods.items()
    }


def contiguous_suffix_range(
    example: Any,
    pack: Any,
    selected_doc_ids: list[int],
) -> list[TokenRange]:
    selected = set(selected_doc_ids)
    if not selected:
        return []
    ordered_ids = [doc.doc_id for doc in example.documents]
    earliest_index = min(index for index, doc_id in enumerate(ordered_ids) if doc_id in selected)
    suffix_doc_ids = set(ordered_ids[earliest_index:])
    ranges = document_ranges_for_ids(example, pack, suffix_doc_ids)
    merged = merge_token_ranges(ranges)
    if not merged:
        return []
    return [TokenRange(merged[0].start, merged[-1].end)]


def suffix_recompute_and_query(
    pack: Any,
    loaded: Any,
    base_cache: Any,
    ranges: list[TokenRange],
) -> Any:
    if not ranges:
        return query_first_token(pack, loaded, base_cache)
    if len(ranges) != 1:
        raise ValueError("suffix recompute latency expects one contiguous range")
    patched_cache = recompute_contiguous_range(pack, loaded, base_cache, ranges[0])
    return query_first_token(pack, loaded, patched_cache)


def recompute_contiguous_range(
    pack: Any,
    loaded: Any,
    base_cache: Any,
    token_range: TokenRange,
) -> Any:
    import torch

    prefix_cache = slice_legacy_cache(base_cache, 0, token_range.start)
    input_ids = torch.tensor(
        [pack.full_input_ids[token_range.start : token_range.end]],
        dtype=torch.long,
        device=loaded.device,
    )
    position_ids = torch.arange(
        token_range.start,
        token_range.end,
        dtype=torch.long,
        device=loaded.device,
    ).unsqueeze(0)
    attention_mask = torch.ones(
        (1, token_range.end),
        dtype=torch.long,
        device=loaded.device,
    )
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=legacy_cache_to_model_cache(prefix_cache),
            use_cache=True,
            # The repair forward consumes only the returned KV cache.
            logits_to_keep=1,
        )
    donor_cache = to_legacy_cache(outputs.past_key_values)
    return replace_cache_slices(base_cache, donor_cache, [token_range])


def timed_call(fn: Callable[[], Any], *, device: str) -> tuple[dict[str, float | None], Any]:
    import torch

    baseline_mb = None
    if device == "cuda":
        torch.cuda.synchronize()
        baseline_mb = torch.cuda.memory_allocated() / (1024 * 1024)
        torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    value = fn()
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    peak_mb = None
    incremental_peak_mb = None
    if device == "cuda":
        peak_mb = torch.cuda.max_memory_allocated() / (1024 * 1024)
        incremental_peak_mb = max(0.0, peak_mb - float(baseline_mb or 0.0))
    return {
        "wall_time_s": elapsed,
        "baseline_cuda_memory_mb": baseline_mb,
        "peak_cuda_memory_mb": peak_mb,
        "incremental_peak_cuda_memory_mb": incremental_peak_mb,
    }, value


def row_for_timing(
    *,
    example: Any,
    pack: Any,
    method: str,
    timing: dict[str, float | None],
    context_cache_length: int,
    patched_token_count: int,
    patched_token_ratio: float,
) -> dict[str, Any]:
    return {
        "example_id": example.id,
        "category": example.category,
        "method": method,
        "prompt_length": len(pack.full_input_ids),
        "context_cache_length": context_cache_length,
        "query_length": pack.query_token_range.length,
        "patched_token_count": patched_token_count,
        "patched_token_ratio": patched_token_ratio,
        "wall_time_s": timing["wall_time_s"],
        "peak_cuda_memory_mb": timing["peak_cuda_memory_mb"],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["method"], []).append(row)
    return {
        "method_level": {
            method: {
                "n": len(items),
                "avg_wall_time_s": mean(float(item["wall_time_s"]) for item in items),
                "median_wall_time_s": percentile(
                    [float(item["wall_time_s"]) for item in items],
                    0.50,
                ),
                "p95_wall_time_s": percentile(
                    [float(item["wall_time_s"]) for item in items],
                    0.95,
                ),
                "avg_peak_cuda_memory_mb": mean(
                    float(item["peak_cuda_memory_mb"] or 0.0) for item in items
                ),
                "avg_patched_token_ratio": mean(float(item["patched_token_ratio"]) for item in items),
                "avg_prompt_length": mean(float(item["prompt_length"]) for item in items),
                "avg_context_cache_length": mean(
                    float(item["context_cache_length"]) for item in items
                ),
            }
            for method, items in sorted(grouped.items())
        }
    }


def mean(values: Any) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


if __name__ == "__main__":
    main()
