#!/usr/bin/env python
"""Warm repeated L40S time-to-first-logit under an existing-cache assumption."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl  # noqa: E402
from safekv.cache_ops import cache_seq_len  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.doc_selector import selected_doc_ids_for_method  # noqa: E402
from safekv.full_prefill import set_deterministic_seed  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from scripts.run_latency_eval import (  # noqa: E402
    build_prefix_conditioned_cache,
    contiguous_suffix_range,
    full_prefill_first_token,
    query_first_token,
    suffix_latency_ranges,
    suffix_recompute_and_query,
    timed_call,
)


TIMED_METHODS = [
    "full_prefill",
    "prefix_query",
    "query_suffix_k1",
    "risk_suffix_k1",
    "hybrid_query_risk_union_suffix_k1",
    "risk_suffix_k2",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmup-examples", type=int, default=3)
    parser.add_argument("--random-seed", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise ValueError(
            "latency evaluation requires PYTHONHASHSEED=0 to pin process-level "
            "hash iteration; set it before launching Python"
        )
    if args.max_examples <= 0 or args.repeats <= 0 or args.warmup_examples < 0:
        raise ValueError("max-examples/repeats must be positive and warmup-examples nonnegative")
    config_path = args.config.resolve()
    startup_config_sha256 = file_sha256(config_path)
    startup_implementation_sha256 = latency_implementation_hashes()
    config = load_config(args.config)
    if (
        file_sha256(config_path) != startup_config_sha256
        or latency_implementation_hashes() != startup_implementation_sha256
    ):
        raise RuntimeError(
            "config or implementation changed while initializing latency evaluation; "
            "rerun from a stable source tree"
        )
    config_dir = config_path.parent.parent
    data_path = (
        args.data_path if args.data_path.is_absolute() else config_dir / args.data_path
    ).resolve()
    start_provenance = {
        "config_sha256": startup_config_sha256,
        "data_sha256": file_sha256(data_path),
        "implementation_sha256": startup_implementation_sha256,
    }
    examples = read_jsonl(data_path)[: args.max_examples]
    if not examples:
        raise ValueError(f"no examples loaded from {data_path}")
    assert_latency_source_provenance_unchanged(
        start_provenance,
        config_path=config_path,
        data_path=data_path,
        results_dir=args.results_dir,
        stage="after_input_load",
    )
    set_deterministic_seed(config.seed)
    loaded = load_causal_lm(config.model)
    assert_latency_source_provenance_unchanged(
        start_provenance,
        config_path=config_path,
        data_path=data_path,
        results_dir=args.results_dir,
        stage="after_model_load",
    )

    cache_build_rows = []

    # Warm each path without retaining a pool of per-example KV caches.  Keeping
    # every cache resident inflates later peak-memory measurements and is not a
    # batch-1 request trace.
    for example in examples[: args.warmup_examples]:
        pack = build_prompt_pack_for_config(example, loaded, config)
        _timing, base_cache = timed_call(
            lambda pack=pack: build_prefix_conditioned_cache(pack, loaded),
            device=loaded.device,
        )
        calls = timed_calls_for_example(
            example=example,
            pack=pack,
            base_cache=base_cache,
            loaded=loaded,
            random_seed=args.random_seed,
        )
        for call in calls.values():
            _timing, value = timed_call(call, device=loaded.device)
            validate_generation_ready_value(value, pack)
            del value
            release_request_tensors(loaded.device)
        del calls
        del base_cache
        release_request_tensors(loaded.device)

    rows = []
    selector_rows = []
    for example_index, example in enumerate(examples):
        pack = build_prompt_pack_for_config(example, loaded, config)
        build_timing, base_cache = timed_call(
            lambda pack=pack: build_prefix_conditioned_cache(pack, loaded),
            device=loaded.device,
        )
        cache_build_rows.append(
            {
                "example_id": example.id,
                "prompt_length": len(pack.full_input_ids),
                "context_length": pack.query_token_range.start,
                "query_length": pack.query_token_range.length,
                "wall_time_s": build_timing["wall_time_s"],
                "baseline_cuda_memory_mb": build_timing["baseline_cuda_memory_mb"],
                "peak_cuda_memory_mb": build_timing["peak_cuda_memory_mb"],
                "incremental_peak_cuda_memory_mb": build_timing[
                    "incremental_peak_cuda_memory_mb"
                ],
            }
        )
        ranges = suffix_latency_ranges(example, pack, args.random_seed)
        selector_rows.extend(measure_selectors(example, repeats=max(20, args.repeats * 5)))
        calls = {
            "full_prefill": lambda example=example, pack=pack: full_prefill_first_token(
                example, pack, loaded
            ),
            "prefix_query": lambda pack=pack, base_cache=base_cache: query_first_token(
                pack, loaded, base_cache
            ),
            "query_suffix_k1": lambda pack=pack, base_cache=base_cache: suffix_recompute_and_query(
                pack,
                loaded,
                base_cache,
                selected_ranges_for_timed_method(
                    "query_suffix_k1", example, pack, args.random_seed
                ),
            ),
            "risk_suffix_k1": lambda pack=pack, base_cache=base_cache: suffix_recompute_and_query(
                pack,
                loaded,
                base_cache,
                selected_ranges_for_timed_method(
                    "risk_suffix_k1", example, pack, args.random_seed
                ),
            ),
            "hybrid_query_risk_union_suffix_k1": (
                lambda pack=pack, base_cache=base_cache: suffix_recompute_and_query(
                    pack,
                    loaded,
                    base_cache,
                    selected_ranges_for_timed_method(
                        "hybrid_query_risk_union_suffix_k1",
                        example,
                        pack,
                        args.random_seed,
                    ),
                )
            ),
            "risk_suffix_k2": lambda pack=pack, base_cache=base_cache: suffix_recompute_and_query(
                pack,
                loaded,
                base_cache,
                selected_ranges_for_timed_method(
                    "risk_suffix_k2", example, pack, args.random_seed
                ),
            ),
        }
        # Warm every method at this example's actual shape before recording it.
        reference_logits: dict[str, Any] = {}
        for method in TIMED_METHODS:
            _warm_timing, value = timed_call(calls[method], device=loaded.device)
            validate_generation_ready_value(value, pack)
            reference_logits[method] = value["first_logits"].detach().cpu().clone()
            del value
            release_request_tensors(loaded.device)
        for repeat in range(args.repeats):
            offset = (example_index + repeat) % len(TIMED_METHODS)
            order = TIMED_METHODS[offset:] + TIMED_METHODS[:offset]
            for method in order:
                timing, value = timed_call(calls[method], device=loaded.device)
                returned_cache_length = validate_generation_ready_value(value, pack)
                validate_first_logits_match(
                    value["first_logits"],
                    reference_logits[method],
                    method=method,
                    example_id=example.id,
                )
                if method == "full_prefill":
                    recomputed_count = pack.query_token_range.start
                    recomputed_ratio = 1.0
                    forward_input_tokens = len(pack.full_input_ids)
                elif method == "prefix_query":
                    recomputed_count = 0
                    recomputed_ratio = 0.0
                    forward_input_tokens = pack.query_token_range.length
                else:
                    method_ranges = ranges[method]
                    recomputed_count = sum(item.length for item in method_ranges)
                    recomputed_ratio = recomputed_count / max(
                        1, pack.query_token_range.start
                    )
                    forward_input_tokens = (
                        recomputed_count + pack.query_token_range.length
                    )
                rows.append(
                    {
                        "example_id": example.id,
                        "repeat": repeat,
                        "method": method,
                        "prompt_length": len(pack.full_input_ids),
                        "query_length": pack.query_token_range.length,
                        "context_recomputed_token_count": recomputed_count,
                        "context_recomputed_token_ratio": recomputed_ratio,
                        "forward_input_token_count": forward_input_tokens,
                        "selector_and_range_planning_included": method not in {
                            "full_prefill",
                            "prefix_query",
                        },
                        "generation_ready_cache_returned": True,
                        "returned_cache_length": returned_cache_length,
                        "untimed_reference_logits_exact": True,
                        "time_to_first_logit_s": timing["wall_time_s"],
                        "baseline_cuda_memory_mb": timing[
                            "baseline_cuda_memory_mb"
                        ],
                        "peak_cuda_memory_mb": timing["peak_cuda_memory_mb"],
                        "incremental_peak_cuda_memory_mb": timing[
                            "incremental_peak_cuda_memory_mb"
                        ],
                    }
                )
                del value
                release_request_tensors(loaded.device)
        del calls
        del reference_logits
        del base_cache
        release_request_tensors(loaded.device)

    end_provenance = {
        "config_sha256": file_sha256(args.config.resolve()),
        "data_sha256": file_sha256(data_path),
        "implementation_sha256": latency_implementation_hashes(),
    }
    if end_provenance != start_provenance:
        args.results_dir.mkdir(parents=True, exist_ok=True)
        drift_report = {
            "status": "INVALID_PROVENANCE_DRIFT",
            "start": start_provenance,
            "end": end_provenance,
        }
        (args.results_dir / "INVALID_PROVENANCE_DRIFT.json").write_text(
            json.dumps(drift_report, indent=2) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError(
            "config, data, or implementation changed during latency run; "
            "discard this directory and rerun fresh"
        )

    args.results_dir.mkdir(parents=True, exist_ok=True)
    latency_trace_path = args.results_dir / "latency_trace.csv"
    selector_latency_path = args.results_dir / "selector_latency.csv"
    cache_build_path = args.results_dir / "cache_build_latency.csv"
    write_csv(latency_trace_path, rows)
    write_csv(selector_latency_path, selector_rows)
    write_csv(cache_build_path, cache_build_rows)
    artifact_sha256 = {
        "latency_trace.csv": file_sha256(latency_trace_path),
        "selector_latency.csv": file_sha256(selector_latency_path),
        "cache_build_latency.csv": file_sha256(cache_build_path),
    }
    summary = {
        "scope": (
            "warm repeated batch-1 time-to-first-logit with one composed cache "
            "resident on GPU; SAFE method timings include CPU selector and range "
            "planning; excludes cache construction, scheduling, lookup, transfer, "
            "token emission, and concurrent-serving effects"
        ),
        "model_name": config.model.name,
        "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
        "tokenizer_sha256": tokenizer_sha256(loaded.tokenizer),
        "config_path": str(args.config.resolve()),
        "config_sha256": start_provenance["config_sha256"],
        "actual_device": loaded.device,
        "torch_dtype": loaded.torch_dtype_name,
        "attention_implementation": getattr(
            loaded.model.config, "_attn_implementation", None
        ),
        "data_path": str(data_path),
        "data_sha256": start_provenance["data_sha256"],
        "gpu": gpu_name(),
        "environment": environment_versions(),
        "implementation_sha256": start_provenance["implementation_sha256"],
        "provenance_consistent_at_end": True,
        "artifact_sha256": artifact_sha256,
        "logit_projection_scope": (
            "logits_to_keep=1 for full prefill, suffix recompute, and query; "
            "only the final input position is projected through the vocabulary head"
        ),
        "num_examples": len(examples),
        "repeats": args.repeats,
        "random_seed": args.random_seed,
        "warmup_examples": min(args.warmup_examples, len(examples)),
        "per_example_method_warmups": 1,
        "timed_output_validation": (
            "every timed call must return a prompt-length generation-ready cache "
            "and bitwise-equal first logits to that method's untimed warm reference"
        ),
        "method_summary": summarize(rows),
        "selector_summary": summarize_selectors(selector_rows),
        "cache_build_summary": {
            "scope": "one-shot prefix-conditioned cache materialization; not part of request timing",
            **summarize_cache_build(cache_build_rows),
        },
    }
    (args.results_dir / "latency_trace_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


def timed_calls_for_example(
    *,
    example: Any,
    pack: Any,
    base_cache: Any,
    loaded: Any,
    random_seed: int,
) -> dict[str, Callable[[], Any]]:
    return {
        "full_prefill": lambda: full_prefill_first_token(example, pack, loaded),
        "prefix_query": lambda: query_first_token(pack, loaded, base_cache),
        "query_suffix_k1": lambda: suffix_recompute_and_query(
            pack,
            loaded,
            base_cache,
            selected_ranges_for_timed_method(
                "query_suffix_k1", example, pack, random_seed
            ),
        ),
        "risk_suffix_k1": lambda: suffix_recompute_and_query(
            pack,
            loaded,
            base_cache,
            selected_ranges_for_timed_method(
                "risk_suffix_k1", example, pack, random_seed
            ),
        ),
        "hybrid_query_risk_union_suffix_k1": lambda: suffix_recompute_and_query(
            pack,
            loaded,
            base_cache,
            selected_ranges_for_timed_method(
                "hybrid_query_risk_union_suffix_k1", example, pack, random_seed
            ),
        ),
        "risk_suffix_k2": lambda: suffix_recompute_and_query(
            pack,
            loaded,
            base_cache,
            selected_ranges_for_timed_method(
                "risk_suffix_k2", example, pack, random_seed
            ),
        ),
    }


def selected_ranges_for_timed_method(
    method: str,
    example: Any,
    pack: Any,
    random_seed: int,
) -> list[Any]:
    if method == "query_suffix_k1":
        selected_ids = selected_doc_ids_for_method(
            "query_similarity_doc_patch_k1", example, seed=random_seed
        )[0]
    elif method == "risk_suffix_k1":
        selected_ids = selected_doc_ids_for_method(
            "risk_guided_doc_patch_k1", example, seed=random_seed
        )[0]
    elif method == "risk_suffix_k2":
        selected_ids = selected_doc_ids_for_method(
            "risk_guided_doc_patch_k2", example, seed=random_seed
        )[0]
    elif method == "hybrid_query_risk_union_suffix_k1":
        query_ids = selected_doc_ids_for_method(
            "query_similarity_doc_patch_k1", example, seed=random_seed
        )[0]
        risk_ids = selected_doc_ids_for_method(
            "risk_guided_doc_patch_k1", example, seed=random_seed
        )[0]
        selected_ids = sorted(set(query_ids) | set(risk_ids))
    else:
        raise ValueError(f"unsupported selected latency method: {method}")
    return contiguous_suffix_range(example, pack, selected_ids)


def measure_selectors(example: Any, repeats: int) -> list[dict[str, Any]]:
    rows = []
    for method in [
        "query_similarity_doc_patch_k1",
        "risk_guided_doc_patch_k1",
        "risk_guided_doc_patch_k2",
        "hybrid_query_risk_union_suffix_k1",
    ]:
        timings = []
        for _ in range(repeats):
            started = time.perf_counter_ns()
            if method == "hybrid_query_risk_union_suffix_k1":
                query_ids = selected_doc_ids_for_method(
                    "query_similarity_doc_patch_k1", example, seed=0
                )[0]
                risk_ids = selected_doc_ids_for_method(
                    "risk_guided_doc_patch_k1", example, seed=0
                )[0]
                _selected_ids = sorted(set(query_ids) | set(risk_ids))
            else:
                _selected_ids = selected_doc_ids_for_method(method, example, seed=0)[0]
            timings.append((time.perf_counter_ns() - started) / 1_000_000.0)
        rows.append(
            {
                "example_id": example.id,
                "method": method,
                "repeats": repeats,
                "median_ms": percentile(timings, 0.50),
                "p95_ms": percentile(timings, 0.95),
                "mean_ms": statistics.fmean(timings),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    example_ids = sorted({str(row["example_id"]) for row in rows})
    full_median_by_example = {
        example_id: percentile(
            [
                float(row["time_to_first_logit_s"])
                for row in rows
                if str(row["example_id"]) == example_id
                and row["method"] == "full_prefill"
            ],
            0.50,
        )
        for example_id in example_ids
    }
    output = []
    for method in TIMED_METHODS:
        items = [row for row in rows if row["method"] == method]
        latencies = [float(item["time_to_first_logit_s"]) for item in items]
        method_median_by_example = {
            example_id: percentile(
                [
                    float(item["time_to_first_logit_s"])
                    for item in items
                    if str(item["example_id"]) == example_id
                ],
                0.50,
            )
            for example_id in example_ids
        }
        paired_example_speedups = [
            full_median_by_example[example_id]
            / method_median_by_example[example_id]
            for example_id in example_ids
        ]
        paired_example_time_saved = [
            full_median_by_example[example_id]
            - method_median_by_example[example_id]
            for example_id in example_ids
        ]
        output.append(
            {
                "method": method,
                "n": len(items),
                "mean_time_to_first_logit_s": statistics.fmean(latencies),
                "median_time_to_first_logit_s": percentile(latencies, 0.50),
                "p95_time_to_first_logit_s": percentile(latencies, 0.95),
                "median_of_example_median_time_to_first_logit_s": percentile(
                    list(method_median_by_example.values()), 0.50
                ),
                "p95_of_example_median_time_to_first_logit_s": percentile(
                    list(method_median_by_example.values()), 0.95
                ),
                "sequential_first_logits_per_s": len(latencies) / sum(latencies),
                "avg_context_recomputed_token_ratio": statistics.fmean(
                    float(item["context_recomputed_token_ratio"]) for item in items
                ),
                "avg_peak_cuda_memory_mb": statistics.fmean(
                    float(item["peak_cuda_memory_mb"] or 0.0) for item in items
                ),
                "avg_incremental_peak_cuda_memory_mb": statistics.fmean(
                    float(item["incremental_peak_cuda_memory_mb"] or 0.0)
                    for item in items
                ),
                "avg_prompt_length": statistics.fmean(
                    float(item["prompt_length"]) for item in items
                ),
                "paired_example_speedup_vs_full_prefill_median": percentile(
                    paired_example_speedups, 0.50
                ),
                "paired_example_speedup_vs_full_prefill_p05": percentile(
                    paired_example_speedups, 0.05
                ),
                "paired_example_speedup_vs_full_prefill_p95": percentile(
                    paired_example_speedups, 0.95
                ),
                "paired_example_time_saved_s_median": percentile(
                    paired_example_time_saved, 0.50
                ),
                "paired_example_time_saved_s_p05": percentile(
                    paired_example_time_saved, 0.05
                ),
                "paired_example_time_saved_s_p95": percentile(
                    paired_example_time_saved, 0.95
                ),
            }
        )
    return output


def summarize_selectors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for method in sorted({row["method"] for row in rows}):
        items = [row for row in rows if row["method"] == method]
        output.append(
            {
                "method": method,
                "num_examples": len(items),
                "median_of_example_medians_ms": percentile(
                    [float(item["median_ms"]) for item in items], 0.50
                ),
                "p95_of_example_medians_ms": percentile(
                    [float(item["median_ms"]) for item in items], 0.95
                ),
            }
        )
    return output


def summarize_cache_build(rows: list[dict[str, Any]]) -> dict[str, float]:
    latencies = [float(item["wall_time_s"]) for item in rows]
    return {
        "mean_s": statistics.fmean(latencies),
        "median_s": percentile(latencies, 0.50),
        "p95_s": percentile(latencies, 0.95),
        "mean_incremental_peak_cuda_memory_mb": statistics.fmean(
            float(item["incremental_peak_cuda_memory_mb"] or 0.0) for item in rows
        ),
    }


def release_request_tensors(device: str) -> None:
    """Drop returned caches/logits before the next method is measured."""

    gc.collect()
    if device == "cuda":
        import torch

        torch.cuda.synchronize()


def validate_generation_ready_value(value: Any, pack: Any) -> int:
    if not isinstance(value, dict) or set(value) != {"first_logits", "full_cache"}:
        raise ValueError("timed path did not return logits plus generation-ready cache")
    if value["first_logits"].ndim != 2 or value["first_logits"].shape[0] != 1:
        raise ValueError("timed path returned malformed first logits")
    returned_cache_length = cache_seq_len(value["full_cache"])
    if returned_cache_length != len(pack.full_input_ids):
        raise ValueError(
            "timed path returned cache length "
            f"{returned_cache_length}, expected {len(pack.full_input_ids)}"
        )
    return returned_cache_length


def validate_first_logits_match(
    observed: Any,
    expected_cpu: Any,
    *,
    method: str,
    example_id: str,
) -> None:
    import torch

    observed_cpu = observed.detach().cpu()
    if not torch.equal(observed_cpu, expected_cpu):
        max_abs = float((observed_cpu.float() - expected_cpu.float()).abs().max().item())
        raise ValueError(
            f"timed logits changed after warm reference for {example_id}/{method}; "
            f"max_abs_diff={max_abs}"
        )


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def gpu_name() -> str:
    try:
        import torch

        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:
        return "unknown"


def environment_versions() -> dict[str, Any]:
    import yaml
    import torch
    import tokenizers
    import transformers

    try:
        import scipy
    except ImportError:
        scipy = None

    output = {
        "python": platform.python_version(),
        "pyyaml": yaml.__version__,
        "scipy_present": scipy is not None,
        "scipy": scipy.__version__ if scipy is not None else None,
        "torch": torch.__version__,
        "tokenizers": tokenizers.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "nvidia_driver": nvidia_driver_version(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "deterministic_algorithms_warn_only": (
            torch.is_deterministic_algorithms_warn_only_enabled()
        ),
        "deterministic_debug_mode": torch.get_deterministic_debug_mode(),
        "cudnn_enabled": torch.backends.cudnn.enabled,
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
        "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
        "cuda_matmul_allow_fp16_reduced_precision_reduction": (
            torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction
        ),
        "cuda_matmul_allow_bf16_reduced_precision_reduction": (
            torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction
        ),
        "cuda_matmul_allow_fp16_accumulation": (
            torch.backends.cuda.matmul.allow_fp16_accumulation
        ),
        "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }
    if torch.cuda.is_available():
        output.update(
            {
                "gpu": torch.cuda.get_device_name(0),
                "cuda_device_capability": list(torch.cuda.get_device_capability(0)),
                "sdpa_flash_enabled": torch.backends.cuda.flash_sdp_enabled(),
                "sdpa_mem_efficient_enabled": (
                    torch.backends.cuda.mem_efficient_sdp_enabled()
                ),
                "sdpa_math_enabled": torch.backends.cuda.math_sdp_enabled(),
                "sdpa_cudnn_enabled": torch.backends.cuda.cudnn_sdp_enabled(),
                "sdpa_fp16_bf16_reduction_math_allowed": (
                    torch.backends.cuda.fp16_bf16_reduction_math_sdp_allowed()
                ),
            }
        )
    return output


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tokenizer_sha256(tokenizer: Any) -> str:
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is None or not hasattr(backend, "to_str"):
        raise ValueError("a serializable fast tokenizer is required for provenance")
    digest = hashlib.sha256()
    digest.update(backend.to_str().encode("utf-8"))
    metadata = {
        "class": f"{tokenizer.__class__.__module__}.{tokenizer.__class__.__qualname__}",
        "special_tokens_map": getattr(tokenizer, "special_tokens_map", {}),
        "chat_template": getattr(tokenizer, "chat_template", None),
        "model_max_length": getattr(tokenizer, "model_max_length", None),
        "padding_side": getattr(tokenizer, "padding_side", None),
        "truncation_side": getattr(tokenizer, "truncation_side", None),
    }
    digest.update(
        json.dumps(
            metadata,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
    )
    return digest.hexdigest()


def latency_implementation_hashes() -> dict[str, str]:
    code_root = Path(__file__).resolve().parents[1]
    paths = [
        Path(__file__).resolve(),
        Path(__file__).with_name("run_latency_eval.py").resolve(),
        *sorted((code_root / "safekv").rglob("*.py")),
    ]
    return {
        str(path.relative_to(code_root)): file_sha256(path)
        for path in paths
    }


def assert_latency_source_provenance_unchanged(
    expected: dict[str, Any],
    *,
    config_path: Path,
    data_path: Path,
    results_dir: Path,
    stage: str,
) -> None:
    """Abort before timing if source inputs drift while loading the model."""

    observed = {
        "config_sha256": file_sha256(config_path),
        "data_sha256": file_sha256(data_path),
        "implementation_sha256": latency_implementation_hashes(),
    }
    if observed == expected:
        return
    results_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "INVALID_PROVENANCE_DRIFT",
        "stage": stage,
        "start": expected,
        "observed": observed,
    }
    (results_dir / "INVALID_PROVENANCE_DRIFT.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    raise RuntimeError(
        "config, data, or implementation changed before latency measurement; "
        "discard this directory and rerun fresh"
    )


def nvidia_driver_version() -> str | None:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            timeout=5,
        ).splitlines()[0].strip()
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
