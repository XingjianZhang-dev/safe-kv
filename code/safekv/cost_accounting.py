"""Cost-accounting helpers for paper-facing SAFE-KV tables."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from safekv.paper_analysis import mean, truthy


def cost_accounting_rows(
    *,
    model: str,
    dataset: str,
    metric_rows: list[dict[str, Any]],
    methods: set[str] | None = None,
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in metric_rows:
        method = row["method"]
        if methods is not None and method not in methods:
            continue
        groups[method].append(row)

    out = []
    for method, rows in sorted(groups.items()):
        patched_ratio = mean(float(row.get("patched_token_ratio") or 0.0) for row in rows)
        changed_wrong_rate = mean(
            1.0 if truthy(row.get("answer_changed_and_gold_wrong")) else 0.0
            for row in rows
        )
        out.append(
            {
                "model": model,
                "dataset": dataset,
                "method": method,
                "n_examples": len({row["example_id"] for row in rows}),
                "answer_equivalence_to_full_prefill": mean(
                    1.0 if truthy(row.get("answer_equivalence_to_full_prefill")) else 0.0
                    for row in rows
                ),
                "changed_wrong_rate": changed_wrong_rate,
                "patched_doc_count": mean(
                    float(row.get("patched_doc_count") or 0.0) for row in rows
                ),
                "patched_token_ratio": patched_ratio,
                "estimated_recompute_ratio": patched_ratio,
                "estimated_prefill_saving": 1.0 - patched_ratio,
            }
        )
    return out


def cost_markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = [
        "model",
        "dataset",
        "method",
        "ans_eq",
        "changed_wrong",
        "patch_ratio",
        "est_saving",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {dataset} | {method} | {ans:.3f} | {wrong:.3f} | {patch:.3f} | {saving:.3f} |".format(
                model=row["model"],
                dataset=row["dataset"],
                method=row["method"],
                ans=float(row["answer_equivalence_to_full_prefill"]),
                wrong=float(row["changed_wrong_rate"]),
                patch=float(row["patched_token_ratio"]),
                saving=float(row["estimated_prefill_saving"]),
            )
        )
    return "\n".join(lines)
