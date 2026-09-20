#!/usr/bin/env python
"""Summarize answer-eval outputs by position-sweep bucket."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import read_answer_rows, summarize_answer_eval_rows  # noqa: E402


POSITION_ORDER = {
    "first": 0,
    "early": 1,
    "middle": 2,
    "late": 3,
    "last": 4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_answer_rows(args.outputs)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        position = extract_position(row["example_id"])
        grouped.setdefault((row["method"], position), []).append(row)

    summary_rows = []
    for (method, position), group_rows in grouped.items():
        virtual_rows = [dict(row, method=f"{method}::{position}") for row in group_rows]
        method_summary = summarize_answer_eval_rows(virtual_rows)["method_level"][
            f"{method}::{position}"
        ]
        summary_rows.append(
            {
                "method": method,
                "position": position,
                "num_examples": method_summary["num_rows"],
                "answer_equivalence": method_summary["answer_equivalence_to_full_prefill"],
                "gold_em": method_summary["gold_exact_match"],
                "gold_f1": method_summary["gold_token_f1"],
                "changed_wrong": method_summary["answer_changed_and_gold_wrong_count"],
                "changed_wrong_rate": method_summary["answer_changed_and_gold_wrong_count"]
                / max(1, method_summary["num_rows"]),
                "patch_ratio": method_summary["avg_patched_token_ratio"],
                "avg_kl": method_summary["avg_first_token_kl"],
            }
        )

    summary_rows.sort(key=lambda item: (item["method"], POSITION_ORDER.get(item["position"], 99)))
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    args.out_json.write_text(
        json.dumps(summary_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary_rows, indent=2, ensure_ascii=False))


def extract_position(example_id: str) -> str:
    match = re.search(r"_pos_([^_]+)$", example_id)
    if match is None:
        return "unknown"
    return match.group(1)


if __name__ == "__main__":
    main()
