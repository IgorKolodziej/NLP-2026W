#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from clickbait.poc import run_poc, verify_poc


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or verify the one-split A/B/C PoC.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--split", default="temporal_main")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    result = verify_poc(args.verify) if args.verify else run_poc(args.output, args.split)
    print(f"split={result['split']} C_minus_B={result.get('delta_macro_f1_C_minus_B')}")


if __name__ == "__main__":
    main()
