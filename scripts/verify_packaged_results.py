#!/usr/bin/env python
"""Verify that the SAFE-KV repository contains the expected artifacts, data row counts, and headline metrics."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


EXPECTED_DATA_COUNTS = {
    "data/diagnostic_1000.jsonl": 1000,
    "data/diagnostic_1000_noisy.jsonl": 1000,
    "data/external_hotpotqa_500.jsonl": 500,
    "data/external_2wiki_500.jsonl": 500,
    "data/noise_sweep_0_250.jsonl": 250,
    "data/noise_sweep_8_250.jsonl": 250,
    "data/noise_sweep_16_250.jsonl": 250,
    "data/noise_sweep_64_50.jsonl": 50,
    "data/position_sweep_noise16_single_50x5_docs19.jsonl": 250,
}


EXPECTED_FILES = [
    "README.md",
    "FULL_REPRODUCTION.md",
    "ARTIFACT_MANIFEST.md",
    "LICENSE",
    "NOTICE",
    "requirements.txt",
    "scripts/camera_ready/build_tables.py",
    "scripts/camera_ready/tie_break_audit.py",
    "scripts/camera_ready/make_figures.py",
    "RESULT_FILE_LISTING.txt",
    "code/requirements.txt",
    "code/pyproject.toml",
    "code/scripts/run_answer_eval.py",
    "code/scripts/run_latency_eval.py",
    "code/tests/test_prompting.py",
    "configs/acl_qwen25_7b_hotpotqa_500.yaml",
    "configs/acl_qwen25_7b_2wiki_500.yaml",
    "results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_summary.json",
    "results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json",
    "results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json",
    "results/acl_qwen25_7b_2wiki_latency_suffix_50_with_hybrid/latency_summary.json",
    "results/acl_qwen25_7b_noise64_latency_suffix_20_with_hybrid/latency_summary.json",
    "paper_reference/final_tables/table1_external_7b_main.tex",
    "paper_reference/final_tables/table8_acl_new_main_results.md",
    "paper_reference/final_tables/table9_robustness_calibration_results.md",
    "paper_reference/final_figures/figure2_category_drift.csv",
    "paper_reference/claim_audit/DATA_TABLE_FIGURE_AUDIT_2026-05-23.md",
]


HEADLINE_CHECKS = [
    (
        "results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_summary.json",
        "prefix_conditioned_naive_global",
        "answer_equivalence_to_full_prefill",
        0.472,
    ),
    (
        "results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_summary.json",
        "risk_guided_suffix_closure_k2",
        "answer_equivalence_to_full_prefill",
        0.998,
    ),
    (
        "results/acl_qwen25_7b_hotpotqa_suffix_main_500/answer_eval_summary.json",
        "hybrid_query_risk_union_suffix_k1",
        "answer_equivalence_to_full_prefill",
        0.996,
    ),
    (
        "results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json",
        "prefix_conditioned_naive_global",
        "answer_equivalence_to_full_prefill",
        0.378,
    ),
    (
        "results/acl_qwen25_7b_2wiki_suffix_main_500/answer_eval_summary.json",
        "hybrid_query_risk_union_suffix_k1",
        "answer_equivalence_to_full_prefill",
        0.974,
    ),
    (
        "results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json",
        "prefix_conditioned_naive_global",
        "answer_equivalence_to_full_prefill",
        0.312,
    ),
    (
        "results/acl_mistral7b_noisy_suffix_250_balanced/answer_eval_summary.json",
        "risk_guided_suffix_closure_k2",
        "answer_equivalence_to_full_prefill",
        0.996,
    ),
]


def main() -> int:
    errors: list[str] = []
    errors.extend(check_expected_files())
    errors.extend(check_forbidden_files())
    errors.extend(check_data_counts())
    errors.extend(check_headline_metrics())
    errors.extend(check_figure2_hybrid_rows())

    if errors:
        print("Supplement verification FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Supplement verification passed.")
    print(f"Root: {ROOT}")
    print(f"Data files checked: {len(EXPECTED_DATA_COUNTS)}")
    print(f"Headline metrics checked: {len(HEADLINE_CHECKS)}")
    return 0


def check_expected_files() -> list[str]:
    errors = []
    for relative in EXPECTED_FILES:
        if not (ROOT / relative).exists():
            errors.append(f"missing expected file: {relative}")
    return errors


def check_forbidden_files() -> list[str]:
    errors = []
    forbidden_names = {".git", ".DS_Store", "__MACOSX", "__pycache__", ".pytest_cache"}
    forbidden_suffixes = {".pyc", ".pt", ".bin", ".ckpt", ".safetensors"}
    for path in ROOT.rglob("*"):
        if any(part in forbidden_names for part in path.parts):
            errors.append(f"forbidden path component: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix in forbidden_suffixes:
            errors.append(f"forbidden file suffix: {path.relative_to(ROOT)}")
    return errors


def check_data_counts() -> list[str]:
    errors = []
    for relative, expected in EXPECTED_DATA_COUNTS.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing data file: {relative}")
            continue
        with path.open("r", encoding="utf-8") as handle:
            count = sum(1 for line in handle if line.strip())
        if count != expected:
            errors.append(f"{relative}: expected {expected} rows, found {count}")
    return errors


def check_headline_metrics() -> list[str]:
    errors = []
    for relative, method, metric, expected in HEADLINE_CHECKS:
        summary = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        method_level = summary.get("method_level", {})
        if method not in method_level:
            errors.append(f"{relative}: missing method {method}")
            continue
        actual = float(method_level[method][metric])
        if abs(actual - expected) > 1e-9:
            errors.append(
                f"{relative}: {method}.{metric} expected {expected}, found {actual}"
            )
    return errors


def check_figure2_hybrid_rows() -> list[str]:
    path = ROOT / "paper_reference/final_figures/figure2_category_drift.csv"
    if not path.exists():
        return [f"missing figure source: {path.relative_to(ROOT)}"]
    with path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    datasets = {
        row["dataset"]
        for row in rows
        if row.get("method") == "hybrid_query_risk_union_suffix_k1"
    }
    required = {"HotpotQA-500", "2Wiki-500"}
    if not required.issubset(datasets):
        return [f"figure2 hybrid rows missing: expected {sorted(required)}, found {sorted(datasets)}"]
    return []


if __name__ == "__main__":
    sys.exit(main())
