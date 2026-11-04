#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd

from clickbait.config import load_config, repo_root
from clickbait.metrics import evaluate_split
from clickbait.models.system_a import build_system_a_pipeline
from clickbait.splits import load_manifest
from clickbait.tuning import make_lr, tune_lr_c


def _subset(df: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    return df.set_index("post_id").loc[ids].reset_index()


def main() -> None:
    parser = argparse.ArgumentParser(description="Train system A (TF-IDF + LR) on a split manifest.")
    parser.add_argument(
        "--split",
        required=True,
        help="Manifest basename without .json (e.g. temporal_main)",
    )
    args = parser.parse_args()

    cfg = load_config()
    root = repo_root()
    seed = int(cfg["random_seed"])

    parquet_path = root / cfg["paths"]["data_processed"] / "posts.parquet"
    manifest_path = root / cfg["paths"]["splits"] / f"{args.split}.json"
    if not parquet_path.is_file():
        raise SystemExit(f"Missing {parquet_path}; run build_dataset.py")
    if not manifest_path.is_file():
        raise SystemExit(f"Missing {manifest_path}; run build_splits.py")

    df = pd.read_parquet(parquet_path)
    manifest = load_manifest(manifest_path)
    train_df = _subset(df, manifest.train_ids)
    val_df = _subset(df, manifest.val_ids)
    test_df = _subset(df, manifest.test_ids)

    pipe = build_system_a_pipeline()
    t0 = time.perf_counter()
    pipe.fit(train_df["post_text"], train_df["label"])
    x_train = pipe.transform(train_df["post_text"])
    x_val = pipe.transform(val_df["post_text"])
    x_test = pipe.transform(test_df["post_text"])
    fit_transform_s = time.perf_counter() - t0

    best_c, val_macro_f1 = tune_lr_c(
        x_train,
        train_df["label"].to_numpy(),
        x_val,
        val_df["label"].to_numpy(),
        cfg,
        seed,
    )

    lr = make_lr(best_c, cfg, seed)
    t1 = time.perf_counter()
    lr.fit(x_train, train_df["label"])
    train_predict_s = time.perf_counter() - t1

    def predict_block(x, y):
        prob = lr.predict_proba(x)[:, 1]
        pred = lr.predict(x)
        return evaluate_split(y.to_numpy(), prob, pred)

    val_metrics = predict_block(x_val, val_df["label"])
    test_metrics = predict_block(x_test, test_df["label"])

    results_dir = root / cfg["paths"]["results"]
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"system_a_{manifest.name}.json"
    payload = {
        "system": "A",
        "split": manifest.name,
        "split_type": manifest.split_type,
        "random_seed": seed,
        "best_C": best_c,
        "tuning": {
            "protocol": "randomized search on validation macro-F1; refit on train only",
            "validation_macro_f1_at_best_C": val_macro_f1,
            "n_iter": int(cfg["randomized_search"]["n_iter"]),
        },
        "timing_seconds": {
            "tfidf_fit_transform_train_val_test": fit_transform_s,
            "lr_fit_train": train_predict_s,
        },
        "validation": val_metrics,
        "test": test_metrics,
        "n_train": len(train_df),
        "n_val": len(val_df),
        "n_test": len(test_df),
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"split={manifest.name} best_C={best_c:.4g}")
    print(f"val macro_f1={val_metrics['macro_f1']:.4f} test macro_f1={test_metrics['macro_f1']:.4f}")
    print(f"wrote {out_path.relative_to(root)}")


if __name__ == "__main__":
    main()
