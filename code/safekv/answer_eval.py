"""Answer-level behavior evaluation helpers for SAFE-KV Milestone 6A."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from safekv.generation import exact_match, normalize_answer, token_f1


DEFAULT_ANSWER_EVAL_METHODS = [
    "full_prefill",
    "prefix_conditioned_naive_global",
    "oracle_evidence_doc_patch",
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_k2",
    "risk_guided_doc_patch_k2",
    "safe_gate_t0.45",
    "safe_gate_t0.60",
    "random_doc_patch_k2_seeded",
]

SEMANTIC_K2_METHODS = [
    "query_similarity_doc_patch_k2",
    "entity_overlap_doc_patch_k2",
    "risk_guided_doc_patch_k2",
]

ANSWER_EVAL_CSV_COLUMNS = [
    "example_id",
    "category",
    "method",
    "generated_answer",
    "full_prefill_answer",
    "gold_answer",
    "normalized_generated_answer",
    "normalized_full_prefill_answer",
    "normalized_gold_answer",
    "answer_equivalence_to_full_prefill",
    "gold_exact_match",
    "gold_token_f1",
    "answer_contains_gold",
    "answer_changed_from_full",
    "answer_changed_and_gold_wrong",
    "patched_doc_count",
    "patched_token_count",
    "patched_token_ratio",
    "first_token_kl_full_to_method",
    "top1_match",
    "prompt_length",
    "query_length",
]


def parse_methods_arg(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return list(DEFAULT_ANSWER_EVAL_METHODS)
    methods = []
    for raw in value.split(","):
        method = raw.strip()
        if method:
            methods.append(method)
    if not methods:
        raise ValueError("--methods must contain at least one method")
    return methods


def internal_selector_method(method: str) -> str:
    aliases = {
        "safe_gate_t0.45": "safe_composition_gate_t0_45",
        "safe_gate_t0_45": "safe_composition_gate_t0_45",
        "safe_gate_t0.60": "safe_composition_gate_t0_60",
        "safe_gate_t0_60": "safe_composition_gate_t0_60",
    }
    return aliases.get(method, method)


def answer_contains_gold(answer: str, gold_answer: str) -> bool:
    normalized_answer = normalize_answer(answer)
    normalized_gold = normalize_answer(gold_answer)
    return bool(normalized_gold and normalized_gold in normalized_answer)


def answer_equivalent(left: str, right: str) -> bool:
    return exact_match(left, right)


def answer_metric_fields(
    *,
    generated_answer: str,
    full_prefill_answer: str,
    gold_answer: str,
) -> dict[str, Any]:
    normalized_generated = normalize_answer(generated_answer)
    normalized_full = normalize_answer(full_prefill_answer)
    normalized_gold = normalize_answer(gold_answer)
    gold_exact = normalized_generated == normalized_gold
    changed = normalized_generated != normalized_full
    return {
        "normalized_generated_answer": normalized_generated,
        "normalized_full_prefill_answer": normalized_full,
        "normalized_gold_answer": normalized_gold,
        "answer_equivalence_to_full_prefill": normalized_generated == normalized_full,
        "gold_exact_match": gold_exact,
        "gold_token_f1": token_f1(generated_answer, gold_answer),
        "answer_contains_gold": bool(normalized_gold and normalized_gold in normalized_generated),
        "answer_changed_from_full": changed,
        "answer_changed_and_gold_wrong": bool(changed and not gold_exact),
    }


def make_answer_eval_row(
    *,
    example_id: str,
    category: str,
    method: str,
    generated_answer: str,
    full_prefill_answer: str,
    gold_answer: str,
    patched_doc_count: int,
    patched_token_count: int,
    patched_token_ratio: float,
    prompt_length: int,
    query_length: int,
    first_token_kl_full_to_method: float | None = None,
    top1_match: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "example_id": example_id,
        "category": category,
        "method": method,
        "generated_answer": generated_answer,
        "full_prefill_answer": full_prefill_answer,
        "gold_answer": gold_answer,
        **answer_metric_fields(
            generated_answer=generated_answer,
            full_prefill_answer=full_prefill_answer,
            gold_answer=gold_answer,
        ),
        "patched_doc_count": patched_doc_count,
        "patched_token_count": patched_token_count,
        "patched_token_ratio": patched_token_ratio,
        "first_token_kl_full_to_method": first_token_kl_full_to_method,
        "top1_match": top1_match,
        "prompt_length": prompt_length,
        "query_length": query_length,
    }
    if extra:
        row.update(extra)
    return row


def summarize_answer_eval_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        method_groups[row["method"]].append(row)
        category_groups[f"{row['method']}::{row['category']}"].append(row)
        category_counts[row["category"]].add(row["example_id"])

    method_level = {
        method: _answer_summary(group)
        for method, group in sorted(method_groups.items())
    }
    category_level = {
        key: _answer_summary(group)
        for key, group in sorted(category_groups.items())
    }
    relation_rows = [
        row
        for row in rows
        if row["method"] != "full_prefill"
        and row.get("first_token_kl_full_to_method") is not None
    ]
    return {
        "num_rows": len(rows),
        "category_counts": {
            category: len(example_ids)
            for category, example_ids in sorted(category_counts.items())
        },
        "method_level": method_level,
        "category_level": category_level,
        "kl_answer_mismatch_relation": kl_answer_mismatch_relation(relation_rows),
        "patched_ratio_answer_equivalence_pareto": patched_ratio_pareto(method_level),
        "method_ranking_by_answer_equivalence": sorted(
            (
                {
                    "method": method,
                    "answer_equivalence_to_full_prefill": summary[
                        "answer_equivalence_to_full_prefill"
                    ],
                    "gold_exact_match": summary["gold_exact_match"],
                    "gold_token_f1": summary["gold_token_f1"],
                    "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                }
                for method, summary in method_level.items()
            ),
            key=lambda item: (
                -float(item["answer_equivalence_to_full_prefill"]),
                float(item["avg_patched_token_ratio"]),
            ),
        ),
    }


def kl_answer_mismatch_relation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [
        (
            float(row["first_token_kl_full_to_method"]),
            1.0 if row["answer_changed_from_full"] else 0.0,
        )
        for row in rows
        if row.get("first_token_kl_full_to_method") is not None
    ]
    result: dict[str, Any] = {
        "num_rows": len(pairs),
        "kl_bins": kl_bin_mismatch_aggregation(rows),
    }
    if len(pairs) < 2:
        result["pearson"] = None
        result["spearman"] = None
        return result

    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    if len(set(xs)) <= 1 or len(set(ys)) <= 1:
        result["pearson"] = None
        result["spearman"] = None
        return result
    try:
        from scipy import stats  # type: ignore

        result["pearson"] = {
            "r": float(stats.pearsonr(xs, ys).statistic),
            "pvalue": float(stats.pearsonr(xs, ys).pvalue),
        }
        result["spearman"] = {
            "rho": float(stats.spearmanr(xs, ys).statistic),
            "pvalue": float(stats.spearmanr(xs, ys).pvalue),
        }
    except Exception:
        result["pearson"] = {"r": _pearson(xs, ys), "pvalue": None}
        result["spearman"] = None
    return result


def kl_bin_mismatch_aggregation(
    rows: list[dict[str, Any]],
    bins: list[float] | None = None,
) -> list[dict[str, Any]]:
    bins = bins or [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 1.0, math.inf]
    bucket_rows: list[list[dict[str, Any]]] = [[] for _ in range(len(bins) - 1)]
    for row in rows:
        if row.get("first_token_kl_full_to_method") is None:
            continue
        kl = float(row["first_token_kl_full_to_method"])
        for index, (low, high) in enumerate(zip(bins[:-1], bins[1:], strict=True)):
            if low <= kl < high or (math.isinf(high) and kl >= low):
                bucket_rows[index].append(row)
                break
    result = []
    for low, high, group in zip(bins[:-1], bins[1:], bucket_rows, strict=True):
        result.append(
            {
                "kl_low": low,
                "kl_high": high,
                "num_rows": len(group),
                "answer_mismatch_rate": _mean(
                    1.0 if row["answer_changed_from_full"] else 0.0 for row in group
                ),
            }
        )
    return result


def patched_ratio_pareto(method_level: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                "method": method,
                "avg_patched_token_ratio": summary["avg_patched_token_ratio"],
                "answer_equivalence_to_full_prefill": summary[
                    "answer_equivalence_to_full_prefill"
                ],
                "gold_exact_match": summary["gold_exact_match"],
                "gold_token_f1": summary["gold_token_f1"],
                "avg_first_token_kl": summary["avg_first_token_kl"],
            }
            for method, summary in method_level.items()
        ),
        key=lambda item: (
            float(item["avg_patched_token_ratio"]),
            -float(item["answer_equivalence_to_full_prefill"]),
        ),
    )


def answer_failure_analysis_markdown(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    top_n: int = 10,
) -> str:
    by_example_method = {
        (row["example_id"], row["method"]): row
        for row in rows
    }
    base_rows = [row for row in rows if row["method"] == "prefix_conditioned_naive_global"]
    base_changed = [row for row in base_rows if row["answer_changed_from_full"]]
    base_changed = sorted(
        base_changed,
        key=lambda row: float(row.get("first_token_kl_full_to_method") or 0.0),
        reverse=True,
    )
    repaired_by_gate = _examples_repaired_by_any(
        base_changed,
        by_example_method,
        ["safe_gate_t0.45", "safe_gate_t0.60"],
    )
    oracle_only = _oracle_repaired_not_semantic(base_changed, by_example_method)
    random_beats = _random_beats_semantic(base_changed, by_example_method)

    lines = [
        "# Answer Failure Analysis",
        "",
        "Rows compare deterministic generated answers against full-prefill generation.",
        "",
        "## Method Summary",
        "",
        "| method | answer equiv | gold EM | gold F1 | changed+wrong | patched ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method, data in sorted(summary.get("method_level", {}).items()):
        lines.append(
            "| {method} | {equiv:.3f} | {em:.3f} | {f1:.3f} | {wrong} | {ratio:.3f} |".format(
                method=_md(method),
                equiv=float(data["answer_equivalence_to_full_prefill"]),
                em=float(data["gold_exact_match"]),
                f1=float(data["gold_token_f1"]),
                wrong=int(data["answer_changed_and_gold_wrong_count"]),
                ratio=float(data["avg_patched_token_ratio"]),
            )
        )

    lines.extend(
        [
            "",
            "## Category Breakdown",
            "",
            "| method::category | answer equiv | gold EM | changed+wrong |",
            "|---|---:|---:|---:|",
        ]
    )
    for key, data in sorted(summary.get("category_level", {}).items()):
        lines.append(
            "| {key} | {equiv:.3f} | {em:.3f} | {wrong} |".format(
                key=_md(key),
                equiv=float(data["answer_equivalence_to_full_prefill"]),
                em=float(data["gold_exact_match"]),
                wrong=int(data["answer_changed_and_gold_wrong_count"]),
            )
        )

    lines.extend(
        [
            "",
            f"## Top {top_n} Base Answer Changes",
            "",
            "| example | category | KL | full answer | base answer | gold |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for row in base_changed[:top_n]:
        lines.append(_answer_case_line(row))
    if not base_changed:
        lines.append("| none | - | 0 | - | - | - |")

    _append_case_section(lines, "Repaired By Safe Gates", repaired_by_gate, top_n)
    _append_case_section(lines, "Repaired By Oracle But Not Semantic K2", oracle_only, top_n)
    _append_case_section(lines, "Random K2 Beats Semantic K2", random_beats, top_n)
    lines.append("")
    return "\n".join(lines)


def read_answer_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def completed_output_keys(path: Path) -> set[tuple[str, str]]:
    return {
        (str(row["example_id"]), str(row["method"]))
        for row in read_answer_rows(path)
    }


def append_answer_rows(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_answer_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANSWER_EVAL_CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in ANSWER_EVAL_CSV_COLUMNS})


def _answer_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "num_rows": len(rows),
        "num_distinct_examples": len({row["example_id"] for row in rows}),
        "answer_equivalence_to_full_prefill": _mean(
            1.0 if row["answer_equivalence_to_full_prefill"] else 0.0 for row in rows
        ),
        "gold_exact_match": _mean(1.0 if row["gold_exact_match"] else 0.0 for row in rows),
        "gold_token_f1": _mean(row["gold_token_f1"] for row in rows),
        "answer_contains_gold_rate": _mean(
            1.0 if row["answer_contains_gold"] else 0.0 for row in rows
        ),
        "answer_changed_from_full_rate": _mean(
            1.0 if row["answer_changed_from_full"] else 0.0 for row in rows
        ),
        "answer_changed_but_gold_correct_count": sum(
            1
            for row in rows
            if row["answer_changed_from_full"] and row["gold_exact_match"]
        ),
        "answer_changed_and_gold_wrong_count": sum(
            1 for row in rows if row["answer_changed_and_gold_wrong"]
        ),
        "avg_patched_doc_count": _mean(row.get("patched_doc_count", 0.0) for row in rows),
        "avg_patched_token_count": _mean(row.get("patched_token_count", 0.0) for row in rows),
        "avg_patched_token_ratio": _mean(row.get("patched_token_ratio", 0.0) for row in rows),
        "avg_first_token_kl": _mean(
            row["first_token_kl_full_to_method"]
            for row in rows
            if row.get("first_token_kl_full_to_method") is not None
        ),
        "top1_match_rate": _mean(
            1.0 if row.get("top1_match") else 0.0
            for row in rows
            if row.get("top1_match") is not None
        ),
    }


def _examples_repaired_by_any(
    base_changed: list[dict[str, Any]],
    by_example_method: dict[tuple[str, str], dict[str, Any]],
    methods: list[str],
) -> list[dict[str, Any]]:
    repaired = []
    for base in base_changed:
        for method in methods:
            row = by_example_method.get((base["example_id"], method))
            if row and row["answer_equivalence_to_full_prefill"]:
                repaired.append(row)
                break
    return repaired


def _oracle_repaired_not_semantic(
    base_changed: list[dict[str, Any]],
    by_example_method: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for base in base_changed:
        oracle = by_example_method.get((base["example_id"], "oracle_evidence_doc_patch"))
        if not oracle or not oracle["answer_equivalence_to_full_prefill"]:
            continue
        semantic_repaired = any(
            (by_example_method.get((base["example_id"], method)) or {}).get(
                "answer_equivalence_to_full_prefill",
                False,
            )
            for method in SEMANTIC_K2_METHODS
        )
        if not semantic_repaired:
            rows.append(oracle)
    return rows


def _random_beats_semantic(
    base_changed: list[dict[str, Any]],
    by_example_method: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for base in base_changed:
        random_row = by_example_method.get((base["example_id"], "random_doc_patch_k2_seeded"))
        if random_row is None:
            continue
        if random_row["answer_equivalence_to_full_prefill"] and not any(
            (by_example_method.get((base["example_id"], method)) or {}).get(
                "answer_equivalence_to_full_prefill",
                False,
            )
            for method in SEMANTIC_K2_METHODS
        ):
            rows.append(random_row)
    return rows


def _append_case_section(
    lines: list[str],
    title: str,
    rows: list[dict[str, Any]],
    top_n: int,
) -> None:
    lines.extend(
        [
            "",
            f"## {title}",
            "",
            "| example | category | KL | full answer | method answer | gold |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for row in rows[:top_n]:
        lines.append(_answer_case_line(row))
    if not rows:
        lines.append("| none | - | 0 | - | - | - |")


def _answer_case_line(row: dict[str, Any]) -> str:
    return "| {example} | {category} | {kl:.6g} | `{full}` | `{answer}` | `{gold}` |".format(
        example=_md(row["example_id"]),
        category=_md(row["category"]),
        kl=float(row.get("first_token_kl_full_to_method") or 0.0),
        full=_md(row.get("full_prefill_answer", "")),
        answer=_md(row.get("generated_answer", "")),
        gold=_md(row.get("gold_answer", "")),
    )


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    mean_x = _mean(xs)
    mean_y = _mean(ys)
    centered_x = [x - mean_x for x in xs]
    centered_y = [y - mean_y for y in ys]
    denom_x = math.sqrt(sum(x * x for x in centered_x))
    denom_y = math.sqrt(sum(y * y for y in centered_y))
    if denom_x == 0.0 or denom_y == 0.0:
        return None
    return float(sum(x * y for x, y in zip(centered_x, centered_y, strict=True)) / (denom_x * denom_y))


def _mean(values: Iterable[Any]) -> float:
    numeric = [float(value) for value in values]
    if not numeric:
        return 0.0
    return float(sum(numeric) / len(numeric))


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "ANSWER_EVAL_CSV_COLUMNS",
    "DEFAULT_ANSWER_EVAL_METHODS",
    "answer_contains_gold",
    "answer_equivalent",
    "answer_failure_analysis_markdown",
    "answer_metric_fields",
    "append_answer_rows",
    "completed_output_keys",
    "internal_selector_method",
    "kl_bin_mismatch_aggregation",
    "make_answer_eval_row",
    "normalize_answer",
    "parse_methods_arg",
    "read_answer_rows",
    "summarize_answer_eval_rows",
    "token_f1",
    "write_answer_metrics_csv",
]
