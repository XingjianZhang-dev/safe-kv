#!/usr/bin/env python
"""Cluster-bootstrap a complete answer grid over source questions.

All retrieval conditions belonging to one original question are resampled
together.  This preserves paired comparisons both across methods and across
retrieval orders, and avoids treating the four orderings as independent data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from safekv_ipm.run_registry import sha256_file  # noqa: E402


METRIC_FIELDS: tuple[tuple[str, str, bool], ...] = (
    ("answer_preservation", "answer_equivalence_to_full_prefill", True),
    ("raw_answer_exact", "raw_trimmed_answer_exact_to_full_prefill", True),
    ("generated_sequence_exact", "generated_token_sequence_exact_to_full_prefill", True),
    ("response_token_f1", "response_token_f1_to_full_prefill", False),
    ("response_rouge_l_f1", "response_rouge_l_f1_to_full_prefill", False),
    ("changed_and_gold_wrong_rate", "answer_changed_and_gold_wrong", True),
    ("gold_exact_match", "gold_exact_match", True),
    ("gold_token_f1", "gold_token_f1", False),
    (
        "online_context_prefill_fraction",
        "online_context_prefill_fraction",
        False,
    ),
    ("first_token_kl", "first_token_kl_full_to_method", False),
    ("first_token_js", "first_token_js_divergence", False),
    ("top1_match", "top1_match", True),
    ("top5_overlap", "top5_overlap", False),
    ("top10_overlap", "top10_overlap", False),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        action="append",
        nargs=2,
        required=True,
        metavar=("ANSWER_RUN_DIR", "DATA_JSONL"),
    )
    parser.add_argument("--methods", required=True)
    parser.add_argument(
        "--pair",
        action="append",
        nargs=2,
        default=[],
        metavar=("LEFT_METHOD", "RIGHT_METHOD"),
    )
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


def as_float(row: dict[str, Any], field: str, boolean: bool) -> float:
    if field not in row:
        raise ValueError(f"missing required metric field {field!r}")
    value = row[field]
    if boolean:
        if isinstance(value, bool):
            return float(value)
        if value in (0, 1):
            return float(value)
        raise ValueError(f"field {field!r} is not boolean: {value!r}")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"field {field!r} is non-finite")
    return result


def verify_declared_input(manifest: dict[str, Any], path: Path) -> None:
    expected_hash = sha256_file(path)
    matches = [
        item
        for item in manifest.get("inputs", [])
        if Path(str(item.get("path", ""))).resolve() == path.resolve()
    ]
    if len(matches) != 1 or matches[0].get("sha256") != expected_hash:
        raise ValueError(f"run manifest does not freeze the declared data input: {path}")


def load_source(
    run_dir: Path,
    data_path: Path,
    *,
    methods: list[str],
    expected_examples: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    run_dir = run_dir.resolve()
    data_path = data_path.resolve()
    manifest_path = run_dir / "run_manifest.json"
    outputs_path = run_dir / "answer_eval_outputs.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed" or manifest.get("exit_code") != 0:
        raise ValueError(f"answer source is not complete: {run_dir}")
    verify_declared_input(manifest, data_path)
    data_rows = read_jsonl(data_path)
    data_by_id = {str(row["id"]): row for row in data_rows}
    if len(data_by_id) != len(data_rows):
        raise ValueError(f"duplicate data ids in {data_path}")
    output_rows = read_jsonl(outputs_path)
    by_id: dict[str, dict[str, dict[str, Any]]] = {}
    ignored_methods = set()
    for row in output_rows:
        example_id = str(row["example_id"])
        method = str(row["method"])
        if method not in methods:
            ignored_methods.add(method)
            continue
        if method in by_id.setdefault(example_id, {}):
            raise ValueError(f"duplicate {method} for {example_id}")
        by_id[example_id][method] = row
    if len(by_id) != expected_examples:
        raise ValueError(
            f"expected {expected_examples} evaluated examples in {run_dir}, found {len(by_id)}"
        )
    unknown = set(by_id) - set(data_by_id)
    if unknown:
        raise ValueError(f"answer ids absent from data: {sorted(unknown)[:3]}")

    records = []
    cell: tuple[str, str] | None = None
    for example_id in sorted(by_id):
        current_methods = by_id[example_id]
        if set(current_methods) != set(methods):
            raise ValueError(f"incomplete method set for {example_id}")
        metadata = data_by_id[example_id].get("source_metadata", {})
        current_cell = (
            str(metadata.get("dataset", "")),
            str(metadata.get("retrieval_condition", "")),
        )
        if metadata.get("split") != "test":
            raise ValueError(f"refusing non-test answer source: {example_id}")
        if cell is None:
            cell = current_cell
        if cell != current_cell:
            raise ValueError(f"mixed dataset/condition in {run_dir}")
        source_id = str(metadata.get("source_id", ""))
        if not source_id:
            raise ValueError(f"missing source_id for {example_id}")
        for method in methods:
            row = current_methods[method]
            context_count = int(row.get("context_token_count", 0))
            online_count = int(row.get("online_context_prefill_token_count", -1))
            online_fraction = as_float(
                row, "online_context_prefill_fraction", False
            )
            if (
                context_count <= 0
                or online_count < 0
                or online_count > context_count
                or not np.isclose(online_fraction, online_count / context_count)
            ):
                raise ValueError(
                    f"invalid online context accounting for {example_id}/{method}"
                )
            records.append(
                {
                    "dataset": current_cell[0],
                    "condition": current_cell[1],
                    "group_id": f"{current_cell[0]}:{source_id}",
                    "example_id": example_id,
                    "method": method,
                    "values": [
                        as_float(row, field, boolean)
                        for _name, field, boolean in METRIC_FIELDS
                    ],
                }
            )
    if cell is None:
        raise ValueError(f"empty answer source: {run_dir}")
    source = {
        "dataset": cell[0],
        "condition": cell[1],
        "run_dir": str(run_dir),
        "run_manifest_sha256": sha256_file(manifest_path),
        "answer_outputs_sha256": sha256_file(outputs_path),
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "n_examples": expected_examples,
        "ignored_additional_methods": sorted(ignored_methods),
    }
    return records, source


def build_dataset_arrays(
    records: list[dict[str, Any]],
    *,
    datasets: list[str],
    conditions: list[str],
    methods: list[str],
    num_metrics: int = len(METRIC_FIELDS),
) -> tuple[dict[str, np.ndarray], dict[str, list[str]]]:
    by_key = {
        (row["dataset"], row["condition"], row["group_id"], row["method"]): row
        for row in records
    }
    if len(by_key) != len(records):
        raise ValueError("duplicate dataset/condition/group/method records")
    arrays = {}
    group_ids_by_dataset = {}
    for dataset in datasets:
        group_ids = sorted(
            {row["group_id"] for row in records if row["dataset"] == dataset}
        )
        if not group_ids:
            raise ValueError(f"no answer groups for {dataset}")
        array = np.empty(
            (len(group_ids), len(conditions), len(methods), num_metrics),
            dtype=np.float64,
        )
        for group_index, group_id in enumerate(group_ids):
            for condition_index, condition in enumerate(conditions):
                for method_index, method in enumerate(methods):
                    key = (dataset, condition, group_id, method)
                    if key not in by_key:
                        raise ValueError(f"missing paired answer record: {key}")
                    array[group_index, condition_index, method_index] = by_key[key][
                        "values"
                    ]
        arrays[dataset] = array
        group_ids_by_dataset[dataset] = group_ids
    return arrays, group_ids_by_dataset


def percentile_interval(draws: np.ndarray) -> tuple[float, float]:
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def make_scope_rows(
    point: np.ndarray,
    draws: np.ndarray,
    *,
    scope: str,
    methods: list[str],
    pairs: list[tuple[str, str]],
    n_groups: int,
    n_condition_rows: int,
    metric_fields: tuple[tuple[str, str, bool], ...] = METRIC_FIELDS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    method_rows = []
    for method_index, method in enumerate(methods):
        for metric_index, (metric, _field, _boolean) in enumerate(metric_fields):
            low, high = percentile_interval(draws[:, method_index, metric_index])
            method_rows.append(
                {
                    "scope": scope,
                    "method": method,
                    "metric": metric,
                    "estimate": float(point[method_index, metric_index]),
                    "cluster_bootstrap_ci95_low": low,
                    "cluster_bootstrap_ci95_high": high,
                    "n_source_groups": n_groups,
                    "n_condition_rows": n_condition_rows,
                }
            )
    method_indices = {method: index for index, method in enumerate(methods)}
    pair_rows = []
    for left, right in pairs:
        left_index = method_indices[left]
        right_index = method_indices[right]
        delta = point[left_index] - point[right_index]
        delta_draws = draws[:, left_index] - draws[:, right_index]
        for metric_index, (metric, _field, _boolean) in enumerate(metric_fields):
            values = delta_draws[:, metric_index]
            low, high = percentile_interval(values)
            pair_rows.append(
                {
                    "scope": scope,
                    "left_method": left,
                    "right_method": right,
                    "metric": metric,
                    "delta_left_minus_right": float(delta[metric_index]),
                    "cluster_bootstrap_ci95_low": low,
                    "cluster_bootstrap_ci95_high": high,
                    "bootstrap_probability_delta_le_zero": float(np.mean(values <= 0.0)),
                    "n_source_groups": n_groups,
                    "n_condition_rows": n_condition_rows,
                }
            )
    return method_rows, pair_rows


def main() -> None:
    args = parse_args()
    methods = [item.strip() for item in args.methods.split(",") if item.strip()]
    datasets = [item.strip() for item in args.required_datasets.split(",") if item.strip()]
    conditions = [item.strip() for item in args.required_conditions.split(",") if item.strip()]
    pairs = [(left, right) for left, right in args.pair]
    if (
        not methods
        or len(methods) != len(set(methods))
        or not datasets
        or not conditions
        or args.expected_examples_per_source <= 0
        or args.iterations <= 0
    ):
        raise ValueError("invalid answer-grid bootstrap protocol")
    if any(left not in methods or right not in methods or left == right for left, right in pairs):
        raise ValueError("all pair methods must be distinct members of --methods")

    records = []
    sources = []
    cells = set()
    for run_text, data_text in args.source:
        current, source = load_source(
            Path(run_text),
            Path(data_text),
            methods=methods,
            expected_examples=args.expected_examples_per_source,
        )
        cell = (source["dataset"], source["condition"])
        if cell in cells:
            raise ValueError(f"duplicate answer grid cell: {cell}")
        cells.add(cell)
        records.extend(current)
        sources.append(source)
    required_cells = {(dataset, condition) for dataset in datasets for condition in conditions}
    if cells != required_cells:
        raise ValueError(
            f"answer grid mismatch; missing={sorted(required_cells-cells)}, "
            f"unexpected={sorted(cells-required_cells)}"
        )
    arrays, group_ids = build_dataset_arrays(
        records, datasets=datasets, conditions=conditions, methods=methods
    )

    rng = np.random.default_rng(args.seed)
    dataset_points = {dataset: arrays[dataset].mean(axis=(0, 1)) for dataset in datasets}
    dataset_draws = {}
    cell_points = {}
    cell_draws = {}
    total_groups = sum(len(group_ids[dataset]) for dataset in datasets)
    overall_point = sum(
        dataset_points[dataset] * len(group_ids[dataset]) for dataset in datasets
    ) / total_groups
    overall_draws = np.zeros(
        (args.iterations, len(methods), len(METRIC_FIELDS)), dtype=np.float64
    )
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
        dataset_draws[dataset] = condition_draws.mean(axis=1)
        overall_draws += (
            dataset_draws[dataset] * len(group_ids[dataset]) / total_groups
        )
        for condition_index, condition in enumerate(conditions):
            cell_points[(dataset, condition)] = array[:, condition_index].mean(axis=0)
            cell_draws[(dataset, condition)] = condition_draws[:, condition_index]

    method_rows = []
    pair_rows = []
    current_methods, current_pairs = make_scope_rows(
        overall_point,
        overall_draws,
        scope="overall",
        methods=methods,
        pairs=pairs,
        n_groups=total_groups,
        n_condition_rows=total_groups * len(conditions),
    )
    method_rows.extend(current_methods)
    pair_rows.extend(current_pairs)
    for dataset in datasets:
        current_methods, current_pairs = make_scope_rows(
            dataset_points[dataset],
            dataset_draws[dataset],
            scope=f"dataset:{dataset}",
            methods=methods,
            pairs=pairs,
            n_groups=len(group_ids[dataset]),
            n_condition_rows=len(group_ids[dataset]) * len(conditions),
        )
        method_rows.extend(current_methods)
        pair_rows.extend(current_pairs)
        for condition in conditions:
            current_methods, current_pairs = make_scope_rows(
                cell_points[(dataset, condition)],
                cell_draws[(dataset, condition)],
                scope=f"cell:{dataset}/{condition}",
                methods=methods,
                pairs=pairs,
                n_groups=len(group_ids[dataset]),
                n_condition_rows=len(group_ids[dataset]),
            )
            method_rows.extend(current_methods)
            pair_rows.extend(current_pairs)

    report = {
        "schema_version": 1,
        "bootstrap_unit": (
            "source question, stratified by dataset; all retrieval conditions and "
            "all methods for a sampled question remain paired"
        ),
        "iterations": args.iterations,
        "seed": args.seed,
        "datasets": datasets,
        "conditions": conditions,
        "methods": methods,
        "pairs": [{"left": left, "right": right} for left, right in pairs],
        "metric_fields": [
            {"metric": name, "source_field": field, "boolean": boolean}
            for name, field, boolean in METRIC_FIELDS
        ],
        "sources": sources,
        "method_summary": method_rows,
        "paired_differences": pair_rows,
        "integrity": {
            "all_inputs_are_test_split": True,
            "complete_required_grid": True,
            "retrieval_conditions_clustered_by_source_question": True,
            "methods_paired_within_every_example": True,
        },
    }
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"refusing to overwrite answer bootstrap: {out}")
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
