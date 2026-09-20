#!/usr/bin/env python
"""Validate completeness and budget accounting for the oracle KV-drift diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@dataclass(frozen=True)
class CandidatePositionAudit:
    context_token_count: int
    candidate_positions: tuple[int, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--expected-examples", type=int, required=True)
    parser.add_argument("--budgets", default="0.20,0.30,0.45,0.60")
    parser.add_argument("--require-range-audit-fields", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    budgets = [float(item) for item in args.budgets.split(",") if item]
    rows = read_jsonl(args.results_dir / "oracle_kv_drift_outputs.jsonl")
    summary = json.loads(
        (args.results_dir / "oracle_kv_drift_summary.json").read_text(encoding="utf-8")
    )
    expected_method_names = {
        "prefix_conditioned_composition",
        "oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1",
        "random_positions_oracle_full_kv_donor_same_budget_as_risk_suffix_k1",
        "risk_suffix_k1_oracle_donor_copy",
        "risk_suffix_k1_actual_recompute",
    }
    for budget in budgets:
        label = budget_label(budget)
        expected_method_names.add(f"oracle_kv_drift_token_local_p{label}")
        expected_method_names.add(
            f"random_positions_oracle_full_kv_donor_p{label}"
        )
    expected_methods = len(expected_method_names)
    expected_rows = args.expected_examples * expected_methods
    failures: list[str] = []
    if len(rows) != expected_rows:
        failures.append(f"row count {len(rows)} != expected {expected_rows}")
    keys = [(row["example_id"], row["method"]) for row in rows]
    if len(keys) != len(set(keys)):
        failures.append("duplicate example/method keys")
    methods = {row["method"] for row in rows}
    if methods != expected_method_names:
        failures.append(
            f"method set mismatch: observed={sorted(methods)}, "
            f"expected={sorted(expected_method_names)}"
        )
    if len(summary["method_summary"]) != expected_methods:
        failures.append("summary method count mismatch")
    if "not a Cache-Craft implementation" not in summary["diagnostic_scope"]:
        failures.append("diagnostic scope does not disclaim Cache-Craft")

    range_fields_present = any(
        bool(range_audit_field_names().intersection(row)) for row in rows
    )
    candidate_audits: dict[str, CandidatePositionAudit] = {}
    candidate_audit_report: dict[str, Any] = {
        "requested": range_fields_present,
        "status": "SKIPPED",
        "num_rebuilt_examples": 0,
    }
    if range_fields_present:
        try:
            candidate_audits, candidate_audit_report = rebuild_candidate_audits(
                summary=summary,
                example_ids={str(row["example_id"]) for row in rows},
            )
        except Exception as exc:
            candidate_audit_report = {
                "requested": True,
                "status": "FAIL",
                "num_rebuilt_examples": 0,
                "error": f"{type(exc).__name__}: {exc}",
            }
            failures.append(
                "failed to independently rebuild document candidate positions: "
                f"{type(exc).__name__}: {exc}"
            )

    by_example: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_example[str(row["example_id"])][str(row["method"])] = row
        by_method[str(row["method"])].append(row)
        for field in ("patched_context_ratio", "patched_document_token_ratio"):
            value = float(row[field])
            if value < 0.0 or value > 1.0:
                failures.append(f"invalid {field} for {row['example_id']}/{row['method']}")
        if row["repair_kind"] == "actual_recompute" and not row["method"].endswith(
            "actual_recompute"
        ):
            failures.append(f"unexpected actual-recompute method: {row['method']}")
        for field in (
            "qa_answer_equivalence_to_fresh_reference",
            "raw_answer_exact_to_fresh_reference",
            "generated_token_sequence_equivalent_to_fresh_reference",
            "top1_match_to_fresh_reference",
        ):
            if float(row[field]) not in {0.0, 1.0}:
                failures.append(f"nonbinary {field} for {row['example_id']}/{row['method']}")
        kl = float(row["first_token_kl_to_fresh_reference"])
        if not math.isfinite(kl) or kl < 0.0:
            failures.append(f"invalid KL for {row['example_id']}/{row['method']}")
        if row["method"] == "prefix_conditioned_composition" and (
            int(row["patched_token_count"]) != 0
            or float(row["patched_context_ratio"]) != 0.0
        ):
            failures.append(f"prefix baseline has repair cost for {row['example_id']}")
        validate_range_audit_fields(
            row,
            failures,
            required=args.require_range_audit_fields,
            expected=candidate_audits.get(str(row["example_id"])),
            reconstruction_required=range_fields_present,
        )

    if len(by_example) != args.expected_examples:
        failures.append(
            f"example count {len(by_example)} != expected {args.expected_examples}"
        )
    for method, items in by_method.items():
        if len(items) != args.expected_examples:
            failures.append(f"method row count mismatch for {method}: {len(items)}")

    for example_id, example_rows in by_example.items():
        drift_matched = example_rows[
            "oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1"
        ]
        random_matched = example_rows[
            "random_positions_oracle_full_kv_donor_same_budget_as_risk_suffix_k1"
        ]
        suffix = example_rows["risk_suffix_k1_oracle_donor_copy"]
        counts = {
            int(drift_matched["patched_token_count"]),
            int(random_matched["patched_token_count"]),
            int(suffix["patched_token_count"]),
        }
        if len(counts) != 1:
            failures.append(f"matched-budget token counts differ for {example_id}")
        actual_suffix = example_rows["risk_suffix_k1_actual_recompute"]
        if int(actual_suffix["patched_token_count"]) != int(
            suffix["patched_token_count"]
        ):
            failures.append(f"donor/actual suffix budgets differ for {example_id}")
        for budget in budgets:
            label = budget_label(budget)
            drift = example_rows[f"oracle_kv_drift_token_local_p{label}"]
            random = example_rows[
                f"random_positions_oracle_full_kv_donor_p{label}"
            ]
            if int(drift["patched_token_count"]) != int(random["patched_token_count"]):
                failures.append(f"fixed-budget token counts differ for {example_id}/p{label}")
            if budget == 0.0:
                prefix = example_rows["prefix_conditioned_composition"]
                for candidate in (drift, random):
                    if int(candidate["patched_token_count"]) != 0:
                        failures.append(f"p0 repaired tokens for {example_id}/{candidate['method']}")
                    for field in (
                        "generated_answer",
                        "qa_answer_equivalence_to_fresh_reference",
                        "raw_answer_exact_to_fresh_reference",
                        "generated_token_sequence_equivalent_to_fresh_reference",
                        "first_token_kl_to_fresh_reference",
                        "top1_match_to_fresh_reference",
                    ):
                        if candidate[field] != prefix[field]:
                            failures.append(
                                f"p0 does not equal prefix for {example_id}/"
                                f"{candidate['method']}/{field}"
                            )
            if budget == 1.0:
                for candidate in (drift, random):
                    if not math.isclose(
                        float(candidate["patched_document_token_ratio"]),
                        1.0,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    ):
                        failures.append(
                            f"p1 does not cover all document tokens for "
                            f"{example_id}/{candidate['method']}"
                        )
                    for field in (
                        "qa_answer_equivalence_to_fresh_reference",
                        "raw_answer_exact_to_fresh_reference",
                        "generated_token_sequence_equivalent_to_fresh_reference",
                        "top1_match_to_fresh_reference",
                    ):
                        if not bool(candidate[field]):
                            failures.append(
                                f"p1 fresh-reference endpoint failed for "
                                f"{example_id}/{candidate['method']}/{field}"
                            )
                    expected = candidate_audits.get(str(example_id))
                    if expected is not None and tuple(
                        positions_from_row(candidate)
                    ) != expected.candidate_positions:
                        failures.append(
                            f"p1 does not select exactly all document tokens for "
                            f"{example_id}/{candidate['method']}"
                        )
                # At p=1 the oracle and random policies both select every
                # document token and must therefore be identical to each other.
                # They need not have KL=0 to the chunk-matched fresh reference:
                # the retained static prefix was computed in a separate forward,
                # which can differ slightly under finite-precision partitioning.
                for field in (
                    "patched_token_count",
                    "patched_ranges",
                    "patched_positions_sha256",
                    "generated_answer",
                    "qa_answer_equivalence_to_fresh_reference",
                    "raw_answer_exact_to_fresh_reference",
                    "generated_token_sequence_equivalent_to_fresh_reference",
                    "first_token_kl_to_fresh_reference",
                    "top1_match_to_fresh_reference",
                ):
                    if drift.get(field) != random.get(field):
                        failures.append(
                            f"p1 oracle/random all-document mismatch for "
                            f"{example_id}/{field}"
                        )

    summary_by_method = {
        str(item["method"]): item for item in summary["method_summary"]
    }
    if set(summary_by_method) != expected_method_names:
        failures.append("summary method key set mismatch")
    metric_fields = {
        "qa_answer_equivalence_to_fresh_reference": (
            "qa_answer_equivalence_to_fresh_reference"
        ),
        "raw_answer_exact_to_fresh_reference": "raw_answer_exact_to_fresh_reference",
        "token_sequence_equivalence_to_fresh_reference": (
            "generated_token_sequence_equivalent_to_fresh_reference"
        ),
        "avg_first_token_kl_to_fresh_reference": (
            "first_token_kl_to_fresh_reference"
        ),
        "avg_patched_context_ratio": "patched_context_ratio",
        "avg_patched_document_token_ratio": "patched_document_token_ratio",
    }
    for method, items in by_method.items():
        summary_item = summary_by_method.get(method)
        if summary_item is None:
            continue
        if int(summary_item.get("num_examples", -1)) != args.expected_examples:
            failures.append(f"summary example count mismatch for {method}")
        for summary_field, raw_field in metric_fields.items():
            expected = statistics.fmean(float(row[raw_field]) for row in items)
            observed = float(summary_item[summary_field])
            if not math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"summary metric mismatch for {method}/{summary_field}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "num_rows": len(rows),
        "expected_rows": expected_rows,
        "num_methods": len(methods),
        "num_examples": len(by_example),
        "candidate_position_audit": candidate_audit_report,
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


def budget_label(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def range_audit_field_names() -> set[str]:
    return {
        "context_token_count",
        "candidate_document_token_count",
        "patched_ranges",
        "patched_positions_sha256",
    }


def validate_range_audit_fields(
    row: dict[str, Any],
    failures: list[str],
    *,
    required: bool,
    expected: CandidatePositionAudit | None = None,
    reconstruction_required: bool = False,
) -> None:
    fields = range_audit_field_names()
    present = fields.intersection(row)
    if not present:
        if required:
            failures.append(
                f"missing range audit fields for {row['example_id']}/{row['method']}"
            )
        return
    if present != fields:
        failures.append(
            f"partial range audit fields for {row['example_id']}/{row['method']}"
        )
        return
    context_count = int(row["context_token_count"])
    candidate_count = int(row["candidate_document_token_count"])
    ranges = row["patched_ranges"]
    if context_count <= 0 or candidate_count < 0 or candidate_count > context_count:
        failures.append(f"invalid context/candidate count for {row['example_id']}/{row['method']}")
        return
    positions: list[int] = []
    previous_end = -1
    for item in ranges:
        start = int(item["start"])
        end = int(item["end"])
        if start < 0 or end <= start or end > context_count or start < previous_end:
            failures.append(f"invalid/overlapping range for {row['example_id']}/{row['method']}")
            return
        positions.extend(range(start, end))
        previous_end = end
    if len(positions) != int(row["patched_token_count"]):
        failures.append(f"range token count mismatch for {row['example_id']}/{row['method']}")
    digest = hashlib.sha256()
    for position in positions:
        digest.update(int(position).to_bytes(8, byteorder="big", signed=False))
    if digest.hexdigest() != row["patched_positions_sha256"]:
        failures.append(f"range position hash mismatch for {row['example_id']}/{row['method']}")

    expected_context_ratio = len(positions) / context_count
    expected_document_ratio = len(positions) / candidate_count if candidate_count else 0.0
    if not math.isclose(
        float(row["patched_context_ratio"]),
        expected_context_ratio,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        failures.append(
            f"patched context ratio/count mismatch for {row['example_id']}/{row['method']}"
        )
    if not math.isclose(
        float(row["patched_document_token_ratio"]),
        expected_document_ratio,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        failures.append(
            f"patched document ratio/count mismatch for {row['example_id']}/{row['method']}"
        )

    if expected is None:
        if reconstruction_required:
            failures.append(
                f"missing reconstructed candidate positions for "
                f"{row['example_id']}/{row['method']}"
            )
        return
    if context_count != expected.context_token_count:
        failures.append(
            f"context count differs from reconstructed prompt for "
            f"{row['example_id']}/{row['method']}"
        )
    if candidate_count != len(expected.candidate_positions):
        failures.append(
            f"candidate count differs from reconstructed prompt for "
            f"{row['example_id']}/{row['method']}"
        )
    candidate_set = set(expected.candidate_positions)
    invalid_positions = [position for position in positions if position not in candidate_set]
    if invalid_positions:
        failures.append(
            f"patched positions leave reconstructed document candidates for "
            f"{row['example_id']}/{row['method']}"
        )


def positions_from_row(row: dict[str, Any]) -> list[int]:
    return [
        position
        for item in row["patched_ranges"]
        for position in range(int(item["start"]), int(item["end"]))
    ]


def rebuild_candidate_audits(
    *,
    summary: dict[str, Any],
    example_ids: set[str],
) -> tuple[dict[str, CandidatePositionAudit], dict[str, Any]]:
    """Re-tokenize saved inputs and independently recover document positions."""

    from transformers import AutoTokenizer

    from safekv.config import load_config
    from safekv.full_prefill import load_examples_for_config
    from safekv.prompting import build_rag_prompt

    config_path = required_existing_path(summary, "config_path")
    dataset_path = required_existing_path(summary, "dataset_path")
    validate_recorded_file_hash(summary, "config_sha256", config_path)
    validate_recorded_file_hash(summary, "dataset_sha256", dataset_path)

    config = load_config(config_path)
    config = replace(config, data=replace(config.data, path=str(dataset_path)))
    model_name = str(summary.get("model_name") or config.model.name)
    if model_name != config.model.name:
        raise ValueError(
            f"summary/config model mismatch: {model_name!r} != {config.model.name!r}"
        )
    tokenizer_kwargs: dict[str, Any] = {
        "use_fast": True,
        "trust_remote_code": config.model.trust_remote_code,
    }
    model_revision = summary.get("model_commit_hash")
    if not model_revision:
        raise ValueError("summary is missing model_commit_hash for tokenizer reconstruction")
    tokenizer_kwargs["revision"] = str(model_revision)
    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    if not getattr(tokenizer, "is_fast", False):
        raise ValueError("candidate reconstruction requires a fast tokenizer")

    examples = load_examples_for_config(config, config_dir=config_path.parent.parent)
    examples_by_id: dict[str, Any] = {}
    for example in examples:
        if example.id in examples_by_id:
            raise ValueError(f"duplicate example ID in dataset: {example.id}")
        examples_by_id[example.id] = example
    missing = sorted(example_ids - set(examples_by_id))
    if missing:
        raise ValueError(f"output example IDs missing from dataset: {missing[:3]}")

    audits: dict[str, CandidatePositionAudit] = {}
    for example_id in sorted(example_ids):
        pack = build_rag_prompt(
            examples_by_id[example_id],
            tokenizer,
            prompt_format=config.experiment.prompt_format,
            boundary_window_tokens=config.prompt.boundary_window_tokens,
            adaptive_boundary_window=config.prompt.adaptive_boundary_window,
        )
        positions = tuple(
            position
            for token_range in pack.doc_ranges
            for position in range(token_range.start, token_range.end)
        )
        if tuple(sorted(set(positions))) != positions:
            raise ValueError(f"reconstructed document positions overlap for {example_id}")
        if positions and (
            positions[0] < 0 or positions[-1] >= pack.query_token_range.start
        ):
            raise ValueError(
                f"reconstructed document positions cross query boundary for {example_id}"
            )
        audits[example_id] = CandidatePositionAudit(
            context_token_count=pack.query_token_range.start,
            candidate_positions=positions,
        )

    return audits, {
        "requested": True,
        "status": "PASS",
        "num_rebuilt_examples": len(audits),
        "config_path": str(config_path),
        "dataset_path": str(dataset_path),
        "model_name": model_name,
        "tokenizer_revision": str(model_revision) if model_revision else None,
    }


def required_existing_path(summary: dict[str, Any], field: str) -> Path:
    value = summary.get(field)
    if not value:
        raise ValueError(f"summary is missing {field}")
    path = Path(str(value)).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"summary {field} does not exist: {path}")
    return path


def validate_recorded_file_hash(
    summary: dict[str, Any],
    field: str,
    path: Path,
) -> None:
    expected = summary.get(field)
    if expected is None:
        raise ValueError(f"summary is missing required provenance field {field}")
    observed = file_sha256(path)
    if str(expected) != observed:
        raise ValueError(f"{field} mismatch for {path}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
