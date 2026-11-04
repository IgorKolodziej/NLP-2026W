from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SplitManifest:
    name: str
    split_type: str
    train_ids: list[str]
    val_ids: list[str]
    test_ids: list[str]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.split_type,
            "train_ids": self.train_ids,
            "val_ids": self.val_ids,
            "test_ids": self.test_ids,
            "metadata": self.metadata,
        }


def partition_stats(ids: list[str], df: pd.DataFrame) -> dict[str, Any]:
    sub = df.set_index("post_id").loc[ids]
    n = len(sub)
    pos = int(sub["label"].sum())
    return {
        "n": n,
        "positive": pos,
        "positive_rate": pos / n if n else 0.0,
    }


def write_manifest(manifest: SplitManifest, splits_dir: Path) -> Path:
    splits_dir.mkdir(parents=True, exist_ok=True)
    path = splits_dir / f"{manifest.name}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)
        f.write("\n")
    return path


def temporal_manifest(
    name: str,
    df: pd.DataFrame,
    train_months: list[str],
    val_months: list[str],
    test_months: list[str],
) -> SplitManifest:
    train_ids = df.loc[df["year_month"].isin(train_months), "post_id"].tolist()
    val_ids = df.loc[df["year_month"].isin(val_months), "post_id"].tolist()
    test_ids = df.loc[df["year_month"].isin(test_months), "post_id"].tolist()
    overlap = (
        set(train_ids) & set(val_ids),
        set(train_ids) & set(test_ids),
        set(val_ids) & set(test_ids),
    )
    if any(overlap):
        raise ValueError(f"Temporal split {name} has overlapping ids")
    meta = {
        "train_months": train_months,
        "val_months": val_months,
        "test_months": test_months,
        "train": partition_stats(train_ids, df),
        "val": partition_stats(val_ids, df),
        "test": partition_stats(test_ids, df),
    }
    return SplitManifest(name, "temporal", train_ids, val_ids, test_ids, meta)


def grouped_random_manifest(
    name: str,
    df: pd.DataFrame,
    seed: int,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
) -> SplitManifest:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1")

    group_meta = (
        df.groupby("article_group_key", sort=False)
        .agg(group_label=("label", "max"))
        .reset_index()
    )
    rng = np.random.default_rng(seed)

    def split_group_list(keys: list[str]) -> tuple[list[str], list[str], list[str]]:
        keys = list(keys)
        rng.shuffle(keys)
        n = len(keys)
        if n == 0:
            return [], [], []
        n_train = max(1, int(round(n * train_ratio))) if n >= 3 else max(1, n - 2)
        n_val = max(1, int(round(n * val_ratio))) if n >= 3 else (1 if n > 1 else 0)
        if n_train + n_val >= n:
            n_train = max(1, n - 2)
            n_val = 1 if n > 1 else 0
        n_test = n - n_train - n_val
        return (
            keys[:n_train],
            keys[n_train : n_train + n_val],
            keys[n_train + n_val : n_train + n_val + n_test],
        )

    pos_keys = group_meta.loc[group_meta["group_label"] == 1, "article_group_key"].tolist()
    neg_keys = group_meta.loc[group_meta["group_label"] == 0, "article_group_key"].tolist()
    tr_p, va_p, te_p = split_group_list(pos_keys)
    tr_n, va_n, te_n = split_group_list(neg_keys)
    train_g = set(tr_p + tr_n)
    val_g = set(va_p + va_n)
    test_g = set(te_p + te_n)

    train_ids = df.loc[df["article_group_key"].isin(train_g), "post_id"].tolist()
    val_ids = df.loc[df["article_group_key"].isin(val_g), "post_id"].tolist()
    test_ids = df.loc[df["article_group_key"].isin(test_g), "post_id"].tolist()

    if train_g & val_g or train_g & test_g or val_g & test_g:
        raise ValueError(f"Random split {name}: group leakage across partitions")

    meta = {
        "seed": seed,
        "group_key": "article_group_key",
        "ratios": {"train": train_ratio, "val": val_ratio, "test": test_ratio},
        "n_groups": len(group_meta),
        "train_groups": len(train_g),
        "val_groups": len(val_g),
        "test_groups": len(test_g),
        "train": partition_stats(train_ids, df),
        "val": partition_stats(val_ids, df),
        "test": partition_stats(test_ids, df),
    }
    return SplitManifest(name, "random_grouped", train_ids, val_ids, test_ids, meta)


def build_all_manifests(df: pd.DataFrame, cfg: dict[str, Any]) -> list[SplitManifest]:
    temporal_specs = [
        (
            "temporal_w1_dec_jan_feb",
            ["2016-12"],
            ["2017-01"],
            ["2017-02"],
        ),
        (
            "temporal_w2_decjan_feb_mar",
            ["2016-12", "2017-01"],
            ["2017-02"],
            ["2017-03"],
        ),
        (
            "temporal_main",
            ["2016-12", "2017-01", "2017-02"],
            ["2017-03"],
            ["2017-04"],
        ),
    ]
    manifests = [
        temporal_manifest(name, df, train_m, val_m, test_m)
        for name, train_m, val_m, test_m in temporal_specs
    ]

    split_cfg = cfg.get("splits", {})
    seeds = split_cfg.get("random_seeds", [42, 43, 44])
    ratios = split_cfg.get("random_ratios", {"train": 0.7, "val": 0.15, "test": 0.15})
    tr = float(ratios["train"])
    va = float(ratios["val"])
    te = float(ratios["test"])

    for seed in seeds:
        manifests.append(
            grouped_random_manifest(
                f"random_grouped_seed{seed}",
                df,
                int(seed),
                tr,
                va,
                te,
            )
        )
    return manifests


def load_manifest(path: Path) -> SplitManifest:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return SplitManifest(
        name=data["name"],
        split_type=data["type"],
        train_ids=list(data["train_ids"]),
        val_ids=list(data["val_ids"]),
        test_ids=list(data["test_ids"]),
        metadata=dict(data["metadata"]),
    )
