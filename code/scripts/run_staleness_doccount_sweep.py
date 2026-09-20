#!/usr/bin/env python
"""Run the ARR staleness-probability by document-count factorial sweep."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.answer_eval import answer_metric_fields  # noqa: E402
from safekv.build_diagnostic import read_jsonl  # noqa: E402
from safekv.cache_ops import cache_seq_len, slice_legacy_cache  # noqa: E402
from safekv.config import load_config  # noqa: E402
from safekv.doc_selector import (  # noqa: E402
    query_similarity_doc_scores,
    risk_guided_doc_scores,
)
from safekv.full_prefill import set_deterministic_seed  # noqa: E402
from safekv.metrics import logit_preservation_metrics  # noqa: E402
from safekv.modeling import load_causal_lm  # noqa: E402
from safekv.naive_composition import build_prompt_pack_for_config  # noqa: E402
from safekv.patch_recompute import replace_cache_slices, token_count  # noqa: E402
from scripts.run_answer_eval import (  # noqa: E402
    recompute_answer_suffix,
    run_base_answer_state,
    run_full_prefill_answer_state,
    run_query_and_generate_from_context_cache,
)


METHODS = [
    "mixed_no_repair",
    "query_actual_doc_only_k1",
    "query_actual_downstream_w4_k1",
    "query_actual_suffix_k1",
    "risk_actual_suffix_k1",
    "risk_actual_suffix_k2",
    "earliest_stale_actual_suffix_oracle",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--data-spec",
        action="append",
        required=True,
        help="LABEL=PATH; may be repeated",
    )
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--probabilities", default="0,0.25,0.5,0.75,1")
    parser.add_argument("--mask-seeds", default="13,29,47")
    parser.add_argument("--strict-invariants", action="store_true")
    parser.add_argument(
        "--require-paired-examples",
        action="store_true",
        help="require every data spec to contain the same ordered example IDs",
    )
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    config_dir = args.config.resolve().parent.parent
    probabilities = parse_float_list(args.probabilities)
    mask_seeds = parse_int_list(args.mask_seeds)
    specs = parse_data_specs(args.data_spec, config_dir)
    pairing_summary = validate_data_pairing(
        specs,
        max_examples=args.max_examples,
        require_paired=args.require_paired_examples,
    )
    set_deterministic_seed(config.seed)
    loaded = load_causal_lm(config.model)

    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / "staleness_doccount_outputs.jsonl"
    manifest_path = args.results_dir / "staleness_doccount_manifest.json"
    manifest = build_manifest(
        args=args,
        config=config,
        specs=specs,
        probabilities=probabilities,
        mask_seeds=mask_seeds,
    )
    if args.resume:
        if not manifest_path.exists():
            raise ValueError(
                f"cannot resume without matching manifest: {manifest_path}"
            )
        if json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
            raise ValueError("resume manifest mismatch; use a new results directory")
    else:
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    completed = read_completed(output_path) if args.resume else set()
    mode = "a" if args.resume else "w"
    invariant_failures: list[dict[str, Any]] = []

    with output_path.open(mode, encoding="utf-8") as handle:
        for label, path in specs:
            examples = read_jsonl(path)
            if args.max_examples is not None:
                examples = examples[: args.max_examples]
            for example in examples:
                evaluate_example_grid(
                    label=label,
                    example=example,
                    loaded=loaded,
                    config=config,
                    probabilities=probabilities,
                    mask_seeds=mask_seeds,
                    completed=completed,
                    handle=handle,
                    invariant_failures=invariant_failures,
                    strict_invariants=args.strict_invariants,
                )

    rows = read_rows(output_path)
    invariant_failures = collect_persisted_invariant_failures(rows)
    summary_rows = summarize(rows)
    write_csv(args.results_dir / "staleness_doccount_summary.csv", summary_rows)
    summary = {
        "model_name": config.model.name,
        "primary_reference": (
            "all-fresh exact-context cache followed by a separate query forward "
            "(chunk-matched to every mixed/repair path)"
        ),
        "staleness_definition": (
            "for positions >= 2, independently replace an exact-context document "
            "KV slice with the same document encoded only against the static prefix"
        ),
        "selector_scope": (
            "operational Query/Risk selectors rank all structurally eligible "
            "positions >= 2 and never observe the sampled stale mask"
        ),
        "data_specs": [{"label": label, "path": str(path)} for label, path in specs],
        "data_pairing": pairing_summary,
        "probabilities": probabilities,
        "mask_seeds": mask_seeds,
        "num_rows": len(rows),
        "num_invariant_failures": len(invariant_failures),
        "invariant_failures": invariant_failures,
        "fresh_reference_vs_one_shot_summary": summarize_reference_sanity(rows),
        "method_cell_summary": summary_rows,
        "outputs": str(output_path),
    }
    (args.results_dir / "staleness_doccount_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


def evaluate_example_grid(
    *,
    label: str,
    example: Any,
    loaded: Any,
    config: Any,
    probabilities: list[float],
    mask_seeds: list[int],
    completed: set[tuple[str, str, int, float, str]],
    handle: Any,
    invariant_failures: list[dict[str, Any]],
    strict_invariants: bool,
) -> None:
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
    fresh_context = slice_legacy_cache(full_state["full_cache"], 0, context_len)
    if context_len != pack.query_token_range.start:
        raise ValueError("context cache and query frontier are misaligned")
    # Every mixed/repaired serving path consumes an existing context cache and
    # runs the query in a separate forward.  Use the all-fresh cache under the
    # same boundary as the primary reference so the sweep isolates staleness
    # rather than one-shot-vs-chunked numerical effects.
    fresh_reference_state = run_query_and_generate_from_context_cache(
        loaded=loaded,
        config=config,
        pack=pack,
        context_cache=fresh_context,
    )
    fresh_vs_one_shot_logits = logit_preservation_metrics(
        full_state["first_logits"],
        fresh_reference_state["first_logits"],
        loaded.tokenizer,
    )

    num_documents = len(example.documents)
    query_scores = query_similarity_doc_scores(example)
    risk_scores = risk_guided_doc_scores(example)

    for mask_seed in mask_seeds:
        uniforms = [
            1.0,
            *[
                stable_uniform(mask_seed, example.id, example.documents[position])
                for position in range(1, num_documents)
            ],
        ]
        for probability in probabilities:
            if all(
                (label, example.id, mask_seed, probability, method) in completed
                for method in METHODS
            ):
                continue
            stale_positions = [
                position
                for position in range(1, num_documents)
                if uniforms[position] < probability
            ]
            stale_ranges = [pack.doc_ranges[position] for position in stale_positions]
            mixed_cache = (
                fresh_context
                if not stale_ranges
                else replace_cache_slices(
                    fresh_context,
                    base_state["context_cache"],
                    stale_ranges,
                )
            )
            mixed_state = run_query_and_generate_from_context_cache(
                loaded=loaded,
                config=config,
                pack=pack,
                context_cache=mixed_cache,
            )

            potentially_stale_ids = {
                example.documents[position].doc_id
                for position in range(1, num_documents)
            }
            query_selected = top_k_candidate_positions(
                query_scores,
                candidate_ids=potentially_stale_ids,
                example=example,
                k=1,
            )
            risk_selected_k1 = top_k_candidate_positions(
                risk_scores,
                candidate_ids=potentially_stale_ids,
                example=example,
                k=1,
            )
            risk_selected_k2 = top_k_candidate_positions(
                risk_scores,
                candidate_ids=potentially_stale_ids,
                example=example,
                k=2,
            )
            query_start = min(query_selected) if query_selected else num_documents
            risk_start_k1 = min(risk_selected_k1) if risk_selected_k1 else num_documents
            risk_start_k2 = min(risk_selected_k2) if risk_selected_k2 else num_documents
            earliest_stale = min(stale_positions) if stale_positions else num_documents
            actions = {
                "mixed_no_repair": (num_documents, num_documents),
                "query_actual_doc_only_k1": (
                    query_start,
                    min(num_documents, query_start + 1),
                ),
                "query_actual_downstream_w4_k1": (
                    query_start,
                    min(num_documents, query_start + 4),
                ),
                "query_actual_suffix_k1": (query_start, num_documents),
                "risk_actual_suffix_k1": (risk_start_k1, num_documents),
                "risk_actual_suffix_k2": (risk_start_k2, num_documents),
                "earliest_stale_actual_suffix_oracle": (earliest_stale, num_documents),
            }

            states: dict[tuple[int, int], dict[str, Any]] = {
                (num_documents, num_documents): mixed_state
            }
            for action in sorted(set(actions.values())):
                start, end = action
                if action in states:
                    continue
                ranges = list(pack.doc_ranges[start:end])
                repaired_cache = recompute_answer_suffix(
                    pack=pack,
                    loaded=loaded,
                    base_cache=mixed_cache,
                    patch_ranges=ranges,
                )
                states[action] = run_query_and_generate_from_context_cache(
                    loaded=loaded,
                    config=config,
                    pack=pack,
                    context_cache=repaired_cache,
                )

            failures = check_invariants(
                label=label,
                example=example,
                probability=probability,
                mask_seed=mask_seed,
                num_documents=num_documents,
                stale_positions=stale_positions,
                fresh_reference_state=fresh_reference_state,
                states=states,
            )
            invariant_failures.extend(failures)
            if failures and strict_invariants:
                raise AssertionError(json.dumps(failures[0], ensure_ascii=False))

            for method, action in actions.items():
                key = (label, example.id, mask_seed, probability, method)
                if key in completed:
                    continue
                start, end = action
                state = states[action]
                ranges = list(pack.doc_ranges[start:end]) if start < end else []
                fresh_metrics = answer_metric_fields(
                    generated_answer=state["generated_answer"],
                    full_prefill_answer=fresh_reference_state["generated_answer"],
                    gold_answer=example.gold_answer,
                )
                one_shot_metrics = answer_metric_fields(
                    generated_answer=state["generated_answer"],
                    full_prefill_answer=full_state["generated_answer"],
                    gold_answer=example.gold_answer,
                )
                logit_metrics = logit_preservation_metrics(
                    fresh_reference_state["first_logits"],
                    state["first_logits"],
                    loaded.tokenizer,
                )
                row = {
                    "dataset_label": label,
                    "example_id": example.id,
                    "category": example.category,
                    "num_documents": num_documents,
                    "stale_probability": probability,
                    "mask_seed": mask_seed,
                    "stale_positions": stale_positions,
                    "stale_doc_count": len(stale_positions),
                    "realized_stale_fraction": (
                        len(stale_positions) / max(1, num_documents - 1)
                        if num_documents > 1
                        else 0.0
                    ),
                    "method": method,
                    "repair_start": start,
                    "repair_end": end,
                    "recomputed_token_count": token_count(ranges),
                    "recomputed_token_ratio": (
                        token_count(ranges) / context_len if context_len else 0.0
                    ),
                    "answer_equivalence_to_fresh_reference": fresh_metrics[
                        "answer_equivalence_to_full_prefill"
                    ],
                    "answer_equivalence_to_one_shot_full_prefill": one_shot_metrics[
                        "answer_equivalence_to_full_prefill"
                    ],
                    "raw_answer_exact_to_fresh_reference": (
                        state["generated_answer"]
                        == fresh_reference_state["generated_answer"]
                    ),
                    "generated_token_sequence_equivalent_to_fresh_reference": (
                        state["generated_token_ids"]
                        == fresh_reference_state["generated_token_ids"]
                    ),
                    "first_token_kl_to_fresh_reference": logit_metrics[
                        "first_token_kl_full_to_method"
                    ],
                    "top1_match_to_fresh_reference": logit_metrics["top1_match"],
                    "generated_answer": state["generated_answer"],
                    "fresh_reference_answer": fresh_reference_state[
                        "generated_answer"
                    ],
                    "one_shot_full_prefill_answer": full_state["generated_answer"],
                    "fresh_reference_vs_one_shot_qa_equivalent": (
                        answer_metric_fields(
                            generated_answer=fresh_reference_state[
                                "generated_answer"
                            ],
                            full_prefill_answer=full_state["generated_answer"],
                            gold_answer=example.gold_answer,
                        )["answer_equivalence_to_full_prefill"]
                    ),
                    "fresh_reference_vs_one_shot_token_exact": (
                        fresh_reference_state["generated_token_ids"]
                        == full_state["generated_token_ids"]
                    ),
                    "fresh_reference_vs_one_shot_first_token_kl": (
                        fresh_vs_one_shot_logits[
                            "first_token_kl_full_to_method"
                        ]
                    ),
                    "p1_mixed_equals_prefix_qa_answer": (
                        answer_metric_fields(
                            generated_answer=mixed_state["generated_answer"],
                            full_prefill_answer=base_state["generated_answer"],
                            gold_answer=example.gold_answer,
                        )["answer_equivalence_to_full_prefill"]
                        if probability == 1.0
                        else None
                    ),
                    "invariant_failures": failures,
                    "gold_answer": example.gold_answer,
                    "normalized_generated_answer": fresh_metrics[
                        "normalized_generated_answer"
                    ],
                    "normalized_fresh_reference_answer": fresh_metrics[
                        "normalized_full_prefill_answer"
                    ],
                    "normalized_gold_answer": fresh_metrics[
                        "normalized_gold_answer"
                    ],
                    "gold_exact_match": fresh_metrics["gold_exact_match"],
                    "gold_token_f1": fresh_metrics["gold_token_f1"],
                    "answer_contains_gold": fresh_metrics["answer_contains_gold"],
                    "answer_changed_from_fresh_reference": fresh_metrics[
                        "answer_changed_from_full"
                    ],
                    "answer_changed_from_fresh_reference_and_gold_wrong": (
                        fresh_metrics["answer_changed_and_gold_wrong"]
                    ),
                }
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                completed.add(key)


def top_k_candidate_positions(
    scores: list[Any],
    *,
    candidate_ids: set[int],
    example: Any,
    k: int,
) -> list[int]:
    # The operational selector cannot inspect the sampled stale mask.  It only
    # knows that documents after the first have a possible predecessor-history
    # mismatch under this controlled definition of staleness.
    eligible = [score for score in scores if score.doc_id in candidate_ids]
    selected = sorted(eligible, key=lambda item: (-item.score, item.doc_id))[:k]
    selected_ids = {item.doc_id for item in selected}
    return [
        position
        for position, doc in enumerate(example.documents)
        if doc.doc_id in selected_ids
    ]


def check_invariants(
    *,
    label: str,
    example: Any,
    probability: float,
    mask_seed: int,
    num_documents: int,
    stale_positions: list[int],
    fresh_reference_state: dict[str, Any],
    states: dict[tuple[int, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    failures = []

    def add(name: str, observed: str, expected: str) -> None:
        failures.append(
            {
                "dataset_label": label,
                "example_id": example.id,
                "num_documents": num_documents,
                "stale_probability": probability,
                "mask_seed": mask_seed,
                "invariant": name,
                "observed": observed,
                "expected": expected,
            }
        )

    mixed_state = states[(num_documents, num_documents)]
    mixed = mixed_state["generated_answer"]
    fresh = fresh_reference_state["generated_answer"]
    if not stale_positions:
        if mixed != fresh:
            add("no-stale raw answer equals chunk-matched fresh reference", mixed, fresh)
        if mixed_state["generated_token_ids"] != fresh_reference_state[
            "generated_token_ids"
        ]:
            add(
                "no-stale generated token sequence equals fresh reference",
                str(mixed_state["generated_token_ids"]),
                str(fresh_reference_state["generated_token_ids"]),
            )
        max_abs_logit_diff = float(
            (
                mixed_state["first_logits"]
                - fresh_reference_state["first_logits"]
            )
            .abs()
            .max()
            .item()
        )
        if max_abs_logit_diff > 1e-6:
            add(
                "no-stale first logits equal fresh reference",
                str(max_abs_logit_diff),
                "max_abs_diff <= 1e-6",
            )
    return failures


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int, float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[
            (
                row["dataset_label"],
                int(row["num_documents"]),
                float(row["stale_probability"]),
                row["method"],
            )
        ].append(row)
    output = []
    for (label, num_documents, probability, method), items in sorted(groups.items()):
        equivalence = mean(
            float(item["answer_equivalence_to_fresh_reference"]) for item in items
        )
        base_items = groups[(label, num_documents, probability, "mixed_no_repair")]
        base_equivalence = mean(
            float(item["answer_equivalence_to_fresh_reference"])
            for item in base_items
        )
        denominator = 1.0 - base_equivalence
        clustered_values = per_example_means(
            items,
            field="answer_equivalence_to_fresh_reference",
        )
        ci_low, ci_high = normal_mean_ci95(clustered_values)
        output.append(
            {
                "dataset_label": label,
                "num_documents": num_documents,
                "stale_probability": probability,
                "method": method,
                "num_rows": len(items),
                "num_examples": len({item["example_id"] for item in items}),
                "num_mask_seeds": len({int(item["mask_seed"]) for item in items}),
                "answer_equivalence_to_fresh_reference": equivalence,
                "clustered_example_ci95_low": ci_low,
                "clustered_example_ci95_high": ci_high,
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
                "answer_equivalence_to_one_shot_full_prefill": mean(
                    float(item["answer_equivalence_to_one_shot_full_prefill"])
                    for item in items
                ),
                "top1_match_to_fresh_reference": mean(
                    float(item["top1_match_to_fresh_reference"]) for item in items
                ),
                "avg_first_token_kl_to_fresh_reference": mean(
                    float(item["first_token_kl_to_fresh_reference"])
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
                "avg_realized_stale_fraction": mean(
                    float(item["realized_stale_fraction"]) for item in items
                ),
                "avg_recomputed_token_ratio": mean(
                    float(item["recomputed_token_ratio"]) for item in items
                ),
                "repair_recovery": (
                    (equivalence - base_equivalence) / denominator
                    if denominator > 0
                    else None
                ),
            }
        )
    return output


def per_example_means(
    rows: list[dict[str, Any]],
    *,
    field: str,
) -> list[float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["example_id"])].append(float(row[field]))
    return [statistics.fmean(values) for values in grouped.values()]


def normal_mean_ci95(values: list[float]) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    estimate = statistics.fmean(values)
    if len(values) == 1:
        return (estimate, estimate)
    standard_error = statistics.stdev(values) / (len(values) ** 0.5)
    half_width = 1.96 * standard_error
    return (max(0.0, estimate - half_width), min(1.0, estimate + half_width))


def summarize_reference_sanity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        unique[(row["dataset_label"], row["example_id"])] = row
    values = list(unique.values())
    return {
        "num_examples": len(values),
        "qa_answer_equivalence": mean(
            float(row["fresh_reference_vs_one_shot_qa_equivalent"])
            for row in values
        ),
        "generated_token_exact": mean(
            float(row["fresh_reference_vs_one_shot_token_exact"])
            for row in values
        ),
        "avg_first_token_kl": mean(
            float(row["fresh_reference_vs_one_shot_first_token_kl"])
            for row in values
        ),
    }


def parse_data_specs(raw_specs: list[str], config_dir: Path) -> list[tuple[str, Path]]:
    specs = []
    for raw in raw_specs:
        if "=" not in raw:
            raise ValueError(f"data spec must be LABEL=PATH: {raw}")
        label, raw_path = raw.split("=", 1)
        path = Path(raw_path)
        if not path.is_absolute():
            path = config_dir / path
        specs.append((label, path))
    return specs


def validate_data_pairing(
    specs: list[tuple[str, Path]],
    *,
    max_examples: int | None,
    require_paired: bool,
) -> dict[str, Any]:
    ids_by_label: dict[str, list[str]] = {}
    if len({label for label, _path in specs}) != len(specs):
        raise ValueError("data-spec labels must be unique")
    for label, path in specs:
        examples = read_jsonl(path)
        if max_examples is not None:
            examples = examples[:max_examples]
        ids_by_label[label] = [str(example.id) for example in examples]
        if len(ids_by_label[label]) != len(set(ids_by_label[label])):
            raise ValueError(f"duplicate example IDs in data spec {label}")
    ordered_lists = list(ids_by_label.values())
    ordered_paired = all(ids == ordered_lists[0] for ids in ordered_lists[1:])
    common_ids = set(ordered_lists[0]) if ordered_lists else set()
    for ids in ordered_lists[1:]:
        common_ids &= set(ids)
    if require_paired and not ordered_paired:
        counts = {label: len(ids) for label, ids in ids_by_label.items()}
        raise ValueError(
            "document-count factorial requires identical ordered example IDs; "
            f"counts={counts}, common={len(common_ids)}"
        )
    return {
        "ordered_example_ids_identical": ordered_paired,
        "common_example_count": len(common_ids),
        "count_by_label": {
            label: len(ids) for label, ids in ids_by_label.items()
        },
    }


def parse_float_list(raw: str) -> list[float]:
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError("probabilities must lie in [0, 1]")
    return values


def parse_int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def stable_uniform(seed: int, example_id: str, doc: Any) -> float:
    # Content identity, rather than prompt position, keeps the same document's
    # stale assignment fixed across nested document-count variants.
    payload = f"{seed}:{example_id}:{doc.title}:{doc.text}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return integer / float(2**64)


def read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_completed(path: Path) -> set[tuple[str, str, int, float, str]]:
    return {
        (
            row["dataset_label"],
            row["example_id"],
            int(row["mask_seed"]),
            float(row["stale_probability"]),
            row["method"],
        )
        for row in read_rows(path)
    }


def build_manifest(
    *,
    args: argparse.Namespace,
    config: Any,
    specs: list[tuple[str, Path]],
    probabilities: list[float],
    mask_seeds: list[int],
) -> dict[str, Any]:
    implementation_paths = [
        Path(__file__).resolve(),
        Path(__file__).with_name("run_answer_eval.py").resolve(),
        Path(__file__).resolve().parents[1] / "safekv" / "doc_selector.py",
        Path(__file__).resolve().parents[1] / "safekv" / "patch_recompute.py",
    ]
    return {
        "schema_version": 1,
        "config_path": str(args.config.resolve()),
        "config_sha256": file_sha256(args.config.resolve()),
        "model_name": config.model.name,
        "model_dtype": config.model.dtype,
        "max_examples": args.max_examples,
        "probabilities": probabilities,
        "mask_seeds": mask_seeds,
        "methods": METHODS,
        "data_specs": [
            {
                "label": label,
                "path": str(path.resolve()),
                "sha256": file_sha256(path.resolve()),
            }
            for label, path in specs
        ],
        "implementation_sha256": {
            str(path): file_sha256(path) for path in implementation_paths
        },
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_persisted_invariant_failures(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for row in rows:
        for failure in row.get("invariant_failures", []):
            key = json.dumps(failure, sort_keys=True, ensure_ascii=False)
            unique[key] = failure
    return list(unique.values())


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
