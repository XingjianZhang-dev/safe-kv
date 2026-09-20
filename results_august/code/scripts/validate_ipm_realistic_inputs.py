#!/usr/bin/env python3
"""Fail-closed validation for the frozen realistic IP&M input variants."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.data_schema import DiagnosticExample


REQUIRED_CONDITIONS = {"natural", "shuffle", "bm25", "dense"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from error
    return rows


def document_fingerprint(row: dict[str, Any]) -> str:
    canonical = sorted(
        (
            int(document["source_doc_index"]),
            str(document["title"]),
            str(document["text"]),
            str(document["role"]),
        )
        for document in row["documents"]
    )
    return hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def validate_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("gold_labels_used_for_ranking") is not False:
        raise ValueError(f"{path}: manifest does not deny gold-label ranking")
    for field in ("source_url", "source_revision", "source_license"):
        if not str(manifest.get(field, "")).strip():
            raise ValueError(f"{path}: missing source provenance field {field}")
    source_path = Path(manifest["source_path"])
    if not source_path.is_file():
        raise ValueError(f"{path}: source file is missing: {source_path}")
    if sha256_file(source_path) != manifest.get("source_sha256"):
        raise ValueError(f"{path}: source SHA-256 mismatch")
    if set(manifest.get("conditions", [])) != REQUIRED_CONDITIONS:
        raise ValueError(f"{path}: expected all four retrieval conditions")
    if not manifest.get("dense_model") or not manifest.get("dense_revision"):
        raise ValueError(f"{path}: dense retriever identity is incomplete")
    by_split: dict[str, dict[str, dict[str, dict[str, Any]]]] = defaultdict(dict)
    output_report: dict[str, Any] = {}
    for key, metadata in manifest["outputs"].items():
        condition, split = key.split(":", 1)
        output_path = Path(metadata["path"])
        if not output_path.is_file():
            raise ValueError(f"{path}: output file is missing: {output_path}")
        if sha256_file(output_path) != metadata.get("sha256"):
            raise ValueError(f"{output_path}: SHA-256 mismatch")
        rows = read_jsonl(output_path)
        if len(rows) != int(metadata["num_examples"]):
            raise ValueError(f"{output_path}: row count mismatch")
        indexed: dict[str, dict[str, Any]] = {}
        for row in rows:
            DiagnosticExample.from_dict(row)
            row_id = str(row["id"])
            if row_id in indexed:
                raise ValueError(f"{output_path}: duplicate id {row_id}")
            source = row.get("source_metadata", {})
            if source.get("gold_labels_used_for_ranking") is not False:
                raise ValueError(f"{output_path}: {row_id} lacks leakage declaration")
            if source.get("split") != split or source.get("retrieval_condition") != condition:
                raise ValueError(f"{output_path}: {row_id} condition/split mismatch")
            scores = [float(document["retrieval_score"]) for document in row["documents"]]
            if condition in {"natural", "shuffle"} and any(score != 0.0 for score in scores):
                raise ValueError(f"{output_path}: neutral condition has nonzero scores")
            if condition in {"bm25", "dense"} and any(not 0.0 <= score <= 1.0 for score in scores):
                raise ValueError(f"{output_path}: ranked score outside [0,1]")
            source_indices = [int(document["source_doc_index"]) for document in row["documents"]]
            if source_indices != [
                int(value)
                for value in source.get("source_doc_indices_in_prompt_order", [])
            ]:
                raise ValueError(f"{output_path}: source index metadata mismatch for {row_id}")
            if condition == "natural" and source_indices != list(range(len(source_indices))):
                raise ValueError(f"{output_path}: natural order changed for {row_id}")
            if condition in {"bm25", "dense"} and scores != sorted(scores, reverse=True):
                raise ValueError(f"{output_path}: ranked scores are not descending for {row_id}")
            ranking_model = source.get("ranking_model")
            if condition == "dense":
                expected_model = {
                    "name": manifest["dense_model"],
                    "revision": manifest["dense_revision"],
                }
                if ranking_model != expected_model:
                    raise ValueError(
                        f"{output_path}: dense model metadata mismatch for {row_id}"
                    )
            elif ranking_model is not None:
                raise ValueError(
                    f"{output_path}: non-dense condition has ranking model for {row_id}"
                )
            evidence_ids = {int(item["doc_id"]) for item in row["evidence"]}
            role_ids = {
                int(document["doc_id"])
                for document in row["documents"]
                if document["role"] == "evidence"
            }
            if evidence_ids != role_ids:
                raise ValueError(f"{output_path}: evidence role mismatch for {row_id}")
            evidence_ranks = sorted(doc_id + 1 for doc_id in evidence_ids)
            if evidence_ranks != sorted(
                int(value) for value in source.get("evidence_ranks_one_based", [])
            ):
                raise ValueError(f"{output_path}: evidence rank mismatch for {row_id}")
            indexed[row_id] = row
        by_split[split][condition] = indexed
        output_report[key] = {
            "num_examples": len(rows),
            "num_unique_ids": len(indexed),
            "sha256": metadata["sha256"],
        }
    expected_outputs = {
        f"{condition}:{split}"
        for condition in REQUIRED_CONDITIONS
        for split in ("calibration", "test")
    }
    if set(manifest["outputs"]) != expected_outputs:
        raise ValueError(f"{path}: output condition/split grid is incomplete")
    for split, conditions in by_split.items():
        reference_name = sorted(conditions)[0]
        reference = conditions[reference_name]
        for condition, rows in conditions.items():
            if rows.keys() != reference.keys():
                raise ValueError(f"{path}: {split} IDs differ for {condition}")
            for row_id, row in rows.items():
                if document_fingerprint(row) != document_fingerprint(reference[row_id]):
                    raise ValueError(
                        f"{path}: source document content differs for {split}/{condition}/{row_id}"
                    )
    return {
        "manifest": str(path),
        "dataset": manifest["dataset"],
        "status": "PASS",
        "outputs": output_report,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    data_dir = Path(args.data_dir).resolve()
    manifests = sorted(data_dir.glob("*_build_manifest.json"))
    if not manifests:
        raise ValueError(f"no build manifests found in {data_dir}")
    report = {
        "schema_version": 1,
        "status": "PASS",
        "datasets": [validate_manifest(path) for path in manifests],
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
