#!/usr/bin/env python3
from pathlib import Path

import pandas as pd

from clickbait.config import load_config, repo_root
from clickbait.splits import build_all_manifests, write_manifest


def main() -> None:
    cfg = load_config()
    root = repo_root()
    parquet_path = root / cfg["paths"]["data_processed"] / "posts.parquet"
    if not parquet_path.is_file():
        raise SystemExit(f"Run build_dataset.py first. Missing {parquet_path}")

    df = pd.read_parquet(parquet_path)
    splits_dir = root / cfg["paths"]["splits"]
    manifests = build_all_manifests(df, cfg)
    for m in manifests:
        path = write_manifest(m, splits_dir)
        meta = m.metadata
        print(
            f"{m.name}: train={meta['train']['n']} val={meta['val']['n']} test={meta['test']['n']} "
            f"-> {path.relative_to(root)}"
        )


if __name__ == "__main__":
    main()
