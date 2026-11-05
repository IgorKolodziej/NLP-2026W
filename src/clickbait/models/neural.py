from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

from clickbait.cues import CUE_NAMES, cues_matrix
from clickbait.embeddings import EMBEDDING_DIM, load_embeddings


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
