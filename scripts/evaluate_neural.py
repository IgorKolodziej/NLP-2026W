#!/usr/bin/env python3
import argparse
import hashlib
import json
import platform
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from clickbait.config import repo_root
from clickbait.evaluation import load_frozen_neural, score_neural_pair
from clickbait.splits import load_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate frozen B/C models on their manifest's test partition.")
    parser.add_argument(
        "--freeze", type=Path, default=Path("results/frozen/temporal_main/protocol.json"),
        help="Frozen protocol path relative to the repository root",
    )
    args = parser.parse_args()
    root = repo_root()
    freeze_path = root / args.freeze
    start = time.perf_counter()
    frozen, models = load_frozen_neural(root, freeze_path)
    load_seconds = time.perf_counter() - start
    cfg = frozen["config"]
    manifest = load_manifest(root / cfg["paths"]["splits"] / f"{frozen['split']}.json")
    source = root / cfg["paths"]["data_processed"] / "posts.parquet"
    posts = pd.read_parquet(
        source, columns=["post_id", "post_text", "label"],
        filters=[("post_id", "in", manifest.test_ids)],
    ).set_index("post_id").loc[manifest.test_ids].reset_index()
    metrics, predictions, timing = score_neural_pair(posts, models, root / cfg["paths"]["cache"] / "embeddings", cfg)
    predictions.insert(1, "split", manifest.name)
    results_dir = root / cfg["paths"]["results"]
    predictions_path = results_dir / f"bc_{manifest.name}_test_predictions.parquet"
    predictions.to_parquet(predictions_path, index=False)
    delta = metrics["C"]["macro_f1"] - metrics["B"]["macro_f1"]
    summary = {
        "split": manifest.name, "split_type": manifest.split_type, "evaluation_partition": "test",
        "n_test": len(posts), "class_order": [0, 1],
        "systems": {
            system: {"selected_C": frozen["models"][system]["selected_C"], "test": metrics[system]}
            for system in ("B", "C")
        },
        "delta_macro_f1_C_minus_B": delta,
        "timing_seconds": {"load_frozen_models_and_check_inputs": load_seconds, **timing},
        "freeze": str(freeze_path.relative_to(root)),
        "freeze_sha256": hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
        "paired_predictions": str(predictions_path.relative_to(root)),
        "paired_predictions_sha256": hashlib.sha256(predictions_path.read_bytes()).hexdigest(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join(["uv", "run", "--locked", "python", *sys.argv]),
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "code_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain", "--", "src", "scripts", "configs", "resources", "pyproject.toml", "uv.lock"],
            cwd=root, text=True,
        ).strip()),
        "python_version": platform.python_version(), "package_versions": frozen["package_versions"],
    }
    summary_path = results_dir / f"bc_{manifest.name}_test.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for system in ("B", "C"):
        print(f"{system} {manifest.name}/test: macro_f1={metrics[system]['macro_f1']:.6f}")
    print(f"C - B: {delta:+.6f}; wrote {summary_path.relative_to(root)}")


if __name__ == "__main__":
    main()
