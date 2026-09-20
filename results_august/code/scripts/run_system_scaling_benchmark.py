#!/usr/bin/env python
"""Shape-controlled GPU scaling benchmark for full prefill and suffix forwarding.

This is deliberately a kernel-path benchmark, not a vLLM serving result.  It
measures exact-prefix-resident suffix forwarding at controlled context lengths
and batch sizes so recomputation cost can be separated from retrieval, cache
construction, transfer, scheduling, and production concurrency.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
import platform
import statistics
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.cache_ops import (  # noqa: E402
    cache_seq_len,
    legacy_cache_to_model_cache,
    to_legacy_cache,
)
from safekv.config import load_config  # noqa: E402
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from scripts.run_latency_eval import timed_call  # noqa: E402


DEFAULT_CONTEXT_LENGTHS = "2048,4096,8192,16384"
DEFAULT_BATCH_SIZES = "1,2,4,8"
DEFAULT_RECOMPUTE_RATIOS = "0,0.10,0.25,0.50,0.75,1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--context-lengths", default=DEFAULT_CONTEXT_LENGTHS)
    parser.add_argument("--batch-sizes", default=DEFAULT_BATCH_SIZES)
    parser.add_argument("--recompute-ratios", default=DEFAULT_RECOMPUTE_RATIOS)
    parser.add_argument("--examples-per-length", type=int, default=2)
    parser.add_argument("--query-tokens", type=int, default=32)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    return parser.parse_args()


def parse_ints(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fixed_length_prompt_tokens(
    pack: Any,
    *,
    context_length: int,
    query_tokens: int,
) -> tuple[list[int], list[int]]:
    source_context = list(pack.full_input_ids[: pack.query_token_range.start])
    source_query = list(
        pack.full_input_ids[pack.query_token_range.start : pack.query_token_range.end]
    )
    if not source_context or not source_query:
        raise ValueError("source prompt must have non-empty context and query")
    repeats = (context_length + len(source_context) - 1) // len(source_context)
    context = (source_context * repeats)[:context_length]
    query = source_query[:query_tokens]
    if len(query) < query_tokens:
        query_repeats = (query_tokens + len(source_query) - 1) // len(source_query)
        query = (source_query * query_repeats)[:query_tokens]
    return context, query


def batched_ids(token_ids: list[int], batch_size: int, device: str) -> Any:
    import torch

    row = torch.tensor(token_ids, dtype=torch.long, device=device).unsqueeze(0)
    return row.expand(batch_size, -1).contiguous()


def build_exact_prefix_cache(
    *,
    loaded: Any,
    context_ids: list[int],
    prefix_length: int,
    batch_size: int,
) -> Any | None:
    import torch

    if prefix_length == 0:
        return None
    input_ids = batched_ids(context_ids[:prefix_length], batch_size, loaded.device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(
        prefix_length, dtype=torch.long, device=loaded.device
    ).unsqueeze(0).expand(batch_size, -1)
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
            logits_to_keep=1,
        )
    cache = to_legacy_cache(outputs.past_key_values)
    if cache_seq_len(cache) != prefix_length:
        raise ValueError("exact-prefix cache length mismatch")
    return cache


def forward_full_prompt(
    *,
    loaded: Any,
    context_ids: list[int],
    query_ids: list[int],
    batch_size: int,
) -> dict[str, Any]:
    import torch

    token_ids = context_ids + query_ids
    input_ids = batched_ids(token_ids, batch_size, loaded.device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(
        len(token_ids), dtype=torch.long, device=loaded.device
    ).unsqueeze(0).expand(batch_size, -1)
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
            logits_to_keep=1,
        )
    cache = to_legacy_cache(outputs.past_key_values)
    if cache_seq_len(cache) != len(token_ids):
        raise ValueError("full-prefill output cache length mismatch")
    return {"first_logits": outputs.logits[:, -1, :], "full_cache": cache}


def forward_suffix_from_exact_prefix(
    *,
    loaded: Any,
    context_ids: list[int],
    query_ids: list[int],
    prefix_cache: Any | None,
    prefix_length: int,
    batch_size: int,
) -> dict[str, Any]:
    import torch

    forwarded_ids = context_ids[prefix_length:] + query_ids
    input_ids = batched_ids(forwarded_ids, batch_size, loaded.device)
    total_length = len(context_ids) + len(query_ids)
    attention_mask = torch.ones(
        (batch_size, total_length), dtype=torch.long, device=loaded.device
    )
    position_ids = torch.arange(
        prefix_length, total_length, dtype=torch.long, device=loaded.device
    ).unsqueeze(0).expand(batch_size, -1)
    with torch.no_grad():
        outputs = loaded.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=(
                legacy_cache_to_model_cache(prefix_cache)
                if prefix_cache is not None
                else None
            ),
            use_cache=True,
            logits_to_keep=1,
        )
    cache = to_legacy_cache(outputs.past_key_values)
    if cache_seq_len(cache) != total_length:
        raise ValueError("suffix-forward output cache length mismatch")
    return {"first_logits": outputs.logits[:, -1, :], "full_cache": cache}


def release() -> None:
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
    except ImportError:
        pass


def logits_max_abs(left: Any, right: Any) -> float:
    return float((left.detach().float() - right.detach().float()).abs().max().item())


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    position = quantile * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row["method"],
            row["context_length"],
            row["batch_size"],
            row["recompute_ratio"],
        )
        groups.setdefault(key, []).append(row)
    output = []
    for key, items in sorted(groups.items(), key=lambda pair: tuple(map(str, pair[0]))):
        latencies = [float(item["time_to_first_logit_s"]) for item in items]
        batch_size = int(items[0]["batch_size"])
        output.append(
            {
                "method": key[0],
                "context_length": key[1],
                "batch_size": batch_size,
                "recompute_ratio": key[3],
                "n": len(items),
                "mean_time_to_first_logit_s": statistics.fmean(latencies),
                "p50_time_to_first_logit_s": percentile(latencies, 0.50),
                "p95_time_to_first_logit_s": percentile(latencies, 0.95),
                "p99_time_to_first_logit_s": percentile(latencies, 0.99),
                "mean_completed_prompts_per_s": batch_size / statistics.fmean(latencies),
                "mean_prompt_tokens_per_s": (
                    batch_size
                    * int(items[0]["forward_input_tokens"])
                    / statistics.fmean(latencies)
                ),
                "mean_incremental_peak_cuda_memory_mb": statistics.fmean(
                    float(item["incremental_peak_cuda_memory_mb"] or 0.0)
                    for item in items
                ),
                "max_abs_logit_diff_vs_one_shot_full": max(
                    float(item["max_abs_logit_diff_vs_one_shot_full"]) for item in items
                ),
            }
        )
    return output


def environment_snapshot(loaded: Any) -> dict[str, Any]:
    import torch
    import transformers

    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cuda_device_capability": (
            list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None
        ),
        "dtype": loaded.torch_dtype_name,
        "attention_implementation": getattr(
            loaded.model.config, "_attn_implementation", None
        ),
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prepare_results_dir(results_dir: Path) -> None:
    """Allow run-registry bookkeeping files without overwriting results."""
    generated_names = {
        "system_scaling_trace.csv",
        "system_scaling_cache_build.csv",
        "system_scaling_failures.jsonl",
        "system_scaling_summary.json",
    }
    registry_names = {"run_manifest.json", "stdout.log", "stderr.log"}
    if results_dir.exists():
        existing_names = {path.name for path in results_dir.iterdir()}
        generated = sorted(existing_names & generated_names)
        unexpected = sorted(existing_names - registry_names - generated_names)
        if generated or unexpected:
            detail = {"generated": generated, "unexpected": unexpected}
            raise FileExistsError(
                f"refusing to overwrite or mix scaling results in {results_dir}: {detail}"
            )
    else:
        results_dir.mkdir(parents=True)


def main() -> None:
    args = parse_args()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise ValueError("set PYTHONHASHSEED=0 before the scaling benchmark")
    context_lengths = parse_ints(args.context_lengths)
    batch_sizes = parse_ints(args.batch_sizes)
    ratios = parse_floats(args.recompute_ratios)
    if (
        not context_lengths
        or not batch_sizes
        or not ratios
        or min(context_lengths) <= 0
        or min(batch_sizes) <= 0
        or any(ratio < 0.0 or ratio > 1.0 for ratio in ratios)
        or min(args.examples_per_length, args.query_tokens, args.repeats) <= 0
        or args.warmups < 0
    ):
        raise ValueError("invalid scaling grid")
    if any(len(values) != len(set(values)) for values in (context_lengths, batch_sizes, ratios)):
        raise ValueError("scaling grid values must be unique")

    config_path = args.config.resolve()
    data_path = args.data_path.resolve()
    results_dir = args.results_dir.resolve()
    prepare_results_dir(results_dir)
    config = load_config(config_path)
    config = replace(config, data=replace(config.data, path=str(data_path)))
    examples = load_examples_for_config(config, config_dir=config_path.parent.parent)
    if len(examples) < args.examples_per_length:
        raise ValueError("not enough source examples for the scaling benchmark")
    set_deterministic_seed(config.seed)
    loaded = load_causal_lm(config.model)
    maximum = int(getattr(loaded.model.config, "max_position_embeddings", 0) or 0)
    packs = [
        build_prompt_pack_for_config(example, loaded, config)
        for example in examples[: args.examples_per_length]
    ]

    provenance = {
        "config_sha256": file_sha256(config_path),
        "data_sha256": file_sha256(data_path),
        "implementation_sha256": file_sha256(Path(__file__).resolve()),
    }
    rows: list[dict[str, Any]] = []
    cache_build_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for context_length in context_lengths:
        if maximum and context_length + args.query_tokens > maximum:
            failures.append(
                {
                    "context_length": context_length,
                    "status": "skipped_model_max_position_embeddings",
                    "model_max_position_embeddings": maximum,
                }
            )
            continue
        for example_index, pack in enumerate(packs):
            context_ids, query_ids = fixed_length_prompt_tokens(
                pack,
                context_length=context_length,
                query_tokens=args.query_tokens,
            )
            for batch_size in batch_sizes:
                full_reference_logits = None
                try:
                    for _ in range(args.warmups):
                        _timing, value = timed_call(
                            lambda: forward_full_prompt(
                                loaded=loaded,
                                context_ids=context_ids,
                                query_ids=query_ids,
                                batch_size=batch_size,
                            ),
                            device=loaded.device,
                        )
                        full_reference_logits = value["first_logits"].detach().cpu()
                        del value
                        release()
                    for repeat in range(args.repeats):
                        timing, value = timed_call(
                            lambda: forward_full_prompt(
                                loaded=loaded,
                                context_ids=context_ids,
                                query_ids=query_ids,
                                batch_size=batch_size,
                            ),
                            device=loaded.device,
                        )
                        observed = value["first_logits"].detach().cpu()
                        if full_reference_logits is None:
                            full_reference_logits = observed.clone()
                        rows.append(
                            {
                                "example_index": example_index,
                                "repeat": repeat,
                                "method": "one_shot_full_prefill",
                                "context_length": context_length,
                                "query_length": len(query_ids),
                                "batch_size": batch_size,
                                "recompute_ratio": 1.0,
                                "prefix_cache_length": 0,
                                "forward_input_tokens": len(context_ids) + len(query_ids),
                                "time_to_first_logit_s": timing["wall_time_s"],
                                "baseline_cuda_memory_mb": timing["baseline_cuda_memory_mb"],
                                "peak_cuda_memory_mb": timing["peak_cuda_memory_mb"],
                                "incremental_peak_cuda_memory_mb": timing[
                                    "incremental_peak_cuda_memory_mb"
                                ],
                                "max_abs_logit_diff_vs_one_shot_full": logits_max_abs(
                                    observed, full_reference_logits
                                ),
                                "cache_residency": "none",
                            }
                        )
                        del value
                        release()
                except Exception as error:
                    failures.append(
                        {
                            "context_length": context_length,
                            "example_index": example_index,
                            "batch_size": batch_size,
                            "method": "one_shot_full_prefill",
                            "error": repr(error),
                        }
                    )
                    release()
                    continue

                for ratio in ratios:
                    prefix_length = context_length - int(round(context_length * ratio))
                    prefix_cache = None
                    try:
                        prefix_timing, prefix_cache = timed_call(
                            lambda: build_exact_prefix_cache(
                                loaded=loaded,
                                context_ids=context_ids,
                                prefix_length=prefix_length,
                                batch_size=batch_size,
                            ),
                            device=loaded.device,
                        )
                        cache_build_rows.append(
                            {
                                "context_length": context_length,
                                "example_index": example_index,
                                "batch_size": batch_size,
                                "recompute_ratio": ratio,
                                "prefix_cache_length": prefix_length,
                                "wall_time_s": prefix_timing["wall_time_s"],
                                "baseline_cuda_memory_mb": prefix_timing[
                                    "baseline_cuda_memory_mb"
                                ],
                                "peak_cuda_memory_mb": prefix_timing[
                                    "peak_cuda_memory_mb"
                                ],
                                "incremental_peak_cuda_memory_mb": prefix_timing[
                                    "incremental_peak_cuda_memory_mb"
                                ],
                            }
                        )
                        reference = None
                        for _ in range(args.warmups):
                            _timing, value = timed_call(
                                lambda: forward_suffix_from_exact_prefix(
                                    loaded=loaded,
                                    context_ids=context_ids,
                                    query_ids=query_ids,
                                    prefix_cache=prefix_cache,
                                    prefix_length=prefix_length,
                                    batch_size=batch_size,
                                ),
                                device=loaded.device,
                            )
                            reference = value["first_logits"].detach().cpu()
                            del value
                            release()
                        for repeat in range(args.repeats):
                            timing, value = timed_call(
                                lambda: forward_suffix_from_exact_prefix(
                                    loaded=loaded,
                                    context_ids=context_ids,
                                    query_ids=query_ids,
                                    prefix_cache=prefix_cache,
                                    prefix_length=prefix_length,
                                    batch_size=batch_size,
                                ),
                                device=loaded.device,
                            )
                            observed = value["first_logits"].detach().cpu()
                            if reference is not None and not observed.equal(reference):
                                raise ValueError("suffix-forward logits changed across repeats")
                            rows.append(
                                {
                                    "example_index": example_index,
                                    "repeat": repeat,
                                    "method": "exact_prefix_resident_suffix_forward",
                                    "context_length": context_length,
                                    "query_length": len(query_ids),
                                    "batch_size": batch_size,
                                    "recompute_ratio": ratio,
                                    "prefix_cache_length": prefix_length,
                                    "forward_input_tokens": (
                                        context_length - prefix_length + len(query_ids)
                                    ),
                                    "time_to_first_logit_s": timing["wall_time_s"],
                                    "baseline_cuda_memory_mb": timing[
                                        "baseline_cuda_memory_mb"
                                    ],
                                    "peak_cuda_memory_mb": timing["peak_cuda_memory_mb"],
                                    "incremental_peak_cuda_memory_mb": timing[
                                        "incremental_peak_cuda_memory_mb"
                                    ],
                                    "max_abs_logit_diff_vs_one_shot_full": logits_max_abs(
                                        observed, full_reference_logits
                                    ),
                                    "cache_residency": "gpu_exact_prefix_shape_proxy",
                                }
                            )
                            del value
                            release()
                    except Exception as error:
                        failures.append(
                            {
                                "context_length": context_length,
                                "example_index": example_index,
                                "batch_size": batch_size,
                                "recompute_ratio": ratio,
                                "method": "exact_prefix_resident_suffix_forward",
                                "error": repr(error),
                            }
                        )
                    finally:
                        del prefix_cache
                        release()

    end_provenance = {
        "config_sha256": file_sha256(config_path),
        "data_sha256": file_sha256(data_path),
        "implementation_sha256": file_sha256(Path(__file__).resolve()),
    }
    if end_provenance != provenance:
        raise RuntimeError("scaling benchmark inputs changed during execution")
    trace_path = results_dir / "system_scaling_trace.csv"
    cache_build_path = results_dir / "system_scaling_cache_build.csv"
    failure_path = results_dir / "system_scaling_failures.jsonl"
    write_csv(trace_path, rows)
    write_csv(cache_build_path, cache_build_rows)
    failure_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in failures),
        encoding="utf-8",
    )
    report = {
        "schema_version": 1,
        "scope": (
            "shape-controlled PyTorch GPU microbenchmark; batch size is a batched "
            "forward, not production request concurrency; suffix runs assume an "
            "exact prefix cache already resident on GPU; excludes retrieval, cache "
            "construction, lookup, transfer, scheduling, and token emission"
        ),
        "model_name": config.model.name,
        "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
        "data_path": str(data_path),
        "provenance": provenance,
        "environment": environment_snapshot(loaded),
        "parameters": {
            "context_lengths": context_lengths,
            "batch_sizes": batch_sizes,
            "recompute_ratios": ratios,
            "examples_per_length": args.examples_per_length,
            "query_tokens": args.query_tokens,
            "warmups": args.warmups,
            "repeats": args.repeats,
        },
        "num_rows": len(rows),
        "num_cache_build_rows": len(cache_build_rows),
        "num_failures": len(failures),
        "method_summary": summarize(rows),
        "artifacts": {
            "trace": str(trace_path),
            "trace_sha256": file_sha256(trace_path),
            "cache_build": str(cache_build_path),
            "cache_build_sha256": file_sha256(cache_build_path),
            "failures": str(failure_path),
            "failures_sha256": file_sha256(failure_path),
        },
    }
    summary_path = results_dir / "system_scaling_summary.json"
    summary_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"num_rows": len(rows), "num_failures": len(failures)}, indent=2))


if __name__ == "__main__":
    main()
