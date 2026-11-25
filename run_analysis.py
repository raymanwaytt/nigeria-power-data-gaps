#!/usr/bin/env python3
"""Rebuild tables and charts from the files in this repository.

    python run_analysis.py
    python run_analysis.py --download

The second form refreshes the publisher files, checks the EIA checksum,
rewrites the ECOWAS slices, and then runs the same comparison.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from nigeria_power.pipeline import main  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Refresh source files from the publishers before rebuilding.",
    )
    args = parser.parse_args()
    main(download=args.download)
