"""Naive KV composition smoke utilities for Milestones 3A through 3D."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from safekv.cache_ops import (
    cache_device_dtype_summary,
    cache_seq_len,
    clone_legacy_cache,
    concat_legacy_caches,
    legacy_cache_to_model_cache,
    slice_legacy_cache,
    to_legacy_cache,
)
from safekv.config import SafeKVConfig
from safekv.data_schema import DiagnosticExample, PromptPack, TokenRange
from safekv.full_prefill import load_examples_for_config, set_deterministic_seed
from safekv.metrics import logit_preservation_metrics
from safekv.modeling import LoadedModel, load_causal_lm
from safekv.prompting import build_rag_prompt


def build_prompt_pack_for_config(
    example: DiagnosticExample, loaded: LoadedModel, config: SafeKVConfig
) -> PromptPack:
    return build_rag_prompt(
        example,
        loaded.tokenizer,
        prompt_format=config.experiment.prompt_format,
        boundary_window_tokens=config.prompt.boundary_window_tokens,
        adaptive_boundary_window=config.prompt.adaptive_boundary_window,
    )


def full_prefill_logits(model: Any, pack: PromptPack, device: str):
    import torch

    input_ids = torch.tensor([pack.full_input_ids], dtype=torch.long, device=device)
    attention_mask = torch.ones_like(input_ids)
    position_ids = torch.arange(input_ids.shape[1], dtype=torch.long, device=device).unsqueeze(0)
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            use_cache=True,
        )
    return outputs.logits[:, -1, :].detach().float().cpu()[0]


def run_sequential_prefill_logits(model: Any, pack: PromptPack, device: str):
    """Run full prompt in ordered chunks and return the final logits."""

    import torch

    chunks = sequential_prefill_chunks(pack)
    past_key_values = None
    outputs = None
    for token_range in chunks:
        input_ids = torch.tensor(
            [pack.full_input_ids[token_range.start : token_range.end]],
            dtype=torch.long,
            device=device,
        )
        attention_mask = torch.ones((1, token_range.end), dtype=torch.long, device=device)
        position_ids = torch.arange(
            token_range.start,
            token_range.end,
            dtype=torch.long,
            device=device,
        ).unsqueeze(0)
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_values=past_key_values,
                use_cache=True,
            )
        past_key_values = outputs.past_key_values
    if outputs is None:
        raise ValueError("prompt has no tokens")
    return outputs.logits[:, -1, :].detach().float().cpu()[0]


def sequential_prefill_chunks(pack: PromptPack) -> list[TokenRange]:
    """Cover the complete prompt with chunks around doc blocks and query."""

    chunks: list[TokenRange] = []
    cursor = 0
    for doc_range in pack.doc_ranges:
        if cursor < doc_range.start:
            chunks.append(TokenRange(cursor, doc_range.start))
        chunks.append(doc_range)
        cursor = doc_range.end
    if cursor < pack.query_token_range.start:
        chunks.append(TokenRange(cursor, pack.query_token_range.start))
    if pack.query_token_range.start < pack.query_token_range.end:
        chunks.append(pack.query_token_range)
        cursor = pack.query_token_range.end
    if cursor < len(pack.full_input_ids):
        chunks.append(TokenRange(cursor, len(pack.full_input_ids)))
    return [chunk for chunk in chunks if chunk.length > 0]


def prefix_token_range(pack: PromptPack) -> TokenRange:
    """Return tokens before the first document block."""

    if not pack.doc_ranges:
        raise ValueError("PromptPack must contain at least one document range")
    return TokenRange(0, pack.doc_ranges[0].start)


def doc_cache_token_length(pack: PromptPack) -> int:
    return sum(doc_range.length for doc_range in pack.doc_ranges)


def composition_length_metadata(pack: PromptPack, includes_prefix_cache: bool) -> dict[str, int | bool]:
    prefix_length = prefix_token_range(pack).length
    doc_length = doc_cache_token_length(pack)
    query_length = pack.query_token_range.length
    return {
        "prompt_length": len(pack.full_input_ids),
        "prefix_length": prefix_length,
        "prefix_cache_length": prefix_length if includes_prefix_cache else 0,
        "doc_cache_length": doc_length,
        "query_length": query_length,
        "composed_context_length": doc_length + (prefix_length if includes_prefix_cache else 0),
        "missing_prefix_length": 0 if includes_prefix_cache else prefix_length,
        "includes_prefix_cache": includes_prefix_cache,
    }


def canonical_composition_method(method: str) -> str:
    aliases = {
        "naive_global": "doc_only_naive_global",
        "naive_local": "doc_only_naive_local",
    }
    return aliases.get(method, method)


def composition_method_specs() -> list[dict[str, Any]]:
    return [
        {
            "method": "doc_only_naive_global",
            "position_mode": "global",
            "includes_prefix_cache": False,
            "doc_conditioning": "none",
        },
        {
            "method": "doc_only_naive_local",
            "position_mode": "local",
            "includes_prefix_cache": False,
            "doc_conditioning": "none",
        },
        {
            "method": "prefix_plus_naive_global",
            "position_mode": "global",
            "includes_prefix_cache": True,
            "doc_conditioning": "none",
        },
        {
            "method": "prefix_plus_naive_local",
            "position_mode": "local",
            "includes_prefix_cache": True,
            "doc_conditioning": "none",
        },
        {
            "method": "prefix_conditioned_naive_global",
            "position_mode": "global",
            "includes_prefix_cache": True,
            "doc_conditioning": "prefix",
        },
        {
            "method": "prefix_conditioned_naive_local",
            "position_mode": "local",
            "includes_prefix_cache": True,
            "doc_conditioning": "prefix",
        },
    ]


def select_composition_method_specs(methods: list[str] | None) -> list[dict[str, Any]]:
    specs = composition_method_specs()
    specs_by_method = {str(spec["method"]): spec for spec in specs}
    supported = set(specs_by_method) | {"naive_global", "naive_local"}
    if not methods:
        return specs

    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for method in methods:
        canonical = canonical_composition_method(method)
        if method not in supported and canonical not in specs_by_method:
            raise ValueError(
                f"unsupported composition method {method!r}; supported methods are "
                f"{sorted(supported)}"
            )
        if canonical in seen:
            continue
        seen.add(canonical)
        selected.append(specs_by_method[canonical])
    return selected


def run_naive_composed_logits(
    model: Any,
    pack: PromptPack,
    device: str,
    position_mode: str,
    includes_prefix_cache: bool = False,
    doc_conditioning: str = "none",
) -> tuple[Any, dict[str, Any]]:
    composed_cache, metadata = build_naive_composed_context_cache(
        model=model,
        pack=pack,
        device=device,
        position_mode=position_mode,
        includes_prefix_cache=includes_prefix_cache,
        doc_conditioning=doc_conditioning,
    )
    logits = evaluate_query_with_context_cache(model, pack, composed_cache, device)
    return logits, metadata


def build_naive_composed_context_cache(
    model: Any,
    pack: PromptPack,
    device: str,
    position_mode: str,
    includes_prefix_cache: bool = False,
    doc_conditioning: str = "none",
) -> tuple[Any, dict[str, Any]]:
    import torch

    if position_mode not in {"global", "local"}:
        raise ValueError("position_mode must be 'global' or 'local'")
    if doc_conditioning not in {"none", "prefix"}:
        raise ValueError("doc_conditioning must be 'none' or 'prefix'")
    if doc_conditioning == "prefix" and not includes_prefix_cache:
        raise ValueError("prefix-conditioned composition must include the prefix cache")

    caches = []
    prefix_range = prefix_token_range(pack)
    prefix_cache = None
    if (includes_prefix_cache or doc_conditioning == "prefix") and prefix_range.length > 0:
        prefix_ids = torch.tensor(
            [pack.full_input_ids[prefix_range.start : prefix_range.end]],
            dtype=torch.long,
            device=device,
        )
        prefix_position_ids = torch.arange(
            prefix_range.start,
            prefix_range.end,
            dtype=torch.long,
            device=device,
        ).unsqueeze(0)
        prefix_attention_mask = torch.ones_like(prefix_ids)
        with torch.no_grad():
            prefix_outputs = model(
                input_ids=prefix_ids,
                attention_mask=prefix_attention_mask,
                position_ids=prefix_position_ids,
                use_cache=True,
            )
        prefix_cache = to_legacy_cache(prefix_outputs.past_key_values)
        if includes_prefix_cache:
            caches.append(prefix_cache)

    for doc_range in pack.doc_ranges:
        input_ids = torch.tensor(
            [pack.full_input_ids[doc_range.start : doc_range.end]],
            dtype=torch.long,
            device=device,
        )
        if position_mode == "global":
            position_ids = torch.arange(
                doc_range.start, doc_range.end, dtype=torch.long, device=device
            ).unsqueeze(0)
        elif doc_conditioning == "prefix":
            position_ids = torch.arange(
                prefix_range.length,
                prefix_range.length + doc_range.length,
                dtype=torch.long,
                device=device,
            ).unsqueeze(0)
        else:
            position_ids = torch.arange(doc_range.length, dtype=torch.long, device=device).unsqueeze(0)
        if doc_conditioning == "prefix" and prefix_cache is not None:
            attention_mask = torch.ones(
                (1, prefix_range.length + doc_range.length),
                dtype=torch.long,
                device=device,
            )
            past_key_values = legacy_cache_to_model_cache(clone_legacy_cache(prefix_cache))
        else:
            attention_mask = torch.ones_like(input_ids)
            past_key_values = None
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_values=past_key_values,
                use_cache=True,
            )
        doc_cache = to_legacy_cache(outputs.past_key_values)
        if doc_conditioning == "prefix" and prefix_cache is not None:
            doc_cache = slice_legacy_cache(
                doc_cache,
                prefix_range.length,
                prefix_range.length + doc_range.length,
            )
        caches.append(doc_cache)

    composed_cache = concat_legacy_caches(caches)
    composed_len = cache_seq_len(composed_cache)
    metadata = cache_device_dtype_summary(composed_cache)
    length_metadata = composition_length_metadata(pack, includes_prefix_cache)
    metadata.update(length_metadata)
    metadata["composed_context_length"] = composed_len
    metadata["position_mode"] = position_mode
    metadata["doc_conditioning"] = doc_conditioning
    if doc_conditioning == "prefix":
        metadata["composition_mode"] = "prefix_conditioned_naive"
    elif includes_prefix_cache:
        metadata["composition_mode"] = "prefix_plus_unconditioned_doc"
    else:
        metadata["composition_mode"] = "doc_only_naive"
    return composed_cache, metadata


def evaluate_query_with_context_cache(
    model: Any,
    pack: PromptPack,
    context_cache: Any,
    device: str,
):
    import torch

    query_range = pack.query_token_range
    query_ids = torch.tensor(
        [pack.full_input_ids[query_range.start : query_range.end]],
        dtype=torch.long,
        device=device,
    )
    query_position_ids = torch.arange(
        query_range.start,
        query_range.end,
        dtype=torch.long,
        device=device,
    ).unsqueeze(0)
    composed_len = cache_seq_len(context_cache)
    attention_mask = torch.ones(
        (1, composed_len + query_ids.shape[1]),
        dtype=torch.long,
        device=device,
    )
    with torch.no_grad():
        outputs = model(
            input_ids=query_ids,
            attention_mask=attention_mask,
            position_ids=query_position_ids,
            past_key_values=legacy_cache_to_model_cache(context_cache),
            use_cache=True,
        )
    return outputs.logits[:, -1, :].detach().float().cpu()[0]


def load_full_reference_logits(results_dir: Path, example_id: str):
    import torch

    path = results_dir / "logits" / "full_prefill" / f"{example_id}.pt"
    if not path.exists():
        raise FileNotFoundError(f"missing full-prefill logits: {path}")
    return torch.load(path, map_location="cpu").float()


def validate_sidecar_prompt_reference(results_dir: Path, example_id: str, pack: PromptPack) -> None:
    """Validate full-prefill sidecar metadata when it exists."""

    path = results_dir / "prompt_packs" / f"{example_id}.json"
    if not path.exists():
        return
    row = json.loads(path.read_text(encoding="utf-8"))
    sidecar_ids = row.get("full_input_ids")
    if sidecar_ids is None:
        return
    if list(sidecar_ids) != list(pack.full_input_ids):
        raise ValueError(
            f"stale sidecar reference for {example_id}: full_input_ids do not match "
            "the current prompt pack"
        )


def reference_logits_for_example(
    current_logits: Any,
    use_sidecar_reference: bool,
    results_dir: Path,
    example_id: str,
    pack: PromptPack,
) -> Any:
    if not use_sidecar_reference:
        return current_logits
    validate_sidecar_prompt_reference(results_dir, example_id, pack)
    return load_full_reference_logits(results_dir, example_id)


def make_metric_row(
    example: DiagnosticExample,
    method: str,
    pack: PromptPack,
    full_logits: Any,
    method_logits: Any,
    tokenizer: Any,
    composed_context_length: int | None = None,
) -> dict[str, Any]:
    metrics = logit_preservation_metrics(full_logits, method_logits, tokenizer)
    return {
        "example_id": example.id,
        "id": example.id,
        "category": example.category,
        "method": canonical_composition_method(method),
        "prompt_length": len(pack.full_input_ids),
        "composed_context_length": composed_context_length,
        **metrics,
    }


def summarize_rows(rows: list[dict[str, Any]], failed_examples: list[dict[str, str]]) -> dict[str, Any]:
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts_by_id: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        method_groups[row["method"]].append(row)
        category_groups[f"{row['method']}::{row['category']}"].append(row)
        category_counts_by_id[row["category"]].add(row["example_id"])
    method_level = {
        method: average_metric_summary(group) for method, group in sorted(method_groups.items())
    }
    method_ranking = sorted(
        (
            {
                "method": method,
                "avg_kl": summary["avg_kl"],
                "top1_match_rate": summary["top1_match_rate"],
                "avg_top10_overlap": summary["avg_top10_overlap"],
            }
            for method, summary in method_level.items()
        ),
        key=lambda row: row["avg_kl"],
    )
    return {
        "num_rows": len(rows),
        "num_failed_examples": len(failed_examples),
        "failed_examples": failed_examples,
        "category_counts": {
            category: len(example_ids)
            for category, example_ids in sorted(category_counts_by_id.items())
        },
        "method_level": method_level,
        "category_level": {
            key: average_metric_summary(group) for key, group in sorted(category_groups.items())
        },
        "method_ranking_by_avg_kl": method_ranking,
        "best_method_by_avg_kl": method_ranking[0]["method"] if method_ranking else None,
    }


def average_metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "num_examples": len(rows),
        "avg_kl": _mean(row["first_token_kl_full_to_method"] for row in rows),
        "avg_js": _mean(row["first_token_js_divergence"] for row in rows),
        "top1_match_rate": _mean(1.0 if row["top1_match"] else 0.0 for row in rows),
        "avg_top5_overlap": _mean(row["top5_overlap"] for row in rows),
        "avg_top10_overlap": _mean(row["top10_overlap"] for row in rows),
        "avg_composed_context_length": _mean(
            row["composed_context_length"] or 0 for row in rows
        ),
        "avg_max_abs_logit_diff": _mean(row["max_abs_logit_diff"] for row in rows),
    }
    summary["bootstrap_95_ci"] = bootstrap_metric_cis(rows)
    return summary


BOOTSTRAP_METRICS = {
    "avg_kl": "first_token_kl_full_to_method",
    "avg_js": "first_token_js_divergence",
    "top1_match_rate": "top1_match",
    "avg_top5_overlap": "top5_overlap",
    "avg_top10_overlap": "top10_overlap",
}


def bootstrap_metric_cis(
    rows: list[dict[str, Any]],
    n_resamples: int = 1000,
    seed: int = 13,
) -> dict[str, dict[str, float]]:
    if not rows:
        return {
            metric: {"low": 0.0, "high": 0.0}
            for metric in BOOTSTRAP_METRICS
        }
    rng = random.Random(seed)
    values_by_metric = {
        metric: [_metric_value(row, source_key) for row in rows]
        for metric, source_key in BOOTSTRAP_METRICS.items()
    }
    result: dict[str, dict[str, float]] = {}
    n = len(rows)
    for metric, values in values_by_metric.items():
        estimates = []
        for _ in range(n_resamples):
            sample = [values[rng.randrange(n)] for _ in range(n)]
            estimates.append(float(sum(sample) / n))
        estimates.sort()
        result[metric] = {
            "low": _percentile(estimates, 0.025),
            "high": _percentile(estimates, 0.975),
        }
    return result


COMPOSITION_CSV_COLUMNS = [
    "example_id",
    "category",
    "method",
    "first_token_kl_full_to_method",
    "first_token_js_divergence",
    "top1_match",
    "top5_overlap",
    "top10_overlap",
    "prompt_length",
    "prefix_length",
    "doc_cache_length",
    "query_length",
    "position_mode",
    "composition_mode",
    "doc_conditioning",
]


def compact_csv_row(row: dict[str, Any]) -> dict[str, Any]:
    return {column: row.get(column, "") for column in COMPOSITION_CSV_COLUMNS}


def write_composition_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPOSITION_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(compact_csv_row(row))


def composition_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    method: str = "prefix_conditioned_naive_global",
    top_n: int = 10,
) -> str:
    method_rows = [row for row in rows if row.get("method") == method]
    sorted_by_kl = sorted(
        method_rows,
        key=lambda row: float(row.get("first_token_kl_full_to_method", 0.0)),
        reverse=True,
    )
    mismatches = [row for row in method_rows if not bool(row.get("top1_match"))]
    category_counts = Counter(row["category"] for row in method_rows)
    mismatch_counts = Counter(row["category"] for row in mismatches)

    lines = [
        "# Composition Failure Analysis",
        "",
        f"Method: `{method}`",
        "",
        "This diagnostic lists first-token behavior preservation failures. "
        "It does not infer task correctness or claim a root cause by itself.",
        "",
        "## Category Breakdown",
        "",
        "| category | examples | top1 mismatches |",
        "|---|---:|---:|",
    ]
    for category in sorted(category_counts):
        lines.append(
            f"| {category} | {category_counts[category]} | {mismatch_counts.get(category, 0)} |"
        )

    lines.extend(
        [
            "",
            f"## Top {top_n} Examples By KL",
            "",
            "| rank | example_id | category | KL | top1_match | full argmax | method argmax | interpretation |",
            "|---:|---|---|---:|---|---|---|---|",
        ]
    )
    for rank, row in enumerate(sorted_by_kl[:top_n], start=1):
        lines.append(_failure_table_row(rank, row))

    lines.extend(
        [
            "",
            "## Top1 Mismatches",
            "",
            "| example_id | category | KL | full argmax | method argmax | interpretation |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for row in mismatches:
        lines.append(
            "| {example_id} | {category} | {kl:.6g} | `{full}` | `{method_token}` | {interp} |".format(
                example_id=_md(row.get("example_id", "")),
                category=_md(row.get("category", "")),
                kl=float(row.get("first_token_kl_full_to_method", 0.0)),
                full=_md(row.get("argmax_full_decoded", "")),
                method_token=_md(row.get("argmax_method_decoded", "")),
                interp=_interpret_failure_row(row),
            )
        )
    if not mismatches:
        lines.append("| none | - | 0 | - | - | No first-token top1 mismatches observed. |")
    lines.append("")
    return "\n".join(lines)


def write_composition_failure_analysis(
    path: Path,
    rows: list[dict[str, Any]],
    method: str = "prefix_conditioned_naive_global",
    top_n: int = 10,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        composition_failure_analysis_markdown(rows, method=method, top_n=top_n),
        encoding="utf-8",
    )


def sequential_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [
        row
        for row in rows
        if (not row["top1_match"]) or row["max_abs_logit_diff"] > 1e-3
    ]
    category_counts = Counter(row["category"] for row in rows)
    return {
        "num_examples": len(rows),
        "passed": len(failed) == 0,
        "num_failed": len(failed),
        "max_abs_diff_threshold": 1e-3,
        "category_counts": dict(sorted(category_counts.items())),
        "max_abs_logit_diff_max": max((row["max_abs_logit_diff"] for row in rows), default=0.0),
        "mean_abs_logit_diff_avg": _mean(row["mean_abs_logit_diff"] for row in rows),
        "top1_match_rate": _mean(1.0 if row["top1_match"] else 0.0 for row in rows),
        "top10_overlap_avg": _mean(row["top10_overlap"] for row in rows),
        "failed_example_ids": [row["example_id"] for row in failed],
    }


def _mean(values) -> float:
    values = list(values)
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _metric_value(row: dict[str, Any], source_key: str) -> float:
    value = row[source_key]
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    return float(value)


def _percentile(sorted_values: list[float], quantile: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = quantile * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return float(sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight)


def _failure_table_row(rank: int, row: dict[str, Any]) -> str:
    return (
        "| {rank} | {example_id} | {category} | {kl:.6g} | {top1} | `{full}` | "
        "`{method}` | {interp} |"
    ).format(
        rank=rank,
        example_id=_md(row.get("example_id", "")),
        category=_md(row.get("category", "")),
        kl=float(row.get("first_token_kl_full_to_method", 0.0)),
        top1=str(bool(row.get("top1_match"))),
        full=_md(row.get("argmax_full_decoded", "")),
        method=_md(row.get("argmax_method_decoded", "")),
        interp=_interpret_failure_row(row),
    )


def _interpret_failure_row(row: dict[str, Any]) -> str:
    if not bool(row.get("top1_match")):
        return "Top-1 next-token changed; inspect category and prompt context before attributing cause."
    if float(row.get("first_token_kl_full_to_method", 0.0)) > 0.5:
        return "Top-1 preserved but distribution shifted."
    return "Low first-token drift under this method."


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
