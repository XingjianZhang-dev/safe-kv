import csv
import json
import math
import sys

import pytest

from scripts import validate_rebuttal_latency_results as validator
from scripts.run_rebuttal_latency_trace import TIMED_METHODS, summarize
from scripts import summarize_latency_paired_bootstrap as paired_bootstrap


SELECTOR_METHODS = [
    "query_similarity_doc_patch_k1",
    "risk_guided_doc_patch_k1",
    "risk_guided_doc_patch_k2",
    "hybrid_query_risk_union_suffix_k1",
]


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def synthetic_latency_rows():
    method_counts = {
        "full_prefill": 8,
        "prefix_query": 0,
        "query_suffix_k1": 2,
        "risk_suffix_k1": 3,
        "hybrid_query_risk_union_suffix_k1": 4,
        "risk_suffix_k2": 5,
    }
    method_scale = {
        "full_prefill": 1.0,
        "prefix_query": 0.4,
        "query_suffix_k1": 0.5,
        "risk_suffix_k1": 0.6,
        "hybrid_query_risk_union_suffix_k1": 0.7,
        "risk_suffix_k2": 0.8,
    }
    full_times = {
        "example-0": [1.0, 1.1, 9.0],
        "example-1": [2.0, 2.1, 2.2],
    }
    rows = []
    for example_id, times in full_times.items():
        for repeat, full_time in enumerate(times):
            for method in TIMED_METHODS:
                count = method_counts[method]
                rows.append(
                    {
                        "example_id": example_id,
                        "repeat": repeat,
                        "method": method,
                        "prompt_length": 10,
                        "query_length": 2,
                        "context_recomputed_token_count": count,
                        "context_recomputed_token_ratio": (
                            1.0 if method == "full_prefill" else count / 8
                        ),
                        "forward_input_token_count": (
                            10
                            if method == "full_prefill"
                            else 2 if method == "prefix_query" else count + 2
                        ),
                        "selector_and_range_planning_included": method
                        not in {"full_prefill", "prefix_query"},
                        "generation_ready_cache_returned": True,
                        "returned_cache_length": 10,
                        "untimed_reference_logits_exact": True,
                        "time_to_first_logit_s": full_time * method_scale[method],
                        "baseline_cuda_memory_mb": 100.0,
                        "peak_cuda_memory_mb": 120.0,
                        "incremental_peak_cuda_memory_mb": 20.0,
                    }
                )
    return rows


def synthetic_summary(tmp_path, rows):
    config_path = tmp_path / "config.yaml"
    data_path = tmp_path / "data.jsonl"
    config_path.write_text("seed: 13\n", encoding="utf-8")
    data_path.write_text('{"id":"example"}\n', encoding="utf-8")
    code_root = validator.Path(validator.__file__).resolve().parents[1]
    implementation_paths = [
        code_root / "scripts" / "run_rebuttal_latency_trace.py",
        code_root / "scripts" / "run_latency_eval.py",
        *sorted((code_root / "safekv").rglob("*.py")),
    ]
    return {
        "num_examples": 2,
        "repeats": 3,
        "actual_device": "cuda",
        "gpu": "NVIDIA L40S",
        "torch_dtype": "float16",
        "attention_implementation": "sdpa",
        "provenance_consistent_at_end": True,
        "environment": {
            "gpu": "NVIDIA L40S",
            "nvidia_driver": "test-driver",
            "tokenizers": "test-tokenizers",
            "pyyaml": "test-pyyaml",
            "scipy_present": True,
            "deterministic_algorithms": False,
            "deterministic_algorithms_warn_only": False,
            "deterministic_debug_mode": 0,
            "cudnn_enabled": True,
            "cudnn_deterministic": False,
            "cudnn_benchmark": False,
            "cuda_matmul_allow_tf32": False,
            "cuda_matmul_allow_fp16_reduced_precision_reduction": True,
            "cuda_matmul_allow_bf16_reduced_precision_reduction": True,
            "cuda_matmul_allow_fp16_accumulation": False,
            "cudnn_allow_tf32": True,
            "sdpa_flash_enabled": True,
            "sdpa_mem_efficient_enabled": True,
            "sdpa_math_enabled": True,
            "sdpa_cudnn_enabled": True,
            "sdpa_fp16_bf16_reduction_math_allowed": False,
            "pythonhashseed": "0",
        },
        "config_path": str(config_path),
        "config_sha256": validator.file_sha256(config_path),
        "data_path": str(data_path),
        "data_sha256": validator.file_sha256(data_path),
        "model_commit_hash": "test-model-commit",
        "tokenizer_sha256": "test-tokenizer-fingerprint",
        "implementation_sha256": {
            str(path.relative_to(code_root)): validator.file_sha256(path)
            for path in implementation_paths
        },
        "artifact_sha256": {
            name: validator.file_sha256(tmp_path / name)
            for name in (
                "latency_trace.csv",
                "selector_latency.csv",
                "cache_build_latency.csv",
            )
        },
        "method_summary": summarize(rows),
    }


