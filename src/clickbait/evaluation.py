from __future__ import annotations

import hashlib
import json
import pickle
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from clickbait.embeddings import EMBEDDING_DIM
from clickbait.metrics import evaluate_split
from clickbait.models.neural import load_neural_inputs


def load_frozen_neural(root: Path, freeze_path: Path) -> tuple[dict[str, Any], dict]:
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    for name, expected in frozen["package_versions"].items():
        if version(name) != expected:
            raise ValueError(f"Frozen environment requires {name}=={expected}")
    for relative, expected in frozen["input_sha256"].items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen input changed: {relative}")
    models = {}
    for system in ("B", "C"):
        entry = frozen["models"][system]
        path = freeze_path.parent / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Frozen model changed: {system}")
        with path.open("rb") as f:
            models[system] = pickle.load(f)
    return frozen, models


def score_neural_pair(
    posts: pd.DataFrame,
    models: dict,
    cache_dir: Path,
    cfg: dict[str, Any],
) -> tuple[dict, pd.DataFrame, dict[str, float]]:
    start = time.perf_counter()
    x_c = load_neural_inputs(posts, cache_dir, cfg, "C")
    x_b = np.ascontiguousarray(x_c[:, :EMBEDDING_DIM])
    timing = {"features_B_and_C": time.perf_counter() - start}
    y_true = posts["label"].to_numpy()
    predictions = pd.DataFrame({
        "post_id": posts["post_id"].to_numpy(), "partition": "test", "y_true": y_true,
    })
    metrics = {}
    for system, features in (("B", x_b), ("C", x_c)):
        start = time.perf_counter()
        probabilities = models[system].predict_proba(features)[:, 1]
        labels = models[system].predict(features)
        timing[f"predict_{system}"] = time.perf_counter() - start
        predictions[f"y_pred_{system}"] = labels
        predictions[f"p_clickbait_{system}"] = probabilities
        metrics[system] = evaluate_split(y_true, probabilities, labels)
    return metrics, predictions, timing
