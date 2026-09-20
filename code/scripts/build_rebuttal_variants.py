#!/usr/bin/env python
"""Build deterministic score-neutral/order-shuffled rebuttal datasets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.build_diagnostic import read_jsonl, write_jsonl  # noqa: E402
from safekv.rebuttal_variants import (  # noqa: E402
    build_nested_single_evidence_variant,
    transform_external_examples,
    variant_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--retrieval-mode",
        choices=["original", "zero", "lexical"],
        default="zero",
    )
    parser.add_argument("--shuffle-seed", type=int, default=None)
    parser.add_argument("--max-documents", type=int, default=None)
    parser.add_argument("--max-examples", type=int, default=None)
    parser.add_argument("--nested-single-evidence", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = read_jsonl(args.input)
    if args.nested_single_evidence:
        if args.max_documents is None or args.shuffle_seed is None:
            raise ValueError(
                "--nested-single-evidence requires --max-documents and --shuffle-seed"
            )
        transformed = [
            build_nested_single_evidence_variant(
                example,
                num_documents=args.max_documents,
                layout_seed=args.shuffle_seed,
                retrieval_mode=args.retrieval_mode,
            )
            for example in source
            if example.category == "single_evidence"
        ]
        transformed = [example for example in transformed if example is not None]
    else:
        transformed = transform_external_examples(
            source,
            retrieval_mode=args.retrieval_mode,
            shuffle_seed=args.shuffle_seed,
            max_documents=args.max_documents,
        )
    if args.max_examples is not None:
        transformed = transformed[: args.max_examples]
    write_jsonl(transformed, args.output)
    summary = {
        "input": str(args.input),
        "output": str(args.output),
        "retrieval_mode": args.retrieval_mode,
        "shuffle_seed": args.shuffle_seed,
        "max_documents": args.max_documents,
        "nested_single_evidence": args.nested_single_evidence,
        **variant_summary(transformed),
    }
    summary_path = args.output.with_suffix(args.output.suffix + ".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
