from __future__ import annotations

import time
import warnings
from typing import Any

import numpy as np
from scipy.stats import loguniform
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from clickbait.metrics import macro_f1


class TuningConvergenceError(RuntimeError):
    def __init__(self, candidates: list[dict[str, Any]]):
        self.candidates = candidates
        super().__init__(f"LR did not converge at C={candidates[-1]['C']:.6g}; search aborted")


def sample_c_values(cfg: dict[str, Any], rng: np.random.Generator) -> list[float]:
    rs = cfg["randomized_search"]
    c_cfg = rs["C"]
    low = float(c_cfg["low"])
    high = float(c_cfg["high"])
    n_iter = int(rs["n_iter"])
    if n_iter < 1:
        raise ValueError("randomized_search.n_iter must be positive")
    return loguniform.rvs(low, high, size=n_iter, random_state=rng).tolist()


def fit_lr(model: LogisticRegression, x_train, y_train) -> LogisticRegression:
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x_train, y_train)
    return model


def tune_lr_c(
    x_train,
    y_train,
    x_val,
    y_val,
    cfg: dict[str, Any],
    seed: int,
) -> tuple[float, float, list[dict[str, Any]]]:
    rng = np.random.default_rng(seed)
    best_c = 1.0
    best_score = -1.0
    candidates = []
    for c in sample_c_values(cfg, rng):
        model = make_lr(float(c), cfg, seed)
        start = time.perf_counter()
        try:
            fit_lr(model, x_train, y_train)
        except ConvergenceWarning as error:
            candidates.append({
                "C": float(c), "converged": False, "validation_macro_f1": None,
                "n_iter": None, "fit_seconds": time.perf_counter() - start, "warning": str(error),
            })
            raise TuningConvergenceError(candidates) from error
        fit_seconds = time.perf_counter() - start
        val_pred = model.predict(x_val)
        score = macro_f1(y_val, val_pred)
        candidates.append({
            "C": float(c), "converged": True, "validation_macro_f1": score,
            "n_iter": int(model.n_iter_[0]), "fit_seconds": fit_seconds,
        })
        if score > best_score:
            best_score = score
            best_c = float(c)
    return best_c, best_score, candidates


def make_lr(c: float, cfg: dict[str, Any], seed: int) -> LogisticRegression:
    lr_cfg = cfg["logistic_regression"]
    return LogisticRegression(
        C=c,
        class_weight=lr_cfg["class_weight"],
        max_iter=int(lr_cfg["max_iter"]),
        solver=lr_cfg["solver"],
        random_state=seed,
    )
