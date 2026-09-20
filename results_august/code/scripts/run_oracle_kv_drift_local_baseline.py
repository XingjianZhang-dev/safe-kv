#!/usr/bin/env python
"""Evaluate an optimistic token-local KV-drift repair diagnostic.

This is deliberately not a Cache-Craft implementation.  It uses full-prefill
states to choose and copy the most drifted token positions, making it an oracle
diagnostic of whether a strong scattered local patch can match suffix closure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import answer_metric_fields  # noqa: E402
from safekv.cache_ops import (  # noqa: E402
    cache_seq_len,
    slice_legacy_cache,
    to_legacy_cache,
)
from safekv.config import load_config  # noqa: E402
from safekv.data_schema import TokenRange  # noqa: E402
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed  # noqa: E402
from safekv.metrics import logit_preservation_metrics  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import (  # noqa: E402
    replace_cache_slices,
    stable_example_seed,
    token_count,
)
from scripts.run_answer_eval import (  # noqa: E402
    patch_ranges_for_answer_method,
    recompute_answer_suffix,
    run_base_answer_state,
    run_full_prefill_answer_state,
    run_query_and_generate_from_context_cache,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--data-path", type=str, default=None)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--budgets", default="0.20,0.30,0.45,0.60")
    parser.add_argument("--random-seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.data_path is not None:
        config = replace(config, data=replace(config.data, path=args.data_path))
    config_dir = args.config.resolve().parent.parent
    data_path = Path(config.data.path)
    if not data_path.is_absolute():
        data_path = config_dir / data_path
    examples = load_examples_for_config(config, config_dir=config_dir)
    if args.max_examples is not None:
        examples = examples[: args.max_examples]
    budgets = [float(item) for item in args.budgets.split(",") if item.strip()]
    if not budgets or any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in budgets):
        raise ValueError("budgets must be finite values in [0, 1]")
    labels = [budget_label(value) for value in budgets]
    if len(labels) != len(set(labels)):
        raise ValueError("budgets produce duplicate method labels")
    set_deterministic_seed(config.seed)
    loaded = load_causal_lm(config.model)

    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / "oracle_kv_drift_outputs.jsonl"
    rows: list[dict[str, Any]] = []
    with output_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            example_rows = evaluate_example(
                example=example,
                loaded=loaded,
                config=config,
                budgets=budgets,
                random_seed=args.random_seed,
            )
            rows.extend(example_rows)
            for row in example_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    summary_rows = summarize(rows)
    write_csv(args.results_dir / "oracle_kv_drift_summary.csv", summary_rows)
    summary = {
        "model_name": config.model.name,
        "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
        "config_path": str(args.config.resolve()),
        "config_sha256": file_sha256(args.config.resolve()),
        "dataset_path": str(data_path.resolve()),
        "dataset_sha256": file_sha256(data_path.resolve()),
        "actual_device": loaded.device,
        "torch_dtype": loaded.torch_dtype_name,
        "attention_implementation": getattr(
            loaded.model.config, "_attn_implementation", None
        ),
        "environment": environment_versions(),
        "implementation_sha256": {
            str(path): file_sha256(path)
            for path in [
                Path(__file__).resolve(),
                Path(__file__).with_name("run_answer_eval.py").resolve(),
                Path(__file__).resolve().parents[1] / "safekv" / "answer_eval.py",
                Path(__file__).resolve().parents[1] / "safekv" / "cache_ops.py",
                Path(__file__).resolve().parents[1] / "safekv" / "naive_composition.py",
                Path(__file__).resolve().parents[1] / "safekv" / "patch_recompute.py",
            ]
        },
        "num_examples": len(examples),
        "budgets": budgets,
        "random_seed": args.random_seed,
        "diagnostic_scope": (
            "oracle-informed token-local full-KV donor copy; not deployable; "
            "not a Cache-Craft implementation"
        ),
        "primary_reference": (
            "all-fresh exact-context cache followed by a separate query forward; "
            "chunk-matched to every evaluated repair path"
        ),
        "method_summary": summary_rows,
        "outputs": str(output_path),
    }
    (args.results_dir / "oracle_kv_drift_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


def evaluate_example(
    *,
    example: Any,
    loaded: Any,
    config: Any,
    budgets: list[float],
    random_seed: int,
) -> list[dict[str, Any]]:
    pack = build_prompt_pack_for_config(example, loaded, config)
    full_state = run_full_prefill_answer_state(
        example=example,
        pack=pack,
        loaded=loaded,
        config=config,
    )
    base_state = run_base_answer_state(
        example=example,
        pack=pack,
        loaded=loaded,
        config=config,
        full_logits=full_state["first_logits"],
    )
    context_len = cache_seq_len(base_state["context_cache"])
    if context_len != pack.query_token_range.start:
        raise ValueError("composed cache and global prompt frontier are misaligned")
    full_context = slice_legacy_cache(full_state["full_cache"], 0, context_len)
    fresh_reference_state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=full_context,
    )
    candidate_positions = sorted(
        position
        for token_range in pack.doc_ranges
        for position in range(token_range.start, token_range.end)
    )
    if len(candidate_positions) != len(set(candidate_positions)):
        raise ValueError("document token ranges overlap")
    if candidate_positions and (
        candidate_positions[0] < 0 or candidate_positions[-1] >= context_len
    ):
        raise ValueError("document token positions fall outside the context cache")
    drift_scores = cache_drift_scores(
        base_state["context_cache"],
        full_context,
    )
    ranked_positions = sorted(
        candidate_positions,
        key=lambda position: (-drift_scores[position], position),
    )

    policies: list[tuple[str, list[TokenRange], str]] = []
    for budget in budgets:
        count = min(len(candidate_positions), round(budget * len(candidate_positions)))
        label = budget_label(budget)
        drift_ranges = positions_to_ranges(sorted(ranked_positions[:count]))
        rng = random.Random(stable_example_seed(random_seed, example.id, f"random_p{label}"))
        random_ranges = positions_to_ranges(sorted(rng.sample(candidate_positions, count)))
        policies.append((f"oracle_kv_drift_token_local_p{label}", drift_ranges, "donor_copy"))
        policies.append(
            (
                f"random_positions_oracle_full_kv_donor_p{label}",
                random_ranges,
                "donor_copy",
            )
        )

    risk_ranges, _selected_ids = patch_ranges_for_answer_method(
        method="risk_guided_suffix_closure_k1",
        example=example,
        pack=pack,
        seed=0,
    )
    matched_count = min(len(candidate_positions), token_count(risk_ranges))
    drift_matched = positions_to_ranges(sorted(ranked_positions[:matched_count]))
    rng = random.Random(stable_example_seed(random_seed, example.id, "random_risk_k1_budget"))
    random_matched = positions_to_ranges(
        sorted(rng.sample(candidate_positions, matched_count))
    )
    policies.extend(
        [
            (
                "oracle_kv_drift_token_local_same_budget_as_risk_suffix_k1",
                drift_matched,
                "donor_copy",
            ),
            (
                "random_positions_oracle_full_kv_donor_same_budget_as_risk_suffix_k1",
                random_matched,
                "donor_copy",
            ),
            ("risk_suffix_k1_oracle_donor_copy", risk_ranges, "donor_copy"),
            ("risk_suffix_k1_actual_recompute", risk_ranges, "actual_recompute"),
        ]
    )

    rows = [
        make_row(
            method="prefix_conditioned_composition",
            state=base_state,
            fresh_reference_state=fresh_reference_state,
            one_shot_full_state=full_state,
            example=example,
            loaded=loaded,
            patched_ranges=[],
            context_len=context_len,
            repair_kind="none",
            candidate_count=len(candidate_positions),
            random_seed=random_seed,
        )
    ]
    for method, ranges, repair_kind in policies:
        if repair_kind == "actual_recompute":
            repaired_cache = recompute_answer_suffix(
                pack=pack,
                loaded=loaded,
                base_cache=base_state["context_cache"],
                patch_ranges=ranges,
            )
        else:
            repaired_cache = replace_cache_slices(
                base_state["context_cache"],
                full_context,
                ranges,
            )
        state = run_query_and_generate_from_context_cache(
            loaded=loaded,
            config=config,
            pack=pack,
            context_cache=repaired_cache,
        )
        rows.append(
            make_row(
                method=method,
                state=state,
                fresh_reference_state=fresh_reference_state,
                one_shot_full_state=full_state,
                example=example,
                loaded=loaded,
                patched_ranges=ranges,
                context_len=context_len,
                repair_kind=repair_kind,
                candidate_count=len(candidate_positions),
                random_seed=random_seed,
            )
        )
    return rows


def cache_drift_scores(base_cache: Any, full_cache: Any) -> list[float]:
    import torch

    base = to_legacy_cache(base_cache)
    full = to_legacy_cache(full_cache)
    if len(base) != len(full):
        raise ValueError("cache layer mismatch")
    sequence_length = cache_seq_len(base)
    scores = torch.zeros(sequence_length, dtype=torch.float64)
    for (base_key, base_value), (full_key, full_value) in zip(base, full, strict=True):
        layer_score = torch.zeros(
            sequence_length,
            dtype=torch.float32,
            device=base_key.device,
        )
        for base_tensor, full_tensor in (
            (base_key, full_key),
            (base_value, full_value),
        ):
            if base_tensor.shape != full_tensor.shape:
                raise ValueError("base/full KV tensor shape mismatch")
            if base_tensor.ndim < 2 or base_tensor.shape[-2] != sequence_length:
                raise ValueError("unsupported KV layout: expected sequence axis at -2")
            difference = (full_tensor.float() - base_tensor.float()).square()
            sequence_axis = difference.ndim - 2
            reduction_axes = tuple(
                axis for axis in range(difference.ndim) if axis != sequence_axis
            )
            per_token = difference.mean(dim=reduction_axes)
            scale = full_tensor.float().square().mean().clamp_min(1e-12)
            layer_score += per_token / scale
        scores += layer_score.detach().double().cpu()
    return scores.tolist()


def make_row(
    *,
    method: str,
    state: dict[str, Any],
    fresh_reference_state: dict[str, Any],
    one_shot_full_state: dict[str, Any],
    example: Any,
    loaded: Any,
    patched_ranges: list[TokenRange],
    context_len: int,
    repair_kind: str,
    candidate_count: int,
    random_seed: int,
) -> dict[str, Any]:
    patched_count = token_count(patched_ranges)
    answer_metrics = answer_metric_fields(
        generated_answer=state["generated_answer"],
        full_prefill_answer=fresh_reference_state["generated_answer"],
        gold_answer=example.gold_answer,
    )
    one_shot_metrics = answer_metric_fields(
        generated_answer=state["generated_answer"],
        full_prefill_answer=one_shot_full_state["generated_answer"],
        gold_answer=example.gold_answer,
    )
    logit_metrics = logit_preservation_metrics(
        fresh_reference_state["first_logits"],
        state["first_logits"],
        loaded.tokenizer,
    )
    return {
        "example_id": example.id,
        "category": example.category,
        "method": method,
        "repair_kind": repair_kind,
        "random_seed": random_seed,
        "context_token_count": context_len,
        "candidate_document_token_count": candidate_count,
        "patched_token_count": patched_count,
        "patched_ranges": [
            {"start": int(token_range.start), "end": int(token_range.end)}
            for token_range in patched_ranges
        ],
        "patched_positions_sha256": positions_sha256(patched_ranges),
        "patched_context_ratio": patched_count / context_len if context_len else 0.0,
        "patched_document_token_ratio": patched_count / candidate_count if candidate_count else 0.0,
        "qa_answer_equivalence_to_fresh_reference": answer_metrics[
            "answer_equivalence_to_full_prefill"
        ],
        "qa_answer_equivalence_to_one_shot_full_prefill": one_shot_metrics[
            "answer_equivalence_to_full_prefill"
        ],
        "raw_answer_exact_to_fresh_reference": (
            state["generated_answer"] == fresh_reference_state["generated_answer"]
        ),
        "generated_token_sequence_equivalent_to_fresh_reference": (
            state.get("generated_token_ids")
            == fresh_reference_state.get("generated_token_ids")
        ),
        "first_token_kl_to_fresh_reference": logit_metrics[
            "first_token_kl_full_to_method"
        ],
        "top1_match_to_fresh_reference": logit_metrics["top1_match"],
        "generated_answer": state["generated_answer"],
        "fresh_reference_answer": fresh_reference_state["generated_answer"],
        "one_shot_full_prefill_answer": one_shot_full_state["generated_answer"],
        "gold_answer": example.gold_answer,
        "gold_exact_match": answer_metrics["gold_exact_match"],
        "gold_token_f1": answer_metrics["gold_token_f1"],
        "answer_changed_from_fresh_reference_and_gold_wrong": answer_metrics[
            "answer_changed_and_gold_wrong"
        ],
    }


def positions_sha256(ranges: list[TokenRange]) -> str:
    """Hash the exact selected token positions without bloating every output row."""

    digest = hashlib.sha256()
    for token_range in ranges:
        for position in range(token_range.start, token_range.end):
            digest.update(int(position).to_bytes(8, byteorder="big", signed=False))
    return digest.hexdigest()


def environment_versions() -> dict[str, Any]:
    import torch
    import transformers

    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def positions_to_ranges(positions: list[int]) -> list[TokenRange]:
    if not positions:
        return []
    ranges = []
    start = positions[0]
    previous = positions[0]
    for position in positions[1:]:
        if position == previous + 1:
            previous = position
            continue
        ranges.append(TokenRange(start, previous + 1))
        start = position
        previous = position
    ranges.append(TokenRange(start, previous + 1))
    return ranges


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["method"]].append(row)
    output = []
    for method, items in sorted(groups.items()):
        output.append(
            {
                "method": method,
                "repair_kind": items[0]["repair_kind"],
                "num_examples": len(items),
                "qa_answer_equivalence_to_fresh_reference": mean(
                    float(item["qa_answer_equivalence_to_fresh_reference"])
                    for item in items
                ),
                "raw_answer_exact_to_fresh_reference": mean(
                    float(item["raw_answer_exact_to_fresh_reference"])
                    for item in items
                ),
                "token_sequence_equivalence_to_fresh_reference": mean(
                    float(
                        item[
                            "generated_token_sequence_equivalent_to_fresh_reference"
                        ]
                    )
                    for item in items
                ),
                "changed_from_fresh_and_gold_wrong_rate": mean(
                    float(
                        item[
                            "answer_changed_from_fresh_reference_and_gold_wrong"
                        ]
                    )
                    for item in items
                ),
                "avg_first_token_kl_to_fresh_reference": mean(
                    float(item["first_token_kl_to_fresh_reference"])
                    for item in items
                ),
                "top1_match_to_fresh_reference": mean(
                    float(item["top1_match_to_fresh_reference"]) for item in items
                ),
                "avg_patched_context_ratio": mean(
                    float(item["patched_context_ratio"]) for item in items
                ),
                "avg_patched_document_token_ratio": mean(
                    float(item["patched_document_token_ratio"]) for item in items
                ),
            }
        )
    return output


def budget_label(value: float) -> str:
    return format(value, ".6f").rstrip("0").rstrip(".").replace(".", "p")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean(values: Any) -> float:
    materialized = list(values)
    return statistics.fmean(materialized) if materialized else 0.0


if __name__ == "__main__":
    main()
