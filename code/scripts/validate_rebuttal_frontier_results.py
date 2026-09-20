#!/usr/bin/env python
"""Validate a token-aware, score-neutral shuffled frontier evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


POLICIES = {
    "query_similarity_suffix_closure_k1",
    "query_similarity_suffix_closure_k2",
    "risk_guided_suffix_closure_k1",
    "risk_guided_suffix_closure_k2",
    "hybrid_query_risk_union_suffix_k1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--data-path", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.results_dir / "frontier_outputs.jsonl")
    data_rows = read_jsonl(args.data_path)[: args.expected_examples]
    summary = json.loads(
        (args.results_dir / "frontier_summary.json").read_text(encoding="utf-8")
    )
    failures: list[str] = []
    if len(rows) != args.expected_examples:
        failures.append(f"frontier rows {len(rows)} != expected {args.expected_examples}")
    if len(data_rows) != args.expected_examples:
        failures.append(f"data rows {len(data_rows)} != expected {args.expected_examples}")
    if len({row["example_id"] for row in rows}) != len(rows):
        failures.append("duplicate frontier example IDs")
    if summary["generated_token_sequence_exact_available_examples"] != len(rows):
        failures.append("token-exact metrics are not available for every example")

    for row in rows:
        num_documents = int(row["num_documents"])
        starts = row["suffix_starts"]
        if [int(item["start"]) for item in starts] != list(range(num_documents)):
            failures.append(f"suffix starts incomplete for {row['example_id']}")
        if int(row["no_repair"]["start"]) != num_documents:
            failures.append(f"no-repair start mismatch for {row['example_id']}")
        if row.get("full_prefill_token_ids") is None:
            failures.append(f"full token IDs missing for {row['example_id']}")
        for item in starts + [row["no_repair"]]:
            if item.get("generated_token_sequence_exact") is None:
                failures.append(f"token exact missing for {row['example_id']}")
        if set(row["selector_results"]) != POLICIES:
            failures.append(f"selector policy set mismatch for {row['example_id']}")

    earliest_positions = []
    for row in data_rows:
        documents = row["documents"]
        if any(float(doc.get("retrieval_score", 0.0)) != 0.0 for doc in documents):
            failures.append(f"nonzero retrieval score in {row['id']}")
        evidence_ids = {int(item["doc_id"]) for item in row.get("evidence", [])}
        positions = [
            position
            for position, doc in enumerate(documents)
            if int(doc["doc_id"]) in evidence_ids
        ]
        if positions:
            earliest_positions.append(min(positions))
    if earliest_positions and max(earliest_positions) == 0:
        failures.append("all support documents remain first; order was not deconfounded")

    for method in summary["selector_metrics"]:
        for metric in ("normalized_qa_equivalent", "raw_trimmed_answer_exact", "generated_token_sequence_exact"):
            if int(method[f"{metric}_available_examples"]) != len(rows):
                failures.append(f"{metric} availability mismatch for {method['method']}")
            if method[f"{metric}_wilson_ci95_low"] is None:
                failures.append(f"{metric} CI missing for {method['method']}")

    report: dict[str, Any] = {
        "status": "PASS" if not failures else "FAIL",
        "num_rows": len(rows),
        "num_data_rows": len(data_rows),
        "mean_earliest_evidence_position": (
            sum(earliest_positions) / len(earliest_positions)
            if earliest_positions
            else None
        ),
        "num_failures": len(failures),
        "failures": failures,
    }
    (args.results_dir / "validation_report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    if failures:
        raise SystemExit(1)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


if __name__ == "__main__":
    main()
