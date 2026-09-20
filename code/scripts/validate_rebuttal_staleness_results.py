#!/usr/bin/env python
"""Validate completeness and invariants of a rebuttal staleness sweep."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_METHODS = {
    "mixed_no_repair",
    "query_actual_doc_only_k1",
    "query_actual_downstream_w4_k1",
    "query_actual_suffix_k1",
    "risk_actual_suffix_k1",
    "risk_actual_suffix_k2",
    "earliest_stale_actual_suffix_oracle",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, default=50)
    parser.add_argument("--probabilities", default="0,0.25,0.5,0.75,1")
    parser.add_argument("--mask-seeds", default="13,29,47")
    parser.add_argument("--labels", default="N1:1,N2:2,N4:4,N8:8,N16:16")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.results_dir / "staleness_doccount_outputs.jsonl")
    probabilities = [float(item) for item in args.probabilities.split(",")]
    mask_seeds = [int(item) for item in args.mask_seeds.split(",")]
    label_docs = {
        label: int(num_documents)
        for label, num_documents in (
            item.split(":", 1) for item in args.labels.split(",")
        )
    }

    failures: list[str] = []
    diagnostics: dict[str, Any] = {}
    keys = [
        (
            row["dataset_label"],
            row["example_id"],
            int(row["mask_seed"]),
            float(row["stale_probability"]),
            row["method"],
        )
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        failures.append("duplicate cell/example/method keys")

    expected_rows = (
        len(label_docs)
        * args.expected_examples
        * len(probabilities)
        * len(mask_seeds)
        * len(EXPECTED_METHODS)
    )
    if len(rows) != expected_rows:
        failures.append(f"row count {len(rows)} != expected {expected_rows}")

    ids_by_label: dict[str, set[str]] = defaultdict(set)
    cell_counts: dict[tuple[str, float, str], int] = defaultdict(int)
    state_by_cell: dict[tuple[str, str, int, float], tuple[int, ...]] = {}
    methods_by_state: dict[tuple[str, str, int, float], set[str]] = defaultdict(set)
    rows_by_cell: dict[tuple[str, float, str], list[dict[str, Any]]] = defaultdict(list)
    observed_probabilities: set[float] = set()
    observed_seeds: set[int] = set()
    oracle_kl_values: list[float] = []
    for row in rows:
        label = str(row["dataset_label"])
        num_documents = int(row["num_documents"])
        if label not in label_docs or num_documents != label_docs.get(label):
            failures.append(f"unexpected label/document count: {label}/{num_documents}")
        if row["method"] not in EXPECTED_METHODS:
            failures.append(f"unexpected method: {row['method']}")
        ids_by_label[label].add(str(row["example_id"]))
        probability = float(row["stale_probability"])
        seed = int(row["mask_seed"])
        observed_probabilities.add(probability)
        observed_seeds.add(seed)
        aggregate_key = (label, probability, row["method"])
        cell_counts[aggregate_key] += 1
        rows_by_cell[aggregate_key].append(row)
        cell_key = (
            label,
            str(row["example_id"]),
            seed,
            probability,
        )
        methods_by_state[cell_key].add(str(row["method"]))
        stale_positions = tuple(int(item) for item in row["stale_positions"])
        previous = state_by_cell.setdefault(cell_key, stale_positions)
        if previous != stale_positions:
            failures.append(f"methods disagree on stale mask for {cell_key}")
        if row.get("invariant_failures"):
            failures.append(f"persisted invariant failure for {cell_key}")

        expected_stale_count = len(stale_positions)
        if int(row["stale_doc_count"]) != expected_stale_count:
            failures.append(f"stale count mismatch for {cell_key}/{row['method']}")
        if any(position < 1 or position >= num_documents for position in stale_positions):
            failures.append(f"stale position out of range for {cell_key}/{row['method']}")
        expected_fraction = (
            expected_stale_count / (num_documents - 1) if num_documents > 1 else 0.0
        )
        if not math.isclose(
            float(row["realized_stale_fraction"]),
            expected_fraction,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            failures.append(f"stale fraction mismatch for {cell_key}/{row['method']}")
        if probability == 0.0 and stale_positions:
            failures.append(f"p=0 mask is nonempty for {cell_key}/{row['method']}")
        if probability == 1.0 and stale_positions != tuple(range(1, num_documents)):
            failures.append(f"p=1 mask is incomplete for {cell_key}/{row['method']}")

        start = int(row["repair_start"])
        end = int(row["repair_end"])
        if not (0 <= start <= end <= num_documents):
            failures.append(f"invalid repair range for {cell_key}/{row['method']}")
        ratio = float(row["recomputed_token_ratio"])
        if not math.isfinite(ratio) or not 0.0 <= ratio <= 1.0:
            failures.append(f"invalid recompute ratio for {cell_key}/{row['method']}")
        if int(row["recomputed_token_count"]) < 0:
            failures.append(f"negative recompute count for {cell_key}/{row['method']}")
        if (start == end) != (int(row["recomputed_token_count"]) == 0):
            failures.append(f"repair range/count disagreement for {cell_key}/{row['method']}")
        method = str(row["method"])
        if method == "mixed_no_repair" and (start, end) != (
            num_documents,
            num_documents,
        ):
            failures.append(f"mixed baseline is not a no-op for {cell_key}")
        if method == "query_actual_doc_only_k1" and end != min(
            num_documents, start + 1
        ):
            failures.append(f"query doc-only range mismatch for {cell_key}")
        if method == "query_actual_downstream_w4_k1" and end != min(
            num_documents, start + 4
        ):
            failures.append(f"query W4 range mismatch for {cell_key}")
        if method in {
            "query_actual_suffix_k1",
            "risk_actual_suffix_k1",
            "risk_actual_suffix_k2",
        } and end != num_documents:
            failures.append(f"suffix action does not end at N for {cell_key}/{method}")
        if method == "earliest_stale_actual_suffix_oracle":
            expected_start = min(stale_positions) if stale_positions else num_documents
            if (start, end) != (expected_start, num_documents):
                failures.append(f"oracle range mismatch for {cell_key}")
            if not row["answer_equivalence_to_fresh_reference"]:
                failures.append(f"oracle normalized-answer mismatch for {cell_key}")
            if not row["raw_answer_exact_to_fresh_reference"]:
                failures.append(f"oracle postprocessed-string mismatch for {cell_key}")
            if not row["generated_token_sequence_equivalent_to_fresh_reference"]:
                failures.append(f"oracle generated-token mismatch for {cell_key}")
            oracle_kl_values.append(float(row["first_token_kl_to_fresh_reference"]))
        if probability == 1.0 and not row.get("p1_mixed_equals_prefix_qa_answer"):
            failures.append(f"p=1 mixed/prefix normalized-answer mismatch for {cell_key}")

        if num_documents == 1:
            if stale_positions or int(row["stale_doc_count"]) != 0:
                failures.append(f"N=1 has a stale document for {cell_key}/{method}")
            if (start, end) != (1, 1):
                failures.append(f"N=1 action is not a no-op for {cell_key}/{method}")
            if int(row["recomputed_token_count"]) != 0 or ratio != 0.0:
                failures.append(f"N=1 has nonzero repair cost for {cell_key}/{method}")

        is_endpoint = float(row["stale_probability"]) == 0.0 or num_documents == 1
        if is_endpoint:
            if not row["raw_answer_exact_to_fresh_reference"]:
                failures.append(f"raw endpoint mismatch for {cell_key}/{row['method']}")
            if not row["generated_token_sequence_equivalent_to_fresh_reference"]:
                failures.append(f"token endpoint mismatch for {cell_key}/{row['method']}")

    id_sets = list(ids_by_label.values())
    if any(len(ids) != args.expected_examples for ids in id_sets):
        failures.append(
            "example count by label mismatch: "
            + json.dumps({label: len(ids) for label, ids in ids_by_label.items()})
        )
    if id_sets and any(ids != id_sets[0] for ids in id_sets[1:]):
        failures.append("example ID sets are not paired across document counts")

    expected_cell_rows = args.expected_examples * len(mask_seeds)
    for label in label_docs:
        for probability in probabilities:
            for method in EXPECTED_METHODS:
                observed = cell_counts[(label, probability, method)]
                if observed != expected_cell_rows:
                    failures.append(
                        f"cell count {label}/{probability}/{method}: "
                        f"{observed} != {expected_cell_rows}"
                    )

    if observed_probabilities != set(probabilities):
        failures.append(
            f"probability set {sorted(observed_probabilities)} != expected {probabilities}"
        )
    if observed_seeds != set(mask_seeds):
        failures.append(f"seed set {sorted(observed_seeds)} != expected {mask_seeds}")
    for state, methods in methods_by_state.items():
        if methods != EXPECTED_METHODS:
            failures.append(
                f"state method set mismatch for {state}: {sorted(methods)}"
            )

    # Bernoulli masks must be nested as p increases for a fixed example/seed.
    masks_by_unit: dict[tuple[str, str, int], list[tuple[float, set[int]]]] = defaultdict(list)
    for (label, example_id, seed, probability), mask in state_by_cell.items():
        masks_by_unit[(label, example_id, seed)].append((probability, set(mask)))
    for unit, masks in masks_by_unit.items():
        ordered = sorted(masks)
        for (_left_p, left), (_right_p, right) in zip(ordered, ordered[1:], strict=False):
            if not left.issubset(right):
                failures.append(f"non-nested probability masks for {unit}")

    manifest_path = args.results_dir / "staleness_doccount_manifest.json"
    manifest = read_json(manifest_path, failures, "manifest")
    data_by_label: dict[str, dict[str, dict[str, Any]]] = {}
    if manifest:
        validate_manifest(
            manifest,
            label_docs=label_docs,
            probabilities=probabilities,
            mask_seeds=mask_seeds,
            expected_examples=args.expected_examples,
            failures=failures,
        )
        data_by_label = load_and_validate_paired_data(
            manifest,
            label_docs=label_docs,
            expected_examples=args.expected_examples,
            failures=failures,
        )
        validate_cross_n_masks(
            state_by_cell,
            data_by_label=data_by_label,
            failures=failures,
        )

    summary_path = args.results_dir / "staleness_doccount_summary.json"
    summary = read_json(summary_path, failures, "summary")
    if summary:
        validate_summary(
            summary,
            rows=rows,
            rows_by_cell=rows_by_cell,
            expected_cell_rows=expected_cell_rows,
            failures=failures,
        )

    diagnostics["oracle_first_token_kl_max"] = (
        max(oracle_kl_values) if oracle_kl_values else None
    )
    diagnostics["oracle_first_token_kl_mean"] = (
        statistics.fmean(oracle_kl_values) if oracle_kl_values else None
    )
    diagnostics["observed_probabilities"] = sorted(observed_probabilities)
    diagnostics["observed_mask_seeds"] = sorted(observed_seeds)

    report: dict[str, Any] = {
        "status": "PASS" if not failures else "FAIL",
        "num_rows": len(rows),
        "expected_rows": expected_rows,
        "num_unique_keys": len(set(keys)),
        "paired_example_count": len(id_sets[0]) if id_sets else 0,
        "num_failures": len(failures),
        "failures": failures,
        "diagnostics": diagnostics,
    }
    output_path = args.results_dir / "validation_report.json"
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_json(path: Path, failures: list[str], label: str) -> dict[str, Any]:
    if not path.exists():
        failures.append(f"missing {label}: {path}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"invalid {label}: {exc}")
        return {}
    if not isinstance(value, dict):
        failures.append(f"{label} is not a JSON object")
        return {}
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(
    manifest: dict[str, Any],
    *,
    label_docs: dict[str, int],
    probabilities: list[float],
    mask_seeds: list[int],
    expected_examples: int,
    failures: list[str],
) -> None:
    if set(manifest.get("methods", [])) != EXPECTED_METHODS:
        failures.append("manifest method list mismatch")
    if [float(item) for item in manifest.get("probabilities", [])] != probabilities:
        failures.append("manifest probability list mismatch")
    if [int(item) for item in manifest.get("mask_seeds", [])] != mask_seeds:
        failures.append("manifest mask-seed list mismatch")
    if int(manifest.get("max_examples", -1)) != expected_examples:
        failures.append("manifest max_examples mismatch")

    config_path = Path(str(manifest.get("config_path", "")))
    if not config_path.exists():
        failures.append(f"manifest config path missing: {config_path}")
    elif file_sha256(config_path) != manifest.get("config_sha256"):
        failures.append("manifest config hash mismatch")

    specs = manifest.get("data_specs", [])
    if {str(item.get("label")) for item in specs} != set(label_docs):
        failures.append("manifest data labels mismatch")
    for item in specs:
        path = Path(str(item.get("path", "")))
        if not path.exists():
            failures.append(f"manifest data path missing: {path}")
        elif file_sha256(path) != item.get("sha256"):
            failures.append(f"manifest data hash mismatch: {path}")
    for raw_path, expected_hash in manifest.get("implementation_sha256", {}).items():
        path = Path(raw_path)
        if not path.exists():
            failures.append(f"manifest implementation path missing: {path}")
        elif file_sha256(path) != expected_hash:
            failures.append(f"manifest implementation hash mismatch: {path}")


def load_and_validate_paired_data(
    manifest: dict[str, Any],
    *,
    label_docs: dict[str, int],
    expected_examples: int,
    failures: list[str],
) -> dict[str, dict[str, dict[str, Any]]]:
    data_by_label: dict[str, dict[str, dict[str, Any]]] = {}
    order_by_label: dict[str, list[str]] = {}
    for spec in manifest.get("data_specs", []):
        label = str(spec.get("label"))
        path = Path(str(spec.get("path")))
        if label not in label_docs or not path.exists():
            continue
        examples = read_jsonl(path)[:expected_examples]
        order = [str(item["id"]) for item in examples]
        order_by_label[label] = order
        mapped: dict[str, dict[str, Any]] = {}
        for item in examples:
            example_id = str(item["id"])
            documents = list(item["documents"])
            if len(documents) != label_docs[label]:
                failures.append(f"input document count mismatch for {label}/{example_id}")
            identities = [
                (str(doc.get("title", "")), str(doc.get("text", "")))
                for doc in documents
            ]
            if len(identities) != len(set(identities)):
                failures.append(f"duplicate input document identity for {label}/{example_id}")
            if any(float(doc.get("retrieval_score", 0.0)) != 0.0 for doc in documents):
                failures.append(f"nonzero retrieval score for {label}/{example_id}")
            mapped[example_id] = {
                "question": item.get("question"),
                "gold_answer": item.get("gold_answer"),
                "documents": identities,
            }
        data_by_label[label] = mapped

    orders = list(order_by_label.values())
    if orders and any(order != orders[0] for order in orders[1:]):
        failures.append("manifest inputs do not have identical ordered IDs")
    labels_by_n = sorted(label_docs, key=label_docs.get)
    for left_label, right_label in zip(labels_by_n, labels_by_n[1:], strict=False):
        left = data_by_label.get(left_label, {})
        right = data_by_label.get(right_label, {})
        for example_id in set(left) & set(right):
            if left[example_id]["question"] != right[example_id]["question"]:
                failures.append(f"question mismatch across N for {example_id}")
            if left[example_id]["gold_answer"] != right[example_id]["gold_answer"]:
                failures.append(f"gold mismatch across N for {example_id}")
            left_docs = left[example_id]["documents"]
            right_docs = right[example_id]["documents"]
            if not set(left_docs).issubset(set(right_docs)):
                failures.append(f"document sets are not nested for {example_id}")
            projected = [identity for identity in right_docs if identity in set(left_docs)]
            if projected != left_docs:
                failures.append(f"shared-document order changed across N for {example_id}")
    return data_by_label


def validate_cross_n_masks(
    state_by_cell: dict[tuple[str, str, int, float], tuple[int, ...]],
    *,
    data_by_label: dict[str, dict[str, dict[str, Any]]],
    failures: list[str],
) -> None:
    stale_identity_sets: dict[tuple[str, str, int, float], set[tuple[str, str]]] = {}
    for state, positions in state_by_cell.items():
        label, example_id, seed, probability = state
        example = data_by_label.get(label, {}).get(example_id)
        if example is None:
            continue
        identities = example["documents"]
        stale_identity_sets[state] = {identities[position] for position in positions}
    grouped: dict[tuple[str, int, float], list[tuple[str, set[tuple[str, str]]]]] = defaultdict(list)
    for (label, example_id, seed, probability), stale in stale_identity_sets.items():
        grouped[(example_id, seed, probability)].append((label, stale))
    for unit, values in grouped.items():
        for index, (left_label, left_stale) in enumerate(values):
            left_docs = set(data_by_label[left_label][unit[0]]["documents"][1:])
            for right_label, right_stale in values[index + 1 :]:
                right_docs = set(
                    data_by_label[right_label][unit[0]]["documents"][1:]
                )
                shared = left_docs & right_docs
                if (left_stale & shared) != (right_stale & shared):
                    failures.append(f"shared-document stale mask mismatch for {unit}")


def validate_summary(
    summary: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    rows_by_cell: dict[tuple[str, float, str], list[dict[str, Any]]],
    expected_cell_rows: int,
    failures: list[str],
) -> None:
    if int(summary.get("num_rows", -1)) != len(rows):
        failures.append("summary row count mismatch")
    if int(summary.get("num_invariant_failures", -1)) != 0:
        failures.append("summary reports invariant failures")
    cell_rows = summary.get("method_cell_summary", [])
    if len(cell_rows) != len(rows_by_cell):
        failures.append("summary cell count mismatch")
        return
    by_key = {
        (
            str(item["dataset_label"]),
            float(item["stale_probability"]),
            str(item["method"]),
        ): item
        for item in cell_rows
    }
    if set(by_key) != set(rows_by_cell):
        failures.append("summary cell key set mismatch")
        return
    metric_fields = {
        "answer_equivalence_to_fresh_reference": "answer_equivalence_to_fresh_reference",
        "raw_answer_exact_to_fresh_reference": "raw_answer_exact_to_fresh_reference",
        "token_sequence_equivalence_to_fresh_reference": (
            "generated_token_sequence_equivalent_to_fresh_reference"
        ),
        "avg_first_token_kl_to_fresh_reference": "first_token_kl_to_fresh_reference",
        "avg_recomputed_token_ratio": "recomputed_token_ratio",
    }
    for key, raw_items in rows_by_cell.items():
        item = by_key[key]
        if int(item.get("num_rows", -1)) != expected_cell_rows:
            failures.append(f"summary cell row count mismatch for {key}")
        for summary_field, raw_field in metric_fields.items():
            expected = statistics.fmean(float(row[raw_field]) for row in raw_items)
            observed = float(item[summary_field])
            if not math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"summary metric mismatch for {key}/{summary_field}")


if __name__ == "__main__":
    main()
