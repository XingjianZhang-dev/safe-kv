#!/usr/bin/env python3
"""Verify every model weight against a pinned upstream LFS manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    digest = hashlib.sha1()
    digest.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(model_dir: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    groups = [
        ("metadata", manifest.get("metadata_files", {})),
        ("weight", manifest["weight_files"]),
    ]
    for role, files in groups:
        for filename, expected in sorted(files.items()):
            path = model_dir / filename
            exists = path.is_file()
            actual_size = path.stat().st_size if exists else None
            actual_sha256 = sha256_file(path) if exists else None
            expected_git_blob_sha1 = expected.get("git_blob_sha1")
            actual_git_blob_sha1 = (
                git_blob_sha1(path) if exists and expected_git_blob_sha1 else None
            )
            sha256_passed = (
                actual_sha256 == expected["sha256"]
                if expected.get("sha256")
                else True
            )
            git_blob_passed = (
                actual_git_blob_sha1 == expected_git_blob_sha1
                if expected_git_blob_sha1
                else True
            )
            if not expected.get("sha256") and not expected_git_blob_sha1:
                raise ValueError(f"{filename}: expected at least one content hash")
            rows.append(
                {
                    "filename": filename,
                    "role": role,
                    "exists": exists,
                    "expected_size_bytes": expected["size_bytes"],
                    "actual_size_bytes": actual_size,
                    "expected_sha256": expected.get("sha256"),
                    "actual_sha256": actual_sha256,
                    "expected_git_blob_sha1": expected_git_blob_sha1,
                    "actual_git_blob_sha1": actual_git_blob_sha1,
                    "passed": exists
                    and actual_size == expected["size_bytes"]
                    and sha256_passed
                    and git_blob_passed,
                }
            )
    return {
        "model_id": manifest["model_id"],
        "huggingface_commit": manifest["huggingface_commit"],
        "model_dir": str(model_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "files": rows,
        "status": "PASS" if all(row["passed"] for row in rows) else "FAIL",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = verify(args.model_dir.resolve(), args.manifest.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
