"""Data checks and provenance artifacts for the proof-of-concept run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from clickbait.config import load_config, repo_root
from clickbait.dataset import build_raw_frame, clean_dataset, normalize_teaser
from clickbait.splits import SplitManifest


def _partition_stats(posts: pd.DataFrame, ids: list[str]) -> dict[str, Any]:
    rows = posts.set_index("post_id").loc[ids]
    return {
        "n": int(len(rows)),
        "positive": int(rows["label"].sum()),
        "positive_rate": float(rows["label"].mean()),
    }


def audit_main(
    posts: pd.DataFrame,
    manifest: SplitManifest,
    min_test_size: int = 1000,
) -> dict[str, Any]:
    """Validate the main chronological pilot manifest and report its counts."""
    required = {"post_id", "post_text", "label", "target_title", "year_month"}
    missing = required - set(posts.columns)
    if missing:
        raise ValueError(f"Posts missing audit columns: {sorted(missing)}")
    if posts["label"].isna().any() or not set(posts["label"].unique()).issubset({0, 1}):
        raise ValueError("Posts labels must be binary 0/1 and non-missing")
    parts = {"train": manifest.train_ids, "val": manifest.val_ids, "test": manifest.test_ids}
    all_ids = [post_id for ids in parts.values() for post_id in ids]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Manifest contains duplicate IDs across partitions")
    post_ids = set(posts["post_id"])
    if len(post_ids) != len(posts):
        raise ValueError("Posts contain duplicate IDs")
    missing_ids = set(all_ids) - post_ids
    if missing_ids:
        raise ValueError(f"Manifest IDs missing from posts: {sorted(missing_ids)[:5]}")

    frame = posts.set_index("post_id")
    norm_teaser = frame["post_text"].map(normalize_teaser)
    norm_title = frame["target_title"].fillna("").map(lambda value: normalize_teaser(str(value)))
    overlap = {}
    for left_name, left_ids in parts.items():
        for right_name, right_ids in parts.items():
            if left_name >= right_name:
                continue
            left, right = set(left_ids), set(right_ids)
            overlap[f"{left_name}_{right_name}"] = {
                "ids": len(left & right),
                "normalized_teasers": len(set(norm_teaser.loc[left_ids]) & set(norm_teaser.loc[right_ids])),
                "normalized_titles": len(
                    (set(norm_title.loc[left_ids]) - {""})
                    & (set(norm_title.loc[right_ids]) - {""})
                ),
            }
            if any(overlap[f"{left_name}_{right_name}"].values()):
                raise ValueError(f"Cross-partition overlap in {left_name}/{right_name}")

    expected = {
        "train": {"2016-12", "2017-01", "2017-02"},
        "val": {"2017-03"},
        "test": {"2017-04"},
    }
    months = {name: set(frame.loc[ids, "year_month"]) for name, ids in parts.items()}
    if any(months[name] != expected[name] for name in parts):
        raise ValueError(f"Unexpected months: {months}")
    stats = {name: _partition_stats(posts, ids) for name, ids in parts.items()}
    if stats["test"]["n"] < min_test_size:
        raise ValueError(f"Test partition has {stats['test']['n']} rows; minimum is {min_test_size}")
    return {
        "manifest": manifest.name,
        "type": manifest.split_type,
        "months": {name: sorted(value) for name, value in months.items()},
        "partitions": stats,
        "cross_partition_overlap": overlap,
        "min_test_size": min_test_size,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _ledger(raw: pd.DataFrame) -> pd.DataFrame:
    work = raw.copy()
    work["_input_order"] = range(len(work))
    work["teaser_norm"] = work["post_text"].map(normalize_teaser)
    work = work.sort_values("post_timestamp", kind="mergesort")
    work["article_group_key"] = [
        normalize_teaser(str(title)) if title is not None and str(title).strip() else f"singleton:{post_id}"
        for title, post_id in zip(work["target_title"], work["post_id"], strict=True)
    ]
    kept_teaser: set[str] = set()
    kept_article: set[str] = set()
    teaser_representatives: dict[str, str] = {}
    article_representatives: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    for row in work.itertuples(index=False):
        if not row.teaser_norm:
            records.append({"post_id": row.post_id, "retained_post_id": "", "reason": "empty_teaser", "stage": "empty_teaser", "label": int(row.label)})
            continue
        if row.teaser_norm in kept_teaser:
            representative = teaser_representatives[row.teaser_norm]
            records.append({"post_id": row.post_id, "retained_post_id": representative, "reason": "repeated_teaser", "stage": "teaser_dedupe", "label": int(row.label)})
            continue
        kept_teaser.add(row.teaser_norm)
        teaser_representatives[row.teaser_norm] = row.post_id
        if row.article_group_key in kept_article:
            representative = article_representatives[row.article_group_key]
            records.append({"post_id": row.post_id, "retained_post_id": representative, "reason": "repeated_article_title", "stage": "article_dedupe", "label": int(row.label)})
            continue
        kept_article.add(row.article_group_key)
        article_representatives[row.article_group_key] = row.post_id
        records.append({"post_id": row.post_id, "retained_post_id": row.post_id, "reason": "retained", "stage": "retained", "label": int(row.label)})
    return pd.DataFrame(records, columns=["post_id", "retained_post_id", "reason", "stage", "label"])


def reconcile_raw(root: Path | None, posts: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    """Rebuild the current cleaning stages and persist an ID-only exclusion ledger."""
    root = root or repo_root()
    cfg = load_config()
    instances = root / cfg["webis17"]["instances"]
    truth = root / cfg["webis17"]["truth"]
    if not instances.is_file() or not truth.is_file():
        raise FileNotFoundError(f"Missing raw inputs: {instances}, {truth}")
    raw = build_raw_frame(instances, truth)
    cleaned, cleaning = clean_dataset(raw)
    expected = posts[["post_id", "post_text", "label"]].sort_values("post_id").reset_index(drop=True)
    actual = cleaned[["post_id", "post_text", "label"]].sort_values("post_id").reset_index(drop=True)
    if not expected.equals(actual):
        raise ValueError("Existing processed posts differ from the raw cleaning result")
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger = _ledger(raw)
    expected_counts = {
        "empty_teasers": cleaning.empty_teasers,
        "repeated_teasers": cleaning.teaser_duplicates_removed,
        "repeated_article_titles": cleaning.article_duplicates_removed,
        "retained": cleaning.final_rows,
    }
    actual_counts = {
        "empty_teasers": int((ledger["reason"] == "empty_teaser").sum()),
        "repeated_teasers": int((ledger["reason"] == "repeated_teaser").sum()),
        "repeated_article_titles": int((ledger["reason"] == "repeated_article_title").sum()),
        "retained": int((ledger["reason"] == "retained").sum()),
    }
    if actual_counts != expected_counts:
        raise ValueError(f"Ledger counts differ from cleaning result: {actual_counts} != {expected_counts}")
    retained_ids = set(ledger.loc[ledger["reason"] == "retained", "post_id"])
    cleaned_ids = set(cleaned["post_id"])
    if retained_ids != cleaned_ids:
        raise ValueError("Ledger retained IDs differ from cleaned dataset")
    ledger.to_csv(output_dir / "exclusion_ledger.csv", index=False)
    stats = {
        "raw_joined": int(len(raw)),
        **actual_counts,
        "final_rows": int(len(cleaned)),
        "positive_count": int(cleaned["label"].sum()),
    }
    payload = {
        "sources": {"instances": str(instances.relative_to(root)), "truth": str(truth.relative_to(root))},
        "source_sha256": {"instances": _sha256(instances), "truth": _sha256(truth)},
        "cleaning": stats,
        "cleaning_dataclass": {"raw_joined": cleaning.raw_joined, "final_rows": cleaning.final_rows},
        "ledger": "exclusion_ledger.csv",
    }
    (output_dir / "data_audit.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
