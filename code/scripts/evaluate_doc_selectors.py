#!/usr/bin/env python
"""Evaluate document selector quality without running the language model."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl  # noqa: E402
from safekv.doc_selector import (  # noqa: E402
    random_doc_ids_same_count,
    selected_doc_ids_for_method,
)
from safekv.learned_selector import (  # noqa: E402
    load_selector_artifact,
    oracle_label_doc_ids,
    select_learned_doc_ids,
)
from safekv.patch_recompute import stable_example_seed  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--selector-artifact", type=Path, default=None)
    parser.add_argument("--random-seed", type=int, default=13)
    parser.add_argument(
        "--methods",
        type=str,
        default=(
            "query_similarity_doc_patch_k1,query_similarity_doc_patch_k2,"
            "risk_guided_doc_patch_k1,risk_guided_doc_patch_k2,"
            "learned_doc_patch_k1,learned_doc_patch_k2,"
            "random_doc_patch_k1_seeded,random_doc_patch_k2_seeded"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = read_jsonl(args.data)
    methods = [item.strip() for item in args.methods.split(",") if item.strip()]
    artifact = load_selector_artifact(args.selector_artifact)
    rows = [
        evaluate_method(
            examples=examples,
            method=method,
            artifact=artifact,
            random_seed=args.random_seed,
        )
        for method in methods
    ]
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    args.out_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2, ensure_ascii=False))


def evaluate_method(
    *,
    examples: list[Any],
    method: str,
    artifact: dict[str, Any] | None,
    random_seed: int,
) -> dict[str, Any]:
    recalls = []
    precisions = []
    any_hits = []
    exact_sets = []
    suffix_ratios = []
    selected_counts = []

    for example in examples:
        positives = oracle_label_doc_ids(example)
        selected = select_docs(
            example=example,
            method=method,
            artifact=artifact,
            random_seed=random_seed,
        )
        selected_set = set(selected)
        hits = selected_set & positives
        recalls.append(len(hits) / max(1, len(positives)))
        precisions.append(len(hits) / max(1, len(selected)))
        any_hits.append(1.0 if hits else 0.0)
        exact_sets.append(1.0 if selected_set == positives else 0.0)
        suffix_ratios.append(suffix_doc_ratio(example, selected))
        selected_counts.append(float(len(selected)))

    return {
        "method": method,
        "num_examples": len(examples),
        "recall": mean(recalls),
        "precision": mean(precisions),
        "any_hit": mean(any_hits),
        "exact_set": mean(exact_sets),
        "avg_selected_docs": mean(selected_counts),
        "avg_suffix_doc_ratio": mean(suffix_ratios),
    }


def select_docs(
    *,
    example: Any,
    method: str,
    artifact: dict[str, Any] | None,
    random_seed: int,
) -> list[int]:
    if method.startswith("learned_doc_patch_"):
        return select_learned_doc_ids(method, example, artifact)
    if method.startswith("random_doc_patch_"):
        k = int(method.split("_k", maxsplit=1)[1].split("_", maxsplit=1)[0])
        return random_doc_ids_same_count(
            example,
            count=k,
            seed=stable_example_seed(random_seed, example.id, method),
        )
    selected, _reason = selected_doc_ids_for_method(method, example, seed=random_seed)
    return selected


def suffix_doc_ratio(example: Any, selected_doc_ids: list[int]) -> float:
    if not selected_doc_ids:
        return 0.0
    selected = set(selected_doc_ids)
    positions = [idx for idx, doc in enumerate(example.documents) if doc.doc_id in selected]
    if not positions:
        return 0.0
    return (len(example.documents) - min(positions)) / max(1, len(example.documents))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
