#!/usr/bin/env python
"""Cluster-bootstrap query-attention versus equal-token random local repair."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402
from scripts.analyze_answer_grid_bootstrap import (  # noqa: E402
    as_float,
    build_dataset_arrays,
    make_scope_rows,
    verify_declared_input,
)
from scripts.run_oracle_kv_drift_local_baseline import budget_label  # noqa: E402


METRIC_FIELDS: tuple[tuple[str, str, bool], ...] = (
    ("answer_preservation", "qa_answer_equivalence_to_fresh_reference", True),
    ("raw_answer_exact", "raw_answer_exact_to_fresh_reference", True),
    (
        "generated_sequence_exact",
        "generated_token_sequence_equivalent_to_fresh_reference",
        True,
    ),
    (
        "changed_and_gold_wrong_rate",
        "answer_changed_from_fresh_reference_and_gold_wrong",
        True,
    ),
    ("gold_exact_match", "gold_exact_match", True),
    ("gold_token_f1", "gold_token_f1", False),
    ("patched_total_context_ratio", "patched_context_ratio", False),
    ("first_token_kl", "first_token_kl_to_fresh_reference", False),
    ("top1_match", "top1_match_to_fresh_reference", True),
    ("selection_planning_seconds", "selection_planning_seconds", False),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        required=True,
        metavar=("ATTENTION_RUN_DIR", "DATA_JSONL"),
    )
    parser.add_argument("--budgets", required=True)
    parser.add_argument("--random-seeds", required=True)
    parser.add_argument("--required-datasets", default="hotpotqa,2wiki,musique")
    parser.add_argument("--required-conditions", default="natural,shuffle,bm25,dense")
    parser.add_argument("--expected-examples-per-source", type=int, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def method_contract(
    budgets: list[float], random_seeds: list[int]
) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    actual = ["prefix_conditioned_composition", "all_fresh_context_chunked_reference"]
    virtual = []
    pairs = []
    for budget in budgets:
        label = budget_label(budget)
        attention = f"query_attention_local_actual_p{label}"
        random_methods = [
            f"random_local_actual_p{label}_seed{seed}" for seed in random_seeds
        ]
        random_mean = f"random_local_actual_p{label}_seed_mean"
        actual.extend([attention, *random_methods])
        virtual.append(random_mean)
        pairs.append((attention, random_mean))
    return actual, virtual, pairs


def load_source(
    run_dir: Path,
    data_path: Path,
    *,
    actual_methods: list[str],
    virtual_methods: list[str],
    budgets: list[float],
    random_seeds: list[int],
    expected_examples: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    manifest_path = run_dir / "run_manifest.json"
    outputs_path = run_dir / "query_attention_local_outputs.jsonl"
    summary_path = run_dir / "query_attention_local_summary.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        raise ValueError(f"attention source is not complete: {run_dir}")
    verify_declared_input(manifest, data_path)
    if summary.get("official_cache_craft_implementation") is not False:
        raise ValueError("attention source incorrectly claims official Cache-Craft code")
    if [float(value) for value in summary.get("budgets", [])] != budgets:
        raise ValueError(f"attention budget contract differs in {run_dir}")
    if [int(value) for value in summary.get("random_seeds", [])] != random_seeds:
        raise ValueError(f"attention random-seed contract differs in {run_dir}")
    if int(summary.get("num_examples", -1)) != expected_examples:
        raise ValueError(f"attention summary example count differs in {run_dir}")
    data_rows = read_jsonl(data_path)
    data_by_id = {str(row["id"]): row for row in data_rows}
    if len(data_by_id) != len(data_rows):
        raise ValueError(f"duplicate data ids in {data_path}")
    by_id: dict[str, dict[str, dict[str, Any]]] = {}
    for row in read_jsonl(outputs_path):
        example_id = str(row["example_id"])
        method = str(row["method"])
        if method in by_id.setdefault(example_id, {}):
            raise ValueError(f"duplicate {method} for {example_id}")
        by_id[example_id][method] = row
    if len(by_id) != expected_examples:
        raise ValueError(
            f"expected {expected_examples} attention examples in {run_dir}, found {len(by_id)}"
        )
    if set().union(*(set(rows) for rows in by_id.values())) != set(actual_methods):
        raise ValueError(f"attention method contract differs in {run_dir}")

    records = []
    cell: tuple[str, str] | None = None
    for example_id in sorted(by_id):
        if example_id not in data_by_id:
            raise ValueError(f"attention id absent from data: {example_id}")
        current = by_id[example_id]
        if set(current) != set(actual_methods):
            raise ValueError(f"incomplete attention methods for {example_id}")
        metadata = data_by_id[example_id].get("source_metadata", {})
        current_cell = (
            str(metadata.get("dataset", "")),
            str(metadata.get("retrieval_condition", "")),
        )
        if metadata.get("split") != "test":
            raise ValueError(f"refusing non-test attention source: {example_id}")
        if cell is None:
            cell = current_cell
        if cell != current_cell:
            raise ValueError(f"mixed attention cell in {run_dir}")
        source_id = str(metadata.get("source_id", ""))
        group_id = f"{current_cell[0]}:{source_id}"
        values_by_method = {
            method: [
                as_float(current[method], field, boolean)
                for _name, field, boolean in METRIC_FIELDS
            ]
            for method in actual_methods
        }
        for budget, virtual_method in zip(budgets, virtual_methods):
            label = budget_label(budget)
            random_methods = [
                f"random_local_actual_p{label}_seed{seed}" for seed in random_seeds
            ]
            values_by_method[virtual_method] = np.asarray(
                [values_by_method[method] for method in random_methods], dtype=np.float64
            ).mean(axis=0).tolist()
        for method, values in values_by_method.items():
            records.append(
                {
                    "dataset": current_cell[0],
                    "condition": current_cell[1],
                    "group_id": group_id,
                    "example_id": example_id,
                    "method": method,
                    "values": values,
                }
            )
    if cell is None:
        raise ValueError(f"empty attention source: {run_dir}")
    return records, {
        "dataset": cell[0],
        "condition": cell[1],
        "run_dir": str(run_dir),
        "run_manifest_sha256": sha256_file(manifest_path),
        "outputs_sha256": sha256_file(outputs_path),
        "summary_sha256": sha256_file(summary_path),
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "n_examples": expected_examples,
    }


def main() -> None:
    args = parse_args()
    budgets = [float(item) for item in args.budgets.split(",") if item.strip()]
    random_seeds = [int(item) for item in args.random_seeds.split(",") if item.strip()]
    datasets = [item.strip() for item in args.required_datasets.split(",") if item.strip()]
    conditions = [item.strip() for item in args.required_conditions.split(",") if item.strip()]
    if (
        not budgets
        or len(budgets) != len(set(budgets))
        or any(value < 0.0 or value > 1.0 for value in budgets)
        or not random_seeds
        or len(random_seeds) != len(set(random_seeds))
        or args.expected_examples_per_source <= 0
        or args.iterations <= 0
    ):
        raise ValueError("invalid attention bootstrap protocol")
    actual_methods, virtual_methods, pairs = method_contract(budgets, random_seeds)
    methods = [*actual_methods, *virtual_methods]

    records = []
    sources = []
    cells = set()
    for run_text, data_text in args.source:
        current, source = load_source(
            Path(run_text),
            Path(data_text),
            actual_methods=actual_methods,
            virtual_methods=virtual_methods,
            budgets=budgets,
            random_seeds=random_seeds,
            expected_examples=args.expected_examples_per_source,
        )
        cell = (source["dataset"], source["condition"])
        if cell in cells:
            raise ValueError(f"duplicate attention cell: {cell}")
        cells.add(cell)
        records.extend(current)
        sources.append(source)
    required_cells = {(dataset, condition) for dataset in datasets for condition in conditions}
    if cells != required_cells:
        raise ValueError(
            f"attention grid mismatch; missing={sorted(required_cells-cells)}, "
            f"unexpected={sorted(cells-required_cells)}"
        )
    arrays, group_ids = build_dataset_arrays(
        records,
        datasets=datasets,
        conditions=conditions,
        methods=methods,
        num_metrics=len(METRIC_FIELDS),
    )

    rng = np.random.default_rng(args.seed)
    total_groups = sum(len(group_ids[dataset]) for dataset in datasets)
    overall_point = sum(
        arrays[dataset].mean(axis=(0, 1)) * len(group_ids[dataset])
        for dataset in datasets
    ) / total_groups
    overall_draws = np.zeros(
        (args.iterations, len(methods), len(METRIC_FIELDS)), dtype=np.float64
    )
    dataset_points = {}
    dataset_draws = {}
    cell_points = {}
    cell_draws = {}
    for dataset in datasets:
        array = arrays[dataset]
        group_count = array.shape[0]
        weights = rng.multinomial(
            group_count,
            np.full(group_count, 1.0 / group_count),
            size=args.iterations,
        ).astype(np.float64)
        weights /= group_count
        condition_draws = np.einsum("bg,gcmk->bcmk", weights, array, optimize=True)
        dataset_points[dataset] = array.mean(axis=(0, 1))
        dataset_draws[dataset] = condition_draws.mean(axis=1)
        overall_draws += dataset_draws[dataset] * len(group_ids[dataset]) / total_groups
        for condition_index, condition in enumerate(conditions):
            cell_points[(dataset, condition)] = array[:, condition_index].mean(axis=0)
            cell_draws[(dataset, condition)] = condition_draws[:, condition_index]

    method_rows = []
    pair_rows = []
    scope_specs = [
        (
            "overall",
            overall_point,
            overall_draws,
            total_groups,
            total_groups * len(conditions),
        )
    ]
    for dataset in datasets:
        count = len(group_ids[dataset])
        scope_specs.append(
            (f"dataset:{dataset}", dataset_points[dataset], dataset_draws[dataset], count, count * len(conditions))
        )
        for condition in conditions:
            scope_specs.append(
                (f"cell:{dataset}/{condition}", cell_points[(dataset, condition)], cell_draws[(dataset, condition)], count, count)
            )
    for scope, point, draws, n_groups, n_rows in scope_specs:
        current_methods, current_pairs = make_scope_rows(
            point,
            draws,
            scope=scope,
            methods=methods,
            pairs=pairs,
            n_groups=n_groups,
            n_condition_rows=n_rows,
            metric_fields=METRIC_FIELDS,
        )
        method_rows.extend(current_methods)
        pair_rows.extend(current_pairs)

    report = {
        "schema_version": 1,
        "method_scope": (
            "operational query-attention-ranked token-local recomputation versus "
            "the per-example mean of three equal-token-budget random seeds; not an "
            "official Cache-Craft implementation"
        ),
        "bootstrap_unit": (
            "source question, stratified by dataset; retrieval conditions, methods, "
            "and random seeds remain paired"
        ),
        "iterations": args.iterations,
        "seed": args.seed,
        "budgets": budgets,
        "random_seeds": random_seeds,
        "datasets": datasets,
        "conditions": conditions,
        "actual_methods": actual_methods,
        "virtual_random_seed_means": virtual_methods,
        "sources": sources,
        "method_summary": method_rows,
        "paired_differences": pair_rows,
        "integrity": {
            "all_inputs_are_test_split": True,
            "complete_required_grid": True,
            "equal_token_budget_random_comparison": True,
            "random_seeds_paired_within_example": True,
            "official_cache_craft_implementation": False,
        },
    }
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite attention bootstrap: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out": str(out),
                "sources": len(sources),
                "source_groups": total_groups,
                "method_rows": len(method_rows),
                "pair_rows": len(pair_rows),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
