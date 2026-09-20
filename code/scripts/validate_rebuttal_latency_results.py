#!/usr/bin/env python
"""Validate completeness and accounting of a rebuttal latency trace."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


METHODS = {
    "full_prefill",
    "prefix_query",
    "query_suffix_k1",
    "risk_suffix_k1",
    "hybrid_query_risk_union_suffix_k1",
    "risk_suffix_k2",
}
SELECTORS = {
    "query_similarity_doc_patch_k1",
    "risk_guided_doc_patch_k1",
    "risk_guided_doc_patch_k2",
    "hybrid_query_risk_union_suffix_k1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, required=True)
    parser.add_argument("--repeats", type=int, required=True)
    parser.add_argument("--expected-gpu", default="NVIDIA L40S")
    parser.add_argument("--expected-dtype", default="float16")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_csv(args.results_dir / "latency_trace.csv")
    selector_rows = read_csv(args.results_dir / "selector_latency.csv")
    cache_rows = read_csv(args.results_dir / "cache_build_latency.csv")
    summary = json.loads(
        (args.results_dir / "latency_trace_summary.json").read_text(encoding="utf-8")
    )
    failures: list[str] = []

    if summary.get("actual_device") != "cuda":
        failures.append("latency run did not use CUDA")
    if summary.get("gpu") != args.expected_gpu:
        failures.append(
            f"GPU mismatch: {summary.get('gpu')!r} != {args.expected_gpu!r}"
        )
    if summary.get("torch_dtype") != args.expected_dtype:
        failures.append(
            f"dtype mismatch: {summary.get('torch_dtype')!r} != {args.expected_dtype!r}"
        )
    environment = summary.get("environment", {})
    for field in (
        "gpu",
        "nvidia_driver",
        "tokenizers",
        "pyyaml",
        "scipy_present",
        "deterministic_algorithms",
        "deterministic_algorithms_warn_only",
        "deterministic_debug_mode",
        "cudnn_enabled",
        "cudnn_deterministic",
        "cudnn_benchmark",
        "cuda_matmul_allow_tf32",
        "cuda_matmul_allow_fp16_reduced_precision_reduction",
        "cuda_matmul_allow_bf16_reduced_precision_reduction",
        "cuda_matmul_allow_fp16_accumulation",
        "cudnn_allow_tf32",
        "sdpa_flash_enabled",
        "sdpa_mem_efficient_enabled",
        "sdpa_math_enabled",
        "sdpa_cudnn_enabled",
        "sdpa_fp16_bf16_reduction_math_allowed",
        "pythonhashseed",
    ):
        if field not in environment:
            failures.append(f"runtime provenance missing {field}")
    if environment.get("gpu") != args.expected_gpu:
        failures.append("runtime GPU does not match expected GPU")
    if environment.get("pythonhashseed") != "0":
        failures.append("runtime PYTHONHASHSEED is not fixed to 0")
    if summary.get("provenance_consistent_at_end") is not True:
        failures.append("run did not certify start/end provenance consistency")

    artifact_paths = {
        "latency_trace.csv": args.results_dir / "latency_trace.csv",
        "selector_latency.csv": args.results_dir / "selector_latency.csv",
        "cache_build_latency.csv": args.results_dir / "cache_build_latency.csv",
    }
    expected_artifact_hashes = summary.get("artifact_sha256", {})
    if set(expected_artifact_hashes) != set(artifact_paths):
        failures.append("artifact hash coverage mismatch")
    else:
        for name, path in artifact_paths.items():
            if file_sha256(path) != expected_artifact_hashes[name]:
                failures.append(f"artifact hash mismatch for {name}")

    for path_field, hash_field in (
        ("config_path", "config_sha256"),
        ("data_path", "data_sha256"),
    ):
        source_path = Path(summary[path_field])
        if not source_path.exists() or file_sha256(source_path) != summary[hash_field]:
            failures.append(f"{path_field} is missing or hash-mismatched")
    if not summary.get("model_commit_hash"):
        failures.append("missing resolved model commit hash")
    if not summary.get("tokenizer_sha256"):
        failures.append("missing tokenizer fingerprint")
    if summary.get("attention_implementation") != "sdpa":
        failures.append("unexpected or missing attention implementation")
    implementation_hashes = summary.get("implementation_sha256", {})
    code_root = Path(__file__).resolve().parents[1]
    expected_implementation_keys = {
        "scripts/run_rebuttal_latency_trace.py",
        "scripts/run_latency_eval.py",
        *{
            str(path.relative_to(code_root))
            for path in (code_root / "safekv").rglob("*.py")
        },
    }
    if set(implementation_hashes) != expected_implementation_keys:
        failures.append("implementation hash coverage mismatch")
    else:
        for relative_path, observed_hash in implementation_hashes.items():
            source_path = code_root / relative_path
            if file_sha256(source_path) != observed_hash:
                failures.append(f"implementation hash mismatch for {relative_path}")

    expected_rows = args.expected_examples * args.repeats * len(METHODS)
    if len(rows) != expected_rows:
        failures.append(f"latency rows {len(rows)} != expected {expected_rows}")
    keys = [(row["example_id"], row["repeat"], row["method"]) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append("duplicate example/repeat/method latency keys")
    if {row["method"] for row in rows} != METHODS:
        failures.append("latency method set mismatch")
    if len(cache_rows) != args.expected_examples:
        failures.append("cache-build row count mismatch")
    if len(selector_rows) != args.expected_examples * len(SELECTORS):
        failures.append("selector row count mismatch")
    if {row["method"] for row in selector_rows} != SELECTORS:
        failures.append("selector method set mismatch")

    example_ids = {row["example_id"] for row in rows}
    if len(example_ids) != args.expected_examples:
        failures.append(
            f"latency example count {len(example_ids)} != expected {args.expected_examples}"
        )
    cache_example_ids = [row["example_id"] for row in cache_rows]
    if len(cache_example_ids) != len(set(cache_example_ids)):
        failures.append("duplicate cache-build example ids")
    if set(cache_example_ids) != example_ids:
        failures.append("cache-build example ids do not match latency trace")
    selector_by_example: dict[str, set[str]] = defaultdict(set)
    for row in selector_rows:
        selector_by_example[row["example_id"]].add(row["method"])
    if set(selector_by_example) != example_ids:
        failures.append("selector example ids do not match latency trace")
    for example_id, methods in selector_by_example.items():
        if methods != SELECTORS:
            failures.append(f"selector method coverage mismatch for {example_id}")

    rows_by_pair: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        method = row["method"]
        pair = (row["example_id"], int(row["repeat"]))
        rows_by_pair[pair][method] = row
        elapsed = float(row["time_to_first_logit_s"])
        ratio = float(row["context_recomputed_token_ratio"])
        recomputed_count = int(row["context_recomputed_token_count"])
        forward_count = int(row["forward_input_token_count"])
        prompt_length = int(row["prompt_length"])
        query_length = int(row["query_length"])
        incremental_peak = float(row["incremental_peak_cuda_memory_mb"])
        includes_selector = row["selector_and_range_planning_included"].lower() == "true"
        generation_ready = row["generation_ready_cache_returned"].lower() == "true"
        reference_exact = row["untimed_reference_logits_exact"].lower() == "true"
        returned_cache_length = int(row["returned_cache_length"])
        if elapsed <= 0:
            failures.append(f"nonpositive latency for {method}")
        if incremental_peak < 0:
            failures.append(f"negative incremental peak for {method}")
        if method == "full_prefill" and ratio != 1.0:
            failures.append("full-prefill recomputation ratio is not 1")
        if method == "prefix_query" and ratio != 0.0:
            failures.append("prefix-query recomputation ratio is not 0")
        if method == "full_prefill" and forward_count != prompt_length:
            failures.append("full-prefill forward token count mismatch")
        if method == "prefix_query" and forward_count != query_length:
            failures.append("prefix-query forward token count mismatch")
        if method not in {"full_prefill", "prefix_query"} and forward_count != (
            recomputed_count + query_length
        ):
            failures.append(f"SAFE forward token count mismatch for {method}")
        if (method not in {"full_prefill", "prefix_query"}) != includes_selector:
            failures.append(f"selector-inclusion flag mismatch for {method}")
        if not generation_ready:
            failures.append(f"generation-ready cache flag false for {method}")
        if not reference_exact:
            failures.append(f"untimed-reference logits flag false for {method}")
        if returned_cache_length != prompt_length:
            failures.append(f"returned cache length mismatch for {method}")
        if ratio < 0.0 or ratio > 1.0:
            failures.append(f"invalid recomputation ratio for {method}: {ratio}")

    expected_pairs = args.expected_examples * args.repeats
    if len(rows_by_pair) != expected_pairs:
        failures.append(f"pair count {len(rows_by_pair)} != expected {expected_pairs}")
    repeats_by_example: dict[str, set[int]] = defaultdict(set)
    for example_id, repeat in rows_by_pair:
        repeats_by_example[example_id].add(repeat)
    expected_repeats = set(range(args.repeats))
    for example_id, repeats in repeats_by_example.items():
        if repeats != expected_repeats:
            failures.append(f"repeat coverage mismatch for {example_id}: {sorted(repeats)}")
    for pair, pair_rows in rows_by_pair.items():
        if set(pair_rows) != METHODS:
            failures.append(f"pair method coverage mismatch for {pair}")
            continue
        context_len = int(pair_rows["full_prefill"]["context_recomputed_token_count"])
        if context_len <= 0:
            failures.append(f"nonpositive context length for {pair}")
            continue
        for method, row in pair_rows.items():
            count = int(row["context_recomputed_token_count"])
            ratio = float(row["context_recomputed_token_ratio"])
            expected_ratio = 1.0 if method == "full_prefill" else count / context_len
            if not math.isclose(ratio, expected_ratio, rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"recompute ratio/count mismatch for {pair}/{method}")

    summary_methods = {item["method"] for item in summary["method_summary"]}
    if summary_methods != METHODS:
        failures.append("summary method set mismatch")
    summary_by_method = {
        str(item["method"]): item for item in summary["method_summary"]
    }
    if int(summary["num_examples"]) != args.expected_examples:
        failures.append("summary example count mismatch")
    if int(summary["repeats"]) != args.repeats:
        failures.append("summary repeat count mismatch")
    for item in summary["method_summary"]:
        if int(item["n"]) != args.expected_examples * args.repeats:
            failures.append(f"summary n mismatch for {item['method']}")
        for field in (
            "paired_example_speedup_vs_full_prefill_median",
            "paired_example_speedup_vs_full_prefill_p05",
            "paired_example_speedup_vs_full_prefill_p95",
        ):
            if float(item[field]) <= 0:
                failures.append(f"invalid {field} for {item['method']}")

    rows_by_example_method: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_example_method[(row["example_id"], row["method"])].append(row)
    example_ids_sorted = sorted(example_ids)
    full_median_by_example = {
        example_id: percentile(
            [
                float(row["time_to_first_logit_s"])
                for row in rows_by_example_method[(example_id, "full_prefill")]
            ],
            0.50,
        )
        for example_id in example_ids_sorted
    }
    for method in METHODS:
        method_rows = [row for row in rows if row["method"] == method]
        latencies = [float(row["time_to_first_logit_s"]) for row in method_rows]
        method_median_by_example = {
            example_id: percentile(
                [
                    float(row["time_to_first_logit_s"])
                    for row in rows_by_example_method[(example_id, method)]
                ],
                0.50,
            )
            for example_id in example_ids_sorted
        }
        paired_example_speedups = [
            full_median_by_example[example_id] / method_median_by_example[example_id]
            for example_id in example_ids_sorted
        ]
        paired_example_saved = [
            full_median_by_example[example_id] - method_median_by_example[example_id]
            for example_id in example_ids_sorted
        ]
        expected_summary = {
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
                float(row["context_recomputed_token_ratio"]) for row in method_rows
            ),
            "avg_peak_cuda_memory_mb": statistics.fmean(
                float(row["peak_cuda_memory_mb"] or 0.0) for row in method_rows
            ),
            "avg_incremental_peak_cuda_memory_mb": statistics.fmean(
                float(row["incremental_peak_cuda_memory_mb"] or 0.0)
                for row in method_rows
            ),
            "avg_prompt_length": statistics.fmean(
                float(row["prompt_length"]) for row in method_rows
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
                paired_example_saved, 0.50
            ),
            "paired_example_time_saved_s_p05": percentile(
                paired_example_saved, 0.05
            ),
            "paired_example_time_saved_s_p95": percentile(
                paired_example_saved, 0.95
            ),
        }
        summary_item = summary_by_method[method]
        for field, expected in expected_summary.items():
            observed = float(summary_item[field])
            if not math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"summary mismatch for {method}/{field}")

    report: dict[str, Any] = {
        "status": "PASS" if not failures else "FAIL",
        "num_latency_rows": len(rows),
        "expected_latency_rows": expected_rows,
        "num_selector_rows": len(selector_rows),
        "num_cache_build_rows": len(cache_rows),
        "num_failures": len(failures),
        "failures": failures,
        "input_artifact_sha256": {
            **{name: file_sha256(path) for name, path in artifact_paths.items()},
            "latency_trace_summary.json": file_sha256(
                args.results_dir / "latency_trace_summary.json"
            ),
        },
        "validator_script_path": str(Path(__file__).resolve()),
        "validator_script_sha256": file_sha256(Path(__file__).resolve()),
    }
    (args.results_dir / "validation_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
