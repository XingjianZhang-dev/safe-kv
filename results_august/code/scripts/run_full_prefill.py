#!/usr/bin/env python
"""Run SAFE-KV Milestone 2 full-prefill reference inference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.config import load_config
from safekv.full_prefill import (
    load_examples_for_config,
    run_full_prefill_dataset,
    set_deterministic_seed,
)
from safekv.modeling import load_causal_lm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if config.experiment.prompt_format not in {"plain_rag", "chat_rag"}:
        raise ValueError("Milestone 2 supports prompt_format='plain_rag' or 'chat_rag'")
    if config.generation.do_sample:
        raise ValueError("Milestone 2 full-prefill generation requires do_sample=false")
    if config.generation.temperature != 0.0:
        raise ValueError("Milestone 2 full-prefill generation requires temperature=0")

    config_dir = args.config.resolve().parent.parent
    set_deterministic_seed(config.seed)
    examples = load_examples_for_config(config, config_dir=config_dir)
    loaded = load_causal_lm(config.model)
    out_dir = args.results_dir or args.out_dir or Path("results")
    summary = run_full_prefill_dataset(
        config=config,
        loaded=loaded,
        examples=examples,
        out_dir=out_dir,
        config_path=args.config,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
