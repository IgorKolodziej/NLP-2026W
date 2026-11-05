from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from clickbait.splits import load_manifest

EMBEDDING_DIM = 384


def encoding_spec(cfg: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_id": cfg["embedding_model"],
        "model_revision": cfg["embeddings"]["revision"],
        "max_seq_length": int(cfg["embeddings"]["max_seq_length"]),
        "normalize_embeddings": bool(cfg["embeddings"]["normalize_embeddings"]),
        "dimension": EMBEDDING_DIM,
        "dtype": "float32",
    }


def _validate_posts(posts: pd.DataFrame) -> None:
    for column in ("post_id", "post_text"):
        if not posts[column].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
            raise ValueError(f"{column} must contain nonempty strings")
    if posts.empty or not posts["post_id"].is_unique:
        raise ValueError("Posts must contain unique IDs and at least one row")


def _text_hashes(posts: pd.DataFrame) -> np.ndarray:
    return np.array([hashlib.sha256(text.encode("utf-8")).hexdigest() for text in posts["post_text"]])


def _validate_vectors(embeddings: np.ndarray, n_rows: int) -> None:
    if embeddings.shape != (n_rows, EMBEDDING_DIM):
        raise ValueError(f"Expected embeddings with shape ({n_rows}, {EMBEDDING_DIM})")
    if embeddings.dtype != np.float32 or not np.isfinite(embeddings).all():
        raise ValueError("Embeddings must be finite float32 values")


def validate_split_coverage(posts: pd.DataFrame, splits_dir: Path) -> dict[str, Any]:
    _validate_posts(posts)
    paths = sorted(splits_dir.glob("*.json"))
    if not paths:
        raise ValueError(f"No split manifests in {splits_dir}")
    available = set(posts["post_id"])
    summary = {}
    for path in paths:
        manifest = load_manifest(path)
        partitions = {"train": manifest.train_ids, "val": manifest.val_ids, "test": manifest.test_ids}
        ids = [post_id for partition in partitions.values() for post_id in partition]
        if any(not partition for partition in partitions.values()):
            raise ValueError(f"{path.stem}: empty partition")
        if len(ids) != len(set(ids)):
            raise ValueError(f"{path.stem}: duplicate or overlapping partition IDs")
        missing = set(ids) - available
        if missing:
            raise ValueError(f"{path.stem}: missing post IDs: {sorted(missing)[:5]}")
        summary[path.stem] = {
            **{name: len(partition) for name, partition in partitions.items()},
            "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return summary


def save_embeddings(
    directory: Path,
    posts: pd.DataFrame,
    embeddings: np.ndarray,
    metadata: dict[str, Any],
) -> None:
    _validate_posts(posts)
    _validate_vectors(embeddings, len(posts))

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


def load_embeddings(directory: Path, posts: pd.DataFrame, cfg: dict[str, Any]) -> np.ndarray:
    """Return vectors in the requested order after checking the encoder, IDs, and text."""
    _validate_posts(posts)
    metadata = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    if metadata["format_version"] != 1:
        raise ValueError("Unsupported embedding cache format")
    for key, expected in encoding_spec(cfg).items():
        if metadata.get(key) != expected:
            raise ValueError(f"Embedding cache {key} differs from configuration; rebuild it")
    archive = directory / "embeddings.npz"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != metadata["archive_sha256"]:
        raise ValueError("Embedding archive checksum mismatch; rebuild the cache")

    with np.load(archive, allow_pickle=False) as data:
        vectors = data["embeddings"]
        _validate_vectors(vectors, len(data["post_ids"]))
        if len(vectors) != metadata["n_rows"]:
            raise ValueError("Embedding row count differs from metadata")
        positions = pd.Index(data["post_ids"]).get_indexer(posts["post_id"])
        if (positions < 0).any():
            missing = posts.loc[positions < 0, "post_id"].tolist()
            raise KeyError(f"IDs missing from embedding cache: {missing[:5]}")
        if not np.array_equal(data["text_sha256"][positions], _text_hashes(posts)):
            raise ValueError("Post text differs from the embedding cache; rebuild it")
        return vectors[positions]
