#!/usr/bin/env python
"""Run an operational query-attention-ranked local recomputation baseline.

This is an algorithmic comparison motivated by Cache-Craft's query/chunk
attention principle.  It is not presented as a Cache-Craft implementation:
selection is token-level, uses the current query's attention over the stale
composed cache, and then truly forwards only the selected local token ranges
while retaining all later unselected stale states.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.attention_baseline import (  # noqa: E402
    aggregate_query_attention,
    candidate_positions_from_ranges,
    fp32_selection_attention_forward,
    positions_to_ranges,
    rank_candidate_positions,
    selected_count,
)
from safekv.cache_ops import (  # noqa: E402
    cache_seq_len,
    legacy_cache_to_model_cache,
    slice_legacy_cache,
)
from safekv.config import load_config  # noqa: E402
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import stable_example_seed  # noqa: E402
from scripts.run_answer_eval import (  # noqa: E402
    recompute_answer_ranges_locally,
    run_base_answer_state,
    run_full_prefill_answer_state,
    run_query_and_generate_from_context_cache,
)
from scripts.run_oracle_kv_drift_local_baseline import (  # noqa: E402
    budget_label,
    environment_versions,
    file_sha256,
    make_row,
    summarize,
    write_csv,
)


DEFAULT_BUDGETS = "0.05,0.10,0.16,0.20,0.30,0.45,0.60"
DEFAULT_RANDOM_SEEDS = "13,29,47"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--data-path", type=str, default=None)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--budgets", default=DEFAULT_BUDGETS)
    parser.add_argument("--random-seeds", default=DEFAULT_RANDOM_SEEDS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("set PYTHONHASHSEED=0 for a tracked baseline run")
    config_path = args.config.resolve()
    config = load_config(config_path)
    if args.data_path is not None:
        config = replace(config, data=replace(config.data, path=args.data_path))
    if config.generation.do_sample or config.generation.temperature != 0.0:
        raise ValueError("baseline requires deterministic greedy decoding")
    config_dir = config_path.parent.parent
    data_path = Path(config.data.path)
    if not data_path.is_absolute():
        data_path = config_dir / data_path
    data_path = data_path.resolve()
    frozen_hashes = implementation_hashes(config_path=config_path, data_path=data_path)

    budgets = parse_floats(args.budgets)
    if not budgets or any(value < 0.0 or value > 1.0 for value in budgets):
        raise ValueError("budgets must be in [0, 1]")
    if len({budget_label(value) for value in budgets}) != len(budgets):
        raise ValueError("budgets produce duplicate method labels")
    random_seeds = parse_ints(args.random_seeds)
    if not random_seeds or len(set(random_seeds)) != len(random_seeds):
        raise ValueError("random seeds must be a non-empty unique list")

    examples = load_examples_for_config(config, config_dir=config_dir)
    if args.max_examples is not None:
        examples = examples[: args.max_examples]
    set_deterministic_seed(config.seed)
    loaded = load_causal_lm(config.model)

    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / "query_attention_local_outputs.jsonl"
    generated_paths = [
        output_path,
        args.results_dir / "query_attention_local_summary.csv",
        args.results_dir / "query_attention_local_summary.json",
    ]
    if any(path.exists() for path in generated_paths):
        raise FileExistsError(
            "refusing to overwrite an existing query-attention baseline result"
        )
    rows: list[dict[str, Any]] = []
    with output_path.open("w", encoding="utf-8") as handle:
        for example in examples:
            example_rows = evaluate_example(
                example=example,
                loaded=loaded,
                config=config,
                budgets=budgets,
                random_seeds=random_seeds,
            )
            rows.extend(example_rows)
            for row in example_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    if implementation_hashes(config_path=config_path, data_path=data_path) != frozen_hashes:
        raise RuntimeError("config, data, or implementation changed during the run")
    summary_rows = summarize(rows)
    write_csv(args.results_dir / "query_attention_local_summary.csv", summary_rows)
    summary = {
        "schema_version": 1,
        "model_name": config.model.name,
        "model_commit_hash": getattr(loaded.model.config, "_commit_hash", None),
        "config_path": str(config_path),
        "data_path": str(data_path),
        "frozen_input_and_implementation_sha256": frozen_hashes,
        "actual_device": loaded.device,
        "torch_dtype": loaded.torch_dtype_name,
        "loaded_attention_implementation": getattr(
            loaded.model.config, "_attn_implementation", None
        ),
        "environment": environment_versions(),
        "num_examples": len(examples),
        "budgets": budgets,
        "random_seeds": random_seeds,
        "selection_inputs": [
            "current query token ids",
            "stale composed context KV",
            "query-to-context attention",
            "document token boundaries",
        ],
        "forbidden_selection_inputs": [
            "full-prefill KV/logits/answer",
            "gold answer",
            "gold evidence labels",
            "sampled mismatch mask",
        ],
        "method_scope": (
            "operational query-attention-ranked token-local recomputation; "
            "algorithmic Cache-Craft-motivated baseline, not Cache-Craft code"
        ),
        "official_cache_craft_implementation": False,
        "planning_cost_scope": (
            "attention selection requires a separate stale-cache query forward; "
            "per-example planning wall time is retained in raw rows"
        ),
        "method_summary": summary_rows,
        "outputs": str(output_path),
    }
    (args.results_dir / "query_attention_local_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def evaluate_example(
    *,
    example: Any,
    loaded: Any,
    config: Any,
    budgets: list[float],
    random_seeds: list[int],
) -> list[dict[str, Any]]:
    pack = build_prompt_pack_for_config(example, loaded, config)
    full_state = run_full_prefill_answer_state(
        example=example, pack=pack, loaded=loaded, config=config
    )
    base_state = run_base_answer_state(
        example=example,
        pack=pack,
        loaded=loaded,
        config=config,
        full_logits=full_state["first_logits"],
    )
    context_cache = base_state["context_cache"]
    context_length = cache_seq_len(context_cache)
    if context_length != pack.query_token_range.start:
        raise ValueError("composed context cache is not aligned to the query frontier")
    candidate_positions = candidate_positions_from_ranges(
        pack.doc_ranges, context_length=context_length
    )
    attention_scores, planning_seconds, attention_backend = query_attention_scores(
        pack=pack,
        loaded=loaded,
        context_cache=context_cache,
    )
    ranked_positions = rank_candidate_positions(attention_scores, candidate_positions)

    rows = [
        with_baseline_metadata(
            make_row(
                method="prefix_conditioned_composition",
                state=base_state,
                fresh_reference_state=full_state,
                one_shot_full_state=full_state,
                example=example,
                loaded=loaded,
                patched_ranges=[],
                context_len=context_length,
                repair_kind="none",
                candidate_count=len(candidate_positions),
                random_seed=0,
            ),
            selection_source="none",
            planning_seconds=0.0,
            attention_backend=attention_backend,
        )
    ]

    full_context = slice_legacy_cache(full_state["full_cache"], 0, context_length)
    chunked_full_state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=full_context,
    )
    rows.append(
        with_baseline_metadata(
            make_row(
                method="all_fresh_context_chunked_reference",
                state=chunked_full_state,
                fresh_reference_state=full_state,
                one_shot_full_state=full_state,
                example=example,
                loaded=loaded,
                patched_ranges=list(pack.doc_ranges),
                context_len=context_length,
                repair_kind="all_fresh_reference",
                candidate_count=len(candidate_positions),
                random_seed=0,
            ),
            selection_source="all_document_tokens",
            planning_seconds=0.0,
            attention_backend=attention_backend,
        )
    )

    for budget in budgets:
        count = selected_count(len(candidate_positions), budget)
        label = budget_label(budget)
        attention_ranges = positions_to_ranges(ranked_positions[:count])
        rows.append(
            evaluate_policy(
                method=f"query_attention_local_actual_p{label}",
                ranges=attention_ranges,
                selection_source="stale_query_attention",
                selection_seed=0,
                planning_seconds=planning_seconds,
                attention_backend=attention_backend,
                example=example,
                pack=pack,
                loaded=loaded,
                config=config,
                base_state=base_state,
                full_state=full_state,
                context_length=context_length,
                candidate_count=len(candidate_positions),
            )
        )
        for seed in random_seeds:
            rng = random.Random(
                stable_example_seed(seed, example.id, f"attention_budget_p{label}")
            )
            random_ranges = positions_to_ranges(
                rng.sample(candidate_positions, count) if count else []
            )
            rows.append(
                evaluate_policy(
                    method=f"random_local_actual_p{label}_seed{seed}",
                    ranges=random_ranges,
                    selection_source="random_equal_token_budget",
                    selection_seed=seed,
                    planning_seconds=0.0,
                    attention_backend=attention_backend,
                    example=example,
                    pack=pack,
                    loaded=loaded,
                    config=config,
                    base_state=base_state,
                    full_state=full_state,
                    context_length=context_length,
                    candidate_count=len(candidate_positions),
                )
            )
    return rows


def query_attention_scores(
    *, pack: Any, loaded: Any, context_cache: Any
) -> tuple[list[float], float, str]:
    import torch

    query_range = pack.query_token_range
    query_ids = torch.tensor(
        [pack.full_input_ids[query_range.start : query_range.end]],
        dtype=torch.long,
        device=loaded.device,
    )
    position_ids = torch.arange(
        query_range.start,
        query_range.end,
        dtype=torch.long,
        device=loaded.device,
    ).unsqueeze(0)
    context_length = cache_seq_len(context_cache)
    attention_mask = torch.ones(
        (1, context_length + query_ids.shape[1]),
        dtype=torch.long,
        device=loaded.device,
    )
    from transformers import AttentionInterface

    selection_backend = "safekv_selection_eager_fp32"
    AttentionInterface.register(selection_backend, fp32_selection_attention_forward)
    original_backend = getattr(loaded.model.config, "_attn_implementation", None)
    loaded.model.config._attn_implementation = selection_backend
    if loaded.device == "cuda":
        torch.cuda.synchronize()
    started = time.perf_counter()
    try:
        with torch.no_grad():
            outputs = loaded.model(
                input_ids=query_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_values=legacy_cache_to_model_cache(context_cache),
                use_cache=False,
                output_attentions=True,
                return_dict=True,
            )
        if loaded.device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        attentions = getattr(outputs, "attentions", None)
        if attentions is None:
            raise RuntimeError(
                "model/backend did not return attention tensors with output_attentions=True"
            )
        scores = aggregate_query_attention(
            attentions,
            context_length=context_length,
            query_length=query_ids.shape[1],
        )
    finally:
        loaded.model.config._attn_implementation = original_backend
    return scores, elapsed, selection_backend


def evaluate_policy(
    *,
    method: str,
    ranges: list[Any],
    selection_source: str,
    selection_seed: int,
    planning_seconds: float,
    attention_backend: str,
    example: Any,
    pack: Any,
    loaded: Any,
    config: Any,
    base_state: dict[str, Any],
    full_state: dict[str, Any],
    context_length: int,
    candidate_count: int,
) -> dict[str, Any]:
    repaired_cache = recompute_answer_ranges_locally(
        pack=pack,
        loaded=loaded,
        base_cache=base_state["context_cache"],
        patch_ranges=ranges,
    )
    state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=repaired_cache,
    )
    row = make_row(
        method=method,
        state=state,
        fresh_reference_state=full_state,
        one_shot_full_state=full_state,
        example=example,
        loaded=loaded,
        patched_ranges=ranges,
        context_len=context_length,
        repair_kind="actual_local_recompute",
        candidate_count=candidate_count,
        random_seed=selection_seed,
    )
    return with_baseline_metadata(
        row,
        selection_source=selection_source,
        planning_seconds=planning_seconds,
        attention_backend=attention_backend,
    )


def with_baseline_metadata(
    row: dict[str, Any],
    *,
    selection_source: str,
    planning_seconds: float,
    attention_backend: str,
) -> dict[str, Any]:
    row.update(
        {
            "selection_source": selection_source,
            "selection_planning_seconds": planning_seconds,
            "selection_attention_backend": attention_backend,
            "official_cache_craft_implementation": False,
        }
    )
    return row


def implementation_hashes(*, config_path: Path, data_path: Path) -> dict[str, str]:
    paths = [
        config_path,
        data_path,
        Path(__file__).resolve(),
        Path(__file__).resolve().parents[1] / "safekv" / "attention_baseline.py",
        Path(__file__).with_name("run_answer_eval.py").resolve(),
        Path(__file__).with_name("run_oracle_kv_drift_local_baseline.py").resolve(),
    ]
    return {str(path): file_sha256(path) for path in paths}


def parse_floats(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_ints(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    main()
