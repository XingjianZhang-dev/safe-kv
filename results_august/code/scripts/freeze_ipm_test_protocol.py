#!/usr/bin/env python
"""Freeze the untouched IP&M test protocol and every executable input hash."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv_ipm.run_registry import (  # noqa: E402
    ensure_code_snapshot,
    input_fingerprints,
    sha256_file,
    tree_fingerprint,
    utc_now,
)
from safekv.config import load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--data-build-manifest",
        action="append",
        type=Path,
        required=True,
        help="repeat once per dataset",
    )
    parser.add_argument("--retriever-model-manifest", type=Path, required=True)
    parser.add_argument("--retriever-verification-report", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument(
        "--model-verification-report",
        action="append",
        type=Path,
        required=True,
        help="repeat once per primary/transfer model after full content verification",
    )
    parser.add_argument("--frontier-artifact", type=Path, required=True)
    parser.add_argument("--frontier-selection-report", type=Path, required=True)
    parser.add_argument("--safety-gate-artifact", type=Path, required=True)
    parser.add_argument("--baseline-audit", type=Path, required=True)
    parser.add_argument(
        "--baseline-evidence",
        action="append",
        type=Path,
        default=[],
        help="repeat for official-baseline manifests, logs, patches, or commit records",
    )
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model-label", default="qwen25")
    parser.add_argument("--datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--answer-max-examples", type=int, default=500)
    parser.add_argument("--frontier-max-examples", type=int, default=100)
    parser.add_argument("--attention-max-examples", type=int, default=100)
    parser.add_argument(
        "--attention-budgets",
        default="0.05,0.10,0.16,0.20,0.30,0.45,0.60",
    )
    parser.add_argument("--attention-random-seeds", default="13,29,47")
    parser.add_argument("--system-context-lengths", default="2048,4096,8192,16384")
    parser.add_argument("--system-batch-sizes", default="1,2,4,8")
    parser.add_argument("--system-recompute-ratios", default="0,0.10,0.25,0.50,0.75,1.0")
    parser.add_argument("--system-examples-per-length", type=int, default=2)
    parser.add_argument("--system-query-tokens", type=int, default=32)
    parser.add_argument("--system-warmups", type=int, default=1)
    parser.add_argument("--system-repeats", type=int, default=20)
    parser.add_argument(
        "--transfer-model",
        action="append",
        nargs=3,
        default=[],
        metavar=("LABEL", "CONFIG", "MODEL_MANIFEST"),
        help=(
            "freeze one cross-model transfer suite; repeat for each transfer model"
        ),
    )
    parser.add_argument("--transfer-answer-max-examples", type=int, default=100)
    parser.add_argument("--transfer-frontier-max-examples", type=int, default=100)
    parser.add_argument("--transfer-version", default="v1")
    parser.add_argument(
        "--answer-methods",
        default=(
            "full_prefill,exact_prefix_reuse,prefix_conditioned_naive_global,"
            "actual_local_recompute::query_similarity_doc_patch_k2,"
            "actual_local_recompute::risk_guided_doc_patch_k2,"
            "actual_local_recompute::query_similarity_downstream_w1_k1,"
            "actual_local_recompute::query_similarity_downstream_w2_k1,"
            "actual_local_recompute::query_similarity_downstream_w4_k1,"
            "actual_local_recompute::query_similarity_downstream_w8_k1,"
            "actual_recompute::query_similarity_suffix_closure_k1,"
            "actual_recompute::query_similarity_suffix_closure_k2,"
            "actual_recompute::risk_guided_suffix_closure_k1,"
            "actual_recompute::risk_guided_suffix_closure_k2,"
            "actual_recompute::random_suffix_closure_k1_seed13,"
            "actual_recompute::random_suffix_closure_k1_seed29,"
            "actual_recompute::random_suffix_closure_k1_seed47,"
            "actual_recompute::random_suffix_closure_k2_seed13,"
            "actual_recompute::random_suffix_closure_k2_seed29,"
            "actual_recompute::random_suffix_closure_k2_seed47,"
            "actual_recompute::oracle_evidence_doc_suffix_closure_patch,"
            "actual_recompute::frozen_frontier_selector"
        ),
    )
    parser.add_argument("--answer-version", default="v1")
    parser.add_argument("--frontier-version", default="v1")
    parser.add_argument("--attention-version", default="v1")
    parser.add_argument("--system-version", default="v1")
    parser.add_argument("--analysis-version", default="v1")
    parser.add_argument("--seed", type=int, default=20260821)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_test_data(
    path: Path,
    *,
    dataset: str,
    condition: str,
    required_examples: int,
) -> dict:
    rows = read_jsonl(path)
    if len(rows) < required_examples:
        raise ValueError(f"{path}: only {len(rows)} rows, need {required_examples}")
    ids = []
    groups = []
    for row in rows[:required_examples]:
        metadata = row.get("source_metadata", {})
        observed = (
            metadata.get("dataset"),
            metadata.get("retrieval_condition"),
            metadata.get("split"),
        )
        expected = (dataset, condition, "test")
        if observed != expected:
            raise ValueError(f"{path}: source metadata {observed} != {expected}")
        ids.append(str(row["id"]))
        groups.append(f"{dataset}:{metadata['source_id']}")
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate example IDs in frozen prefix: {path}")
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "rows_in_file": len(rows),
        "answer_prefix_rows": required_examples,
        "frontier_prefix_rows": min(required_examples, 100),
        "frozen_prefix_example_ids": ids,
        "frozen_prefix_group_ids": groups,
    }


def main() -> None:
    args = parse_args()
    if min(
        args.answer_max_examples,
        args.frontier_max_examples,
        args.attention_max_examples,
        args.transfer_answer_max_examples,
        args.transfer_frontier_max_examples,
    ) <= 0:
        raise ValueError("test sample sizes must be positive")
    if max(args.frontier_max_examples, args.attention_max_examples) > args.answer_max_examples:
        raise ValueError(
            "frontier and attention test prefixes must be contained in the answer test prefix"
        )
    if max(
        args.transfer_answer_max_examples,
        args.transfer_frontier_max_examples,
    ) > args.answer_max_examples:
        raise ValueError("cross-model test prefixes must be contained in the main test prefix")
    datasets = [item for item in args.datasets.split(",") if item]
    conditions = [item for item in args.conditions.split(",") if item]
    methods = [item for item in args.answer_methods.split(",") if item]
    attention_budgets = [item for item in args.attention_budgets.split(",") if item]
    attention_random_seeds = [
        int(item) for item in args.attention_random_seeds.split(",") if item
    ]
    system_context_lengths = [
        int(item) for item in args.system_context_lengths.split(",") if item
    ]
    system_batch_sizes = [
        int(item) for item in args.system_batch_sizes.split(",") if item
    ]
    system_recompute_ratios = [
        float(item) for item in args.system_recompute_ratios.split(",") if item
    ]
    if len(methods) != len(set(methods)) or not methods:
        raise ValueError("answer methods must be non-empty and unique")
    answer_pairs = [
        ("exact_prefix_reuse", "full_prefill"),
        (
            "actual_recompute::query_similarity_suffix_closure_k2",
            "actual_local_recompute::query_similarity_doc_patch_k2",
        ),
        (
            "actual_recompute::risk_guided_suffix_closure_k2",
            "actual_local_recompute::risk_guided_doc_patch_k2",
        ),
        *[
            (
                "actual_recompute::query_similarity_suffix_closure_k1",
                f"actual_local_recompute::query_similarity_downstream_w{window}_k1",
            )
            for window in (1, 2, 4, 8)
        ],
        (
            "actual_recompute::frozen_frontier_selector",
            "prefix_conditioned_naive_global",
        ),
        (
            "actual_recompute::frozen_frontier_selector",
            "actual_recompute::query_similarity_suffix_closure_k2",
        ),
        (
            "actual_recompute::frozen_frontier_selector",
            "actual_recompute::risk_guided_suffix_closure_k2",
        ),
        *[
            (
                "actual_recompute::query_similarity_suffix_closure_k2",
                f"actual_recompute::random_suffix_closure_k2_seed{seed}",
            )
            for seed in (13, 29, 47)
        ],
        *[
            (
                "actual_recompute::risk_guided_suffix_closure_k2",
                f"actual_recompute::random_suffix_closure_k2_seed{seed}",
            )
            for seed in (13, 29, 47)
        ],
        (
            "actual_recompute::oracle_evidence_doc_suffix_closure_patch",
            "actual_recompute::frozen_frontier_selector",
        ),
    ]
    if any(left not in methods or right not in methods for left, right in answer_pairs):
        raise ValueError("predeclared answer comparison is absent from --answer-methods")
    if (
        not attention_budgets
        or len(attention_budgets) != len(set(attention_budgets))
        or not attention_random_seeds
        or len(attention_random_seeds) != len(set(attention_random_seeds))
    ):
        raise ValueError("attention budgets and random seeds must be non-empty and unique")
    if (
        not system_context_lengths
        or not system_batch_sizes
        or not system_recompute_ratios
        or min(system_context_lengths) <= 0
        or min(system_batch_sizes) <= 0
        or any(value < 0.0 or value > 1.0 for value in system_recompute_ratios)
        or min(
            args.system_examples_per_length,
            args.system_query_tokens,
            args.system_repeats,
        )
        <= 0
        or args.system_warmups < 0
    ):
        raise ValueError("invalid system scaling protocol")

    transfer_models = []
    transfer_labels = []
    for label, config_text, manifest_text in args.transfer_model:
        if not re.fullmatch(r"[a-z0-9_]+", label):
            raise ValueError(f"invalid transfer model label: {label}")
        transfer_labels.append(label)
        transfer_models.append(
            {
                "label": label,
                "config": Path(config_text).resolve(),
                "model_manifest": Path(manifest_text).resolve(),
            }
        )
    if (
        len(transfer_labels) != len(set(transfer_labels))
        or args.model_label in transfer_labels
    ):
        raise ValueError("main and transfer model labels must be unique")

    data_root = args.data_root.resolve()
    code_root = args.code_root.resolve()
    registry = args.registry_dir.resolve()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite frozen protocol: {out}")

    verification_paths = [path.resolve() for path in args.model_verification_report]
    data_build_paths = [path.resolve() for path in args.data_build_manifest]
    retriever_manifest_path = args.retriever_model_manifest.resolve()
    retriever_report_path = args.retriever_verification_report.resolve()
    primary_fixed_paths = [
        args.config.resolve(),
        args.model_manifest.resolve(),
        args.frontier_artifact.resolve(),
        args.frontier_selection_report.resolve(),
        args.safety_gate_artifact.resolve(),
        args.baseline_audit.resolve(),
    ]
    fixed_paths = primary_fixed_paths + [
        path
        for model in transfer_models
        for path in (model["config"], model["model_manifest"])
    ] + verification_paths + data_build_paths + [
        retriever_manifest_path,
        retriever_report_path,
    ] + [path.resolve() for path in args.baseline_evidence]
    for path in fixed_paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    frontier_artifact = json.loads(primary_fixed_paths[2].read_text(encoding="utf-8"))
    selection = json.loads(primary_fixed_paths[3].read_text(encoding="utf-8"))
    safety_gate = json.loads(primary_fixed_paths[4].read_text(encoding="utf-8"))
    if selection["integrity"].get("test_set_used") is not False:
        raise ValueError("frontier selection report does not certify untouched test data")
    if frontier_artifact["integrity"].get("test_set_used") is not False:
        raise ValueError("frontier artifact does not certify calibration-only fitting")
    if selection["selected"]["sha256"] != sha256_file(primary_fixed_paths[2]):
        raise ValueError("frontier artifact is not the artifact frozen by selection")
    if safety_gate["integrity"].get("test_set_used") is not False:
        raise ValueError("safety gate artifact does not certify calibration-only fitting")

    model_specs = [
        {
            "label": args.model_label,
            "config": args.config.resolve(),
            "model_manifest": args.model_manifest.resolve(),
        },
        *transfer_models,
    ]
    if len(verification_paths) != len(model_specs):
        raise ValueError("require exactly one verification report per frozen model")
    verification_by_manifest: dict[Path, tuple[Path, dict]] = {}
    for report_path in verification_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "PASS":
            raise ValueError(f"model verification did not pass: {report_path}")
        manifest_path = Path(str(report.get("manifest_path", ""))).resolve()
        if manifest_path in verification_by_manifest:
            raise ValueError(f"duplicate model verification manifest: {manifest_path}")
        verification_by_manifest[manifest_path] = (report_path, report)
    model_verifications = []
    for spec in model_specs:
        manifest_path = spec["model_manifest"].resolve()
        if manifest_path not in verification_by_manifest:
            raise ValueError(f"missing verification for model manifest: {manifest_path}")
        report_path, report = verification_by_manifest[manifest_path]
        expected_model_dir = Path(load_config(spec["config"]).model.name).resolve()
        if Path(str(report.get("model_dir", ""))).resolve() != expected_model_dir:
            raise ValueError(
                f"verification model directory differs from config for {spec['label']}"
            )
        model_verifications.append(
            {
                "label": spec["label"],
                "config": str(spec["config"]),
                "config_sha256": sha256_file(spec["config"]),
                "model_manifest": str(manifest_path),
                "model_manifest_sha256": sha256_file(manifest_path),
                "verification_report": str(report_path),
                "verification_report_sha256": sha256_file(report_path),
                "model_dir": str(expected_model_dir),
                "status": "PASS",
            }
        )

    if len(data_build_paths) != len(datasets):
        raise ValueError("require exactly one data build manifest per dataset")
    build_by_dataset = {}
    for path in data_build_paths:
        build = json.loads(path.read_text(encoding="utf-8"))
        dataset = str(build.get("dataset", ""))
        if dataset in build_by_dataset:
            raise ValueError(f"duplicate data build manifest for {dataset}")
        if set(build.get("conditions", [])) != set(conditions):
            raise ValueError(f"retrieval conditions differ in {path}")
        if build.get("gold_labels_used_for_ranking") is not False:
            raise ValueError(f"gold labels were used for retrieval ranking in {path}")
        build_by_dataset[dataset] = (path, build)
    if set(build_by_dataset) != set(datasets):
        raise ValueError("data build manifest dataset set differs from protocol")

    retriever_manifest = json.loads(retriever_manifest_path.read_text(encoding="utf-8"))
    retriever_report = json.loads(retriever_report_path.read_text(encoding="utf-8"))
    if retriever_report.get("status") != "PASS":
        raise ValueError("retriever model verification did not pass")
    if (
        Path(str(retriever_report.get("manifest_path", ""))).resolve()
        != retriever_manifest_path
    ):
        raise ValueError("retriever verification references another manifest")
    for path, build in build_by_dataset.values():
        if build.get("dense_model") != retriever_manifest.get("model_id"):
            raise ValueError(f"dense retriever model differs in {path}")
        if build.get("dense_revision") != retriever_manifest.get("huggingface_commit"):
            raise ValueError(f"dense retriever revision differs in {path}")

    target_runs = []
    data = []
    frozen_groups: dict[str, list[str]] = {}
    for dataset in datasets:
        for condition in conditions:
            path = data_root / f"{dataset}_{condition}_test.jsonl"
            item = validate_test_data(
                path,
                dataset=dataset,
                condition=condition,
                required_examples=args.answer_max_examples,
            )
            item["frontier_prefix_rows"] = args.frontier_max_examples
            item["attention_prefix_rows"] = args.attention_max_examples
            item["transfer_answer_prefix_rows"] = args.transfer_answer_max_examples
            item["transfer_frontier_prefix_rows"] = args.transfer_frontier_max_examples
            build_path, build = build_by_dataset[dataset]
            build_key = f"{condition}:test"
            if build_key not in build.get("outputs", {}):
                raise ValueError(f"missing {build_key} in {build_path}")
            declared = build["outputs"][build_key]
            if (
                Path(str(declared.get("path", ""))).resolve() != path.resolve()
                or declared.get("sha256") != item["sha256"]
                or int(declared.get("num_examples", 0)) < args.answer_max_examples
            ):
                raise ValueError(f"test data differs from build manifest: {path}")
            item["build_manifest"] = str(build_path)
            item["build_manifest_sha256"] = sha256_file(build_path)
            data.append(item)
            key = f"{dataset}/{condition}"
            frozen_groups[key] = item["frozen_prefix_group_ids"]
            target_runs.extend(
                [
                    (
                        "answer",
                        f"{args.model_label}_answers_{dataset}_{condition}_test_"
                        f"n{args.answer_max_examples}_{args.answer_version}",
                    ),
                    (
                        "frontier",
                        f"{args.model_label}_frontier_{dataset}_{condition}_test_"
                        f"n{args.frontier_max_examples}_{args.frontier_version}",
                    ),
                    (
                        "attention",
                        f"{args.model_label}_query_attention_{dataset}_{condition}_test_"
                        f"n{args.attention_max_examples}_{args.attention_version}",
                    ),
                ]
            )
            for model in transfer_models:
                target_runs.extend(
                    [
                        (
                            "cross_model_answer",
                            f"{model['label']}_answers_{dataset}_{condition}_test_"
                            f"n{args.transfer_answer_max_examples}_{args.transfer_version}",
                        ),
                        (
                            "cross_model_frontier",
                            f"{model['label']}_frontier_{dataset}_{condition}_test_"
                            f"n{args.transfer_frontier_max_examples}_{args.transfer_version}",
                        ),
                    ]
                )
    target_runs.append(
        (
            "system_scaling",
            f"{args.model_label}_system_scaling_test_{args.system_version}",
        )
    )
    target_runs.extend(
        [
            (
                "answer_grid_bootstrap",
                f"{args.model_label}_answer_grid_analysis_test_{args.analysis_version}",
            ),
            (
                "safety_gate_evaluation",
                f"{args.model_label}_safety_gate_test_{args.analysis_version}",
            ),
            (
                "frontier_selector_evaluation",
                f"{args.model_label}_frontier_selector_test_{args.analysis_version}",
            ),
            (
                "frontier_selector_bootstrap",
                f"{args.model_label}_frontier_selector_bootstrap_test_"
                f"{args.analysis_version}",
            ),
            (
                "query_attention_bootstrap",
                f"{args.model_label}_query_attention_analysis_test_"
                f"{args.analysis_version}",
            ),
        ]
    )
    for model in transfer_models:
        target_runs.extend(
            [
                (
                    "cross_model_answer_grid_bootstrap",
                    f"{model['label']}_answer_grid_analysis_test_{args.analysis_version}",
                ),
                (
                    "cross_model_frontier_selector_evaluation",
                    f"{model['label']}_frontier_selector_transfer_test_"
                    f"{args.analysis_version}",
                ),
                (
                    "cross_model_frontier_selector_bootstrap",
                    f"{model['label']}_frontier_selector_transfer_bootstrap_test_"
                    f"{args.analysis_version}",
                ),
            ]
        )
    existing = [run_id for _kind, run_id in target_runs if (registry / run_id).exists()]
    if existing:
        raise FileExistsError(
            "target test run IDs already exist before protocol freeze: " + ", ".join(existing)
        )

    # Retrieval conditions for one dataset must preserve the same source-question order.
    for dataset in datasets:
        reference = frozen_groups[f"{dataset}/{conditions[0]}"]
        for condition in conditions[1:]:
            if frozen_groups[f"{dataset}/{condition}"] != reference:
                raise ValueError(
                    f"test source-question prefix differs across retrieval conditions: "
                    f"{dataset}/{condition}"
                )

    code = tree_fingerprint(code_root)
    code["snapshot"] = ensure_code_snapshot(registry, code)
    report = {
        "schema_version": 1,
        "frozen_at_utc": utc_now(),
        "purpose": (
            "pre-register untouched main and cross-model journal test evaluations "
            "before any target run"
        ),
        "model_label": args.model_label,
        "model_verifications": model_verifications,
        "retrieval_data_provenance": {
            "build_manifests": input_fingerprints(data_build_paths),
            "gold_labels_used_for_ranking": False,
            "retriever_model_manifest": {
                "path": str(retriever_manifest_path),
                "sha256": sha256_file(retriever_manifest_path),
                "model_id": retriever_manifest["model_id"],
                "huggingface_commit": retriever_manifest["huggingface_commit"],
            },
            "retriever_verification_report": {
                "path": str(retriever_report_path),
                "sha256": sha256_file(retriever_report_path),
                "status": "PASS",
            },
        },
        "datasets": datasets,
        "retrieval_conditions": conditions,
        "random_seed": args.seed,
        "answer_evaluation": {
            "examples_per_cell": args.answer_max_examples,
            "methods": methods,
            "metrics": [
                "normalized answer equivalence to full prefill",
                "raw trimmed exact match to full prefill",
                "generated token-sequence exact match",
                "token F1 and ROUGE-L to full prefill",
                "first-token KL and Jensen-Shannon divergence",
                "top-1 match and top-5/top-10 overlap",
                "steady-state online context prefill fraction (full prefill=1, exact cache hit=0)",
                "exact-prefix reuse control",
                "three fixed random seeds for each K1/K2 suffix budget",
            ],
            "cluster_bootstrap_iterations": 10000,
            "cluster_bootstrap_seed": args.seed,
            "predeclared_pairs": [
                {"left": left, "right": right} for left, right in answer_pairs
            ],
        },
        "frontier_evaluation": {
            "examples_per_cell": args.frontier_max_examples,
            "artifact_sha256": sha256_file(primary_fixed_paths[2]),
            "threshold_reoptimization_on_test": False,
            "metrics": [
                "answer preservation",
                "per-dataset Wilson 95% interval",
                "full-prefill fallback rate",
                "mean recomputed context ratio",
                "frontier exact and within-one conservative accuracy",
            ],
        },
        "query_attention_local_baseline": {
            "examples_per_cell": args.attention_max_examples,
            "budgets": [float(item) for item in attention_budgets],
            "random_seeds": attention_random_seeds,
            "selection_inputs": "current query attention over the stale composed cache",
            "repair_execution": "actual token-local forward recomputation",
            "official_cache_craft_implementation": False,
            "label": "Cache-Craft-motivated operational equal-token-budget baseline",
            "cluster_bootstrap_iterations": 10000,
            "cluster_bootstrap_seed": args.seed,
            "random_comparator": "per-example mean across the three frozen seeds",
        },
        "system_scaling_benchmark": {
            "run_id": f"{args.model_label}_system_scaling_test_{args.system_version}",
            "context_lengths": system_context_lengths,
            "batch_sizes": system_batch_sizes,
            "recompute_ratios": system_recompute_ratios,
            "examples_per_length": args.system_examples_per_length,
            "query_tokens": args.system_query_tokens,
            "warmups": args.system_warmups,
            "repeats": args.system_repeats,
            "scope": (
                "shape-controlled PyTorch GPU microbenchmark with an exact prefix "
                "cache resident on GPU; not production request concurrency"
            ),
        },
        "cross_model_transfer": {
            "models": [
                {
                    "label": model["label"],
                    "config": str(model["config"]),
                    "config_sha256": sha256_file(model["config"]),
                    "model_manifest": str(model["model_manifest"]),
                    "model_manifest_sha256": sha256_file(model["model_manifest"]),
                }
                for model in transfer_models
            ],
            "answer_examples_per_cell": args.transfer_answer_max_examples,
            "frontier_examples_per_cell": args.transfer_frontier_max_examples,
            "answer_methods": methods,
            "selector_artifact_source_model": args.model_label,
            "selector_threshold_reoptimization_on_transfer_models": False,
            "cluster_bootstrap_iterations": 10000,
            "cluster_bootstrap_seed": args.seed,
            "datasets": datasets,
            "retrieval_conditions": conditions,
        },
        "fixed_inputs": input_fingerprints(fixed_paths),
        "baseline_availability_audit": {
            "path": str(args.baseline_audit.resolve()),
            "sha256": sha256_file(args.baseline_audit.resolve()),
            "evidence_files": input_fingerprints(
                [path.resolve() for path in args.baseline_evidence]
            ),
        },
        "test_data": data,
        "target_runs": [
            {"kind": kind, "run_id": run_id, "absent_at_freeze": True}
            for kind, run_id in target_runs
        ],
        "code": code,
        "integrity": {
            "test_outputs_inspected_for_model_selection": False,
            "all_target_run_directories_absent_at_freeze": True,
            "same_source_question_order_across_conditions": True,
            "frontier_prefix_contained_in_answer_prefix": True,
            "attention_prefix_contained_in_answer_prefix": True,
            "cross_model_prefixes_contained_in_main_answer_prefix": True,
            "cross_model_selector_reoptimization": False,
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"out": str(out), "sha256": sha256_file(out)}, indent=2))


if __name__ == "__main__":
    main()
