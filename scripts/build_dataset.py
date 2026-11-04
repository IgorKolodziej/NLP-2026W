#!/usr/bin/env python3
import json
from pathlib import Path

from clickbait.config import load_config, repo_root
from clickbait.dataset import build_raw_frame, clean_dataset, stats_to_dict


def main() -> None:
    cfg = load_config()
    root = repo_root()
    paths = cfg["paths"]
    w17 = cfg["webis17"]

    instances = root / w17["instances"]
    truth = root / w17["truth"]
    if not instances.is_file() or not truth.is_file():
        raise SystemExit(
            f"Missing Webis-17 JSONL. Expected:\n  {instances}\n  {truth}\n"
            "Download clickbait17-train-170630.zip from Zenodo and extract jsonl files "
            "(see docs/data.md)."
        )

    out_dir = root / paths["data_processed"]
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = out_dir / "posts.parquet"
    stats_path = out_dir / "dataset_stats.json"

    raw = build_raw_frame(instances, truth)
    cleaned, stats = clean_dataset(raw)
    cleaned.to_parquet(parquet_path, index=False)

    payload = {
        "sources": {"instances": str(instances.relative_to(root)), "truth": str(truth.relative_to(root))},
        "output": str(parquet_path.relative_to(root)),
        "cleaning": stats_to_dict(stats),
    }
    stats_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    c = stats
    print(f"Joined rows: {c.raw_joined}")
    print(f"Empty teasers dropped: {c.empty_teasers}")
    print(f"Teaser dedupe removed: {c.teaser_duplicates_removed} -> {c.after_teaser_dedupe} rows")
    print(f"Article dedupe removed: {c.article_duplicates_removed} -> {c.final_rows} rows")
    print(f"Positive: {c.positive_count} ({100 * c.positive_count / c.final_rows:.2f}%)")
    print(f"Wrote {parquet_path} and {stats_path}")


if __name__ == "__main__":
    main()
