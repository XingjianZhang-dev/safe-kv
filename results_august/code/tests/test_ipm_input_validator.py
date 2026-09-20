from __future__ import annotations

import json

import pytest

from scripts.validate_ipm_realistic_inputs import sha256_file, validate_manifest


def build_fixture(tmp_path):
    source = tmp_path / "source.json"
    source.write_text("{}\n", encoding="utf-8")
    outputs = {}
    for condition in ("natural", "shuffle", "bm25", "dense"):
        for split in ("calibration", "test"):
            source_indices = [0, 1] if condition != "shuffle" else [1, 0]
            scores = [1.0, 0.0] if condition in {"bm25", "dense"} else [0.0, 0.0]
            documents = [
                {
                    "doc_id": index,
                    "title": f"title-{source_index}",
                    "text": f"evidence-{source_index}",
                    "role": "evidence",
                    "retrieval_score": scores[index],
                    "source_doc_index": source_index,
                }
                for index, source_index in enumerate(source_indices)
            ]
            row = {
                "id": "example",
                "category": "external_2wiki",
                "documents": documents,
                "question": "question",
                "gold_answer": "answer",
                "evidence": [
                    {"doc_id": index, "text": document["text"]}
                    for index, document in enumerate(documents)
                ],
                "conflicting_docs": [],
                "requires_cross_doc": True,
                "source_metadata": {
                    "dataset": "test",
                    "source_id": "example",
                    "split": split,
                    "retrieval_condition": condition,
                    "source_doc_indices_in_prompt_order": source_indices,
                    "evidence_ranks_one_based": [1, 2],
                    "gold_labels_used_for_ranking": False,
                    "ranking_model": (
                        {"name": "test/dense", "revision": "abc"}
                        if condition == "dense"
                        else None
                    ),
                },
            }
            output = tmp_path / f"{condition}_{split}.jsonl"
            output.write_text(json.dumps(row) + "\n", encoding="utf-8")
            outputs[f"{condition}:{split}"] = {
                "path": str(output),
                "sha256": sha256_file(output),
                "num_examples": 1,
            }
    manifest = tmp_path / "test_build_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "dataset": "test",
                "source_path": str(source),
                "source_sha256": sha256_file(source),
                "source_url": "https://example.test/source",
                "source_revision": "revision",
                "source_license": "license",
                "conditions": ["natural", "shuffle", "bm25", "dense"],
                "gold_labels_used_for_ranking": False,
                "dense_model": "test/dense",
                "dense_revision": "abc",
                "outputs": outputs,
            }
        ),
        encoding="utf-8",
    )
    return manifest, outputs


def test_realistic_input_validator_checks_complete_grid_and_hashes(tmp_path):
    manifest, outputs = build_fixture(tmp_path)
    assert validate_manifest(manifest)["status"] == "PASS"

    changed = outputs["dense:test"]["path"]
    with open(changed, "a", encoding="utf-8") as handle:
        handle.write("\n")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_manifest(manifest)
