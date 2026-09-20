#!/usr/bin/env python3
"""Record immutable fingerprints and file hashes for Hugging Face datasets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import datasets
import huggingface_hub
from datasets import load_dataset


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(resolved),
        "size_bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def snapshot(name: str, config: str, split: str) -> dict[str, Any]:
    dataset = load_dataset(name, config, split=split)
    cache_paths = sorted(
        {Path(row["filename"]).resolve() for row in dataset.cache_files}
    )
    info_paths = sorted(
        {
            path.parent / "dataset_info.json"
            for path in cache_paths
            if (path.parent / "dataset_info.json").is_file()
        }
    )
    info = dataset.info
    return {
        "dataset_name": name,
        "config_name": config,
        "split": split,
        "fingerprint": dataset._fingerprint,
        "num_rows": len(dataset),
        "dataset_version": str(info.version),
        "builder_name": info.builder_name,
        "dataset_size_bytes": info.dataset_size,
        "download_size_bytes": info.download_size,
        "features": dataset.features.to_dict(),
        "cache_files": [file_record(path) for path in cache_paths],
        "dataset_info_files": [file_record(path) for path in info_paths],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec",
        nargs=3,
        action="append",
        metavar=("DATASET", "CONFIG", "SPLIT"),
        required=True,
        help="Dataset repository, configuration, and split; repeat as needed.",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = {
        "schema_version": 1,
        "datasets_version": datasets.__version__,
        "huggingface_hub_version": huggingface_hub.__version__,
        "snapshots": [snapshot(*spec) for spec in args.spec],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
