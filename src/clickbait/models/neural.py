from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from clickbait.cues import CUE_NAMES, cues_matrix
from clickbait.embeddings import EMBEDDING_DIM, load_embeddings
from clickbait.metrics import evaluate_split
from clickbait.tuning import fit_lr, make_lr, tune_lr_c


def load_neural_inputs(
    posts: pd.DataFrame,
    cache_dir: Path,
    cfg: dict[str, Any],
    system: str,
) -> np.ndarray:
    """Load ordered embeddings, appending unscaled cues for system C."""
    if system not in {"B", "C"}:
        raise ValueError("System must be B or C")
    embeddings = np.ascontiguousarray(load_embeddings(cache_dir, posts, cfg), dtype=np.float64)
    if system == "B":
        return embeddings
    return np.hstack((embeddings, cues_matrix(posts["post_text"])))


def build_cue_scaler() -> ColumnTransformer:
    """Create C's preprocessor; fit on training inputs and transform other partitions."""
    return ColumnTransformer(
        [
            ("embeddings", "passthrough", slice(0, EMBEDDING_DIM)),
            ("cues", StandardScaler(), slice(EMBEDDING_DIM, EMBEDDING_DIM + len(CUE_NAMES))),
        ]
    )


def train_b_validation(
    train_posts: pd.DataFrame,
    val_posts: pd.DataFrame,
    cache_dir: Path,
    cfg: dict[str, Any],
) -> tuple[LogisticRegression, dict[str, Any], pd.DataFrame]:
    if cfg["training"]["refit_on"] != "train":
        raise ValueError("B validation runs require training.refit_on: train")
    seed = int(cfg["random_seed"])
    start = time.perf_counter()
    x_train = load_neural_inputs(train_posts, cache_dir, cfg, "B")
    x_val = load_neural_inputs(val_posts, cache_dir, cfg, "B")
    load_seconds = time.perf_counter() - start
    y_train = train_posts["label"].to_numpy()
    y_val = val_posts["label"].to_numpy()

    start = time.perf_counter()
    best_c, best_score, candidates = tune_lr_c(x_train, y_train, x_val, y_val, cfg, seed)
    tuning_seconds = time.perf_counter() - start
    start = time.perf_counter()
    model = fit_lr(make_lr(best_c, cfg, seed), x_train, y_train)
    fit_seconds = time.perf_counter() - start
    start = time.perf_counter()
    probabilities = model.predict_proba(x_val)[:, 1]
    predictions = model.predict(x_val)
    predict_seconds = time.perf_counter() - start

    summary = {
        "system": "B", "evaluation_partition": "val", "random_seed": seed,
        "n_train": len(train_posts), "n_val": len(val_posts), "n_features": x_train.shape[1],
        "best_C": best_c,
        "tuning": {
            "protocol": "randomized search on validation macro-F1; refit on train only",
            "validation_macro_f1_at_best_C": best_score,
            "n_iter": int(cfg["randomized_search"]["n_iter"]),
            "tie_break": "first sampled candidate",
            "candidates": candidates,
        },
        "classifier_parameters": model.get_params(),
        "final_fit_n_iter": int(model.n_iter_[0]),
        "validation": evaluate_split(y_val, probabilities, predictions),
        "timing_seconds": {
            "cache_load": load_seconds, "tuning": tuning_seconds,
            "lr_fit_train": fit_seconds, "validation_predict": predict_seconds,
        },
    }
    output = pd.DataFrame({
        "post_id": val_posts["post_id"].to_numpy(), "partition": "val",
        "y_true": y_val, "y_pred": predictions, "p_clickbait": probabilities,
    })
    return model, summary, output
