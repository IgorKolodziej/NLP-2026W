from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EMBEDDING_DIM = 384


def _validate_posts(posts: pd.DataFrame) -> None:
    for column in ("post_id", "post_text"):
        if not posts[column].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
            raise ValueError(f"{column} must contain nonempty strings")
    if posts.empty or not posts["post_id"].is_unique:
        raise ValueError("Posts must contain unique IDs and at least one row")


def _text_hashes(posts: pd.DataFrame) -> np.ndarray:
    return np.array([hashlib.sha256(text.encode("utf-8")).hexdigest() for text in posts["post_text"]])


def save_embeddings(
    directory: Path,
    posts: pd.DataFrame,
    embeddings: np.ndarray,
    metadata: dict[str, Any],
) -> None:
    _validate_posts(posts)
    if embeddings.shape != (len(posts), EMBEDDING_DIM):
        raise ValueError(f"Expected embeddings with shape ({len(posts)}, {EMBEDDING_DIM})")
    if embeddings.dtype != np.float32 or not np.isfinite(embeddings).all():
        raise ValueError("Embeddings must be finite float32 values")

    directory.mkdir(parents=True, exist_ok=True)
    archive = directory / "embeddings.npz"
    temporary = directory / "embeddings.npz.tmp"
    with temporary.open("wb") as f:
        np.savez(
            f,
            post_ids=posts["post_id"].to_numpy(dtype=str),
            text_sha256=_text_hashes(posts),
            embeddings=embeddings,
        )
    temporary.replace(archive)

    payload = {
        **metadata,
        "format_version": 1,
        "n_rows": len(posts),
        "dimension": EMBEDDING_DIM,
        "dtype": "float32",
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }
    # Publishing metadata last makes interrupted replacements detectable by checksum.
    temporary_meta = directory / "meta.json.tmp"
    temporary_meta.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary_meta.replace(directory / "meta.json")


def load_embeddings(directory: Path, posts: pd.DataFrame) -> np.ndarray:
    """Return cached vectors in the requested post order, checking IDs and text."""
    _validate_posts(posts)
    metadata = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    archive = directory / "embeddings.npz"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != metadata["archive_sha256"]:
        raise ValueError("Embedding archive checksum mismatch; rebuild the cache")

    with np.load(archive, allow_pickle=False) as data:
        positions = pd.Index(data["post_ids"]).get_indexer(posts["post_id"])
        if (positions < 0).any():
            missing = posts.loc[positions < 0, "post_id"].tolist()
            raise KeyError(f"IDs missing from embedding cache: {missing[:5]}")
        if not np.array_equal(data["text_sha256"][positions], _text_hashes(posts)):
            raise ValueError("Post text differs from the embedding cache; rebuild it")
        return data["embeddings"][positions]
