#!/usr/bin/env python3
"""Validate and summarize the official KV Packet native reproduction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DATASETS = {
    "hotpotqa": {
        "author_directory": "hotpot_qa",
        "dataset_name": "hotpot_qa",
        "local_files": {
            "kv_packet": "kvpacket_qwen3_hotpotqa_n100_result.json",
            "full_recompute": "full_recompute_qwen3_hotpotqa_n100_result.json",
        },
        "run_ids": {
            "kv_packet": "kvpacket_official_qwen3_hotpotqa_n100_20260822_v1",
            "full_recompute": "kvpacket_official_fullrecompute_qwen3_hotpotqa_n100_20260822_v1",
        },
    },
    "musique": {
        "author_directory": "musique",
        "dataset_name": "musique",
        "local_files": {
            "kv_packet": "kvpacket_qwen3_musique_n100_result.json",
            "full_recompute": "full_recompute_qwen3_musique_n100_result.json",
        },
        "run_ids": {
            "kv_packet": "kvpacket_official_qwen3_musique_n100_20260822_v2",
            "full_recompute": "kvpacket_official_fullrecompute_qwen3_musique_n100_20260822_v1",
        },
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_result(
    payload: dict[str, Any], dataset_name: str, method: str
) -> None:
    config = payload["config"]
    assert config["dataset"]["dataset_name"] == dataset_name
    assert config["dataset"]["num_samples"] == 100
    assert config["dataset"]["split"] == "validation"
    assert config["dataset"]["seed"] == 42
    assert config["seed"] == 42
    assert config["cache_comb"]["method"] == method
    for key in ("precision", "recall", "f1", "ttft", "flops"):
        assert key in payload["result"]


def summarize_dataset(
    key: str,
    spec: dict[str, Any],
    repository_root: Path,
    reproduction_results: Path,
    run_registry: Path,
) -> dict[str, Any]:
    reproduced: dict[str, Any] = {}
    author_stored: dict[str, Any] = {}
    runs: dict[str, Any] = {}
    for method in ("kv_packet", "full_recompute"):
        local_path = reproduction_results / spec["local_files"][method]
        local_payload = load_json(local_path)
        validate_result(local_payload, spec["dataset_name"], method)
        reproduced[method] = {
            "result_file": str(local_path.resolve()),
            "metrics": local_payload["result"],
            "resolved_config": local_payload["config"],
        }

        author_path = (
            repository_root
            / "eval_config"
            / "qwen_3_4b"
            / spec["author_directory"]
            / "eval_results"
            / f"{method}_result.json"
        )
        author_stored[method] = {
            "result_file": str(author_path.resolve()),
            "metrics": load_json(author_path)["result"],
        }

        run_id = spec["run_ids"][method]
        run_manifest_path = run_registry / run_id / "run_manifest.json"
        manifest = load_json(run_manifest_path)
        assert manifest["status"] == "completed"
        runs[method] = {
            "run_id": run_id,
            "manifest": str(run_manifest_path.resolve()),
            "duration_seconds": manifest["duration_seconds"],
        }

    kv_metrics = reproduced["kv_packet"]["metrics"]
    full_metrics = reproduced["full_recompute"]["metrics"]
    derived = {
        "kv_packet_minus_full_recompute_f1": (
            kv_metrics["f1"] - full_metrics["f1"]
        ),
        "full_recompute_over_kv_packet_ttft_speedup": (
            full_metrics["ttft"] / kv_metrics["ttft"]
        ),
        "kv_packet_ttft_reduction_fraction": (
            1.0 - kv_metrics["ttft"] / full_metrics["ttft"]
        ),
        "kv_packet_flops_reduction_fraction": (
            1.0 - kv_metrics["flops"] / full_metrics["flops"]
        ),
    }
    return {
        "dataset_key": key,
        "reproduced_same_host": reproduced,
        "author_repository_stored_reference": author_stored,
        "tracked_runs": runs,
        "derived_same_host_comparison": derived,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--reproduction-results", type=Path, required=True)
    parser.add_argument("--run-registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = {
        "schema_version": 1,
        "scope": (
            "Official KV Packet native QA/TTFT protocol; not SAFE-KV "
            "full-prefill behavior-preservation evaluation."
        ),
        "datasets": {
            key: summarize_dataset(
                key,
                spec,
                args.repository_root.resolve(),
                args.reproduction_results.resolve(),
                args.run_registry.resolve(),
            )
            for key, spec in DATASETS.items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