def test_summary_uses_example_medians_and_validator_recomputes_it(tmp_path, monkeypatch):
    rows = synthetic_latency_rows()
    method_summary = summarize(rows)
    by_method = {item["method"]: item for item in method_summary}

    # Query is exactly 2.5x faster within each example after taking the median
    # across repeats; the outlying repeat must not be treated as an independent
    # example in the paired statistic.
    assert math.isclose(
        by_method["prefix_query"][
            "paired_example_speedup_vs_full_prefill_median"
        ],
        2.5,
    )

    write_csv(tmp_path / "latency_trace.csv", rows)
    write_csv(
        tmp_path / "selector_latency.csv",
        [
            {
                "example_id": example_id,
                "method": method,
                "repeats": 20,
                "median_ms": 0.1,
                "p95_ms": 0.2,
                "mean_ms": 0.1,
            }
            for example_id in ("example-0", "example-1")
            for method in SELECTOR_METHODS
        ],
    )
    write_csv(
        tmp_path / "cache_build_latency.csv",
        [
            {
                "example_id": example_id,
                "prompt_length": 10,
                "context_length": 8,
                "query_length": 2,
                "wall_time_s": 0.25,
                "baseline_cuda_memory_mb": 100.0,
                "peak_cuda_memory_mb": 120.0,
                "incremental_peak_cuda_memory_mb": 20.0,
            }
            for example_id in ("example-0", "example-1")
        ],
    )
    (tmp_path / "latency_trace_summary.json").write_text(
        json.dumps(synthetic_summary(tmp_path, rows)),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rebuttal_latency_results.py",
            "--results-dir",
            str(tmp_path),
            "--expected-examples",
            "2",
            "--repeats",
            "3",
        ],
    )
    validator.main()
    report = json.loads((tmp_path / "validation_report.json").read_text())
    assert report["status"] == "PASS"
    assert report["num_failures"] == 0

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "summarize_latency_paired_bootstrap.py",
            "--results-dir",
            str(tmp_path),
            "--bootstrap-replicates",
            "100",
            "--seed",
            "7",
        ],
    )
    paired_bootstrap.main()
    bootstrap_report = json.loads(
        (tmp_path / "latency_paired_bootstrap_summary.json").read_text()
    )
    assert bootstrap_report["bootstrap_replicates"] == 100
    assert bootstrap_report["input_latency_trace_sha256"] == report[
        "input_artifact_sha256"
    ]["latency_trace.csv"]

    with (tmp_path / "latency_trace.csv").open("a", encoding="utf-8") as handle:
        handle.write("\n")
    with pytest.raises(ValueError, match="changed after validation"):
        paired_bootstrap.main()


def test_validator_rejects_false_reference_logits_flag(tmp_path, monkeypatch):
    rows = synthetic_latency_rows()
    rows[0]["untimed_reference_logits_exact"] = False
    write_csv(tmp_path / "latency_trace.csv", rows)
    write_csv(
        tmp_path / "selector_latency.csv",
        [
            {
                "example_id": example_id,
                "method": method,
                "repeats": 20,
                "median_ms": 0.1,
                "p95_ms": 0.2,
                "mean_ms": 0.1,
            }
            for example_id in ("example-0", "example-1")
            for method in SELECTOR_METHODS
        ],
    )
    write_csv(
        tmp_path / "cache_build_latency.csv",
        [
            {
                "example_id": example_id,
                "prompt_length": 10,
                "context_length": 8,
                "query_length": 2,
                "wall_time_s": 0.25,
                "baseline_cuda_memory_mb": 100.0,
                "peak_cuda_memory_mb": 120.0,
                "incremental_peak_cuda_memory_mb": 20.0,
            }
            for example_id in ("example-0", "example-1")
        ],
    )
    (tmp_path / "latency_trace_summary.json").write_text(
        json.dumps(synthetic_summary(tmp_path, rows)),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_rebuttal_latency_results.py",
            "--results-dir",
            str(tmp_path),
            "--expected-examples",
            "2",
            "--repeats",
            "3",
        ],
    )
    with pytest.raises(SystemExit):
        validator.main()
    report = json.loads((tmp_path / "validation_report.json").read_text())
    assert report["status"] == "FAIL"
    assert any("untimed-reference logits flag false" in item for item in report["failures"])
