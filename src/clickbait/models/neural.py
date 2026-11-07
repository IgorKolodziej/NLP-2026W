from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
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


def train_neural_validation(
    train_posts: pd.DataFrame,
    val_posts: pd.DataFrame,
    cache_dir: Path,
    cfg: dict[str, Any],
    system: str,
) -> tuple[LogisticRegression | Pipeline, dict[str, Any], pd.DataFrame]:
    if cfg["training"]["refit_on"] != "train":
        raise ValueError("B/C validation runs require training.refit_on: train")
    seed = int(cfg["random_seed"])
    start = time.perf_counter()
    x_train = load_neural_inputs(train_posts, cache_dir, cfg, system)
    x_val = load_neural_inputs(val_posts, cache_dir, cfg, system)
    load_seconds = time.perf_counter() - start
    y_train = train_posts["label"].to_numpy()
    y_val = val_posts["label"].to_numpy()

    preprocessor = None
    train_features, val_features = x_train, x_val
    scaling_seconds = 0.0
    if system == "C":
        start = time.perf_counter()
        preprocessor = build_cue_scaler()
        train_features = preprocessor.fit_transform(x_train)
        val_features = preprocessor.transform(x_val)
        scaling_seconds = time.perf_counter() - start

    start = time.perf_counter()
    best_c, best_score, candidates = tune_lr_c(train_features, y_train, val_features, y_val, cfg, seed)
    tuning_seconds = time.perf_counter() - start
    start = time.perf_counter()
    classifier = fit_lr(make_lr(best_c, cfg, seed), train_features, y_train)
    fit_seconds = time.perf_counter() - start
    model = classifier if preprocessor is None else Pipeline([
        ("preprocessor", preprocessor), ("classifier", classifier),
    ])
    start = time.perf_counter()
    probabilities = model.predict_proba(x_val)[:, 1]
    predictions = model.predict(x_val)
    predict_seconds = time.perf_counter() - start

    summary = {
        "system": system, "evaluation_partition": "val", "random_seed": seed,
        "n_train": len(train_posts), "n_val": len(val_posts), "n_features": x_train.shape[1],
        "best_C": best_c,
        "tuning": {
            "protocol": "randomized search on validation macro-F1; refit on train only",
            "validation_macro_f1_at_best_C": best_score,
            "n_iter": int(cfg["randomized_search"]["n_iter"]),
            "tie_break": "first sampled candidate",
            "candidates": candidates,
        },
        "classifier_parameters": classifier.get_params(),
        "final_fit_n_iter": int(classifier.n_iter_[0]),
        "validation": evaluate_split(y_val, probabilities, predictions),
        "timing_seconds": {
            "feature_load": load_seconds, "cue_scaling": scaling_seconds, "tuning": tuning_seconds,
            "lr_fit_train": fit_seconds, "validation_predict": predict_seconds,
        },
    }
    if system == "C":
        summary["cue_names"] = CUE_NAMES
    output = pd.DataFrame({
        "post_id": val_posts["post_id"].to_numpy(), "partition": "val",
        "y_true": y_val, "y_pred": predictions, "p_clickbait": probabilities,
    })
    return model, summary, output
