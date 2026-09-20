#!/usr/bin/env python
"""Summarize an answer_eval_outputs.jsonl file while a run is still in progress."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import summarize_answer_eval_rows  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outputs_jsonl", type=Path)
    parser.add_argument("--out-csv", type=Path, default=None)
    parser.add_argument("--out-category-csv", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(args.outputs_jsonl)
    summary = summarize_answer_eval_rows(rows)
    compact_summary = compact(summary)
    print(json.dumps(compact_summary, indent=2, ensure_ascii=False))
    if args.out_csv:
        write_csv(args.out_csv, compact_summary["method_level"])
    if args.out_category_csv:
        write_category_csv(args.out_category_csv, summary.get("category_level", {}))


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def compact(summary: dict) -> dict:
    return {
        "num_rows": summary.get("num_rows", 0),
        "category_counts": summary.get("category_counts", {}),
        "method_level": [
            {
                "method": method,
                "answer_equivalence": data["answer_equivalence_to_full_prefill"],
                "gold_em": data["gold_exact_match"],
                "gold_f1": data["gold_token_f1"],
                "changed_wrong": data["answer_changed_and_gold_wrong_count"]
                / max(1, data["num_rows"]),
                "patch_ratio": data["avg_patched_token_ratio"],
                "avg_kl": data["avg_first_token_kl"],
            }
            for method, data in sorted(summary.get("method_level", {}).items())
        ],
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "method",
        "answer_equivalence",
        "gold_em",
        "gold_f1",
        "changed_wrong",
        "patch_ratio",
        "avg_kl",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_category_csv(path: Path, category_level: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "method",
        "category",
        "num_rows",
        "answer_equivalence",
        "gold_em",
        "gold_f1",
        "changed_wrong",
        "patch_ratio",
        "avg_kl",
    ]
    rows = []
    for key, data in sorted(category_level.items()):
        method, category = key.split("::", 1)
        rows.append(
            {
                "method": method,
                "category": category,
                "num_rows": data["num_rows"],
                "answer_equivalence": data["answer_equivalence_to_full_prefill"],
                "gold_em": data["gold_exact_match"],
                "gold_f1": data["gold_token_f1"],
                "changed_wrong": data["answer_changed_and_gold_wrong_count"]
                / max(1, data["num_rows"]),
                "patch_ratio": data["avg_patched_token_ratio"],
                "avg_kl": data["avg_first_token_kl"],
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
