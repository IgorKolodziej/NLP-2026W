from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class CleaningStats:
    raw_joined: int
    empty_teasers: int
    after_empty_drop: int
    teaser_duplicates_removed: int
    after_teaser_dedupe: int
    article_duplicates_removed: int
    final_rows: int
    positive_count: int


def normalize_teaser(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.strip().lower())


def teaser_from_post_text(post_text: Any) -> str:
    if post_text is None:
        return ""
    if isinstance(post_text, list):
        parts = [str(p) for p in post_text if p is not None]
        return " ".join(parts).strip()
    return str(post_text).strip()


def article_group_key(target_title: Any, instance_id: str) -> str:
    if target_title is None:
        return f"singleton:{instance_id}"
    title = str(target_title).strip()
    if not title:
        return f"singleton:{instance_id}"
    return normalize_teaser(title)


def truth_to_label(truth_class: str) -> int:
    normalized = truth_class.replace("-", "_")
    if normalized == "clickbait":
        return 1
    if normalized == "no_clickbait":
        return 0
    raise ValueError(f"Unknown truthClass: {truth_class!r}")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_raw_frame(instances_path: Path, truth_path: Path) -> pd.DataFrame:
    instances = {row["id"]: row for row in load_jsonl(instances_path)}
    truth_rows = load_jsonl(truth_path)
    records: list[dict[str, Any]] = []
    missing_instance = 0
    for t in truth_rows:
        tid = t["id"]
        inst = instances.get(tid)
        if inst is None:
            missing_instance += 1
            continue
        teaser = teaser_from_post_text(inst.get("postText"))
        records.append(
            {
                "post_id": tid,
                "post_text": teaser,
                "post_timestamp": inst["postTimestamp"],
                "target_title": inst.get("targetTitle"),
                "truth_class": t["truthClass"],
                "label": truth_to_label(t["truthClass"]),
                "truth_judgments": t.get("truthJudgments"),
            }
        )
    if missing_instance:
        raise ValueError(f"{missing_instance} truth ids missing from instances")
    df = pd.DataFrame(records)
    df["post_timestamp"] = pd.to_datetime(df["post_timestamp"], utc=True)
    return df


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningStats]:
    raw_joined = len(df)
    df = df.copy()
    df["teaser_norm"] = df["post_text"].map(normalize_teaser)
    empty_mask = df["teaser_norm"] == ""
    empty_teasers = int(empty_mask.sum())
    df = df.loc[~empty_mask].copy()
    after_empty = len(df)

    df = df.sort_values("post_timestamp", kind="mergesort")
    teaser_dup_removed = int(df.duplicated(subset=["teaser_norm"], keep="first").sum())
    df = df.drop_duplicates(subset=["teaser_norm"], keep="first")
    after_teaser = len(df)

    df["article_group_key"] = [
        article_group_key(tt, pid)
        for tt, pid in zip(df["target_title"], df["post_id"], strict=True)
    ]
    article_dup_removed = int(df.duplicated(subset=["article_group_key"], keep="first").sum())
    df = df.drop_duplicates(subset=["article_group_key"], keep="first")
    final_rows = len(df)

    out = df[
        [
            "post_id",
            "post_text",
            "post_timestamp",
            "target_title",
            "article_group_key",
            "truth_class",
            "label",
            "truth_judgments",
        ]
    ].reset_index(drop=True)
    out["year_month"] = out["post_timestamp"].dt.strftime("%Y-%m")

    stats = CleaningStats(
        raw_joined=raw_joined,
        empty_teasers=empty_teasers,
        after_empty_drop=after_empty,
        teaser_duplicates_removed=teaser_dup_removed,
        after_teaser_dedupe=after_teaser,
        article_duplicates_removed=article_dup_removed,
        final_rows=final_rows,
        positive_count=int(out["label"].sum()),
    )
    return out, stats


def stats_to_dict(stats: CleaningStats) -> dict[str, Any]:
    return {
        "raw_joined": stats.raw_joined,
        "empty_teasers": stats.empty_teasers,
        "after_empty_drop": stats.after_empty_drop,
        "teaser_duplicates_removed": stats.teaser_duplicates_removed,
        "after_teaser_dedupe": stats.after_teaser_dedupe,
        "article_duplicates_removed": stats.article_duplicates_removed,
        "final_rows": stats.final_rows,
        "positive_count": stats.positive_count,
        "positive_rate": stats.positive_count / stats.final_rows if stats.final_rows else 0.0,
    }
