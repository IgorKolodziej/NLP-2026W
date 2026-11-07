#!/usr/bin/env python3
import argparse
import hashlib
import json
import pickle
import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version

import pandas as pd

from clickbait.config import load_config, repo_root
from clickbait.models.neural import train_b_validation
from clickbait.splits import load_manifest
from clickbait.tuning import TuningConvergenceError


def main() -> None:
    parser = argparse.ArgumentParser(description="Train system B and evaluate on validation only.")
    parser.add_argument("--system", choices=["B"], required=True)
    parser.add_argument("--split", required=True, help="Manifest basename, e.g. temporal_main")
    args = parser.parse_args()
    cfg = load_config()
    root = repo_root()
    source = root / cfg["paths"]["data_processed"] / "posts.parquet"
    manifest_path = root / cfg["paths"]["splits"] / f"{args.split}.json"
    manifest = load_manifest(manifest_path)
    posts = pd.read_parquet(
        source, columns=["post_id", "post_text", "label"],
        filters=[("post_id", "in", manifest.train_ids + manifest.val_ids)],
    ).set_index("post_id")
    train = posts.loc[manifest.train_ids].reset_index()
    val = posts.loc[manifest.val_ids].reset_index()
    cache_dir = root / cfg["paths"]["cache"] / "embeddings"
    results_dir = root / cfg["paths"]["results"]
    run_dir = results_dir / "runs" / f"b_{manifest.name}_validation"
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        model, summary, predictions = train_b_validation(train, val, cache_dir, cfg)
    except TuningConvergenceError as error:
        failure = run_dir / "tuning_failure.json"
        failure.write_text(json.dumps({
            "system": "B", "split": manifest.name, "status": "failed",
            "config": cfg, "candidates": error.candidates,
        }, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(f"{error}; details: {failure.relative_to(root)}") from error

    model_path = run_dir / "model.pkl"
    predictions_path = run_dir / "validation_predictions.parquet"
    with model_path.open("wb") as f:
        pickle.dump(model, f)
    predictions.to_parquet(predictions_path, index=False)
    cache_meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
    summary.update({
        "split": manifest.name, "split_type": manifest.split_type,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join(["uv", "run", "--locked", "python", *sys.argv]),
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "code_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--", "src", "scripts", "configs", "pyproject.toml", "uv.lock"],
            cwd=root, text=True,
        ).strip()),
        "python_version": platform.python_version(),
        "package_versions": {name: version(name) for name in ("numpy", "pandas", "scipy", "scikit-learn", "pyarrow")},
        "config": cfg,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "uv_lock_sha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
        "embedding_archive_sha256": cache_meta["archive_sha256"],
        "artifacts": {
            "model": str(model_path.relative_to(root)),
            "validation_predictions": str(predictions_path.relative_to(root)),
        },
    })
    summary_path = results_dir / f"system_b_{manifest.name}_validation.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"B {manifest.name}/val: macro_f1={summary['validation']['macro_f1']:.6f}; best_C={summary['best_C']:.6g}")
    print(f"All {len(summary['tuning']['candidates'])} candidates converged; wrote {summary_path.relative_to(root)}")


if __name__ == "__main__":
    main()
