#!/usr/bin/env python3
"""CLI wrapper for leakage-controlled IP&M evaluation input construction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safekv_ipm.data_build import main


if __name__ == "__main__":
    main()
