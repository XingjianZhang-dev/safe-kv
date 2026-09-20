#!/usr/bin/env python
"""Build the SAFE-KV ARR drafting package from existing results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv.paper_package import build_paper_package  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("paper"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_paper_package(args.results_root.resolve(), args.out_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
