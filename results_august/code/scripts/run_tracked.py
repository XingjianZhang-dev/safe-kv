#!/usr/bin/env python3
"""CLI wrapper for the append-only IP&M experiment registry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv_ipm.run_registry import main


if __name__ == "__main__":
    main()
