from __future__ import annotations

import json

from scripts.verify_model_snapshot import git_blob_sha1, sha256_file, verify


def test_snapshot_verification_checks_size_and_hash(tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    weight = model_dir / "model-00001-of-00001.safetensors"
    weight.write_bytes(b"weights")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "model_id": "test/model",
                "huggingface_commit": "abc",
                "weight_files": {
                    weight.name: {
                        "size_bytes": weight.stat().st_size,
                        "sha256": sha256_file(weight),
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    assert verify(model_dir, manifest)["status"] == "PASS"
    weight.write_bytes(b"changed")
    assert verify(model_dir, manifest)["status"] == "FAIL"


def test_snapshot_verification_checks_metadata_files(tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    metadata = model_dir / "tokenizer.json"
    weight = model_dir / "model.safetensors"
    metadata.write_bytes(b"tokenizer")
    weight.write_bytes(b"weights")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "model_id": "test/model",
                "huggingface_commit": "abc",
                "metadata_files": {
                    metadata.name: {
                        "size_bytes": metadata.stat().st_size,
                        "sha256": sha256_file(metadata),
                    }
                },
                "weight_files": {
                    weight.name: {
                        "size_bytes": weight.stat().st_size,
                        "sha256": sha256_file(weight),
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    assert verify(model_dir, manifest)["status"] == "PASS"
    metadata.write_bytes(b"changed")
    assert verify(model_dir, manifest)["status"] == "FAIL"


def test_snapshot_verification_supports_upstream_git_blob_id(tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    config = model_dir / "config.json"
    weight = model_dir / "model.safetensors"
    config.write_bytes(b"config")
    weight.write_bytes(b"weights")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "model_id": "test/model",
                "huggingface_commit": "abc",
                "metadata_files": {
                    config.name: {
                        "size_bytes": config.stat().st_size,
                        "git_blob_sha1": git_blob_sha1(config),
                    }
                },
                "weight_files": {
                    weight.name: {
                        "size_bytes": weight.stat().st_size,
                        "sha256": sha256_file(weight),
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    assert verify(model_dir, manifest)["status"] == "PASS"
    config.write_bytes(b"drift")
    assert verify(model_dir, manifest)["status"] == "FAIL"
