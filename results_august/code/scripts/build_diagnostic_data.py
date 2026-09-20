#!/usr/bin/env python
"""Build SAFE-KV synthetic diagnostic JSONL data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import build_diagnostic_examples, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-per-category", type=int, default=20)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument(
        "--variant",
        choices=["default", "noisy_retrieval"],
        default="default",
    )
    parser.add_argument("--out", type=Path, default=Path("data/diagnostic_100.jsonl"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    examples = build_diagnostic_examples(
        n_per_category=args.n_per_category,
        seed=args.seed,
        variant=args.variant,
    )
    write_jsonl(examples, args.out)
    print(f"Wrote {len(examples)} {args.variant} examples to {args.out}")


if __name__ == "__main__":
    main()
