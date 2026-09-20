#!/usr/bin/env python
"""Train a lightweight supervised SAFE-KV document selector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl  # noqa: E402
from safekv.learned_selector import (  # noqa: E402
    FEATURE_NAMES,
    feature_matrix,
    learned_doc_scores,
    oracle_label_doc_ids,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--dev", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=800)
    parser.add_argument("--lr", type=float, default=0.03)
    parser.add_argument("--l2", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=13)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = train_selector(
        train_path=args.train,
        epochs=args.epochs,
        lr=args.lr,
        l2=args.l2,
        seed=args.seed,
    )
    train_examples = read_jsonl(args.train)
    report: dict[str, Any] = {
        "train": evaluate_selector(train_examples, artifact),
    }
    if args.dev is not None:
        dev_examples = read_jsonl(args.dev)
        report["dev"] = evaluate_selector(dev_examples, artifact)
    artifact["report"] = report
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Wrote selector artifact to {args.out}")


def train_selector(
    *,
    train_path: Path,
    epochs: int,
    lr: float,
    l2: float,
    seed: int,
) -> dict[str, Any]:
    import torch

    torch.manual_seed(seed)
    examples = read_jsonl(train_path)
    matrix, labels = feature_matrix(examples)
    x = torch.tensor(matrix, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    means = x.mean(dim=0)
    stds = x.std(dim=0).clamp_min(1e-6)
    x_norm = (x - means) / stds

    weights = torch.zeros(x_norm.shape[1], dtype=torch.float32, requires_grad=True)
    bias = torch.zeros((), dtype=torch.float32, requires_grad=True)
    positives = float(y.sum().item())
    negatives = float(y.numel() - y.sum().item())
    pos_weight = torch.tensor(negatives / max(1.0, positives), dtype=torch.float32)
    optimizer = torch.optim.Adam([weights, bias], lr=lr)

    for _epoch in range(epochs):
        optimizer.zero_grad()
        logits = x_norm @ weights + bias
        loss = torch.nn.functional.binary_cross_entropy_with_logits(
            logits,
            y,
            pos_weight=pos_weight,
        )
        loss = loss + l2 * (weights * weights).sum()
        loss.backward()
        optimizer.step()

    return {
        "type": "linear_logistic_doc_selector",
        "feature_names": FEATURE_NAMES,
        "means": [float(value) for value in means.tolist()],
        "stds": [float(value) for value in stds.tolist()],
        "weights": [float(value) for value in weights.detach().tolist()],
        "bias": float(bias.detach().item()),
        "train_path": str(train_path),
        "epochs": epochs,
        "lr": lr,
        "l2": l2,
        "seed": seed,
    }


def evaluate_selector(examples: list[Any], artifact: dict[str, Any]) -> dict[str, Any]:
    recall_at = {1: [], 2: [], 4: []}
    precision_at = {1: [], 2: [], 4: []}
    mrr_values = []
    for example in examples:
        positives = oracle_label_doc_ids(example)
        scores = learned_doc_scores(example, artifact)
        ordered = [doc_id for doc_id, _score in sorted(scores, key=lambda item: (-item[1], item[0]))]
        first_rank = None
        for rank, doc_id in enumerate(ordered, start=1):
            if doc_id in positives:
                first_rank = rank
                break
        mrr_values.append(0.0 if first_rank is None else 1.0 / first_rank)
        for k in recall_at:
            selected = set(ordered[:k])
            recall_at[k].append(len(selected & positives) / max(1, len(positives)))
            precision_at[k].append(len(selected & positives) / max(1, k))
    return {
        "num_examples": len(examples),
        "recall_at_1": _mean(recall_at[1]),
        "recall_at_2": _mean(recall_at[2]),
        "recall_at_4": _mean(recall_at[4]),
        "precision_at_1": _mean(precision_at[1]),
        "precision_at_2": _mean(precision_at[2]),
        "precision_at_4": _mean(precision_at[4]),
        "mrr": _mean(mrr_values),
    }


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
