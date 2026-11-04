from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import loguniform
from sklearn.linear_model import LogisticRegression

from clickbait.metrics import macro_f1


def sample_c_values(cfg: dict[str, Any], rng: np.random.Generator) -> list[float]:
    rs = cfg["randomized_search"]
    c_cfg = rs["C"]
    low = float(c_cfg["low"])
    high = float(c_cfg["high"])
    n_iter = int(rs["n_iter"])
    return loguniform.rvs(low, high, size=n_iter, random_state=rng).tolist()


def tune_lr_c(
    x_train,
    y_train,
    x_val,
    y_val,
    cfg: dict[str, Any],
    seed: int,
) -> tuple[float, float]:
    lr_cfg = cfg["logistic_regression"]
    rng = np.random.default_rng(seed)
    best_c = 1.0
    best_score = -1.0
    for c in sample_c_values(cfg, rng):
        model = LogisticRegression(
            C=float(c),
            class_weight=lr_cfg["class_weight"],
            max_iter=int(lr_cfg["max_iter"]),
            solver=lr_cfg["solver"],
            random_state=seed,
        )
        model.fit(x_train, y_train)
        val_pred = model.predict(x_val)
        score = macro_f1(y_val, val_pred)
        if score > best_score:
            best_score = score
            best_c = float(c)
    return best_c, best_score


def make_lr(c: float, cfg: dict[str, Any], seed: int) -> LogisticRegression:
    lr_cfg = cfg["logistic_regression"]
    return LogisticRegression(
        C=c,
        class_weight=lr_cfg["class_weight"],
        max_iter=int(lr_cfg["max_iter"]),
        solver=lr_cfg["solver"],
        random_state=seed,
    )
