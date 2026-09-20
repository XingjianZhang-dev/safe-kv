#!/usr/bin/env python
"""Build SAFE-KV external multi-hop JSONL data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_external import (  # noqa: E402
    build_2wiki_examples,
    build_hotpotqa_examples,
    load_2wiki_records,
    load_hotpotqa_records,
    write_external_jsonl,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["hotpotqa", "2wiki"], required=True)
    parser.add_argument("--input-json", type=Path, default=None)
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dataset == "hotpotqa":
        records = load_hotpotqa_records(args.input_json)
        result = build_hotpotqa_examples(records, n=args.n, seed=args.seed)
    else:
        records = load_2wiki_records(args.input_json)
        result = build_2wiki_examples(records, n=args.n, seed=args.seed)

    write_external_jsonl(result, args.out)
    print(json.dumps(result.summary, indent=2, ensure_ascii=False))
    if len(result.examples) < args.n:
        print(
            f"Warning: built {len(result.examples)} examples, fewer than requested {args.n}.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
